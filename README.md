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

**Before doing anything, please read [Leapp framework documentation](https://leapp.readthedocs.io/).**

## Running
Make sure your system is fully updated before starting the elevation process.

Download and execute the preparation script: https://raw.githubusercontent.com/prilr/leapp-repository/cloudlinux/utils/cl_elevate_prepare.sh

Start a preupgrade check. In the meantime, the Leapp utility creates a special /var/log/leapp/leapp-report.txt file that contains possible problems and recommended solutions. No rpm packages will be installed at this phase.

`sudo leapp preupgrade`

> NOTE: In certain configurations, Leapp generates `/var/log/leapp/answerfile` with true/false questions. Leapp utility requires answers to all these questions in order to proceed with the upgrade.

Once the preupgrade process completes, the results will be contained in `/var/log/leapp/leapp-report.txt` file.
It's advised to review the report and consider how the changes will affect your system.

Start an upgrade. You’ll be offered to reboot the system after this process is completed.

```bash
sudo leapp upgrade
sudo reboot
```

A new entry in GRUB called ELevate-Upgrade-Initramfs will appear. The system will be automatically booted into it. See how the update process goes in the console.

After reboot, login to the system and check how the migration went. Verify that the current OS is the one you need.

```bash
cat /etc/redhat-release
cat /etc/os-release
```

Check the leapp logs for .rpmnew configuration files that may have been created during the upgrade process. In some cases os-release or yum package files may not be replaced automatically, requiring the user to rename the .rpmnew files manually.

## How to gather debugging information and create issues
If you encounter an unresolvable issue during an attempt to perform the system upgrade, all relevant information will be placed by leapp in the folder `/var/log/leapp/`.

**You can pack all logs with this command:**

`# tar -czf leapp-logs.tgz /var/log/leapp /var/lib/leapp/leapp.db`

Then you may attach only the `leapp-logs.tgz` file.

When filing an issue, include:
- Steps to reproduce the issue
- *All files in /var/log/leapp*
- */var/lib/leapp/leapp.db*
- *journalctl*
- If you want, you can optionally send anything else would you like to provide (e.g. storage info)

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

The file contains two sections, `mapping` and `repositories`. `repositories` descripes the source and target repositories themselves, while `mapping` establishes connections between them.

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

### Example
Suppose you would like to create an actor to copy a pre-supplied repository file into the upgraded system’s /etc/yum.repos.d.

First, you would create the new actor:
```
cd ./leapp-repository/repos/system_upgrade/common
snactor new-actor addcustomrepositories
```

Since you'd want to run this actor after the upgrade has successfully completed, you’d use the FirstBootPhase tag in its tags field.

```python
	tags = (IPUWorkflowTag, FirstBootPhaseTag)
```

If you wanted to ensure that the actor only runs on AlmaLinux systems, and not on any target OS variant, you could check the release name by importing the corresponding function from leapp API:

```python
from leapp.libraries.common.config import version

	def process(self):
					# We only want to run this actor on AlmaLinux systems.
					# current_version returns a tuple (release_name, version_value).
					if (version.current_version()[0] == "almalinux"):
									copy_custom_repo_files()
```

Files that are accessible by all actors in the repository should be placed into the files/ subdirectory. For the main leapp repository, that directory has the path leapp-repository/repos/system_upgrade/common/files.

Create the subfolder `custom-repos` to place repo files into, then finalize the actor’s code:

```python
import os
import os.path
import shutil

from leapp.libraries.stdlib import api

CUSTOM_REPOS_FOLDER = 'custom-repos'
REPO_ROOT_PATH = "/etc/yum.repos.d"

def copy_custom_repo_files():
		custom_repo_dir = api.get_common_folder_path(CUSTOM_REPOS_FOLDER)

		for repofile in os.listdir(custom_repo_dir):
				full_repo_path = os.path.join(custom_repo_dir, repofile)
				shutil.copy(full_repo_path, REPO_ROOT_PATH)
```

Refer to existing actors and [Leapp documentation](https://leapp.readthedocs.io/) to use more complex functionality in your actors.
