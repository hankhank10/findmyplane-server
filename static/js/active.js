$('document').ready(function(){


  //======> Testimonial Slider
  $('.testimonial-slider').slick({
    infinite:true,
    slidesToShow: 4,
    slidesToScroll: 1,
    dots:false,
    arrows: true,
    appendArrows: '.testimonial-slider-wrapper .slider-btns',
    prevArrow:'<button type="button" class="slick-prev"><i class="icon icon-tail-left"></i></button>',
    nextArrow:'<button type="button" class="slick-next"><i class="icon icon-tail-right"></i></button>',
    responsive: [
      {
        breakpoint: 991,
        settings: {
          slidesToShow: 2,
          

        }
      },
      {
        breakpoint: 768,
        settings: {
          slidesToShow: 1
        }
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          autoplay: true
        }
      }
    ]
  });

  //======>  Mobile Menu Activation
  $('.main-navigation').meanmenu({
      meanScreenWidth: "992",
      meanMenuContainer: '.mobile-menu',
      meanMenuClose: "<i class='icon icon-simple-remove'></i>",
      meanMenuOpen: "<i class='icon icon-menu-34'></i>",
      meanExpand: "",
  });

});