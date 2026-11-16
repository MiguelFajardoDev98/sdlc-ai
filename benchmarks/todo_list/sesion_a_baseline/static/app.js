/**
 * Lógica del cliente Web para la Lista de Tareas (To-Do List).
 * Conecta con la API REST local en Python sin dependencias externas.
 */

const estadoApp = {
  todasLasTareas: [],
  tareasFiltradas: [],
  estadisticas: null,
  editandoId: null,
};

// Referencias del DOM
const dom = {
  contenedorAlertas: document.getElementById("contenedor-alertas"),
  statTotal: document.getElementById("stat-total"),
  statPendientes: document.getElementById("stat-pendientes"),
  statEnProgreso: document.getElementById("stat-en-progreso"),
  statCompletadas: document.getElementById("stat-completadas"),
  statVencidas: document.getElementById("stat-vencidas"),
  statBloqueadas: document.getElementById("stat-bloqueadas"),
  statPorcentaje: document.getElementById("stat-porcentaje"),
  statDetallePrioridades: document.getElementById("stat-detalle-prioridades"),
  barraProgresoRelleno: document.getElementById("barra-progreso-relleno"),
  barraProgresoContenedor: document.getElementById("barra-progreso-contenedor"),

  formulario: document.getElementById("formulario-tarea"),
  tituloFormulario: document.getElementById("titulo-formulario"),
  modoEdicionBadge: document.getElementById("modo-edicion-badge"),
  inputId: document.getElementById("input-id"),
  inputTitulo: document.getElementById("input-titulo"),
  inputDescripcion: document.getElementById("input-descripcion"),
  inputPrioridad: document.getElementById("input-prioridad"),
  inputEstado: document.getElementById("input-estado"),
  inputFechaLimite: document.getElementById("input-fecha-limite"),
  inputEtiquetas: document.getElementById("input-etiquetas"),
  selectorDependencias: document.getElementById("selector-dependencias"),
  btnGuardar: document.getElementById("btn-guardar-tarea"),
  btnCancelarEdicion: document.getElementById("btn-cancelar-edicion"),

  filtroBusqueda: document.getElementById("filtro-busqueda"),
  filtroEstado: document.getElementById("filtro-estado"),
  filtroPrioridad: document.getElementById("filtro-prioridad"),
  filtroEtiqueta: document.getElementById("filtro-etiqueta"),
  filtroVencidas: document.getElementById("filtro-vencidas"),
  btnLimpiarFiltros: document.getElementById("btn-limpiar-filtros"),

  contadorVisibles: document.getElementById("contador-tareas-visibles"),
  listaTareas: document.getElementById("lista-tareas"),
  btnNuevaTareaRapida: document.getElementById("btn-nueva-tarea-rapida"),
  btnRefrescar: document.getElementById("btn-refrescar"),
};

/**
 * Escapa caracteres HTML para prevenir inyección XSS.
 */
