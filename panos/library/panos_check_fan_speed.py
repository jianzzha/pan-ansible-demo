#!/usr/bin/python
"""
indeni@PA-5060> show system environmentals

----Thermal----
Slot   Description                         Alarm    Degrees C  Min C   Max C
 S1    Temperature @ 10G Phys [U171]       False    35.00      5.00    60.00
 S1    Temperature @ Jaguar [U172]         False    55.00      5.00    60.00
 S1    Temperature @ Tiger [U173]          False    52.60      5.00    60.00
 S1    Temperature @ Dune [U174]           False    42.50      5.00    60.00

----Fan Tray----
Slot   Description                         Alarm    Inserted
 S1    Fan Tray                            False    True

----Fans----
Slot   Description                         Alarm     RPMs Min RPM
 S1    Fan #1 RPM                          False     7336  2500
 S1    Fan #2 RPM                          False     6705  2500
 S1    Fan #3 RPM                          False     7206  2500
 S1    Fan #4 RPM                          False     7117  2500
 S1    Fan #5 RPM                          False     7284  2500
 S1    Fan #6 RPM                          False     7068  2500
 S1    Fan #7 RPM                          False     7143  2500
 S1    Fan #8 RPM                          False     7117  2500
 S1    Fan #9 RPM                          False     7180  2500
 S1    Fan #10 RPM                         False     7193  2500

----Power----
Slot   Description                         Alarm    Volts  Min V  Max V
 S1    1.0V Power Rail                     False    1.00   0.90   1.10
 S1    1.2V Power Rail                     False    1.20   1.08   1.32
 S1    1.8V Power Rail                     False    1.78   1.62   1.98
 S1    2.5V Power Rail                     False    2.45   2.25   2.75
 S1    3.3V Power Rail                     False    3.32   2.97   3.63
 S1    5.0V Power Rail                     False    4.80   4.50   5.50
 S1    1.15V Power Rail                    False    1.15   1.03   1.26
 S1    1.1V Power Rail                     False    1.10   0.99   1.21
 S1    1.05V Power Rail                    False    1.06   0.94   1.16
 S1    3.3V_SD Power Rail                  False    3.32   2.97   3.63

----Power Supplies----
Slot   Description                         Alarm    Inserted
 S1    Power Supply #1 (left)              True     True
 S1    Power Supply #2 (right)             False    True
"""

from ansible.module_utils.basic import AnsibleModule
import re

def main():
    argument_spec = dict(
        input_str=dict(required=True)
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)
    input_str = module.params['input_str']

    fan_mode = False

    for line in input_str.splitlines():
        # ----Fans---- 
        if re.search('----Fans----', line):
            fan_mode = True
            continue
        if fan_mode is True and re.search('\d+\s+\d+', line):
            # S1    Fan #1 RPM                          False     7336  2500
            fields = line.strip().split()
            min_rpm = int(fields[-1])
            rpm = int(fields[-2])
            alarm = fields[-3]
            fan_slot = fields[0]
            if alarm != "False" or rpm < min_rpm:
                module.exit_json(status="success", fan_error=True, extra_info="Slot {0} Alarm state is {1}, RPM {2}, Min RPM {3}".format(fan_slot, alarm, rpm, min_rpm))
        else:
            continue
    module.exit_json(status="success", fan_error=False)


if __name__ == '__main__':
    main()

