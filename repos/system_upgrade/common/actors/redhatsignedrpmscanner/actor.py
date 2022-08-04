from leapp.actors import Actor
from leapp.models import (
    InstalledRedHatSignedRPM,
    InstalledRPM,
    InstalledUnsignedRPM,
    VendorSignatures,
)
from leapp.tags import FactsPhaseTag, IPUWorkflowTag
from leapp.libraries.common import rhui


VENDOR_SIGS = {
    'rhel': ['199e2f91fd431d51',
             '5326810137017186',
             '938a80caf21541eb',
             'fd372689897da07a',
             '45689c882fa658e0'],
    'centos': ['24c6a8a7f4a80eb5',
               '05b555b38483c65d',
               '4eb84e71f2ee9d55'],
    'cloudlinux': ['8c55a6628608cb71']
}

VENDOR_PACKAGERS = {
    "rhel": "Red Hat, Inc.",
    "centos": "CentOS",
    "cloudlinux": "CloudLinux Packaging Team",
}


class VendorSignedRpmScanner(Actor):
    """Provide data about installed RPM Packages signed by Red Hat.

    After filtering the list of installed RPM packages by signature, a message
    with relevant data will be produced.
    """

    name = "vendor_signed_rpm_scanner"
    consumes = (InstalledRPM, VendorSignatures)
    produces = (
        InstalledRedHatSignedRPM,
        InstalledUnsignedRPM,
    )
    tags = (IPUWorkflowTag, FactsPhaseTag)

    def process(self):
        vendor = self.configuration.os_release.release_id
        vendor_keys = sum(VENDOR_SIGS.values(), [])
        vendor_packager = VENDOR_PACKAGERS.get(vendor, "not-available")

        for siglist in self.consume(VendorSignatures):
            vendor_keys.extend(siglist.sigs)

        self.log.debug("Signature list: {}".format(vendor_keys))

        signed_pkgs = InstalledRedHatSignedRPM()
        unsigned_pkgs = InstalledUnsignedRPM()

        env_vars = self.configuration.leapp_env_vars
        # if we start upgrade with LEAPP_DEVEL_RPMS_ALL_SIGNED=1, we consider
        # all packages to be signed
        all_signed = [
            env
            for env in env_vars
            if env.name == "LEAPP_DEVEL_RPMS_ALL_SIGNED" and env.value == "1"
        ]

        def has_vendorsig(pkg):
            return any(key in pkg.pgpsig for key in vendor_keys)

        def is_gpg_pubkey(pkg):
            """Check if gpg-pubkey pkg exists or LEAPP_DEVEL_RPMS_ALL_SIGNED=1

            gpg-pubkey is not signed as it would require another package
            to verify its signature
            """
            return (  # pylint: disable-msg=consider-using-ternary
                pkg.name == "gpg-pubkey"
                and (pkg.packager.startswith(vendor_packager))
                or all_signed
            )

        def has_katello_prefix(pkg):
            """Whitelist the katello package."""
            return pkg.name.startswith("katello-ca-consumer")

        def is_azure_pkg(pkg):
            """Whitelist Azure config package."""
            arch = self.configuration.architecture

            el7_pkg = rhui.RHUI_CLOUD_MAP[arch]["azure"]["el7_pkg"]
            el8_pkg = rhui.RHUI_CLOUD_MAP[arch]["azure"]["el8_pkg"]
            return pkg.name in [el7_pkg, el8_pkg]

        for rpm_pkgs in self.consume(InstalledRPM):
            for pkg in rpm_pkgs.items:
                if any(
                    [
                        has_vendorsig(pkg),
                        is_gpg_pubkey(pkg),
                        has_katello_prefix(pkg),
                        is_azure_pkg(pkg),
                    ]
                ):
                    signed_pkgs.items.append(pkg)
                    self.log.debug(
                        "Package {} is signed, packager: {}, signature: {}".format(
                            pkg.name, pkg.packager, pkg.pgpsig
                        )
                    )
                    continue

                unsigned_pkgs.items.append(pkg)
                self.log.debug(
                    "Package {} is unsigned, packager: {}, signature: {}".format(pkg.name, pkg.packager, pkg.pgpsig)
                )

        self.produce(signed_pkgs)
        self.produce(unsigned_pkgs)
