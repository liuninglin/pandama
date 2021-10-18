(function ($) {
    'use strict';

    var suhaWindow = $(window);
    var sideNavWrapper = $("#sidenavWrapper");
    var headerArea = $("#headerArea");
    var footerNav = $("#footerNav");
    var blackOverlay = $(".sidenav-black-overlay");

    // :: 1.0 Preloader
    suhaWindow.on('load', function () {
        $('#preloader').fadeOut('1000', function () {
            $(this).remove();
        });
    });

    // :: 2.0 Navbar
    $("#suhaNavbarToggler").on("click", function () {
        sideNavWrapper.addClass("nav-active");
        headerArea.addClass("header-out");
        footerNav.addClass("footer-out");
        blackOverlay.addClass("active");
    });

    $("#goHomeBtn").on("click", function () {
        sideNavWrapper.removeClass("nav-active");
        headerArea.removeClass("header-out");
        footerNav.removeClass("footer-out");
        blackOverlay.removeClass("active");
    });

    blackOverlay.on("click", function () {
        $(this).removeClass("active");
        sideNavWrapper.removeClass("nav-active");
        headerArea.removeClass("header-out");
        footerNav.removeClass("footer-out");
    })

    // 3.0 Size Selection
    $(".choose-size-radio li").on("click", function () {
        $(".choose-size-radio li").removeClass("active");
        $(this).addClass("active");
    });

    // 4.0 Add To Cart Notify
    $(".add2cart-notify").on("click", function () {
        $("body").append("<div class='add2cart-notification animated fadeIn'>Added to cart successfully!</div>");
        $(".add2cart-notification").delay(2000).fadeOut();
    });

    // :: 5.0 Hero Slides
    if ($.fn.owlCarousel) {
        var welcomeSlider = $('.hero-slides');
        welcomeSlider.owlCarousel({
            items: 1,
            loop: true,
            autoplay: true,
            dots: true,
            center: true,
            margin: 0,
            nav: true,
            navText: [('<i class="lni-chevron-left"></i>'), ('<i class="lni-chevron-right"></i>')]
        })

        welcomeSlider.on('translate.owl.carousel', function () {
            var layer = $("[data-animation]");
            layer.each(function () {
                var anim_name = $(this).data('animation');
                $(this).removeClass('animated ' + anim_name).css('opacity', '0');
            });
        });

        $("[data-delay]").each(function () {
            var anim_del = $(this).data('delay');
            $(this).css('animation-delay', anim_del);
        });

        $("[data-duration]").each(function () {
            var anim_dur = $(this).data('duration');
            $(this).css('animation-duration', anim_dur);
        });

        welcomeSlider.on('translated.owl.carousel', function () {
            var layer = welcomeSlider.find('.owl-item.active').find("[data-animation]");
            layer.each(function () {
                var anim_name = $(this).data('animation');
                $(this).addClass('animated ' + anim_name).css('opacity', '1');
            });
        });
    }

    // :: 6.0 Flash Sale Slides
    if ($.fn.owlCarousel) {
        var flashSlide = $('.flash-sale-slide');
        flashSlide.owlCarousel({
            items: 3,
            margin: 10,
            loop: true,
            autoplay: true,
            smartSpeed: 800,
            autoplayTimeout: 5000,
            dots: true,
            nav: false
        })
    }

    // :: 7.0 Products Slides
    if ($.fn.owlCarousel) {
        var productslides = $('.product-slides');
        productslides.owlCarousel({
            items: 1,
            margin: 0,
            loop: false,
            autoplay: true,
            autoplayTimeout: 5000,
            dots: true,
            nav: true,
            navText: [('<i class="lni-chevron-left"></i>'), ('<i class="lni-chevron-right"></i>')]
        })
    }

    // :: 8.0 Tooltip
    if ($.fn.tooltip) {
        $('[data-toggle="tooltip"]').tooltip();
    }

    // :: 9.0 Jarallax
    if ($.fn.jarallax) {
        $('.jarallax').jarallax({
            speed: 0.5
        });
    }

    // :: 10.0 Counter Up
    if ($.fn.counterUp) {
        $('.counter').counterUp({
            delay: 150,
            time: 3000
        });
    }

    // :: 11.0 Prevent Default 'a' Click
    $('a[href="#"]').on('click', function ($) {
        $.preventDefault();
    });

    // :: 12.0 Password Strength Active Code
    if ($.fn.passwordStrength) {
        $('#registerPassword').passwordStrength({
            minimumChars: 8
        });
    }

})(jQuery);