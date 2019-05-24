#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage PaloAltoNetworks Firewall
# (c) 2019, Jianzhu Zhang<jianzhan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: panos_log
short_description: retrieve device log on a PAN-OS device
description:
  - Retrieve log via xapi based on filter and timestamp 
  - See https://github.com/kevinsteves/pan-python/blob/master/doc/pan.xapi.rst for details
author: "Jianzhu Zhang"
version_added: "2.7"
requirements:
  - pan-python
options:
  ip_address:
    description:
      - IP address or host FQDN of the target PAN-OS NVA
    required: true
  username:
    description:
      - User name for a user with admin rights on the PAN-OS NVA
    default: admin
  password:
    description:
      - Password for the given 'username'
    required: true
  log_type:
    description:
      - log type to retrieve
    choices:
      - system 
      - traffic 
    default: system 
  filter:
    description:
      - The filter string to filter log
    required: false
  device_time:
    description:
      - The current time on the remote device, can use show clock to get it
    required: true 
  local_time:
    description:
      - The current time on the ansible host, can use date to get it
    required: false
  local_search_time:
      - The timestamp on the ansible host used to derive the timestamp in the log
    required: false
  delta:
      - The tolerance used to derive the timestamp range in the log, e.g. 30 seconds 
    required: false
extends_documentation_fragment: panos
'''

EXAMPLES = '''

- name: get system restart log based on specified host timestamp 
  panos_log:
    ip_address: "192.168.1.1"
    username: "my-random-admin"
    password: "admin1234"
    filter: "(contains 'System restart')"
    log_type: "system"
    device_time: "{{current_device_time}}"
    local_time: "{{lookup('pipe','date')}}"
    local_search_time: "{{local_search_time}}"
    delta: "600"
'''

RETURN = '''
# Default return values
'''

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

from ansible.module_utils.basic import AnsibleModule

try:
    import pan.xapi
    import xmltodict
    import json
    from dateutil import parser
    from datetime import datetime, timedelta
    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def main():
    argument_spec = dict(
        ip_address=dict(required=True),
        password=dict(required=True, no_log=True),
        username=dict(default='admin'),
        log_type=dict(default="system"),
        log_fields=dict(type="list", default=["severity", "time_generated", "opaque"]),
        filter=dict(default=None),
        device_time=dict(default=None),
        local_time=dict(default=None),
        local_search_time=dict(default=None),
        delta=dict(defult="30")
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)
    if not HAS_LIB:
        module.fail_json(msg='pan-python is required for this module')

    ip_address = module.params["ip_address"]
    password = module.params["password"]
    username = module.params['username']
    log_type = module.params['log_type']
    log_fields = module.params['log_fields']
    filter = module.params['filter']
    device_time = module.params['device_time']
    local_time = module.params['local_time']
    local_search_time = module.params['local_search_time']
    delta=int(module.params['delta'])

    xapi = pan.xapi.PanXapi(
        hostname=ip_address,
        api_username=username,
        api_password=password,
        timeout=60
    )

    # on local host, how many seconds ago the event is received
    if local_search_time is not None:
        host_time_diff = (parser.parse(local_time) - parser.parse(local_search_time)).total_seconds()
    else:
        host_time_diff = 0

    # current device time
    if device_time is not None:
        device_datetime = parser.parse(device_time)
        # corresponding event time on device
        device_event_datetime = device_datetime - timedelta(seconds=host_time_diff)
        # time range lower point on device 
        device_delta_low_datetime = device_event_datetime - timedelta(seconds=delta)

        # filter example (time_generated geq '2019/01/28 04:45:00') and (time_generated leq '2019/01/29 07:30:00')
        time_format = '%Y/%m/%d %H:%M:%S'
        device_event_timestr = device_event_datetime.strftime(time_format)
        device_delta_low_timestr = device_delta_low_datetime.strftime(time_format) 

        # timebased filter
        filter_time = "(time_generated geq '" + device_delta_low_timestr + "')" + " and " + \
                      "(time_generated leq '" + device_event_timestr + "')"

        # combined with user supplied filter
        if filter is not None and len(filter):
            if "(" in filter:
                filter = filter_time + " and " + filter
            else:
                filter = filter_time + " and " + "(" + filter + ")"
        else:
            filter = filter_time

    # retrieve log with filter
    try:
        xapi.log(log_type=log_type, filter=filter, nlogs=500)
    except Exception as e:
        raise Exception("Failed to run log over xmlapi with log_type: '%s', filter: '%s' with the following error: %s" % (log_type, filter_combined, e))
    logs = []
    for element in xapi.element_result.findall('./log/logs/entry'):
        logs.append({field: element.find(field).text for field in log_fields})
    entries = len(logs) 
    module.exit_json(
        status="success",
        logs=logs,
        selected_entries=entries
    )


if __name__ == '__main__':
    main()
