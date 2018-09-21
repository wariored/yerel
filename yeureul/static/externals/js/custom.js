/*
Template Name: OBootstrap Classified | Bootstrap Responsive Website Template
Author: askbootstrap
Author URI: https://themeforest.net/user/askbootstrap
Version: 1.0
*/

/*
	1) Preloader
	2) Featured Owl Carousel
	3) Categories List Page
	4) Categories Nav Smooth Scroll Animation
	5) File Style
	6) Tooltip
	7) Back To Top
	8) Single Ads Slider
*/

$(document).ready(function(){
		"use strict";
		
		// ===========Preloader============
		$(window).on('load', function(){
			$('#preloader').fadeOut('slow',function(){$(this).remove();});
		});
   
		// ===========Featured Owl Carousel============
		var objowlcarousel=$(".owl-carousel-featured");
		if (objowlcarousel.length > 0) {
			objowlcarousel.owlCarousel({
				items: 4,
				lazyLoad: true,
				pagination: false,
				autoPlay: 2000,
				navigation: true,
				navigationText: ["<i class='fa fa-chevron-left'></i>","<i class='fa fa-chevron-right'></i>"],
				stopOnHover: true
			});
		}
		
		// ===========Categories List Page============
		var mycategorylistpage=$(".categories-list-page");
		if (mycategorylistpage.length > 0) {
			mycategorylistpage.owlCarousel({
				items: 3,
				lazyLoad: true,
				pagination: false,
				navigation: true,
				navigationText: ["<i class='fa fa-chevron-left'></i>","<i class='fa fa-chevron-right'></i>"],
				autoPlay: 2000,
				stopOnHover: true
			});
		}
		
		// ===========Categories Nav Smooth Scroll Animation============
		$('.all-categories-nav a').on('click', function () {
			if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'')
			&& location.hostname == this.hostname) {
			  var $target = $(this.hash);
			  $target = $target.length && $target
			  || $('[name=' + this.hash.slice(1) +']');
			  if ($target.length) {
				var targetOffset = $target.offset().top;
				$('html,body')
				.animate({scrollTop: targetOffset}, 2000);
			   return false;
			  }
			}
		});
		
		// ===========File Style============	
        $('.filestyle').each(function() {
            var $this = $(this),
                options = {
                    'buttonText': $this.attr('data-buttonText'),
                    'input': $this.attr('data-input') === 'false' ? false : true,
                    'icon': $this.attr('data-icon') === 'false' ? false : true,
                    'classButton': $this.attr('data-classButton'),
                    'classInput': $this.attr('data-classInput'),
                    'classIcon': $this.attr('data-classIcon')
                };
            $this.filestyle(options);
        });
		
		// ===========Tooltip============
		$('[data-toggle="tooltip"]').tooltip();
		
		// ===========Back To Top============	
		$(window).scroll(function () {
			if ($(this).scrollTop() > 200) {
				 $('#back-to-top').fadeIn();
			} else {
				 $('#back-to-top').fadeOut();
			}
		});
		$('#back-to-top').on('click', function () {
			 $('#back-to-top').tooltip('hide');
			 $('body,html').animate({
				  scrollTop: 0
			 }, 800);
			 return false;
		});
		$('#back-to-top').tooltip('hide');
		
		// ===========Single Ads Slider============	
		var sync1 = $("#sync1");
		var sync2 = $("#sync2");
		  sync1.owlCarousel({
			singleItem : true,
			slideSpeed : 1000,
			pagination: false,
			navigation: true,
			navigationText: ["<i class='fa fa-chevron-left'></i>","<i class='fa fa-chevron-right'></i>"],
			autoPlay: 1500,
			afterAction : syncPosition,
			responsiveRefreshRate : 200,
		});
		sync2.owlCarousel({
			items : 4,
			itemsDesktop      : [1199,10],
			itemsDesktopSmall     : [979,10],
			itemsTablet       : [768,8],
			itemsMobile       : [479,4],
			pagination:false,
			responsiveRefreshRate : 100,
			afterInit : function(el){
			  el.find(".owl-item").eq(0).addClass("synced");
			}
		});
		function syncPosition(el){
			var current = this.currentItem;
			$("#sync2")
			  .find(".owl-item")
			  .removeClass("synced")
			  .eq(current)
			  .addClass("synced")
			if($("#sync2").data("owlCarousel") !== undefined){
			  center(current)
			}
		}
		$("#sync2").on("click", ".owl-item", function(e){
			e.preventDefault();
			var number = $(this).data("owlItem");
			sync1.trigger("owl.goTo",number);
		});
		function center(number){
			var sync2visible = sync2.data("owlCarousel").owl.visibleItems;
			var num = number;
			var found = false;
			for(var i in sync2visible){
			  if(num === sync2visible[i]){
				var found = true;
			  }
			}
			if(found===false){
			  if(num>sync2visible[sync2visible.length-1]){
				sync2.trigger("owl.goTo", num - sync2visible.length+2)
			  }else{
				if(num - 1 === -1){
				  num = 0;
				}
				sync2.trigger("owl.goTo", num);
			  }
			} else if(num === sync2visible[sync2visible.length-1]){
			  sync2.trigger("owl.goTo", sync2visible[1])
			} else if(num === sync2visible[0]){
			  sync2.trigger("owl.goTo", num-1)
			}
		}
	
});
