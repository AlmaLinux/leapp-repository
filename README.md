# Leapp ELevate Repository

**Before doing anything, please read [Leapp framework documentation](https://leapp.readthedocs.io/).**

## Running
Make sure your system is fully updated before starting the upgrade process.

```bash
sudo yum update -y
```

Install `elevate-release` package with the project repo and GPG key.

`sudo yum install -y http://repo.almalinux.org/elevate/elevate-release-latest-el7.noarch.rpm`

Install leapp packages and migration data for the OS you want to upgrade. Possible options are:
  - leapp-data-almalinux
  - leapp-data-centos
  - leapp-data-eurolinux
  - leapp-data-oraclelinux
  - leapp-data-rocky

`sudo yum install -y leapp-upgrade leapp-data-almalinux`

Start a preupgrade check. In the meantime, the Leapp utility creates a special /var/log/leapp/leapp-report.txt file that contains possible problems and recommended solutions. No rpm packages will be installed at this phase.

`sudo leapp preupgrade`

The preupgrade process may stall with the following message:
> Inhibitor: Newest installed kernel not in use

Make sure your system is running the latest kernel before proceeding with the upgrade. If you updated the system recently, a reboot may be sufficient to do so. Otherwise, edit your Grub configuration accordingly.

> NOTE: In certain configurations, Leapp generates `/var/log/leapp/answerfile` with true/false questions. Leapp utility requires answers to all these questions in order to proceed with the upgrade.

Once the preupgrade process completes, the results will be contained in `/var/log/leapp/leapp-report.txt` file.
It's advised to review the report and consider how the changes will affect your system.

Start an upgrade. You’ll be offered to reboot the system after this process is completed.

```bash
sudo leapp upgrade
sudo reboot
```

> NOTE: The upgrade process after the reboot may take a long time, up to 40-50 minutes, depending on the machine resources. If the machine remains unresponsive for more than 2 hours, assume the upgrade process failed during the post-reboot phase.
> If it's still possible to access the machine in some way, for example, through remote VNC access, the logs containing the information on what went wrong are located in this folder: `/var/log/leapp`

A new entry in GRUB called ELevate-Upgrade-Initramfs will appear. The system will be automatically booted into it. Observe the update process in the console.

After the reboot, login into the system and check the migration report. Verify that the current OS is the one you need.

```bash
cat /etc/redhat-release
cat /etc/os-release
```

Check the leapp logs for .rpmnew configuration files that may have been created during the upgrade process. In some cases os-release or yum package files may not be replaced automatically, requiring the user to rename the .rpmnew files manually.

## Troubleshooting

### Where can I report an issue or RFE related to the framework or other actors?

- GitHub issues are preferred:
  - Leapp framework: [https://github.com/oamg/leapp/issues/new/choose](https://github.com/oamg/leapp/issues/new/choose)
  - Leapp actors: [https://github.com/oamg/leapp-repository/issues/new/choose](https://github.com/oamg/leapp-repository/issues/new/choose)

### Where can I report an issue or RFE related to the AlmaLinux actor or data modifications?
- GitHub issues are preferred:
  - Leapp actors: [https://github.com/AlmaLinux/leapp-repository/issues/new/choose](https://github.com/AlmaLinux/leapp-repository/issues/new/choose)
  - Leapp data: [https://github.com/AlmaLinux/leapp-data/issues/new/choose](https://github.com/AlmaLinux/leapp-data/issues/new/choose)

### What data should be provided when making a report?

- When filing an issue, include:
  - Steps to reproduce the issue
  - *All files in /var/log/leapp*
  - */var/lib/leapp/leapp.db*
  - *journalctl*
  - If you want, you can optionally send anything else would you like to provide (e.g. storage info)

**For your convenience you can pack all logs with this command:**

`# tar -czf leapp-logs.tgz /var/log/leapp /var/lib/leapp/leapp.db`

Then you may attach only the `leapp-logs.tgz` file.

### Where can I seek help?
We’ll gladly answer your questions and lead you to through any troubles with the actor development.

You can reach the primary Leapp development team at IRC: `#leapp` on freenode.

## Third-party integration

If you would like to add your **signed** 3rd party packages into the upgrade process, you can use the third-party integration mechanism.

There are four components for adding your information to the elevation process:
- <vendor_name>_map.json: repository mapping file
- <vendor_name>.repo: package repository information
- <vendor_name>.sigs: list of package signatures of vendor repositories
- <vendor_name>_pes.json: package migration event list

All these files **must** have the same <vendor_name> part.

### Repository mapping file

This JSON file provides information on mappings between source system repositories (repositories present on the system being upgraded) and target system repositories (package repositories to be used during the upgrade).

The file contains two sections, `mapping` and `repositories`.

`repositories` descripes the source and target repositories themselves. Each entry should have a unique string ID specific to mapping/PES files - `pesid`, and a list of attributes:
- major_version: major system version that this repository targets
- repo_type: repository type, see below
- repoid: repository ID, same as in *.repo files. Doesn't have to exactly match `pesid`
- arch: system architecture for which this repository is relevant
- channel: repository channel, see below


**Repository types**:
- rpm: normal RPM packages
- srpm: source packages
- debuginfo: packages with debug information

**Repository channels**:
- ga: general availability repositories
  - AKA stable repositories.
- beta: beta-testing repositories
- eus, e4s, aus, tus: Extended Update Support, Update Services for SAP Solutions, Advanced Update Support, Telco Extended Update Support
  - Red Hat update channel classification. Most of the time you won't need to use these.

`mapping` establishes connections between described repositories.
Each entry in the list defines a mapping between major system versions, and contains the following elements:
- source_major_version: major system version from which the system would be upgraded
- target_major_version: major system version to which the system would be elevated
- entries: the list of repository mappings
  - source: source repository, one that would be found on a pre-upgrade system
  - target: a list of target upgrade repositores that would contain new package versions. Each source repository can map to one or multiple target repositories


> **Important**: The repository mapping file also defines whether a vendor's packages will be included into the upgrade process at all.
> If at least one source repository listed in the file is present on the system, the vendor is considered active, and package repositories/PES events are enabled - otherwise, they **will not** affect the upgrade process.

### Package repository information

This file defines the vendor's package repositories to be used during the upgrade.

The file has the same format normal YUM/DNF package repository files do.

> NOTE: The repositories listed in this file are only used *during* the upgrade. Package repositories on the post-upgrade system should be provided through updated packages or custom repository deployment.

### Package signature list

This file should contain the list of public signature headers that the packages are signed with, one entry per line.

You can find signature headers for your packages by running the following command:

`rpm -qa --queryformat "%{NAME} || %|DSAHEADER?{%{DSAHEADER:pgpsig}}:{%|RSAHEADER?{%{RSAHEADER:pgpsig}}:{(none)}|}|\n" <PACKAGE_NAME>`

rpm will return an entry like the following:
`package-name || DSA/SHA1, Mon Aug 23 08:17:13 2021, Key ID 8c55a6628608cb71`

The value after "Key ID", in this case, `8c55a6628608cb71`, is what you should put into the signature list file.

### Package migration event list

The Leapp upgrade process uses information from the AlmaLinux PES (Package Evolution System) to keep track of how packages change between the OS versions. This data is located in `leapp-data/vendors.d/<vendor_name>_pes.json` in the GitHub repository and in `/etc/leapp/files/vendors.d/<vendor_name>_pes.json` on a system being upgraded.

> **Warning**: leapp doesn't force packages from out_packageset to be installed from the specific repository; instead, it enables repo from out_packageset and then DNF installs the latest package version from all enabled repos.

#### Creating event lists through PES

The recommended way to create new event lists is to use the PES mechanism.

The web interface can create, manage and export groups of events to JSON files.

This video demonstration walks through the steps of adding an action event group and exporting it as a JSON file to make use of it in the elevation process.

> https://drive.google.com/file/d/1VqnQkUsxzLijIqySMBGu5lDrA72BVd5A/view?usp=sharing

Please refer to the [PES contribution guide](https://wiki.almalinux.org/elevate/Contribution-guide.html) for additional information on entry fields.

#### Manual editing

To add new rules to the list, add a new entry to the `packageinfo` array.

**Important**: actions from PES JSON files will be in effect only for those packages that are signed **and** have their signatures in one of the active <vendor_name>.sigs files. Unsigned packages will be updated only if some signed package requires a new version, otherwise they will by left as they are.

Required fields:

- action: what action to perform on the listed package
- 0 - present
- 1 - removed
- 2 - deprecated
- 3 - replaced
- 4 - split
- 5 - merged
- 6 - moved to new repository
- 7 - renamed
- arches: what system architectures the listed entry relates to
- id: entry ID, must be unique
- in_packageset: set of packages on the old system
- out_packageset: set of packages to switch to, empty if removed or deprecated
- initial_release: source OS release
- release: target OS release

`in_packageset` and `out_packageset` have the following format:

```json
      "in_packageset": {
        "package": [
          {
            "module_stream": null,
            "name": "PackageKit",
            "repository": "base"
          },
          {
            "module_stream": null,
            "name": "PackageKit-yum",
            "repository": "base"
          }
        ],
        "set_id": 1592
      },
```

For `in_packageset`, `repository` field defines the package repository the package was installed from on the source system.
For `out_packageset`, `repository` field for packages should be the same as the "Target system repo name in PES" field in the associated vendor repository mapping file.

### Providing the data

Once you've prepared the vendor data for migration, you can make a pull request to https://github.com/AlmaLinux/leapp-data/ to make it available publicly.
Files should be placed into the `vendors.d` subfolder if the data should be available for all elevation target OS variants, or into the `files/<target_OS>/vendors.d/` if intended for a specific one.

Alternatively, you can deploy the vendor files on a system prior to starting the upgrade. In this case, place the files into the folder `/etc/leapp/files/vendors.d/`.

## Adding complex changes (custom actors for migration)
To perform any changes of arbitrary complexity during the migration process, add a component to the existing Leapp pipeline.

To begin, clone the code repository: https://github.com/AlmaLinux/leapp-repository
For instructions on how to deploy a development enviroment, refer to [Leapp framework documentation](https://leapp.readthedocs.io/en/latest/devenv-install.html).

Create an actor inside the main system_upgrade leapp repository:

```bash
cd ./leapp-repository/repos/system_upgrade/common
snactor new-actor testactor
```

Alternatively, you can [create your own repository](https://leapp.readthedocs.io/en/latest/create-repository.html) in the system_upgrade folder, if you wish to keep your actors separate from others.
Keep in mind that you’ll need to link all other repositories whose functions you will use.
The created subfolder will contain the main Python file of your new actor.

The actor’s main class has three fields of interest:
- consumes
- produces
- tags

consumes and produces defines the [data that the actor may receive or provide to other actors](https://leapp.readthedocs.io/en/latest/messaging.html).

Tags define the phase of the upgrade process during which the actor runs.
All actors also must be assigned the `IPUWorkflowTag` to mark them as a part of the in-place upgrade process.
The file `leapp-repository/repos/system_upgrade/common/workflows/inplace_upgrade.py` lists all phases of the elevation process.

### Submitting changes
Changes you want to submit upstream should be sent through pull requests to repositories https://github.com/AlmaLinux/leapp-repository and https://github.com/AlmaLinux/leapp-data.
The standard GitHub contribution process applies - fork the repository, make your changes inside of it, then submit the pull request to be reviewed.

### Custom actor example

"Actors" in Leapp terminology are Python scripts that run during the upgrade process.
Actors are a core concept of the framework, and the entire process is built from them.

Custom actors are the actors that are added by third-party developers, and are not present in the upstream Leapp repository.

Actors can gather data, communicate with each other and modify the system during the upgrade.

Let's examine how an upgrade problem might be resolved with a custom actor.

#### Problem

If you ever ran `leapp preupgrade` on unprepared systems before, you likely have seen the following message:

```
Upgrade has been inhibited due to the following problems:
    1. Inhibitor: Possible problems with remote login using root account
```

It's caused by the change in default behaviour for permitting root logins between RHEL 7 and 8.
In RHEL 8 logging in as root via password authentication is no longer allowed by default, which means that some machines can become inaccessible after the upgrade.

Some configurations require an administrator's intervention to resolve this issue, but SSHD configurations where no `PermitRootLogin` options were explicitly set can be modified to preserve the RHEL 7 default behaviour and not require manual modification.

Let's create a custom actor to handle such cases for us.

#### Creating an actor

Actors are contained in ["repositories"](https://leapp.readthedocs.io/en/latest/leapp-repositories.html) - subfolders containing compartmentalized code and resources that the Leapp framework will use during the upgrade.

> Do not confuse Leapp repositories with Git repositories - these are two different concepts, independent of one another.

Inside the `leapp-repository` GitHub repo, Leapp repositories are contained inside the `repos` subfolder.

Everything related to system upgrade proper is inside the `system_upgrade` folder.
`el7toel8` contains resources used when upgrading from RHEL 7 to RHEL 8, `el8toel9` - RHEL 8 to 9, `common` - shared resources.

Since the change in system behaviour we're looking to mitigate occurs between RHEL 7 and 8, the appopriate repository to place the actor in is `el7toel8`.

You can [create new actors](https://leapp.readthedocs.io/en/latest/first-actor.html) by using the `snactor` tool provided by Leapp, or manually.

`snactor new-actor ACTOR_NAME`

The bare-bones actor code consists of a file named `actor.py` contained inside the `actors/<actor_name>` subfolder of a Leapp repository.

In this case, then, it should be located in a directory like `leapp-repository/repos/system_upgrade/el7toel8/actors/opensshmodifypermitroot`

If you used snactor to create it, you'll see contents like the following:

```python
from leapp.actors import Actor


class OpenSSHModifyPermitRoot(Actor):
    """
    No documentation has been provided for the open_ssh_actor_example actor.
    """

    name = 'openssh_modify_permit_root'
    consumes = ()
    produces = ()
    tags = ()

    def process(self):
        pass
```

#### Configuring the actor

Actors' `consumes` and `produces` attributes define types of [*messages*](https://leapp.readthedocs.io/en/latest/messaging.html) these actors receive or send.

For instance, during the initial upgrade stages several standard actors gather system information and *produce* messages with gathered data to other actors.

> Messages are defined by *message models*, which are contained inside Leapp repository's `models` subfolder, just like all actors are contained in `actors`.

Actors' `tags` attributes define the [phase of the upgrade](https://leapp.readthedocs.io/en/latest/working-with-workflows.html) during which that actor gets executed.

> The list of all phases can be found in file `leapp-repository/repos/system_upgrade/common/workflows/inplace_upgrade.py`.

##### Receiving messages

Leapp already provides information about the OpenSSH configuration through the `OpenSshConfigScanner` actor. This actor provides a message with a message model `OpenSshConfig`.

Instead of opening and reading the configuration file in our own actor, we can simply read the provided message to see if we can safely alter the configuration automatically.

To begin with, import the message model from `leapp.models`:

```python
from leapp.models import OpenSshConfig
```

> It doesn't matter in which Leapp repository the model is located. Leapp will gather all availabile data inside its submodules.

Add the message model to the list of messages to be received:

```python
consumes = (OpenSshConfig, )
```

The actor now will be able to read messages of this format provided by other actors that were executed prior to its own execution.

##### Sending messages

To ensure that the user knows about the automatic configuration change that will occur, we can send a *report*.

> Reports are a built-in type of Leapp messages that are added to the `/var/log/leapp/leapp-report.txt` file at the end of the upgrade process.

To start off with, add a Report message model to the `produces` attribute of the actor.

```python
produces = (Report, )
```

Don't forget to import the model type from `leapp.models`.

All done - now we're ready to make use of the models inside the actor's code.


##### Running phase

Both workflow and phase tags are imported from leapp.tags:

```python
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag
```

All actors to be run during the upgrade must contain the upgrade workflow tag. It looks as follows:

```python
tags = (IPUWorkflowTag, )
```

To define the upgrade phase during which an actor will run, set the appropriate tag in the `tags` attribute.

Standard actor `OpenSshPermitRootLoginCheck` that blocks the upgrade if it detects potential problems in SSH configuration, runs during the *checks* phase, and has the `ChecksPhaseTag` inside its `tags`.

Therefore, we want to run our new actor before it. We can select an earlier phase from the list of phases - or we can mark our actor to run *before other actors* in the phase with a modifier as follows:

```python
tags = (ChecksPhaseTag.Before, IPUWorkflowTag, )
```

All phases have built-in `.Before` and `.After` stages that can be used this way. Now our actor is guaranteed to be run before the `OpenSshPermitRootLoginCheck` actor.


#### Actor code

With configuration done, it's time to write the actual code of the actor that will be executed during the upgrade.

The entry point for it is the actor's `process` function.

First, let's start by reading the SSH config message we've set the actor to receive.

```python
# Importing from Leapp built-ins.
from leapp.exceptions import StopActorExecutionError
from leapp.libraries.stdlib import api

def process(self):
    # Retreive the OpenSshConfig message.

    # Actors have `consume` and `produce` methods that work with messages.
    # `consume` expects a message type that is listed inside the `consumes` attribute.
    openssh_messages = self.consume(OpenSshConfig)

    # The return value of self.consume is an iterator.
    config = next(openssh_messages, None)
    # We expect to get only one message of this type. If there's more than one, something's wrong.
    if list(openssh_messages):
        # api.current_logger lets you pass messages into Leapp's log. By default, they will
        # be displayed in `/var/log/leapp/leapp-preupgrade.log`
        # or `/var/log/leapp/leapp-upgrade.log`, depending on which command you ran.
        api.current_logger().warning('Unexpectedly received more than one OpenSshConfig message.')
    # If the config message is not present, the standard actor failed to read it.
    # Stop here.
    if not config:
        # StopActorExecutionError is a Leapp built-in exception type that halts the actor execution.
        # By default this will also halt the upgrade phase and the upgrade process in general.
        raise StopActorExecutionError(
            'Could not check openssh configuration', details={'details': 'No OpenSshConfig facts found.'}
        )
```

Next, let's read the received message and see if we can modify the configuration.

```python
import errno

CONFIG = '/etc/ssh/sshd_config'

    # The OpenSshConfig model has a permit_root_login attribute that contains
    # all instances of PermitRootLogin option present in the config.
    # See leapp-repository/repos/system_upgrade/el7toel8/models/opensshconfig.py

    # We can only safely modify the config to preserve the default behaviour if no
    # explicit PermitRootLogin option was set anywhere in the config.
    if not config.permit_root_login:
        try:
            # Read the config into memory to prepare for its modification.
            with open(CONFIG, 'r') as fd:
                sshd_config = fd.readlines()

                # If the last line of the config doesn't have a newline, add it.
                if sshd_config[-1][-1] != '\n':
                    sshd_config[-1].append('\n')

                # These are the lines we want to add to the configuration file.
                permit_autoconf = [
                    "\n",
                    "# Automatically added by Leapp to preserve RHEL7 default\n",
                    "# behaviour after migration.\n",
                    "PermitRootLogin yes\n"
                ]
                sshd_config.extend(permit_autoconf)
            # Write the changed config into the file.
            with open(CONFIG, 'w') as fd:
                fd.writelines(sshd_config)

        # Handle errors.
        except IOError as err:
            if err.errno != errno.ENOENT:
                error = 'Failed to open sshd_config: {}'.format(str(err))
                api.current_logger().error(error)
            return
```

The functional part of the actor itself is done. Now, let's add a report to let the user know
the machine's SSH configuration has changed.

```python
from leapp import reporting
from leapp.models import Report
from leapp.reporting import create_report

# Tags signify the categories the report and the associated issue are related to.
COMMON_REPORT_TAGS = [
    reporting.Tags.AUTHENTICATION,
    reporting.Tags.SECURITY,
    reporting.Tags.NETWORK,
    reporting.Tags.SERVICES
]

    # Related resources are listed in the report to help resolving the issue.
    resources = [
        reporting.RelatedResource('package', 'openssh-server'),
        reporting.RelatedResource('file', '/etc/ssh/sshd_config')
    ]
    # This function creates and submits the actual report message.
    # Normally you'd need to call self.produce() to send messages,
    # but reports are a special case that gets handled automatically.
    create_report([
        # Report title and summary.
        reporting.Title('SSH configuration automatically modified to permit root login'),
        reporting.Summary(
            'Your OpenSSH configuration file does not explicitly state '
            'the option PermitRootLogin in sshd_config file. '
            'Its default is "yes" in RHEL7, but will change in '
            'RHEL8 to "prohibit-password", which may affect your ability '
            'to log onto this machine after the upgrade. '
            'To prevent this from occuring, the PermitRootLogin option '
            'has been explicity set to "yes" to preserve the default behaivour '
            'after migration.'
        ),
        # Reports are ordered by severity in the list.
        reporting.Severity(reporting.Severity.MEDIUM),
        reporting.Tags(COMMON_REPORT_TAGS),
        # Remediation section contains hints on how to resolve the reported (potential) problem.
        reporting.Remediation(
            hint='If you would prefer to configure the root login policy yourself, '
                    'consider setting the PermitRootLogin option '
                    'in sshd_config explicitly.'
        )
    ] + resources)
```

The actor code is now complete. The final version with less verbose comments will look something like this:

```python
from leapp import reporting
from leapp.actors import Actor
from leapp.exceptions import StopActorExecutionError
from leapp.libraries.stdlib import api
from leapp.models import OpenSshConfig, Report
from leapp.reporting import create_report
from leapp.tags import ChecksPhaseTag, IPUWorkflowTag

import errno

CONFIG = '/etc/ssh/sshd_config'

COMMON_REPORT_TAGS = [
    reporting.Tags.AUTHENTICATION,
    reporting.Tags.SECURITY,
    reporting.Tags.NETWORK,
    reporting.Tags.SERVICES
]


class OpenSSHModifyPermitRoot(Actor):
    """
    OpenSSH doesn't allow root logins with password by default on RHEL8.

    Check the values of PermitRootLogin in OpenSSH server configuration file
    and see if it was set explicitly.
    If not, adding an explicit "PermitRootLogin yes" will preserve the current
    default behaviour.
    """

    name = 'openssh_modify_permit_root'
    consumes = (OpenSshConfig, )
    produces = (Report, )
    tags = (ChecksPhaseTag.Before, IPUWorkflowTag, )

    def process(self):
        # Retreive the OpenSshConfig message.
        openssh_messages = self.consume(OpenSshConfig)
        config = next(openssh_messages, None)
        if list(openssh_messages):
            api.current_logger().warning('Unexpectedly received more than one OpenSshConfig message.')
        if not config:
            raise StopActorExecutionError(
                'Could not check openssh configuration', details={'details': 'No OpenSshConfig facts found.'}
            )

        # Read and modify the config.
        # Only act if there's no explicit PermitRootLogin option set anywhere in the config.
        if not config.permit_root_login:
            try:
                with open(CONFIG, 'r') as fd:
                    sshd_config = fd.readlines()

                    # If the last line of the config doesn't have a newline, add it.
                    if sshd_config[-1][-1] != '\n':
                        sshd_config[-1].append('\n')

                    permit_autoconf = [
                        "\n",
                        "# Automatically added by Leapp to preserve RHEL7 default\n",
                        "# behaviour after migration.\n",
                        "PermitRootLogin yes\n"
                    ]
                    sshd_config.extend(permit_autoconf)
                with open(CONFIG, 'w') as fd:
                    fd.writelines(sshd_config)

            except IOError as err:
                if err.errno != errno.ENOENT:
                    error = 'Failed to open sshd_config: {}'.format(str(err))
                    api.current_logger().error(error)
                return

            # Create a report letting the user know what happened.
            resources = [
                reporting.RelatedResource('package', 'openssh-server'),
                reporting.RelatedResource('file', '/etc/ssh/sshd_config')
            ]
            create_report([
                reporting.Title('SSH configuration automatically modified to permit root login'),
                reporting.Summary(
                    'Your OpenSSH configuration file does not explicitly state '
                    'the option PermitRootLogin in sshd_config file. '
                    'Its default is "yes" in RHEL7, but will change in '
                    'RHEL8 to "prohibit-password", which may affect your ability '
                    'to log onto this machine after the upgrade. '
                    'To prevent this from occuring, the PermitRootLogin option '
                    'has been explicity set to "yes" to preserve the default behaivour '
                    'after migration.'
                ),
                reporting.Severity(reporting.Severity.MEDIUM),
                reporting.Tags(COMMON_REPORT_TAGS),
                reporting.Remediation(
                    hint='If you would prefer to configure the root login policy yourself, '
                            'consider setting the PermitRootLogin option '
                            'in sshd_config explicitly.'
                )
            ] + resources)
```

Due to this actor's small size, the entire code can be fit inside the `process()` function.

#### Libraries

Larger actors can import code from [common libraries](https://leapp.readthedocs.io/en/latest/best-practices.html#move-generic-functionality-to-libraries) or define their own "libraries" and run code from them inside the `process()` function.

In such cases, the directory layout looks like this:
```
actors
+  example_actor_name
|  + libraries
|       + example_actor_name.py
|  + actor.py
...
```

and importing code from them looks like this:

`from leapp.libraries.actor.example_actor_name import example_lib_function`

This is also the main way of [writing unit-testable code](https://leapp.readthedocs.io/en/latest/best-practices.html#write-unit-testable-code), since the code contained inside the `process()` function cannot be unit-tested normally.

#### Debugging

The Leapp utility `snactor` can also be used for unit-testing the created actors.

It is capable of saving the output of actors as locally stored messages, so that they can be consumed by other actors that are being developed.

We need the OpenSshConfig message, which is produced by the OpenSshConfigScanner standard actor. To make the data consumable, run the actor producing the data with the –save-output option:

`snactor run --save-output OpenSshConfigScanner`

The output of the actor is stored in the local repository data file, and it can be used by other actors. To flush all saved messages from the repository database, run `snactor messages clear`.

With the input messages available and stored, the actor being developed can be tested.

`snactor run --print-output OpenSshModifyPermitRoot`

#### Additional information

For more information about Leapp and additional tutorials, visit the (official Leapp documentation)[https://leapp.readthedocs.io/en/latest/tutorials.html].
