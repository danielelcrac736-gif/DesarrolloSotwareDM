/* =============================================================================
   main.js — JavaScript global del sistema Acumatica ERP Prototipo
   SIS-315 Sistemas de Gestión Empresarial · USFX 2025

   Funciones disponibles en todas las páginas:
     initDataTable(tableId, searchInputId, options)
     showModal(modalId)  /  closeModal(modalId)
     abrirModal(modalId) /  cerrarModal(modalId)   ← alias en español
     cerrarAlClickAfuera(event, modalId)
     confirmDelete(formId, nombre)
     formatCurrency(amount)
     showAlert(message, type)
     initTabSystem(containerSelector)
     initFlashMessages()
     initSidebarActiveLink()
     initHamburger()
     initTooltips()
   ============================================================================= */


/* =============================================================================
   1. initDataTable — Búsqueda en tiempo real para cualquier tabla del sitio
   =============================================================================
   Parámetros:
     tableId      → string : id del elemento <table>
     searchInputId → string : id del <input> de búsqueda
     options      → objeto  (opcional):
       ignorarColumnas : array de índices de columna a excluir de la búsqueda
       onFiltrar       : callback(visibles, total) ejecutado al filtrar
   ============================================================================= */
function initDataTable(tableId, searchInputId, options) {
  options = options || {};

  var tabla = document.getElementById(tableId);
  var input = document.getElementById(searchInputId);
  if (!tabla || !input) return;

  var tbody = tabla.querySelector('tbody');
  if (!tbody) return;

  // Columnas que se ignoran al comparar texto (ej. columna de acciones)
  var ignorar  = options.ignorarColumnas || [];
  // Callback opcional que recibe (visibles, total) tras cada filtrado
  var callback = typeof options.onFiltrar === 'function' ? options.onFiltrar : null;

  input.addEventListener('input', function () {
    var texto   = this.value.toLowerCase().trim();
    var filas   = Array.from(tbody.querySelectorAll('tr'));
    var visible = 0;

    filas.forEach(function (fila) {
      var celdas = Array.from(fila.querySelectorAll('td'));
      var coincide = false;

      if (!texto) {
        // Sin texto de búsqueda → mostrar todo
        coincide = true;
      } else {
        celdas.forEach(function (celda, idx) {
          // Saltar columnas marcadas para ignorar
          if (ignorar.indexOf(idx) !== -1) return;
          if (celda.textContent.toLowerCase().includes(texto)) {
            coincide = true;
          }
        });
      }

      fila.style.display = coincide ? '' : 'none';
      if (coincide) visible++;
    });

    // Ejecutar callback con el recuento de filas visibles
    if (callback) callback(visible, filas.length);
  });
}


/* =============================================================================
   2. showModal / closeModal — Apertura y cierre de modales con animación
   =============================================================================
   El CSS define .modal-overlay { display:none } y
                  .modal-overlay.active { display:flex; animation:fadeIn }
   El JS solo agrega / quita la clase .active.
   También bloquea el scroll del body mientras hay algún modal abierto.
   ============================================================================= */

/* Abre el modal cuyo id es modalId */
function showModal(modalId) {
  var overlay = document.getElementById(modalId);
  if (!overlay) return;

  // Agregar clase .active activa el display:flex y la animación CSS
  overlay.classList.add('active');

  // Bloquear el scroll del body mientras el modal esté abierto
  document.body.style.overflow = 'hidden';

  // Enfocar el primer campo interactivo para accesibilidad
  setTimeout(function () {
    var primerCampo = overlay.querySelector(
      'input:not([type="hidden"]), select, textarea, button:not(.modal-close)'
    );
    if (primerCampo) primerCampo.focus();
  }, 80);
}

/* Cierra el modal cuyo id es modalId */
function closeModal(modalId) {
  var overlay = document.getElementById(modalId);
  if (!overlay) return;

  overlay.classList.remove('active');

  // Restaurar scroll solo si no queda ningún otro modal abierto
  var hayOtrosModales = document.querySelector('.modal-overlay.active');
  if (!hayOtrosModales) {
    document.body.style.overflow = '';
  }
}

/* Cierra el modal al hacer clic directamente en el overlay (fuera del .modal) */
function cerrarAlClickAfuera(event, modalId) {
  // Solo cerrar si el clic fue en el overlay en sí, no en su contenido
  if (event.target === event.currentTarget) {
    closeModal(modalId);
  }
}

/* Aliases en español — usados en clientes.html e inventario.html */
var abrirModal  = showModal;
var cerrarModal = closeModal;

/* Cerrar modal al presionar Escape */
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    var modalAbierto = document.querySelector('.modal-overlay.active');
    if (modalAbierto && modalAbierto.id) {
      closeModal(modalAbierto.id);
    }
  }
});

/* Cerrar modal al hacer clic en cualquier elemento con [data-close-modal] */
document.addEventListener('click', function (e) {
  var btn = e.target.closest('[data-close-modal]');
  if (btn) {
    var modalId = btn.dataset.closeModal;
    if (modalId) closeModal(modalId);
  }
});


