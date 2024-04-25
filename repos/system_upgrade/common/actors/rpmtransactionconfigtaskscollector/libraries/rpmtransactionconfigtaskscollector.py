import os.path

from leapp.libraries.stdlib import api
from leapp.models import InstalledRedHatSignedRPM, RpmTransactionTasks


def load_tasks_file(path, logger):
    # Loads the given file and converts it to a deduplicated list of strings that are stripped
    if os.path.isfile(path):
        try:
            with open(path, 'r') as f:
                return list(
                    {entry.strip() for entry in f.read().split('\n') if entry.strip() and
                        not entry.strip().startswith('#')}
                )
        except IOError as e:
            logger.warning('Failed to open %s to load additional transaction data. Error: %s', path, str(e))
    return []


def filter_out(installed_rpm_names, to_filter, debug_msg):
    # These are the packages that aren't installed on the system.
    filtered_ok = [pkg for pkg in to_filter if pkg not in installed_rpm_names]

    # And these ones are the ones that are.
    filtered_out = list(set(to_filter) - set(filtered_ok))
    if filtered_out:
        api.current_logger().debug(
            debug_msg +
            '\n- ' + '\n- '.join(filtered_out)
        )
    # We may want to use either of the two sets.
    return filtered_ok, filtered_out


def load_tasks(base_dir, logger):
    # Loads configuration files to_install, to_keep, and to_remove from the given base directory
    rpms = next(api.consume(InstalledRedHatSignedRPM))
    rpm_names = [rpm.name for rpm in rpms.items]

    to_install = load_tasks_file(os.path.join(base_dir, 'to_install'), logger)
    install_debug_msg = 'The following packages from "to_install" file will be ignored as they are already installed:'
    # we do not want to put into rpm transaction what is already installed (it will go to "to_upgrade" bucket)
    to_install_filtered, _ = filter_out(rpm_names, to_install, install_debug_msg)

    to_reinstall = load_tasks_file(os.path.join(base_dir, 'to_reinstall'), logger)
    reinstall_debug_msg = 'The following packages from "to_reinstall" file will be ignored as they are not installed:'
    _, to_reinstall_filtered = filter_out(rpm_names, to_reinstall, reinstall_debug_msg)

    return RpmTransactionTasks(
        to_install=to_install_filtered,
        to_reinstall=to_reinstall_filtered,
        to_keep=load_tasks_file(os.path.join(base_dir, 'to_keep'), logger),
        to_remove=load_tasks_file(os.path.join(base_dir, 'to_remove'), logger))
