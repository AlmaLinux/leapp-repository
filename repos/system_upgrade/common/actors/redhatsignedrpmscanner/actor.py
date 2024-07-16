from leapp.actors import Actor
from leapp.libraries.common import rhui
from leapp.models import InstalledRedHatSignedRPM, InstalledRPM, InstalledUnsignedRPM, VendorSignatures
from leapp.tags import FactsPhaseTag, IPUWorkflowTag


VENDOR_SIGS = {
    'rhel': ['199e2f91fd431d51',
             '5326810137017186',
             '938a80caf21541eb',
             'fd372689897da07a',
             '45689c882fa658e0'],
    'centos': ['24c6a8a7f4a80eb5',
               '05b555b38483c65d',
               '4eb84e71f2ee9d55',
               'a963bbdbf533f4fa',
               '6c7cb6ef305d49d6'],
    'cloudlinux': ['8c55a6628608cb71',
                   'd07bf2a08d50eb66'], # TuxCare
    'almalinux': ['51d6647ec21ad6ea',
                  'd36cb86cb86b3716',
                  '2ae81e8aced7258b',
                  '429785e181b961a5'], # ELevate
    'rocky': ['15af5dac6d745a60',
              '702d426d350d275d'],
    'ol': ['72f97b74ec551f03',
           '82562ea9ad986da3',
           'bc4d06a08d8b756f'],
    'eurolinux': ['75c333f418cd4a9e',
                  'b413acad6275f250',
                  'f7ad3e5a1c9fd080'],
    'scientific': ['b0b4183f192a7d7d']
}

VENDOR_PACKAGERS = {
    "rhel": "Red Hat, Inc.",
    "centos": "CentOS",
    "almalinux": "AlmaLinux Packaging Team",
    "rocky": "infrastructure@rockylinux.org",
    "eurolinux": "EuroLinux",
    "scientific": "Scientific Linux",
}


class RedHatSignedRpmScanner(Actor):
    """Provide data about installed RPM Packages signed by vendors.

    The "Red Hat" in the name of the actor is a historical artifact - the actor
    is used for all vendors present in the config.

    After filtering the list of installed RPM packages by signature, a message
    with relevant data will be produced.
    """

    name = 'red_hat_signed_rpm_scanner'
    consumes = (InstalledRPM, VendorSignatures)
    produces = (InstalledRedHatSignedRPM, InstalledUnsignedRPM,)
    tags = (IPUWorkflowTag, FactsPhaseTag)

    def process(self):
        # Packages from multiple vendors can be installed on the system.
        # Picking the vendor based on the OS release is not enough.
        vendor_keys = sum(VENDOR_SIGS.values(), [])

        for siglist in self.consume(VendorSignatures):
            vendor_keys.extend(siglist.sigs)

        signed_pkgs = InstalledRedHatSignedRPM()
        unsigned_pkgs = InstalledUnsignedRPM()

        env_vars = self.configuration.leapp_env_vars
        # if we start upgrade with LEAPP_DEVEL_RPMS_ALL_SIGNED=1, we consider
        # all packages to be signed
        all_signed = [
            env
            for env in env_vars
            if env.name == 'LEAPP_DEVEL_RPMS_ALL_SIGNED' and env.value == '1'
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
                or all_signed
            )

        def has_katello_prefix(pkg):
            """Whitelist the katello package."""
            return pkg.name.startswith('katello-ca-consumer')

        upg_path = rhui.get_upg_path()
        # AWS RHUI packages do not have to be whitelisted because they are signed by RedHat
        whitelisted_cloud_flavours = (
            'azure',
            'azure-eus',
            'azure-sap-ha',
            'azure-sap-apps',
            'google',
            'google-sap',
            'alibaba'
        )
        whitelisted_cloud_pkgs = {
            rhui.RHUI_CLOUD_MAP[upg_path].get(flavour, {}).get('src_pkg') for flavour in whitelisted_cloud_flavours
        }
        whitelisted_cloud_pkgs.update(
            rhui.RHUI_CLOUD_MAP[upg_path].get(flavour, {}).get('target_pkg') for flavour in whitelisted_cloud_flavours
        )
        whitelisted_cloud_pkgs.update(
            rhui.RHUI_CLOUD_MAP[upg_path].get(flavour, {}).get('leapp_pkg') for flavour in whitelisted_cloud_flavours
        )

        for rpm_pkgs in self.consume(InstalledRPM):
            for pkg in rpm_pkgs.items:
                if any(
                    [
                        has_vendorsig(pkg),
                        is_gpg_pubkey(pkg),
                        has_katello_prefix(pkg),
                        pkg.name in whitelisted_cloud_pkgs,
                    ]
                ):
                    signed_pkgs.items.append(pkg)
                    continue

                unsigned_pkgs.items.append(pkg)

        self.produce(signed_pkgs)
        self.produce(unsigned_pkgs)
