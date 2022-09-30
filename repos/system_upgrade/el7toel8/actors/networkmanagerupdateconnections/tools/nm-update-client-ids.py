from __future__ import print_function

import sys

import gi

try:
    gi.require_version("NM", "1.0")
except ValueError:
    # If we're missing NetworkManager-libnm, the script won't function.
    print(
        "PyGObject bindings for NetworkManager not found - do you have NetworkManager-libnm installed?"
    )
    print(
        "If you have dhcp=dhclient, you may need to convert your string-formatted client IDs to hexadecimal"
        "to preserve the format they're sent on the wire with. Otherwise, they will now have a zero byte"
        "prepended while being sent."
    )
    sys.exit()

from gi.repository import NM  # noqa: E402; pylint: disable=wrong-import-position


def is_hexstring(s):
    arr = s.split(":")
    for a in arr:
        if len(a) != 1 and len(a) != 2:
            return False
        try:
            int(a, 16)
        except ValueError:
            return False
    return True


client = NM.Client.new(None)
if not client:
    print("Cannot create NM client instance")
    sys.exit(79)

processed = 0
changed = 0
errors = 0

for c in client.get_connections():
    s_ip4 = c.get_setting_ip4_config()
    processed += 1
    if s_ip4 is not None:
        client_id = s_ip4.get_dhcp_client_id()
        if client_id is not None:
            if not is_hexstring(client_id):
                new_client_id = ":".join(hex(ord(x))[2:] for x in client_id)
                s_ip4.set_property(NM.SETTING_IP4_CONFIG_DHCP_CLIENT_ID, new_client_id)
                success = c.commit_changes(True, None)
                if success:
                    changed += 1
                else:
                    errors += 1
                print(
                    "Connection {}: '{}' -> '{}' ({})".format(
                        c.get_uuid(),
                        client_id,
                        new_client_id,
                        "OK" if success else "FAIL",
                    )
                )

print("{} processed, {} changed, {} errors".format(processed, changed, errors))
