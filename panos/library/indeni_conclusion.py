#!/usr/bin/python
  
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

from ansible.module_utils.basic import AnsibleModule

def main():
    argument_spec = dict(
        triage_conclusion=dict(required=False, default=""),
        triage_conclusion_title=dict(required=False, default=""),
        triage_has_conclusion=dict(required=False, default=False, type='bool'),
        triage_remediation_steps=dict(required=False, default=""),
        triage_has_remediation_steps=dict(required=False, default=False, type='bool')
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)
    triage_conclusion = module.params['triage_conclusion']
    triage_conclusion_title = module.params['triage_conclusion_title']
    triage_has_conclusion = module.params['triage_has_conclusion']
    triage_remediation_steps = module.params['triage_remediation_steps']
    triage_has_remediation_steps = module.params['triage_has_remediation_steps']
    module.exit_json(status="success", triage_conclusion=triage_conclusion, triage_has_conclusion=triage_has_conclusion, triage_conclusion_title=triage_conclusion_title, triage_remediation_steps=triage_remediation_steps, triage_has_remediation_steps=triage_has_remediation_steps)


if __name__ == '__main__':
    main()

