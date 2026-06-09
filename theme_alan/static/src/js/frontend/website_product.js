/** @odoo-module **/

import Dialog from '@web/legacy/js/core/dialog';
import publicWidget from "@web/legacy/js/public/public_widget";

export const ProductDetailInfo = publicWidget.Widget.extend({
    selector:".as-product-detail",
    events:{
        'mouseenter .as-pager-prod':'_show_pager_product_info',
        'mouseleave .as-pager-prod':'_hide_pager_product_info',
        'scroll':'_stickyCart',
        'click .as_sticky_action':'_sticky_btn',
    },
    init: function () {
        this._super.apply(this, arguments);
        this.rpc = this.bindService("rpc");
    },
    start: function () {
        new Swiper(".as-al-ass-swiper", {
            slidesPerView: 1.75,
            spaceBetween: 10,
            navigation: {
              nextEl: ".swiper-button-ass-next",
              prevEl: ".swiper-button-ass-prev",
            },
            breakpoints: {
              640: {
                slidesPerView: 2,
                spaceBetween: 24,
              },
              768: {
                slidesPerView: 3,
                spaceBetween: 24,
              },
              1024: {
                slidesPerView: 4,
                spaceBetween: 24,
              },

            },
        });

        new Swiper(".as-al-alt-swiper", {
            slidesPerView: 1.75,
            spaceBetween: 10,
            navigation: {
              nextEl: ".swiper-button-alt-next",
              prevEl: ".swiper-button-alt-prev",
            },
            breakpoints: {
              640: {
                slidesPerView: 2,
                spaceBetween: 24,
              },
              768: {
                slidesPerView: 3,
                spaceBetween: 24,
              },
              1024: {
                slidesPerView: 4,
                spaceBetween: 24,
              },

            },
        });
        this.trigger_up('widgets_start_request', {$target: $(".as_color_variant")});

        return this._super.apply(this, arguments);
    },
    _show_pager_product_info(ev){
        if($(ev.currentTarget).attr('id') == "as-pre-prod-info"){
            this.$target.find(".as-pre-prod-info").removeClass("d-none");
        }else{
            this.$target.find(".as-next-prod-info").removeClass("d-none");
        }
    },
    _hide_pager_product_info(ev){
        this.$target.find(".as-pager-prod-info").addClass("d-none")
    },
    _stickyCart:function(ev){
        var cr = this;
        var addToCartBtns = cr.$target.find('#add_to_cart');
        if(cr.$target.find('.as-sticky-cart-active').length != 0 && addToCartBtns.length != 0){
            const top = cr.$target.find('#add_to_cart').offset().top;
            const bottom = cr.$target.find('#add_to_cart').offset().top + cr.$target.find('#add_to_cart').outerHeight();
            const bottom_screen = $(window).scrollTop() + $(window).innerHeight();
            const top_screen = $(window).scrollTop();
            if ((bottom_screen > top) && (top_screen < bottom)){
                if(cr.$target.find('.as-product-sticky-cart').hasClass("as-stikcy-show")){
                    cr.$target.find('.as-product-sticky-cart').removeClass("as-stikcy-show");
                }
            } else {
                if(top < 0){
                    if(!cr.$target.find('.as-product-sticky-cart').hasClass("as-stikcy-show")){
                        cr.$target.find('.as-product-sticky-cart').addClass("as-stikcy-show");
                    }
                }
            }
        }
        var offset = 450;
        var $back_to_top = $('.as-scroll-to-top');
        ($('#wrapwrap').scrollTop() > offset) ? $back_to_top.addClass('as-bt-visible'): $back_to_top.removeClass('as-bt-visible');
    },
    _sticky_btn:function(ev){
        this.$target.find($(ev.target).data('target_id')).trigger("click");
    },
})

publicWidget.registry.ProductDetailInfo = ProductDetailInfo;


let AlanAdvanceInfo = Dialog.extend({
    events:({ 'click .as_close': 'close',
    }),
    init(ele, otps) {
        this.advance_info_id = otps.advance_info_id;
        this._super(ele, {
            backdrop: true,
            size: 'extra-large',
            technical: false,
            renderHeader: false,
            renderFooter: false,
        });
        this.rpc = this.bindService("rpc");
    },
    willStart: async function () {
        var template = this.rpc('/get_advance_info', { advance_info_id: this.advance_info_id });
        return Promise.all([this._super(...arguments), template]).then((response) => {
            this.$content = $("<div>" + response[1] + "</div>");
        });
    },

    start: function () {
        $(this.$content).appendTo(this.$el);
        this.trigger_up('widgets_start_request', {
            $target: this.$content,
        });
        return this._super.apply(this, arguments);
    },
});

export const ProductAdvanceInfo = publicWidget.Widget.extend({
    "selector": ".show_advance_product",
    events : {
        "click": "_show_advance_info_dialog"
    },
    _show_advance_info_dialog: function(){
        new AlanAdvanceInfo(this, { advance_info_id: parseInt(this.$target.attr("data-info_id")) }).open();
    }
});
publicWidget.registry.ProductAdvanceInfo = ProductAdvanceInfo;

export default {
    ProductDetailInfo: publicWidget.registry.ProductDetailInfo,
    ProductAdvanceInfo: publicWidget.registry.ProductAdvanceInfo,
};
