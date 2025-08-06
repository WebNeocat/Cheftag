(function ($) {
  'use strict';
  $(function () {
    // Verificar si el banner existe antes de manipularlo
    const proBanner = document.querySelector('#proBanner');
    const navbar = document.querySelector('.navbar');
    const pageBodyWrapper = document.querySelector('.page-body-wrapper');

    if (proBanner && navbar && pageBodyWrapper) {
      if ($.cookie('staradmin2-pro-banner') !== "true") {
        proBanner.classList.add('d-flex');
        navbar.classList.remove('fixed-top');
      } else {
        proBanner.classList.add('d-none');
        navbar.classList.add('fixed-top');
      }

      if (navbar.classList.contains("fixed-top")) {
        pageBodyWrapper.classList.remove('pt-0');
        navbar.classList.remove('pt-5');
      } else {
        pageBodyWrapper.classList.add('pt-0');
        navbar.classList.add('pt-5');
        navbar.classList.add('mt-3');
      }

      const bannerClose = document.querySelector('#bannerClose');
      if (bannerClose) {
        bannerClose.addEventListener('click', function () {
          proBanner.classList.add('d-none');
          proBanner.classList.remove('d-flex');
          navbar.classList.remove('pt-5');
          navbar.classList.add('fixed-top');
          pageBodyWrapper.classList.add('proBanner-padding-top');
          navbar.classList.remove('mt-3');
          var date = new Date();
          date.setTime(date.getTime() + 24 * 60 * 60 * 1000);
          $.cookie('staradmin2-pro-banner', "true", { expires: date });
        });
      }
    }

    // Gráfico de rendimiento
    if ($("#performanceLine").length) {
      const ctx = document.getElementById('performanceLine');
      var graphGradient = ctx.getContext('2d');
      var saleGradientBg = graphGradient.createLinearGradient(5, 0, 5, 100);
      saleGradientBg.addColorStop(0, 'rgba(26, 115, 232, 0.18)');
      saleGradientBg.addColorStop(1, 'rgba(26, 115, 232, 0.02)');

      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"],
          datasets: [{
            label: 'This week',
            data: [50, 110, 60, 290, 200, 115, 130],
            backgroundColor: saleGradientBg,
            borderColor: '#1F3BB3',
            borderWidth: 1.5,
            fill: true,
            pointRadius: [4, 4, 4, 4, 4, 4, 4],
            pointHoverRadius: [2, 2, 2, 2, 2, 2, 2],
            pointBackgroundColor: ['#1F3BB3'],
            pointBorderColor: ['#fff'],
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              grid: {
                color: "#F0F0F0",
              },
              ticks: {
                color: "#6B778C",
              }
            },
            x: {
              grid: {
                display: false,
              },
              ticks: {
                color: "#6B778C",
              }
            }
          },
          plugins: {
            legend: {
              display: false,
            }
          }
        }
      });
    }

    // Gráfico de resumen de estado
    if ($("#status-summary").length) {
      const statusSummaryChartCanvas = document.getElementById('status-summary');
      new Chart(statusSummaryChartCanvas, {
        type: 'line',
        data: {
          labels: ["SUN", "MON", "TUE", "WED", "THU", "FRI"],
          datasets: [{
            label: '# of Votes',
            data: [50, 68, 70, 10, 12, 80],
            backgroundColor: "#ffcc00",
            borderColor: '#01B6A0',
            borderWidth: 2,
            fill: false,
            pointRadius: [0, 0, 0, 0, 0, 0],
            pointHoverRadius: [0, 0, 0, 0, 0, 0],
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              display: false,
              grid: {
                display: false,
              }
            },
            x: {
              display: false,
              grid: {
                display: false,
              }
            }
          },
          plugins: {
            legend: {
              display: false,
            }
          }
        }
      });
    }

    // Gráfico de marketing
    if ($("#marketingOverview").length) {
      const marketingOverviewCanvas = document.getElementById('marketingOverview');
      new Chart(marketingOverviewCanvas, {
        type: 'bar',
        data: {
          labels: ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"],
          datasets: [{
            label: 'Last week',
            data: [110, 220, 200, 190, 220, 110, 210, 110, 205, 202, 201, 150],
            backgroundColor: "#52CDFF",
            borderColor: '#52CDFF',
            borderWidth: 0,
            barPercentage: 0.35,
          }, {
            label: 'This week',
            data: [215, 290, 210, 250, 290, 230, 290, 210, 280, 220, 190, 300],
            backgroundColor: "#1F3BB3",
            borderColor: '#1F3BB3',
            borderWidth: 0,
            barPercentage: 0.35,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              grid: {
                color: "#F0F0F0",
              },
              ticks: {
                color: "#6B778C",
              }
            },
            x: {
              grid: {
                display: false,
              },
              ticks: {
                color: "#6B778C",
              }
            }
          },
          plugins: {
            legend: {
              display: false,
            }
          }
        }
      });
    }

    // Gráfico de visitantes totales
    if ($('#totalVisitors').length) {
      var bar = new ProgressBar.Circle(totalVisitors, {
        color: '#fff',
        strokeWidth: 15,
        trailWidth: 15,
        easing: 'easeInOut',
        duration: 1400,
        text: {
          autoStyleContainer: false
        },
        from: {
          color: '#52CDFF',
          width: 15
        },
        to: {
          color: '#677ae4',
          width: 15
        },
        step: function (state, circle) {
          circle.path.setAttribute('stroke', state.color);
          circle.path.setAttribute('stroke-width', state.width);

          var value = Math.round(circle.value() * 100);
          if (value === 0) {
            circle.setText('');
          } else {
            circle.setText(value);
          }
        }
      });

      bar.text.style.fontSize = '0rem';
      bar.animate(.64); // Número de 0.0 a 1.0
    }

    // Gráfico de visitas por día
    if ($('#visitperday').length) {
      var bar = new ProgressBar.Circle(visitperday, {
        color: '#fff',
        strokeWidth: 15,
        trailWidth: 15,
        easing: 'easeInOut',
        duration: 1400,
        text: {
          autoStyleContainer: false
        },
        from: {
          color: '#34B1AA',
          width: 15
        },
        to: {
          color: '#677ae4',
          width: 15
        },
        step: function (state, circle) {
          circle.path.setAttribute('stroke', state.color);
          circle.path.setAttribute('stroke-width', state.width);

          var value = Math.round(circle.value() * 100);
          if (value === 0) {
            circle.setText('');
          } else {
            circle.setText(value);
          }
        }
      });

      bar.text.style.fontSize = '0rem';
      bar.animate(.34); // Número de 0.0 a 1.0
    }

    // Gráfico de donut
    if ($("#doughnutChart").length) {
      const doughnutChartCanvas = document.getElementById('doughnutChart');
      new Chart(doughnutChartCanvas, {
        type: 'doughnut',
        data: {
          labels: ['Total', 'Net', 'Gross', 'AVG'],
          datasets: [{
            data: [40, 20, 30, 10],
            backgroundColor: [
              "#1F3BB3",
              "#FDD0C7",
              "#52CDFF",
              "#81DADA"
            ],
            borderColor: [
              "#1F3BB3",
              "#FDD0C7",
              "#52CDFF",
              "#81DADA"
            ],
          }]
        },
        options: {
          cutout: 90,
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              display: false,
            }
          }
        }
      });
    }

    // Gráfico de informe de licencias
    if ($("#leaveReport").length) {
      const leaveReportCanvas = document.getElementById('leaveReport');
      new Chart(leaveReportCanvas, {
        type: 'bar',
        data: {
          labels: ["Jan", "Feb", "Mar", "Apr", "May"],
          datasets: [{
            label: 'Last week',
            data: [18, 25, 39, 11, 24],
            backgroundColor: "#52CDFF",
            borderColor: '#52CDFF',
            borderWidth: 0,
            barPercentage: 0.5,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              grid: {
                display: false,
              },
              ticks: {
                color: "#6B778C",
              }
            },
            x: {
              grid: {
                display: false,
              },
              ticks: {
                color: "#6B778C",
              }
            }
          },
          plugins: {
            legend: {
              display: false,
            }
          }
        }
      });
    }
  });
})(jQuery);