function escaparHTML(texto) {
  if (texto === null || texto === undefined) return "";
  return String(texto)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Muestra un mensaje de alerta en la parte superior.
 */
function mostrarAlerta(mensaje, tipo = "info", duracionMs = 6000) {
  const div = document.createElement("div");
  div.className = `alerta alerta-${tipo}`;
  div.setAttribute("role", "alert");

  const span = document.createElement("span");
  span.textContent = mensaje;

  const btnCerrar = document.createElement("button");
  btnCerrar.type = "button";
  btnCerrar.className = "alerta-cerrar";
  btnCerrar.innerHTML = "&times;";
  btnCerrar.setAttribute("aria-label", "Cerrar alerta");
  btnCerrar.addEventListener("click", () => div.remove());

  div.appendChild(span);
  div.appendChild(btnCerrar);
  dom.contenedorAlertas.prepend(div);

  if (duracionMs > 0) {
    setTimeout(() => {
      if (div.parentNode) div.remove();
    }, duracionMs);
  }
}

/**
 * Petición auxiliar a la API JSON.
 */
async function peticionAPI(url, opciones = {}) {
  const cabeceras = {
    "Content-Type": "application/json",
    ...(opciones.headers || {}),
  };
  const respuesta = await fetch(url, {
    ...opciones,
    headers: cabeceras,
  });
  const datos = await respuesta.json().catch(() => ({}));
  if (!respuesta.ok || datos.ok === false) {
    const mensajeError = datos.error || `Error HTTP ${respuesta.status}`;
    const error = new Error(mensajeError);
    error.codigo = datos.codigo || "ERROR_API";
    error.status = respuesta.status;
    throw error;
  }
  return datos;
}

/**
 * Carga tanto el catálogo completo de tareas (para el selector de dependencias)
 * como la lista filtrada según los controles activos.
 */
async function cargarDatos() {
  try {
    const todasResp = await peticionAPI("/api/tareas");
    estadoApp.todasLasTareas = todasResp.tareas || [];
    estadoApp.estadisticas = todasResp.estadisticas || null;

    const params = new URLSearchParams();
    const busqueda = dom.filtroBusqueda.value.trim();
    const estado = dom.filtroEstado.value;
    const prioridad = dom.filtroPrioridad.value;
    const etiqueta = dom.filtroEtiqueta.value;
    const soloVencidas = dom.filtroVencidas.checked;

    if (busqueda) params.set("busqueda", busqueda);
    if (estado) params.set("estado", estado);
    if (prioridad) params.set("prioridad", prioridad);
    if (etiqueta) params.set("etiqueta", etiqueta);
    if (soloVencidas) params.set("vencidas", "true");

    const queryStr = params.toString();
    if (queryStr) {
      const filtradasResp = await peticionAPI(`/api/tareas?${queryStr}`);
      estadoApp.tareasFiltradas = filtradasResp.tareas || [];
    } else {
      estadoApp.tareasFiltradas = estadoApp.todasLasTareas;
    }

    renderizarEstadisticas();
    actualizarFiltroEtiquetas();
    renderizarSelectorDependencias(obtenerDependenciasSeleccionadas());
    renderizarListaTareas();
  } catch (err) {
    mostrarAlerta(`No se pudieron cargar las tareas: ${err.message}`, "error");
  }
}

/**
 * Actualiza el panel de resumen estadístico en pantalla.
 */
function renderizarEstadisticas() {
  const stats = estadoApp.estadisticas;
  if (!stats) return;

  dom.statTotal.textContent = stats.total ?? 0;
  dom.statPendientes.textContent = stats.pendientes ?? 0;
  dom.statEnProgreso.textContent = stats.en_progreso ?? 0;
  dom.statCompletadas.textContent = stats.completadas ?? 0;
  dom.statVencidas.textContent = stats.vencidas ?? 0;
  dom.statBloqueadas.textContent = stats.bloqueadas ?? 0;

  const porcentaje = stats.porcentaje_completado ?? 0;
  dom.statPorcentaje.textContent = `${porcentaje}%`;
  dom.barraProgresoRelleno.style.width = `${porcentaje}%`;
  dom.barraProgresoContenedor.setAttribute("aria-valuenow", String(porcentaje));

  const prio = stats.por_prioridad || { alta: 0, media: 0, baja: 0 };
  dom.statDetallePrioridades.textContent = `Alta: ${prio.alta || 0} · Media: ${prio.media || 0} · Baja: ${prio.baja || 0}`;
}

/**
 * Actualiza el desplegable de filtro por etiquetas con las etiquetas existentes.
 */
function actualizarFiltroEtiquetas() {
  const actual = dom.filtroEtiqueta.value;
  const etiquetasObj = (estadoApp.estadisticas && estadoApp.estadisticas.etiquetas) || {};
  const nombresEtiquetas = Object.keys(etiquetasObj).sort((a, b) => a.localeCompare(b, "es"));

  dom.filtroEtiqueta.innerHTML = `<option value="">Todas las etiquetas</option>`;
  for (const et of nombresEtiquetas) {
    const opt = document.createElement("option");
    opt.value = et;
    opt.textContent = `#${et} (${etiquetasObj[et]})`;
    if (et.toLowerCase() === actual.toLowerCase()) {
      opt.selected = true;
    }
    dom.filtroEtiqueta.appendChild(opt);
  }
}

/**
 * Obtiene los IDs de dependencias actualmente marcados en el formulario.
 */
function obtenerDependenciasSeleccionadas() {
  const checks = dom.selectorDependencias.querySelectorAll('input[name="dependencia_id"]:checked');
  return Array.from(checks).map((ch) => ch.value);
}

/**
 * Renderiza la lista de checkboxes de tareas existentes para elegir dependencias.
 */
function renderizarSelectorDependencias(seleccionadas = []) {
  const conjuntoSeleccionadas = new Set(seleccionadas);
  const candidatas = estadoApp.todasLasTareas.filter((t) => t.id !== estadoApp.editandoId);

  if (candidatas.length === 0) {
    dom.selectorDependencias.innerHTML = `<p class="texto-vacio-pequeno">No hay otras tareas disponibles para vincular como dependencia.</p>`;
    return;
  }

  const etiquetasEstado = {
    pendiente: "Pendiente",
    en_progreso: "En progreso",
    completada: "Completada",
  };

  dom.selectorDependencias.innerHTML = candidatas
    .map((t) => {
      const checked = conjuntoSeleccionadas.has(t.id) ? "checked" : "";
      const icono = t.estado === "completada" ? "✓" : "⏳";
      return `
        <label class="item-dependencia-check">
          <input type="checkbox" name="dependencia_id" value="${escaparHTML(t.id)}" ${checked} />
          <span class="dep-check-titulo" title="${escaparHTML(t.titulo)}">${escaparHTML(t.titulo)}</span>
          <span class="badge badge-estado-${escaparHTML(t.estado)}">${icono} ${etiquetasEstado[t.estado] || t.estado}</span>
        </label>
      `;
    })
    .join("");
}

/**
 * Formatea los textos legibles de estado y prioridad.
 */
function textoEstado(estado) {
  const mapa = {
    pendiente: "Pendiente",
    en_progreso: "En progreso",
    completada: "Completada",
  };
  return mapa[estado] || estado;
}

function textoPrioridad(prioridad) {
  const mapa = {
    alta: "Prioridad Alta",
    media: "Prioridad Media",
    baja: "Prioridad Baja",
  };
  return mapa[prioridad] || prioridad;
}

/**
 * Renderiza las tarjetas de tareas en el listado principal.
 */
function renderizarListaTareas() {
  const tareas = estadoApp.tareasFiltradas;
  dom.contadorVisibles.textContent = String(tareas.length);

  if (tareas.length === 0) {
    dom.listaTareas.innerHTML = `
      <div class="estado-vacio">
        <h3>No se encontraron tareas</h3>
        <p>Crea una nueva tarea en el panel izquierdo o ajusta los filtros de búsqueda.</p>
      </div>
    `;
    return;
  }

  dom.listaTareas.innerHTML = tareas
    .map((t) => {
      const clasesTarjeta = [
        "tarjeta-tarea",
        `prioridad-borde-${t.prioridad}`,
        t.estado === "completada" ? "tarea-completada" : "",
        t.vencida ? "tarea-vencida" : "",
      ]
        .filter(Boolean)
        .join(" ");

      const badgeVencida = t.vencida
        ? `<span class="badge badge-vencida">⚠ Vencida</span>`
        : "";

      const badgeBloqueada =
        t.bloqueada && t.estado !== "completada"
          ? `<span class="badge badge-bloqueada">🔒 Bloqueada por dependencias</span>`
          : "";

      const descripcionHTML = t.descripcion
        ? `<p class="tarea-descripcion">${escaparHTML(t.descripcion)}</p>`
        : "";

      const fechaHTML = t.fecha_limite
        ? `<span class="meta-item">📅 Fecha límite: <strong>${escaparHTML(t.fecha_limite)}</strong></span>`
        : `<span class="meta-item">📅 Sin fecha límite</span>`;

      const etiquetasHTML =
        t.etiquetas && t.etiquetas.length > 0
          ? `<div class="etiquetas-lista">
              ${t.etiquetas
                .map(
                  (et) =>
                    `<button type="button" class="etiqueta-chip" data-filtrar-etiqueta="${escaparHTML(et)}">#${escaparHTML(et)}</button>`
                )
                .join("")}
            </div>`
          : "";

      let dependenciasHTML = "";
      if (t.dependencias_detalle && t.dependencias_detalle.length > 0) {
        const claseCaja =
          t.bloqueada && t.estado !== "completada"
            ? "caja-dependencias caja-dependencias-bloqueada"
            : "caja-dependencias";
        const tituloDep =
          t.bloqueada && t.estado !== "completada"
            ? "🔒 Requiere completar primero estas tareas previas:"
            : "🔗 Tareas previas (dependencias):";

        const pills = t.dependencias_detalle
          .map((d) => {
            const clasePill = d.completada ? "pill-dep pill-dep-ok" : "pill-dep pill-dep-pendiente";
            const icono = d.completada ? "✓" : "⏳";
            return `<span class="${clasePill}">${icono} ${escaparHTML(d.titulo)} <small>(${escaparHTML(d.id)})</small></span>`;
          })
          .join("");

        dependenciasHTML = `
          <div class="${claseCaja}">
            <span class="titulo-dependencias">${tituloDep}</span>
            <div class="pills-dependencias">${pills}</div>
          </div>
        `;
      }

      const botonCompletar =
        t.estado !== "completada"
          ? `<button
              type="button"
              class="btn btn-exito btn-pequeno"
              data-accion="completar"
              data-id="${escaparHTML(t.id)}"
              title="${t.bloqueada ? "Tiene dependencias pendientes" : "Marcar tarea como completada"}"
            >
              ✓ Completar
            </button>`
          : "";

      return `
        <article class="${clasesTarjeta}" data-tarea-id="${escaparHTML(t.id)}" role="listitem">
          <div class="tarea-cabecera">
            <div class="tarea-titulo-grupo">
              <h3 class="tarea-titulo">${escaparHTML(t.titulo)}</h3>
              <span class="tarea-id">#${escaparHTML(t.id)}</span>
            </div>
            <div class="tarea-badges">
              ${badgeVencida}
              ${badgeBloqueada}
              <span class="badge badge-prioridad-${escaparHTML(t.prioridad)}">${textoPrioridad(t.prioridad)}</span>
              <span class="badge badge-estado-${escaparHTML(t.estado)}">${textoEstado(t.estado)}</span>
            </div>
          </div>

          ${descripcionHTML}

          <div class="tarea-metadatos">
            ${fechaHTML}
            ${etiquetasHTML}
          </div>

          ${dependenciasHTML}

          <div class="tarea-acciones">
            <div class="acciones-estado">
              ${botonCompletar}
              <label class="sr-only" for="select-estado-${escaparHTML(t.id)}">Cambiar estado</label>
              <select
                id="select-estado-${escaparHTML(t.id)}"
                class="select-cambio-estado"
                data-accion="cambiar-estado"
                data-id="${escaparHTML(t.id)}"
              >
                <option value="pendiente" ${t.estado === "pendiente" ? "selected" : ""}>Estado: Pendiente</option>
                <option value="en_progreso" ${t.estado === "en_progreso" ? "selected" : ""}>Estado: En progreso</option>
                <option value="completada" ${t.estado === "completada" ? "selected" : ""}>Estado: Completada</option>
              </select>
            </div>

            <div class="acciones-crud">
              <button
                type="button"
                class="btn btn-editar btn-pequeno"
                data-accion="editar"
                data-id="${escaparHTML(t.id)}"
              >
                ✎ Editar
              </button>
              <button
                type="button"
                class="btn btn-peligro btn-pequeno"
                data-accion="eliminar"
                data-id="${escaparHTML(t.id)}"
              >
                🗑 Eliminar
              </button>
            </div>
          </div>
        </article>
      `;
    })
    .join("");
}

/**
 * Carga una tarea en el formulario para editarla.
 */
function iniciarEdicionTarea(tareaId) {
  const tarea = estadoApp.todasLasTareas.find((t) => t.id === tareaId);
  if (!tarea) return;

  estadoApp.editandoId = tarea.id;
  dom.inputId.value = tarea.id;
  dom.inputTitulo.value = tarea.titulo;
  dom.inputDescripcion.value = tarea.descripcion || "";
  dom.inputPrioridad.value = tarea.prioridad;
  dom.inputEstado.value = tarea.estado;
  dom.inputFechaLimite.value = tarea.fecha_limite || "";
  dom.inputEtiquetas.value = (tarea.etiquetas || []).join(", ");

  dom.tituloFormulario.textContent = "Editar Tarea";
  dom.modoEdicionBadge.classList.remove("oculto");
  dom.btnGuardar.textContent = "Guardar Cambios";
  dom.btnCancelarEdicion.classList.remove("oculto");

  renderizarSelectorDependencias(tarea.dependencias || []);
  dom.inputTitulo.focus();
  dom.formulario.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/**
 * Restablece el formulario al modo de creación de tarea.
 */
function cancelarEdicion() {
  estadoApp.editandoId = null;
  dom.formulario.reset();
  dom.inputId.value = "";
  dom.inputPrioridad.value = "media";
  dom.inputEstado.value = "pendiente";

  dom.tituloFormulario.textContent = "Nueva Tarea";
  dom.modoEdicionBadge.classList.add("oculto");
  dom.btnGuardar.textContent = "Crear Tarea";
  dom.btnCancelarEdicion.classList.add("oculto");

  renderizarSelectorDependencias([]);
}

/**
 * Maneja el envío del formulario para crear o actualizar una tarea.
 */
async function manejarSubmitFormulario(evento) {
  evento.preventDefault();

  const titulo = dom.inputTitulo.value.trim();
  if (!titulo) {
    mostrarAlerta("Por favor ingresa un título para la tarea.", "error");
    dom.inputTitulo.focus();
    return;
  }

  const etiquetasTexto = dom.inputEtiquetas.value.trim();
  const etiquetas = etiquetasTexto
    ? etiquetasTexto
        .split(",")
        .map((e) => e.trim())
        .filter(Boolean)
    : [];

  const payload = {
    titulo,
    descripcion: dom.inputDescripcion.value.trim(),
    prioridad: dom.inputPrioridad.value,
    estado: dom.inputEstado.value,
    fecha_limite: dom.inputFechaLimite.value ? dom.inputFechaLimite.value.trim() : null,
    etiquetas,
    dependencias: obtenerDependenciasSeleccionadas(),
  };

  try {
    if (estadoApp.editandoId) {
      await peticionAPI(`/api/tareas/${encodeURIComponent(estadoApp.editandoId)}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      mostrarAlerta(`Tarea "${titulo}" actualizada correctamente.`, "exito");
    } else {
      await peticionAPI("/api/tareas", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      mostrarAlerta(`Tarea "${titulo}" creada correctamente.`, "exito");
    }
    cancelarEdicion();
    await cargarDatos();
  } catch (err) {
    mostrarAlerta(err.message, "error", 8000);
  }
}

