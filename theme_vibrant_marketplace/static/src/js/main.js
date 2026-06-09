/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

  publicWidget.registry.MarketPlaceInfo = publicWidget.Widget.extend({
    selector: "#seller_other_info",
    start: function () {
      var element = $("#seller_other_info .fa-map-marker");
      if (!(element.length == 0)) {
        $("#seller_other_info>div:first-child").css("display", "block");
      }
    },
  });

  publicWidget.registry.MarketPlaceBrand = publicWidget.Widget.extend({
    selector: ".vb_brands",
    start: function () {
      $.ajax({
        url: "/our/brands",
        type: "GET",
        beforeSend: function () {
          $(".vb_brands").html(
            "<div class='text-center cp-spinner cp-balls outer_div'></div>"
          );
          // console.log($(".vb_brands"));
        },
        complete: function (data) {
          $(".vb_brands .outer_div").replaceWith($(data.responseText));
  
          $(".vb_brands .owl").owlCarousel({
            loop: true,
            dots: false,
            nav: true,
            autoplay: true,
            animateIn: "fadeIn",
            slideTransition: "linear",
            autoplaySpeed: 2000,
            autoplayHoverPause: true,
            responsive: {
              0: {
                items: 4,
              },
              576: {
                items: 4,
              },
              786: {
                items: 5,
              },
              1024: {
                items: 6,
              },
            },
          });
        },
      });
    },
  });

  publicWidget.registry.MarketPlaceSale = publicWidget.Widget.extend({
    selector: "#pink_panther",
    events: {
      "click #recently_product_tab": "removeWebsiteSale",
    },
    start: function () {
      this.removeWebsiteSale($(".oe_website_sale .oe_website_sale"));
    },
    removeWebsiteSale: function (ev) {
      var element = $(document).find(".oe_website_sale .oe_website_sale");
      setTimeout(function (ev) {
        element.removeClass("oe_website_sale");
      }, 1000);
    },
  });

