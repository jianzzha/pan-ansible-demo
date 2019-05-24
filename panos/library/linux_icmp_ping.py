#!/usr/bin/env python

from ansible.module_utils.basic import *

DOCUMENTATION = '''
---
module: linux_icmp_ping
short_description: ICMP ping
requirements:
description:
  - From linux machine send ICMP ping to remote device to test connectivity.
options:
  host:
    required: true
      description:
        - IP address or hostname of host to ping
    type: str
author: "Jianzhu Zhang"
'''

EXAMPLES = '''
- name: test icmp ping to the remote host
  linux_icmp_ping:
    host: "1.1.1.1"
'''


def main():
    argument_spec = dict(
        host=dict(required=True)
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    host = module.params['host']
    result = module.run_command('ping -c 2 {}'.format(host))
    failed = (result[0] != 0)
    msg = result[1] if result[1] else result[2]

    module.exit_json(changed=False, failed=failed, msg=msg)


if __name__ == '__main__':
    main()