/**
 * Marca una tarea como completada llamando al endpoint dedicado.
 */
async function marcarTareaCompletada(tareaId) {
  try {
    const resp = await peticionAPI(`/api/tareas/${encodeURIComponent(tareaId)}/completar`, {
      method: "POST",
    });
    mostrarAlerta(resp.mensaje || "Tarea marcada como completada.", "exito");
    await cargarDatos();
  } catch (err) {
    mostrarAlerta(err.message, "error", 8000);
    await cargarDatos();
  }
}

/**
 * Cambia el estado de una tarea desde el selector rápido de la tarjeta.
 */
async function cambiarEstadoTarea(tareaId, nuevoEstado) {
  try {
    const resp = await peticionAPI(`/api/tareas/${encodeURIComponent(tareaId)}/estado`, {
      method: "POST",
      body: JSON.stringify({ estado: nuevoEstado }),
    });
    mostrarAlerta(resp.mensaje || "Estado actualizado.", "exito");
    await cargarDatos();
  } catch (err) {
    mostrarAlerta(err.message, "error", 8000);
    await cargarDatos();
  }
}

/**
 * Elimina una tarea por su ID.
 */
async function eliminarTarea(tareaId) {
  try {
    await peticionAPI(`/api/tareas/${encodeURIComponent(tareaId)}`, {
      method: "DELETE",
    });
    if (estadoApp.editandoId === tareaId) {
      cancelarEdicion();
    }
    mostrarAlerta("Tarea eliminada correctamente.", "info");
    await cargarDatos();
  } catch (err) {
    mostrarAlerta(err.message, "error");
  }
}

