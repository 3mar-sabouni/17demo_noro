# -*- coding: utf-8 -*-
{
    'name': "dental_management_extension",

    'summary': "",

    'description': """
   """,

    'author': "Babylon tech",
    'website': "https://www.babylontech.com",

    'category': 'Uncategorized',
    'version': '17.0.0.4',
    'depends': ['pragtech_dental_management','account'],
    'data': [
        'security/dental_security.xml',
        'security/ir.model.access.csv',
        'data/mold_data.xml',
        'data/xray_data.xml',
        'data/paper_format.xml',
        'views/medical_mold_views.xml',
        'views/medical_laboratory_views.xml',
        'views/medical_appointment_views.xml',
        'views/teeth_treatment_views.xml',
        'views/medical_physician_views.xml',
        'views/medical_reference_views.xml',
        'views/res_users_views.xml',
        'views/medical_xray_views.xml',
        'views/medical_xray_type_views.xml',
        'views/medical_patient_view.xml',
        'report/report_patient_sticker_template.xml',
        'views/account_payment_views.xml'
    ],
}

