# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details
{
    'name': 'Spiffy Backend Theme - Website Login Addon',
    'category': 'Extra Tools',
    'version': '1.0',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com/',
    'summary': 'This module is an add-on module of Spiffy Backend Theme for the Website Login page design which is compatible with Web Login Design working with both Community and Enterprise Edition.',
    'description': """ This module is an add-on module of Spiffy Backend Theme for the Website Login page design which is compatible with Web Login Design working with both Community and Enterprise Edition. """,
    'depends': ['website',],
    'data': [
        'views/login_page_style.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_frontend': [
            '/spiffy_website_login/static/src/scss/loginpage.scss',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'sequence': 1,
    'installable': True,
    'application': True,
    'price': 20,
    'license': 'OPL-1',
    'currency': 'EUR',
}