/**
 * Configura todos los escuchadores de eventos de la interfaz.
 */
function inicializarEventos() {
  dom.formulario.addEventListener("submit", manejarSubmitFormulario);
  dom.btnCancelarEdicion.addEventListener("click", cancelarEdicion);

  dom.btnNuevaTareaRapida.addEventListener("click", () => {
    cancelarEdicion();
    dom.inputTitulo.focus();
    dom.formulario.scrollIntoView({ behavior: "smooth" });
  });

  dom.btnRefrescar.addEventListener("click", () => {
    cargarDatos();
  });

  // Filtros y búsqueda reactiva
  let temporizadorBusqueda = null;
  dom.filtroBusqueda.addEventListener("input", () => {
    clearTimeout(temporizadorBusqueda);
    temporizadorBusqueda = setTimeout(() => cargarDatos(), 180);
  });

  dom.filtroEstado.addEventListener("change", cargarDatos);
  dom.filtroPrioridad.addEventListener("change", cargarDatos);
  dom.filtroEtiqueta.addEventListener("change", cargarDatos);
  dom.filtroVencidas.addEventListener("change", cargarDatos);

  dom.btnLimpiarFiltros.addEventListener("click", () => {
    dom.filtroBusqueda.value = "";
    dom.filtroEstado.value = "";
    dom.filtroPrioridad.value = "";
    dom.filtroEtiqueta.value = "";
    dom.filtroVencidas.checked = false;
    cargarDatos();
  });

  // Clic rápido en tarjetas de estadísticas
  document.querySelectorAll(".tarjeta-stat[data-filtro-rapido]").forEach((card) => {
    card.addEventListener("click", () => {
      const filtro = card.getAttribute("data-filtro-rapido");
      dom.filtroBusqueda.value = "";
      dom.filtroPrioridad.value = "";
      dom.filtroEtiqueta.value = "";
      if (filtro === "todos") {
        dom.filtroEstado.value = "";
        dom.filtroVencidas.checked = false;
      } else if (filtro === "vencidas") {
        dom.filtroEstado.value = "";
        dom.filtroVencidas.checked = true;
      } else {
        dom.filtroVencidas.checked = false;
        dom.filtroEstado.value = filtro;
      }
      cargarDatos();
    });
  });

  // Delegación de eventos en la lista de tareas
  dom.listaTareas.addEventListener("click", (ev) => {
    const btnEtiqueta = ev.target.closest("[data-filtrar-etiqueta]");
    if (btnEtiqueta) {
      const et = btnEtiqueta.getAttribute("data-filtrar-etiqueta");
      dom.filtroEtiqueta.value = et;
      cargarDatos();
      return;
    }

    const botonAccion = ev.target.closest("button[data-accion]");
    if (!botonAccion) return;

    const accion = botonAccion.getAttribute("data-accion");
    const tareaId = botonAccion.getAttribute("data-id");
    if (!tareaId) return;

    if (accion === "completar") {
      marcarTareaCompletada(tareaId);
    } else if (accion === "editar") {
      iniciarEdicionTarea(tareaId);
    } else if (accion === "eliminar") {
      eliminarTarea(tareaId);
    }
  });

  dom.listaTareas.addEventListener("change", (ev) => {
    const selectEstado = ev.target.closest('select[data-accion="cambiar-estado"]');
    if (!selectEstado) return;
    const tareaId = selectEstado.getAttribute("data-id");
    const nuevoEstado = selectEstado.value;
    if (tareaId && nuevoEstado) {
      cambiarEstadoTarea(tareaId, nuevoEstado);
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  inicializarEventos();
  cargarDatos();
});
