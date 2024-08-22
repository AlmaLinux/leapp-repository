# AlmaLinux Leapp Repository

**Before doing anything, please read [Leapp framework documentation](https://leapp.readthedocs.io/).**

## Running
Make sure your system is fully updated before starting the upgrade process.

```bash
sudo yum update -y
```

Install `elevate-release` package with the project repo and GPG key.

`sudo yum install -y http://repo.almalinux.org/elevate/elevate-release-latest-el$(rpm --eval %rhel).noarch.rpm`

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

Start the upgrade. You’ll be offered to reboot the system after this process is completed.

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

Before gathering data, if possible, run the *leapp* command that encountered an issue with the `--debug` flag, e.g.: `leapp upgrade --debug`.

- When filing an issue, include:
  - Steps to reproduce the issue
  - *All files in /var/log/leapp*
  - */var/lib/leapp/leapp.db*
  - *journalctl*
  - If you want, you can optionally send anything else you would like to provide (e.g. storage info)

**For your convenience you can pack all logs with this command:**

`# tar -czf leapp-logs.tgz /var/log/leapp /var/lib/leapp/leapp.db`

Then you may attach only the `leapp-logs.tgz` file.

### Where can I seek help?
We’ll gladly answer your questions and lead you to through any troubles with the actor development.

You can reach us at IRC: `#leapp` on Libera.Chat.
