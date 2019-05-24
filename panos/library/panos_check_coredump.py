#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

from ansible.module_utils.basic import AnsibleModule

from datetime import datetime, timedelta
from dateutil import parser
import re


def main():
    argument_spec = dict(
        input_str=dict(required=True),
        local_time=dict(required=True),
        local_search_time=dict(required=True),
        device_time = dict(required=True),
        delta=dict(default='30')
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)
    input_str = module.params['input_str']
    local_time = module.params['local_time']
    local_search_time = module.params['local_search_time']
    device_time = module.params['device_time']
    delta = int(module.params['delta'])

    now = datetime.now()
    for line in input_str.splitlines():
        # /var/cores/:
        m = re.search('(/.*):$', line)
        if m:
            dirname = m.group(1)
            if not dirname.endswith('/'):
                dirname += '/'
            continue

        # drwxr-xr-x 2 root root 4.0K Feb 12 12:37 crashinfo
        fields = line.strip().split()
        if len(fields) > 5:
            # skip directory which starts with letter d
            if line.startswith('d'):
                continue
            if re.search('core', dirname):
                if re.search(':', fields[-2]):
                    hour_min = fields[-2]
                    year = now.year
                else:
                    year = fields[-2]
                    hour_min = None
                coredump = dirname + fields[-1]
                month = fields[-4]
                day = fields[-3]
                if hour_min is not None:
                    hour, minute = hour_min.split(':')
                else:
                    hour = '0'
                    minute = '0'
                # device_time: Wed Apr 10 00:46:45 PDT 2019
                device_tz = device_time.split()[-2]
                coredump_datetime = parser.parse("%s %s %s:%s:00 %s %s" %(month, day, hour, minute, device_tz, year))
                local_datetime = parser.parse(local_time)
                local_search_datetime = parser.parse(local_search_time)
                host_time_diff = (local_datetime - local_search_datetime).total_seconds()
                device_datetime = parser.parse(device_time)
                device_event_datetime = device_datetime - timedelta(seconds=host_time_diff)
                if abs((device_event_datetime - coredump_datetime).total_seconds()) < delta:
                    module.exit_json(status="success", found_coredump="True", extra_info="%s" % (coredump))
    module.exit_json(status="success", found_coredump="False")


if __name__ == '__main__':
    main()


