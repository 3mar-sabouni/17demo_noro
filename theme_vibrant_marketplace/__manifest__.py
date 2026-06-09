# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Marketplace Theme Vibrant",
  "summary"              :  """Theme Vibrant Marketplace consists wide range of things, such as font types, sizes, colors and other areas that affect the aesthetics of your site""",
  "category"             :  "Theme/eCommerce",
  "version"              :  "1.0.5",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "description"          :  """Theme Vibrant Marketplace. This Theme is depenedent on theme vibrant and odoo multivendor marketplace, this is aplicable for website only.""",
  "live_test_url"        :  "https://marketplace_vibrant_14.odoothemes.webkul.in",
  "depends"              :  [
                             'odoo_marketplace',
                             'theme_vibrant',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                            #  'view/frontend_assets.xml',
                             'view/templates.xml',
                             'view/snippets.xml',
                             'view/view.xml',
                            ],
  "images"               :  [
                             'static/description/Banner.png',
                             'static/description/vibrant_marketplace_screenshot.gif',
                            ],
  'assets'               :  {
                        'web.assets_frontend': [
                            "/theme_vibrant_marketplace/static/src/scss/product_page_seller.scss",
                            "/theme_vibrant_marketplace/static/src/scss/seller_shop_list.scss",
                            "/theme_vibrant_marketplace/static/src/scss/snippets.scss",
                            "/theme_vibrant_marketplace/static/src/scss/landing_page.scss",
                            "/theme_vibrant_marketplace/static/src/js/main.js",
                            "/theme_vibrant_marketplace/static/src/css/css2.css"
                        ]
                        },
  "application"          :  False,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  51,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}