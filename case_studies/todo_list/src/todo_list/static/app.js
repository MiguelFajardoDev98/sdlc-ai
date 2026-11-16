(() => {
  "use strict";

  const state = {
    allTasks: [],
    filteredTasks: [],
    editingTaskId: null,
  };

  const els = {
    alertBanner: document.getElementById("alert-banner"),
    alertTitle: document.getElementById("alert-title"),
    alertMessage: document.getElementById("alert-message"),
    alertClose: document.getElementById("alert-close"),
    kpiTotal: document.getElementById("kpi-total"),
    kpiCompletionRate: document.getElementById("kpi-completion-rate"),
    kpiProgressFill: document.getElementById("kpi-progress-fill"),
    kpiPendiente: document.getElementById("kpi-pendiente"),
    kpiEnProgreso: document.getElementById("kpi-en-progreso"),
    kpiCompletada: document.getElementById("kpi-completada"),
    kpiOverdue: document.getElementById("kpi-overdue"),
    kpiBlocked: document.getElementById("kpi-blocked"),
    kpiPrioAlta: document.getElementById("kpi-prio-alta"),
    kpiPrioMedia: document.getElementById("kpi-prio-media"),
    kpiPrioBaja: document.getElementById("kpi-prio-baja"),
    formTitle: document.getElementById("form-title"),
    btnCancelEdit: document.getElementById("btn-cancel-edit"),
    taskForm: document.getElementById("task-form"),
    taskId: document.getElementById("task-id"),
    taskTitle: document.getElementById("task-title"),
    taskDescription: document.getElementById("task-description"),
    taskPriority: document.getElementById("task-priority"),
    taskStatus: document.getElementById("task-status"),
    taskDueDate: document.getElementById("task-due-date"),
    taskTags: document.getElementById("task-tags"),
    dependenciesSelector: document.getElementById("dependencies-selector"),
    btnSubmit: document.getElementById("btn-submit"),
    filterSearch: document.getElementById("filter-search"),
    filterStatus: document.getElementById("filter-status"),
    filterPriority: document.getElementById("filter-priority"),
    filterTag: document.getElementById("filter-tag"),
    filterOverdue: document.getElementById("filter-overdue"),
    btnClearFilters: document.getElementById("btn-clear-filters"),
    btnRefresh: document.getElementById("btn-refresh"),
    tasksCounter: document.getElementById("tasks-counter"),
    tasksContainer: document.getElementById("tasks-container"),
  };

  const STATUS_LABELS = {
    pendiente: "Pendiente",
    en_progreso: "En progreso",
    completada: "Completada",
  };

  const PRIORITY_LABELS = {
    alta: "Prioridad Alta",
    media: "Prioridad Media",
    baja: "Prioridad Baja",
  };

  function showAlert(title, message, isSuccess = false) {
    els.alertTitle.textContent = title;
    els.alertMessage.textContent = message;
    els.alertBanner.classList.remove("hidden", "alert-success");
    if (isSuccess) {
      els.alertBanner.classList.add("alert-success");
    }
  }

  function hideAlert() {
    els.alertBanner.classList.add("hidden");
  }

  async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const errorMsg = data.error || `Error HTTP ${response.status}`;
      throw new Error(errorMsg);
    }
    return data;
  }

  function renderSummary(summary) {
    if (!summary) return;
    els.kpiTotal.textContent = summary.total ?? 0;
    const rate = summary.completion_rate ?? 0;
    els.kpiCompletionRate.textContent = `${rate}% completado`;
    els.kpiProgressFill.style.width = `${Math.min(100, Math.max(0, rate))}%`;

    const byStatus = summary.by_status || {};
    els.kpiPendiente.textContent = byStatus.pendiente ?? 0;
    els.kpiEnProgreso.textContent = byStatus.en_progreso ?? 0;
    els.kpiCompletada.textContent = byStatus.completada ?? 0;

    els.kpiOverdue.textContent = summary.overdue_count ?? 0;
    els.kpiBlocked.textContent = summary.blocked_count ?? 0;

    const byPriority = summary.by_priority || {};
    els.kpiPrioAlta.textContent = byPriority.alta ?? 0;
    els.kpiPrioMedia.textContent = byPriority.media ?? 0;
    els.kpiPrioBaja.textContent = byPriority.baja ?? 0;
  }

  function renderDependenciesSelector(selectedIds = []) {
    const currentId = state.editingTaskId;
    const candidates = state.allTasks.filter((t) => t.id !== currentId);
    if (candidates.length === 0) {
      els.dependenciesSelector.innerHTML =
        '<span class="empty-hint">No hay otras tareas disponibles como dependencia.</span>';
      return;
    }

    const selectedSet = new Set(selectedIds);
    els.dependenciesSelector.innerHTML = "";
    candidates.forEach((task) => {
      const label = document.createElement("label");
      label.className = "dep-option";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.value = task.id;
      checkbox.checked = selectedSet.has(task.id);

      const textSpan = document.createElement("span");
      const statusText = STATUS_LABELS[task.status] || task.status;
      textSpan.textContent = `${task.title} [${statusText}]`;

      label.appendChild(checkbox);
      label.appendChild(textSpan);
      els.dependenciesSelector.appendChild(label);
    });
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text ?? "";
    return div.innerHTML;
  }

  function renderTasksList(tasks) {
    els.tasksCounter.textContent = `${tasks.length} tarea(s) mostrada(s)`;
    if (tasks.length === 0) {
      els.tasksContainer.innerHTML =
        '<div class="empty-state">No se encontraron tareas con los criterios actuales.</div>';
      return;
    }

    els.tasksContainer.innerHTML = "";
    tasks.forEach((task) => {
      const card = document.createElement("article");
      const classes = ["task-card"];
      if (task.status === "completada") classes.push("task-completed");
      else if (task.is_overdue) classes.push("task-overdue");
      else if (task.is_blocked) classes.push("task-blocked");
      card.className = classes.join(" ");

      const badgesHtml = [
        `<span class="badge priority-${escapeHtml(task.priority)}">${escapeHtml(
          PRIORITY_LABELS[task.priority] || task.priority
        )}</span>`,
        `<span class="badge status-${escapeHtml(task.status)}">${escapeHtml(
          STATUS_LABELS[task.status] || task.status
        )}</span>`,
      ];

      if (task.is_overdue) {
        badgesHtml.push('<span class="badge badge-overdue">Vencida</span>');
      }
      if (task.is_blocked) {
        badgesHtml.push('<span class="badge badge-blocked">Bloqueada por dependencias</span>');
      }

      const tagsHtml = (task.tags || [])
        .map((tag) => `<span class="tag-chip">#${escapeHtml(tag)}</span>`)
        .join(" ");

      let depsSection = "";
      const depDetails = task.dependency_details || [];
      if (depDetails.length > 0) {
        const depItems = depDetails
          .map(
            (d) =>
              `<strong>${escapeHtml(d.title)}</strong> (${escapeHtml(
                STATUS_LABELS[d.status] || d.status
              )})`
          )
          .join(", ");
        const blockedClass = task.is_blocked ? "blocked-warning" : "";
        depsSection = `
          <div class="dependencies-info ${blockedClass}">
            🔗 <strong>Depende de:</strong> ${depItems}
          </div>
        `;
      }

      const dueText = task.due_date
        ? `📅 Fecha límite: <strong>${escapeHtml(task.due_date)}</strong>`
        : "📅 Sin fecha límite";

      card.innerHTML = `
        <div class="task-top">
          <div class="task-title-group">
            <h3 class="task-title">${escapeHtml(task.title)}</h3>
            ${
              task.description
                ? `<p class="task-description">${escapeHtml(task.description)}</p>`
                : ""
            }
          </div>
          <div class="badges-row">${badgesHtml.join("")}</div>
        </div>
        ${tagsHtml ? `<div class="badges-row">${tagsHtml}</div>` : ""}
        ${depsSection}
        <div class="task-footer">
          <div class="task-meta">${dueText}</div>
          <div class="task-actions">
            ${
              task.status !== "completada"
                ? `<button class="btn btn-sm btn-success" data-action="complete" data-id="${escapeHtml(
                    task.id
                  )}" type="button">✓ Completar</button>`
                : `<button class="btn btn-sm btn-ghost" data-action="reopen" data-id="${escapeHtml(
                    task.id
                  )}" type="button">↺ Reabrir</button>`
            }
            ${
              task.status === "pendiente"
                ? `<button class="btn btn-sm btn-ghost" data-action="progress" data-id="${escapeHtml(
                    task.id
                  )}" type="button">▶ En progreso</button>`
                : ""
            }
            <button class="btn btn-sm btn-ghost" data-action="edit" data-id="${escapeHtml(
              task.id
            )}" type="button">✎ Editar</button>
            <button class="btn btn-sm btn-danger" data-action="delete" data-id="${escapeHtml(
              task.id
            )}" type="button">🗑 Eliminar</button>
          </div>
        </div>
      `;
      els.tasksContainer.appendChild(card);
    });
  }

  function buildFilterQuery() {
    const params = new URLSearchParams();
    const search = els.filterSearch.value.trim();
    const status = els.filterStatus.value;
    const priority = els.filterPriority.value;
    const tag = els.filterTag.value.trim();
    const overdue = els.filterOverdue.checked;

    if (search) params.set("search", search);
    if (status) params.set("status", status);
    if (priority) params.set("priority", priority);
    if (tag) params.set("tag", tag);
    if (overdue) params.set("overdue_only", "true");
    return params.toString();
  }

  async function refreshBoard() {
    try {
      const allData = await apiRequest("/api/tasks");
      state.allTasks = allData.tasks || [];
      renderSummary(allData.summary);

      const query = buildFilterQuery();
      if (query) {
        const filteredData = await apiRequest(`/api/tasks?${query}`);
        state.filteredTasks = filteredData.tasks || [];
      } else {
        state.filteredTasks = state.allTasks;
      }

      renderTasksList(state.filteredTasks);
      const selectedDeps = getSelectedDependencies();
      renderDependenciesSelector(selectedDeps);
    } catch (err) {
      showAlert("Error al cargar tareas", err.message);
    }
  }

  function getSelectedDependencies() {
    const checkboxes = els.dependenciesSelector.querySelectorAll(
      'input[type="checkbox"]:checked'
    );
    return Array.from(checkboxes).map((cb) => cb.value);
  }

  function resetForm() {
    state.editingTaskId = null;
    els.taskId.value = "";
    els.taskForm.reset();
    els.taskPriority.value = "media";
    els.taskStatus.value = "pendiente";
    els.formTitle.textContent = "Nueva Tarea";
    els.btnSubmit.textContent = "Crear Tarea";
    els.btnCancelEdit.classList.add("hidden");
    renderDependenciesSelector([]);
  }

  function startEditTask(taskId) {
    const task = state.allTasks.find((t) => t.id === taskId);
    if (!task) return;
    state.editingTaskId = task.id;
    els.taskId.value = task.id;
    els.taskTitle.value = task.title;
    els.taskDescription.value = task.description || "";
    els.taskPriority.value = task.priority;
    els.taskStatus.value = task.status;
    els.taskDueDate.value = task.due_date || "";
    els.taskTags.value = (task.tags || []).join(", ");
    els.formTitle.textContent = "Editar Tarea";
    els.btnSubmit.textContent = "Guardar Cambios";
    els.btnCancelEdit.classList.remove("hidden");
    renderDependenciesSelector(task.dependencies || []);
    els.taskTitle.focus();
  }

  async function handleFormSubmit(event) {
    event.preventDefault();
    hideAlert();

    const tags = els.taskTags.value
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const payload = {
      title: els.taskTitle.value.trim(),
      description: els.taskDescription.value.trim(),
      priority: els.taskPriority.value,
      status: els.taskStatus.value,
      due_date: els.taskDueDate.value ? els.taskDueDate.value : null,
      tags,
      dependencies: getSelectedDependencies(),
    };

    try {
      if (state.editingTaskId) {
        await apiRequest(`/api/tasks/${encodeURIComponent(state.editingTaskId)}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
        showAlert("Tarea actualizada", `Se actualizó "${payload.title}" correctamente.`, true);
      } else {
        await apiRequest("/api/tasks", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        showAlert("Tarea creada", `Se registró "${payload.title}" correctamente.`, true);
      }
      resetForm();
      await refreshBoard();
    } catch (err) {
      showAlert("Operación rechazada", err.message, false);
    }
  }

  async function handleTaskAction(event) {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const action = button.dataset.action;
    const taskId = button.dataset.id;
    if (!taskId) return;

    hideAlert();
    try {
      if (action === "edit") {
        startEditTask(taskId);
        return;
      }
      if (action === "complete") {
        await apiRequest(`/api/tasks/${encodeURIComponent(taskId)}/complete`, {
          method: "POST",
          body: JSON.stringify({}),
        });
        showAlert("Tarea completada", "La tarea fue marcada como completada.", true);
      } else if (action === "progress") {
        await apiRequest(`/api/tasks/${encodeURIComponent(taskId)}/status`, {
          method: "PATCH",
          body: JSON.stringify({ status: "en_progreso" }),
        });
        showAlert("Estado actualizado", "La tarea pasó a 'En progreso'.", true);
      } else if (action === "reopen") {
        await apiRequest(`/api/tasks/${encodeURIComponent(taskId)}/status`, {
          method: "PATCH",
          body: JSON.stringify({ status: "pendiente" }),
        });
        showAlert("Tarea reabierta", "La tarea volvió al estado 'Pendiente'.", true);
      } else if (action === "delete") {
        await apiRequest(`/api/tasks/${encodeURIComponent(taskId)}`, {
          method: "DELETE",
        });
        if (state.editingTaskId === taskId) resetForm();
        showAlert("Tarea eliminada", "La tarea y sus referencias fueron eliminadas.", true);
      }
      await refreshBoard();
    } catch (err) {
      showAlert("Acción bloqueada por reglas de negocio", err.message, false);
    }
  }

  function bindEvents() {
    els.taskForm.addEventListener("submit", handleFormSubmit);
    els.btnCancelEdit.addEventListener("click", resetForm);
    els.alertClose.addEventListener("click", hideAlert);
    els.tasksContainer.addEventListener("click", handleTaskAction);
    els.btnRefresh.addEventListener("click", refreshBoard);

    [
      els.filterSearch,
      els.filterStatus,
      els.filterPriority,
      els.filterTag,
      els.filterOverdue,
    ].forEach((input) => {
      input.addEventListener("input", refreshBoard);
      input.addEventListener("change", refreshBoard);
    });

    els.btnClearFilters.addEventListener("click", () => {
      els.filterSearch.value = "";
      els.filterStatus.value = "";
      els.filterPriority.value = "";
      els.filterTag.value = "";
      els.filterOverdue.checked = false;
      refreshBoard();
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    bindEvents();
    refreshBoard();
  });
})();
