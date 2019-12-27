{
    'name': 'Multiple Employee Contract',
    'version': '1.0',
    'author': 'Al Kidhma Group',
    'website': '',
    'summary': 'Create Multiple Contract at a same time.',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'depends': ['hr_payroll', 'resource', 'hr_automatic_leave_alloc'],
    'data': [
            'wizard/mutli_employee_contract.xml',
            'wizard/employee_form_contract.xml',
            'views/hr_job.xml',
            'views/hr_employee.xml',

    ],
    'description': """
        This module helps to create multiple employee's contracts from a
        wizard only if the previous contract is in expired state.
    """,
    'images': [],
    'auto_install': False,
    'installable': True,
    'application': True,
}
