/** @odoo-module **/

    import { _t } from "@web/core/l10n/translation";
    var flag = 0;

    $(document).ready(function() {
        var oe_website_sale = this;
        var $payment = $("panel panel-default");
        var $carrier = $("#delivery_carrier");
        var payment_form = $('.o_payment_form');

        payment_form.find('.o_outline').each(function(){
          if($(this).find('label').length == 0){
             $(this).hide();
          }
        });

        if(payment_form.find('.card-body').css('display') == 'none'){
          payment_form.parent().hide()
        }

    });