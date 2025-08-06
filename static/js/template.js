(function ($) {
  'use strict';
  $(function () {
    var body = $('body');
    var contentWrapper = $('.content-wrapper');
    var scroller = $('.container-scroller');
    var footer = $('.footer');
    var sidebar = $('.sidebar');

    // Obtener la ruta actual
    var current = window.location.pathname; // Obtiene la ruta actual del navegador

    // Función para agregar la clase 'active' a los enlaces de navegación
    function addActiveClass(element) {
      if (!element || !element.attr('href')) {
        return; // Si el elemento no existe o no tiene un atributo 'href', salir de la función
      }

      var href = element.attr('href'); // Obtener el valor del atributo 'href'

      if (current === "/" || current === "") {
        // Para la URL raíz
        if (href.indexOf("index.html") !== -1) {
          element.parents('.nav-item').last().addClass('active');
          if (element.parents('.sub-menu').length) {
            element.closest('.collapse').addClass('show');
            element.addClass('active');
          }
        }
      } else {
        // Para otras URLs
        if (href.indexOf(current) !== -1) {
          element.parents('.nav-item').last().addClass('active');
          if (element.parents('.sub-menu').length) {
            element.closest('.collapse').addClass('show');
            element.addClass('active');
          }
          if (element.parents('.submenu-item').length) {
            element.addClass('active');
          }
        }
      }
    }

    // Aplicar la función a todos los enlaces de navegación en la barra lateral
    $('.nav li a', sidebar).each(function () {
      var $this = $(this);
      addActiveClass($this);
    });

    // Aplicar la función a todos los enlaces de navegación en el menú horizontal
    $('.horizontal-menu .nav li a').each(function () {
      var $this = $(this);
      addActiveClass($this);
    });

    // Cerrar otros submenús en la barra lateral al abrir uno
    sidebar.on('show.bs.collapse', '.collapse', function () {
      sidebar.find('.collapse.show').collapse('hide');
    });

    // Cambiar la altura de la barra lateral y el contenido
    applyStyles();

    function applyStyles() {
      // Aplicar perfect scrollbar
      if (!body.hasClass("rtl")) {
        if ($('.settings-panel .tab-content .tab-pane.scroll-wrapper').length) {
          const settingsPanelScroll = new PerfectScrollbar('.settings-panel .tab-content .tab-pane.scroll-wrapper');
        }
        if ($('.chats').length) {
          const chatsScroll = new PerfectScrollbar('.chats');
        }
        if (body.hasClass("sidebar-fixed")) {
          if ($('#sidebar').length) {
            var fixedSidebarScroll = new PerfectScrollbar('#sidebar .nav');
          }
        }
      }
    }

    $('[data-bs-toggle="minimize"]').on("click", function () {
      if ((body.hasClass('sidebar-toggle-display')) || (body.hasClass('sidebar-absolute'))) {
        body.toggleClass('sidebar-hidden');
      } else {
        body.toggleClass('sidebar-icon-only');
      }
    });

    // Checkbox y radios
    $(".form-check label,.form-radio label").append('<i class="input-helper"></i>');

    // Menú horizontal en móviles
    $('[data-toggle="horizontal-menu-toggle"]').on("click", function () {
      $(".horizontal-menu .bottom-navbar").toggleClass("header-toggled");
    });

    // Navegación en el menú horizontal en móviles
    var navItemClicked = $('.horizontal-menu .page-navigation >.nav-item');
    navItemClicked.on("click", function (event) {
      if (window.matchMedia('(max-width: 991px)').matches) {
        if (!($(this).hasClass('show-submenu'))) {
          navItemClicked.removeClass('show-submenu');
        }
        $(this).toggleClass('show-submenu');
      }
    });

    $(window).scroll(function () {
      if (window.matchMedia('(min-width: 992px)').matches) {
        var header = $('.horizontal-menu');
        if ($(window).scrollTop() >= 70) {
          $(header).addClass('fixed-on-scroll');
        } else {
          $(header).removeClass('fixed-on-scroll');
        }
      }
    });

    if ($("#datepicker-popup").length) {
      $('#datepicker-popup').datepicker({
        enableOnReadonly: true,
        todayHighlight: true,
      });
      $("#datepicker-popup").datepicker("setDate", "0");
    }
  });

  // Marcar todas las casillas en el estado del pedido
  $("#check-all").click(function () {
    $(".form-check-input").prop('checked', $(this).prop('checked'));
  });

  // Enfocar el input al hacer clic en el icono de búsqueda
  $('#navbar-search-icon').click(function () {
    $("#navbar-search-input").focus();
  });

  $(window).scroll(function () {
    var scroll = $(window).scrollTop();

    if (scroll >= 97) {
      $(".fixed-top").addClass("headerLight");
    } else {
      $(".fixed-top").removeClass("headerLight");
    }
  });
})(jQuery);