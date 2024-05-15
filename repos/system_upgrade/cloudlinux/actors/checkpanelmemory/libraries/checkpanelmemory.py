from leapp import reporting
from leapp.exceptions import StopActorExecutionError
from leapp.libraries.stdlib import api
from leapp.models import MemoryInfo, InstalledControlPanel

from leapp.libraries.common.detectcontrolpanel import (
    NOPANEL_NAME,
    UNKNOWN_NAME,
    INTEGRATED_NAME,
    CPANEL_NAME,
)

required_memory = {
    NOPANEL_NAME: 1536 * 1024,  # 1.5 Gb
    UNKNOWN_NAME: 1536 * 1024,  # 1.5 Gb
    INTEGRATED_NAME: 1536 * 1024,  # 1.5 Gb
    CPANEL_NAME: 2048 * 1024,  # 2 Gb
}

# The kernel subtracts memory pages used for its own overhead from the total
# memory reported to userspace. The subtracted amount varies depending on a
# variety of factors, but based on a few samples, it seems to use somewhere
# between 50-75 MiB on a 2 GiB machine, not counting memory reserved for the
# crash kernel.  Allow for a little more than this to be missing from the total
# before this check is considered a failure.
ALLOWABLE_OVERHEAD = 96 * 1024  # 96 MiB


def _check_memory(panel, mem_info):
    msg = {}

    min_req = required_memory[panel]
    is_ok = mem_info.mem_total >= min_req - ALLOWABLE_OVERHEAD
    msg = {} if is_ok else {"detected": mem_info.mem_total, "minimal_req": min_req}

    return msg


def process():
    panel = next(api.consume(InstalledControlPanel), None)
    memoryinfo = next(api.consume(MemoryInfo), None)
    if panel is None:
        raise StopActorExecutionError(message=("Missing information about the installed web panel."))
    if memoryinfo is None:
        raise StopActorExecutionError(message=("Missing information about system memory."))

    minimum_req_error = _check_memory(panel.name, memoryinfo)

    if minimum_req_error:
        title = "Minimum memory requirements for panel {} are not met".format(panel.name)
        summary = (
            "Insufficient memory may result in an instability of the upgrade process."
            " This can cause an interruption of the process,"
            " which can leave the system in an unusable state. Memory detected:"
            " {} KiB, required: {} KiB".format(minimum_req_error["detected"], minimum_req_error["minimal_req"])
        )
        reporting.create_report(
            [
                reporting.Title(title),
                reporting.Summary(summary),
                reporting.Severity(reporting.Severity.HIGH),
                reporting.Tags([reporting.Tags.SANITY]),
                reporting.Flags([reporting.Flags.INHIBITOR]),
            ]
        )