/* =============================================================================
   3. confirmDelete — Confirmación nativa antes de eliminar un registro
   =============================================================================
   Parámetros:
     formId → string : id del <form> de eliminación
     nombre → string : nombre del elemento a eliminar (aparece en el mensaje)
   Si el usuario confirma, hace submit del formulario indicado.
   ============================================================================= */
function confirmDelete(formId, nombre) {
  var mensaje = '¿Eliminar a ' + nombre + '? Esta acción no se puede deshacer.';
  if (window.confirm(mensaje)) {
    var form = document.getElementById(formId);
    if (form) form.submit();
  }
}


/* =============================================================================
   4. formatCurrency — Formatea un número como moneda boliviana
   =============================================================================
   Retorna: "Bs. 1.234,50"
   Usa punto como separador de miles y coma como separador decimal (formato BO).
   ============================================================================= */
function formatCurrency(amount) {
  var num = parseFloat(amount) || 0;
  // Separar la parte entera y los decimales
  var partes = num.toFixed(2).split('.');
  // Insertar punto como separador de miles en la parte entera
  partes[0] = partes[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  // Unir con coma como separador decimal (formato boliviano)
  return 'Bs. ' + partes[0] + ',' + partes[1];
}


/* =============================================================================
   5. showAlert — Flash message dinámico creado por JavaScript
   =============================================================================
   Parámetros:
     message → string : texto a mostrar
     type    → string : 'success' | 'error' | 'warning' | 'info'
   Aparece en la esquina superior derecha usando las mismas clases CSS de
   los flash messages de Flask (.flash-container, .flash-message).
   Se auto-elimina a los 4 segundos con animación de salida.
   ============================================================================= */
function showAlert(message, type) {
  type = type || 'info';

  // Mapa de tipo → clase CSS e ícono de Font Awesome
  var CONFIG = {
    success: { clase: 'flash-success', icono: 'fa-circle-check'       },
    error:   { clase: 'flash-danger',  icono: 'fa-circle-exclamation'  },
    warning: { clase: 'flash-warning', icono: 'fa-triangle-exclamation' },
    info:    { clase: 'flash-info',    icono: 'fa-circle-info'          },
  };
  var cfg = CONFIG[type] || CONFIG.info;

  // Obtener el .flash-container existente o crear uno nuevo
  var contenedor = document.querySelector('.flash-container');
  if (!contenedor) {
    contenedor = document.createElement('div');
    contenedor.className = 'flash-container';
    document.body.appendChild(contenedor);
  }

  // Construir el elemento del mensaje flash
  var msg = document.createElement('div');
  msg.className = 'flash-message ' + cfg.clase;
  msg.setAttribute('role', 'alert');
  msg.innerHTML =
    '<span class="flash-icon"><i class="fa-solid ' + cfg.icono + '"></i></span>' +
    '<span class="flash-text">' + message + '</span>' +
    '<button class="flash-close" aria-label="Cerrar">' +
      '<i class="fa-solid fa-xmark"></i>' +
    '</button>';

  contenedor.appendChild(msg);

  // Botón × cierra inmediatamente con animación de salida
  var closeBtn = msg.querySelector('.flash-close');
  if (closeBtn) {
    closeBtn.addEventListener('click', function () { desvanecerFlash(msg); });
  }

  // Auto-eliminar después de 4 segundos
  setTimeout(function () { desvanecerFlash(msg); }, 4000);
}

/* Utilidad interna: desvanece y elimina un .flash-message del DOM */
function desvanecerFlash(el) {
  if (!el || !el.parentNode) return;
  // Animación de salida vía estilos inline
  el.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
  el.style.opacity    = '0';
  el.style.transform  = 'translateX(24px)';
  setTimeout(function () {
    if (el.parentNode) el.remove();
  }, 360);
}


/* =============================================================================
   6. initFlashMessages — Auto-dismiss de mensajes flash del DOM (Flask)
   =============================================================================
   A los 4 segundos de cargar, desvanece cada .flash-message existente.
   Los botones × ya tienen onclick en el HTML de base.html, pero aquí
   también se vinculan para que la animación de desvanecimiento sea consistente.
   ============================================================================= */
function initFlashMessages() {
  var mensajes = document.querySelectorAll('.flash-message');

  mensajes.forEach(function (msg, idx) {
    // Auto-dismiss escalonado: +500ms por cada mensaje
    setTimeout(function () {
      desvanecerFlash(msg);
    }, 4000 + idx * 500);

    // Mejorar el botón × para usar animación en vez de .remove() directo
    var closeBtn = msg.querySelector('.flash-close');
    if (closeBtn) {
      // Quitar el onclick inline del HTML y reemplazar por el animado
      closeBtn.removeAttribute('onclick');
      closeBtn.addEventListener('click', function () { desvanecerFlash(msg); });
    }
  });
}


/* =============================================================================
   7. initSidebarActiveLink — Marca el enlace activo en el sidebar
   =============================================================================
   Compara el href de cada .nav-link con window.location.pathname.
   Actúa como complemento al marcado server-side de base.html (Jinja2).
   ============================================================================= */
function initSidebarActiveLink() {
  var ruta    = window.location.pathname;
  var enlaces = document.querySelectorAll('.sidebar-nav .nav-link');

  enlaces.forEach(function (enlace) {
    var href = enlace.getAttribute('href');
    if (!href || href === '#') return;

    // Coincidencia exacta o el path actual comienza con el href (rutas anidadas)
    var esActivo = ruta === href ||
                   (href !== '/' && ruta.startsWith(href));

    if (esActivo) {
      enlace.classList.add('active');
    }
  });
}


/* =============================================================================
   8. initHamburger — Toggle del sidebar en dispositivos móviles
   =============================================================================
   Vincula el botón hamburguesa para abrir/cerrar el sidebar en móvil.
   El CSS usa .sidebar.sidebar-open y .sidebar-backdrop.active.
   NOTA: base.html tiene un script inline que también maneja esto; esta función
   es un refuerzo para que main.js sea autónomo si se usa sin ese inline script.
   La bandera [data-hamb-init] evita doble binding.
   ============================================================================= */
function initHamburger() {
  var btn      = document.getElementById('hamburgerBtn');
  var sidebar  = document.getElementById('sidebar');
  var backdrop = document.getElementById('sidebarBackdrop');

  // Salir si los elementos no existen o si ya fue inicializado por este módulo
  if (!btn || !sidebar || btn.dataset.hambInit) return;
  btn.dataset.hambInit = '1';

  // Abrir/cerrar sidebar al pulsar el botón hamburguesa
  btn.addEventListener('click', function () {
    sidebar.classList.toggle('sidebar-open');
    if (backdrop) backdrop.classList.toggle('active');
  });

  // Cerrar sidebar al tocar el overlay oscuro de fondo
  if (backdrop) {
    backdrop.addEventListener('click', function () {
      sidebar.classList.remove('sidebar-open');
      backdrop.classList.remove('active');
    });
  }

  // Cerrar sidebar al redimensionar la ventana a tamaño escritorio
  window.addEventListener('resize', function () {
    if (window.innerWidth > 768) {
      sidebar.classList.remove('sidebar-open');
      if (backdrop) backdrop.classList.remove('active');
    }
  });
}


/* =============================================================================
   9. initTooltips — Inicialización de tooltips para [data-tooltip]
   =============================================================================
   El CSS ya implementa los tooltips mediante [data-tooltip]::after.
   Esta función agrega el atributo title nativo como fallback accesible
   para lectores de pantalla y navegadores que no soporten CSS ::after.
   ============================================================================= */
function initTooltips() {
  document.querySelectorAll('[data-tooltip]').forEach(function (el) {
    // Agregar title solo si el elemento no tiene uno ya definido
    if (!el.title && el.dataset.tooltip) {
      el.title = el.dataset.tooltip;
    }
  });
}


/* =============================================================================
   10. initTabSystem — Sistema de tabs reutilizable para cualquier sección
   =============================================================================
   Parámetro:
     containerSelector → string CSS o elemento DOM que contiene los tabs

   Estructura HTML esperada:
     <div id="misTabs">
       <button class="tab-btn" data-tab="panel1">Tab 1</button>
       <button class="tab-btn" data-tab="panel2">Tab 2</button>
       <div class="tab-pane" id="panel1">Contenido 1</div>
       <div class="tab-pane" id="panel2">Contenido 2</div>
     </div>

   Uso:  initTabSystem('#misTabs')

   El CSS controla la visibilidad con .tab-btn.active y .tab-pane.active.
   ============================================================================= */
function initTabSystem(containerSelector) {
  // Aceptar tanto selector string como elemento DOM directamente
  var container = typeof containerSelector === 'string'
    ? document.querySelector(containerSelector)
    : containerSelector;

  if (!container) return;

  var botones = container.querySelectorAll('.tab-btn[data-tab]');
  var paneles = container.querySelectorAll('.tab-pane');

  botones.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var targetId = btn.dataset.tab;

      // Desactivar todos los botones y ocultar todos los paneles
      botones.forEach(function (b) { b.classList.remove('active'); });
      paneles.forEach(function (p) { p.classList.remove('active'); });

      // Activar el botón pulsado
      btn.classList.add('active');

      // Mostrar el panel correspondiente (buscar por id o por data-tab-panel)
      var panel = container.querySelector('#' + targetId) ||
                  container.querySelector('[data-tab-panel="' + targetId + '"]');
      if (panel) panel.classList.add('active');
    });
  });

  // Si ningún tab tiene .active, activar el primero por defecto
  var hayActivo = container.querySelector('.tab-btn.active');
  if (!hayActivo && botones.length > 0) {
    botones[0].click();
  }
}


/* =============================================================================
   DOMContentLoaded — Inicialización automática al cargar el DOM
   ============================================================================= */
document.addEventListener('DOMContentLoaded', function () {

  // Desvanece automáticamente los flash messages de Flask a los 4 segundos
  initFlashMessages();

  // Marca el enlace del sidebar que corresponde a la página actual
  initSidebarActiveLink();

  // Vincula el botón hamburguesa para el sidebar responsivo en móvil
  initHamburger();

  // Agrega atributos title como fallback accesible para los tooltips CSS
  initTooltips();

});
