const state = {
  usuario: null,
  cuentas: [],
  categorias: [],
  transacciones: [],
  presupuestos: [],
  selectedCuentaId: null,
  cuentaEditandoId: null,
  categoriaEditandoId: null,
  transaccionEditandoId: null,
  presupuestoEditandoId: null,
};

function showMessage(elementId, message, type = 'error') {
  const box = document.getElementById(elementId);
  if (!box) return;

  box.className = `mt-3 rounded-lg border px-3 py-2 text-sm ${type === 'success' ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' : 'border-rose-500/40 bg-rose-500/10 text-rose-300'}`;
  box.textContent = message;
}

function formatCurrency(value) {
  const number = Number(value || 0);
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'EUR',
  }).format(number);
}

function formatDate(value) {
  if (!value) return '-';
  return new Date(value).toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

function logout() {
  clearSession();
  window.location.href = 'login.html';
}

async function initDashboard() {
  if (!getToken()) {
    redirectToLogin();
    return;
  }

  try {
    state.usuario = await getMe();
    const nombre = document.getElementById('usuario-nombre');
    if (nombre) {
      nombre.textContent = state.usuario?.nombre || 'Usuario';
    }
  } catch (error) {
    console.error(error);
  }

  await loadAllData();
  bindForms();
}

async function loadAllData() {
  try {
    const [cuentas, categorias, transacciones, presupuestos] = await Promise.all([
      getCuentas(),
      getCategorias(),
      getTransacciones(),
      getPresupuestos(),
    ]);

    state.cuentas = cuentas || [];
    state.categorias = categorias || [];
    state.transacciones = transacciones || [];
    state.presupuestos = presupuestos || [];

    if (!state.selectedCuentaId || !state.cuentas.some((cuenta) => cuenta.id === state.selectedCuentaId)) {
      state.selectedCuentaId = state.cuentas[0]?.id ?? null;
    }

    renderResumen();
    renderCuentas();
    renderCategorias();
    renderTransacciones();
    renderPresupuestos();
    populateCategoriaSelect();
    populateCuentaActivaSelect();
    syncTransactionFormAvailability();
    populatePresupuestoSelect();
  } catch (error) {
    showMessage('dashboard-message', error.message);
  }
}

function renderResumen() {
  const transaccionesActivas = state.transacciones.filter((t) => !state.selectedCuentaId || t.cuenta_id === state.selectedCuentaId);
  const ingresos = transaccionesActivas.filter((t) => t.tipo === 'ingreso').reduce((acc, t) => acc + Number(t.monto || 0), 0);
  const gastos = transaccionesActivas.filter((t) => t.tipo === 'gasto').reduce((acc, t) => acc + Number(t.monto || 0), 0);
  const balance = ingresos - gastos;
  const saldoCuentas = state.cuentas.reduce((acc, cuenta) => acc + Number(cuenta.saldo || 0), 0);
  const cuentaActiva = state.cuentas.find((cuenta) => cuenta.id === state.selectedCuentaId);

  const ingresosEl = document.getElementById('total-ingresos');
  const gastosEl = document.getElementById('total-gastos');
  const balanceEl = document.getElementById('total-libre');
  const saldoEl = document.getElementById('total-cuentas');

  if (ingresosEl) ingresosEl.textContent = formatCurrency(ingresos);
  if (gastosEl) gastosEl.textContent = formatCurrency(gastos);
  if (balanceEl) balanceEl.textContent = formatCurrency(balance);
  if (saldoEl) saldoEl.textContent = formatCurrency(cuentaActiva ? Number(cuentaActiva.saldo || 0) : saldoCuentas);

  const alerta = document.getElementById('alerta-presupuesto');
  if (alerta) {
    const totalPresupuestos = state.presupuestos.reduce((acc, p) => acc + Number(p.monto_limite || 0), 0);
    alerta.innerHTML = `
      <p class="text-amber-400 text-xs font-semibold uppercase tracking-wider">Estado Presupuesto</p>
      <p class="text-gray-300 text-sm mt-1">${totalPresupuestos > 0 ? `Límite total: ${formatCurrency(totalPresupuestos)}` : 'Sin presupuestos aún'}</p>
    `;
  }
}

function renderCuentas() {
  const tbody = document.getElementById('lista-cuentas');
  if (!tbody) return;

  tbody.innerHTML = state.cuentas.length
    ? state.cuentas.map((cuenta) => `
        <tr class="border-b border-gray-700">
          <td class="p-3">${cuenta.nombre}</td>
          <td class="p-3">${formatCurrency(cuenta.saldo)}</td>
          <td class="p-3 text-right">
            <button data-action="edit-cuenta" data-id="${cuenta.id}" class="mr-2 text-amber-400 hover:text-amber-300">Editar</button>
            <button data-action="delete-cuenta" data-id="${cuenta.id}" class="text-rose-400 hover:text-rose-300">Eliminar</button>
          </td>
        </tr>
      `).join('')
    : '<tr><td colspan="3" class="p-3 text-gray-400">No hay cuentas registradas.</td></tr>';
}

function renderCategorias() {
  const tbody = document.getElementById('lista-categorias');
  if (!tbody) return;

  tbody.innerHTML = state.categorias.length
    ? state.categorias.map((categoria) => `
        <tr class="border-b border-gray-700">
          <td class="p-3">${categoria.nombre}</td>
          <td class="p-3">${categoria.tipo}</td>
          <td class="p-3 text-right">
            <button data-action="edit-categoria" data-id="${categoria.id}" class="mr-2 text-amber-400 hover:text-amber-300">Editar</button>
            <button data-action="delete-categoria" data-id="${categoria.id}" class="text-rose-400 hover:text-rose-300">Eliminar</button>
          </td>
        </tr>
      `).join('')
    : '<tr><td colspan="3" class="p-3 text-gray-400">No hay categorías registradas.</td></tr>';
}

function renderTransacciones() {
  const tbody = document.getElementById('lista-transacciones');
  if (!tbody) return;

  const transaccionesActivas = state.transacciones.filter((transaccion) => !state.selectedCuentaId || transaccion.cuenta_id === state.selectedCuentaId);

  tbody.innerHTML = transaccionesActivas.length
    ? transaccionesActivas.slice(0, 8).map((transaccion) => {
        const categoria = state.categorias.find((item) => item.id === transaccion.categoria_id);
        return `
          <tr class="border-b border-gray-700">
            <td class="p-3">${formatDate(transaccion.fecha)}</td>
            <td class="p-3">${transaccion.descripcion || '-'}</td>
            <td class="p-3">${state.cuentas.find((item) => item.id === transaccion.cuenta_id)?.nombre || transaccion.cuenta_id || '-'}</td>
            <td class="p-3">${categoria ? categoria.nombre : transaccion.categoria_id}</td>
            <td class="p-3">${transaccion.tipo}</td>
            <td class="p-3">${transaccion.factura_img ? 'Sí' : 'No'}</td>
            <td class="p-3 text-right ${transaccion.tipo === 'gasto' ? 'text-rose-400' : 'text-emerald-400'}">${formatCurrency(transaccion.monto)}</td>
            <td class="p-3 text-right">
              <button data-action="edit-transaccion" data-id="${transaccion.id}" class="mr-2 text-amber-400 hover:text-amber-300">Editar</button>
              <button data-action="delete-transaccion" data-id="${transaccion.id}" class="text-rose-400 hover:text-rose-300">Eliminar</button>
            </td>
          </tr>
        `;
      }).join('')
    : '<tr><td colspan="8" class="p-3 text-gray-400">No hay transacciones todavía para esta cuenta.</td></tr>';
}

function renderPresupuestos() {
  const tbody = document.getElementById('lista-presupuestos');
  if (!tbody) return;

  tbody.innerHTML = state.presupuestos.length
    ? state.presupuestos.map((presupuesto) => {
        const categoria = state.categorias.find((item) => item.id === presupuesto.categoria_id);
        return `
          <tr class="border-b border-gray-700">
            <td class="p-3">${categoria ? categoria.nombre : presupuesto.categoria_id}</td>
            <td class="p-3">${formatCurrency(presupuesto.monto_limite)}</td>
            <td class="p-3">${presupuesto.periodo}</td>
            <td class="p-3 text-right">
              <button data-action="edit-presupuesto" data-id="${presupuesto.id}" class="mr-2 text-amber-400 hover:text-amber-300">Editar</button>
              <button data-action="delete-presupuesto" data-id="${presupuesto.id}" class="text-rose-400 hover:text-rose-300">Eliminar</button>
            </td>
          </tr>
        `;
      }).join('')
    : '<tr><td colspan="4" class="p-3 text-gray-400">No hay presupuestos creados.</td></tr>';
}

function populateCategoriaSelect() {
  const select = document.getElementById('transaccion-categoria');
  if (!select) return;

  select.innerHTML = state.categorias.length
    ? state.categorias.map((categoria) => `<option value="${categoria.id}">${categoria.nombre}</option>`).join('')
    : '<option value="">Sin categorías</option>';
}

function populateCuentaActivaSelect() {
  const select = document.getElementById('cuenta-activa-select');
  if (!select) return;

  select.innerHTML = state.cuentas.length
    ? state.cuentas.map((cuenta) => `<option value="${cuenta.id}" ${state.selectedCuentaId === cuenta.id ? 'selected' : ''}>${cuenta.nombre}</option>`).join('')
    : '<option value="">Sin cuentas</option>';

  select.value = state.selectedCuentaId || '';
}

function syncTransactionFormAvailability() {
  const form = document.getElementById('form-transaccion');
  const button = document.getElementById('btn-transaccion');
  if (!form || !button) return;

  const isEnabled = Boolean(state.selectedCuentaId);
  form.querySelectorAll('input, select, button').forEach((element) => {
    if (element.id !== 'cuenta-activa-select') {
      element.disabled = !isEnabled;
    }
  });

  button.textContent = isEnabled ? 'Crear transacción' : 'Selecciona una cuenta';
}

function populatePresupuestoSelect() {
  const select = document.getElementById('presupuesto-categoria');
  if (!select) return;

  select.innerHTML = state.categorias.length
    ? state.categorias.map((categoria) => `<option value="${categoria.id}">${categoria.nombre}</option>`).join('')
    : '<option value="">Sin categorías</option>';
}

function bindForms() {
  const selectCuentaActiva = document.getElementById('cuenta-activa-select');
  if (selectCuentaActiva) {
    selectCuentaActiva.addEventListener('change', (event) => {
      state.selectedCuentaId = event.target.value ? Number(event.target.value) : null;
      syncTransactionFormAvailability();
      renderResumen();
      renderTransacciones();
    });
  }

  const formCuenta = document.getElementById('form-cuenta');
  if (formCuenta) {
    formCuenta.addEventListener('submit', async (event) => {
      event.preventDefault();
      const data = {
        nombre: document.getElementById('cuenta-nombre').value,
        saldo: document.getElementById('cuenta-saldo').value,
      };

      try {
        if (state.cuentaEditandoId) {
          await actualizarCuenta(state.cuentaEditandoId, data);
        } else {
          await crearCuenta(data);
        }

        formCuenta.reset();
        state.cuentaEditandoId = null;
        document.getElementById('btn-cuenta').textContent = 'Crear cuenta';
        await loadAllData();
        showMessage('cuenta-message', 'Cuenta guardada.', 'success');
      } catch (error) {
        showMessage('cuenta-message', error.message);
      }
    });
  }

  const formCategoria = document.getElementById('form-categoria');
  if (formCategoria) {
    formCategoria.addEventListener('submit', async (event) => {
      event.preventDefault();
      const data = {
        nombre: document.getElementById('categoria-nombre').value,
        tipo: document.getElementById('categoria-tipo').value,
      };

      try {
        if (state.categoriaEditandoId) {
          await actualizarCategoria(state.categoriaEditandoId, data);
        } else {
          await crearCategoria(data);
        }

        formCategoria.reset();
        state.categoriaEditandoId = null;
        document.getElementById('btn-categoria').textContent = 'Crear categoría';
        await loadAllData();
        showMessage('categoria-message', 'Categoría guardada.', 'success');
      } catch (error) {
        showMessage('categoria-message', error.message);
      }
    });
  }

  const formTransaccion = document.getElementById('form-transaccion');
  if (formTransaccion) {
    formTransaccion.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!state.selectedCuentaId) {
        showMessage('transaccion-message', 'Selecciona una cuenta antes de registrar una transacción.');
        return;
      }

      const data = {
        monto: document.getElementById('transaccion-monto').value,
        tipo: document.getElementById('transaccion-tipo').value,
        descripcion: document.getElementById('transaccion-descripcion').value,
        cuenta_id: state.selectedCuentaId,
        categoria_id: Number(document.getElementById('transaccion-categoria').value),
        fecha: document.getElementById('transaccion-fecha').value || null,
      };

      try {
        if (state.transaccionEditandoId) {
          await actualizarTransaccion(state.transaccionEditandoId, data);
        } else {
          await crearTransaccion(data);
        }

        formTransaccion.reset();
        state.transaccionEditandoId = null;
        document.getElementById('btn-transaccion').textContent = 'Crear transacción';
        await loadAllData();
        showMessage('transaccion-message', 'Transacción guardada.', 'success');
      } catch (error) {
        showMessage('transaccion-message', error.message);
      }
    });
  }

  const formPresupuesto = document.getElementById('form-presupuesto');
  if (formPresupuesto) {
    formPresupuesto.addEventListener('submit', async (event) => {
      event.preventDefault();
      const data = {
        categoria_id: Number(document.getElementById('presupuesto-categoria').value),
        monto_limite: document.getElementById('presupuesto-monto').value,
        periodo: document.getElementById('presupuesto-periodo').value,
      };

      try {
        if (state.presupuestoEditandoId) {
          await actualizarPresupuesto(state.presupuestoEditandoId, data);
        } else {
          await crearPresupuesto(data);
        }

        formPresupuesto.reset();
        state.presupuestoEditandoId = null;
        document.getElementById('btn-presupuesto').textContent = 'Crear presupuesto';
        await loadAllData();
        showMessage('presupuesto-message', 'Presupuesto guardado.', 'success');
      } catch (error) {
        showMessage('presupuesto-message', error.message);
      }
    });
  }

  document.addEventListener('click', async (event) => {
    const button = event.target.closest('button');
    if (!button) return;

    const action = button.dataset.action;
    const id = Number(button.dataset.id);

    if (action === 'delete-cuenta') {
      try {
        await eliminarCuenta(id);
        await loadAllData();
        showMessage('cuenta-message', 'Cuenta eliminada.', 'success');
      } catch (error) {
        showMessage('cuenta-message', error.message);
      }
    }

    if (action === 'edit-cuenta') {
      const cuenta = state.cuentas.find((item) => item.id === id);
      if (cuenta) {
        document.getElementById('cuenta-nombre').value = cuenta.nombre;
        document.getElementById('cuenta-saldo').value = cuenta.saldo;
        state.cuentaEditandoId = id;
        document.getElementById('btn-cuenta').textContent = 'Guardar cambios';
      }
    }

    if (action === 'delete-categoria') {
      try {
        await eliminarCategoria(id);
        await loadAllData();
        showMessage('categoria-message', 'Categoría eliminada.', 'success');
      } catch (error) {
        showMessage('categoria-message', error.message);
      }
    }

    if (action === 'edit-categoria') {
      const categoria = state.categorias.find((item) => item.id === id);
      if (categoria) {
        document.getElementById('categoria-nombre').value = categoria.nombre;
        document.getElementById('categoria-tipo').value = categoria.tipo;
        state.categoriaEditandoId = id;
        document.getElementById('btn-categoria').textContent = 'Guardar cambios';
      }
    }

    if (action === 'delete-transaccion') {
      try {
        await eliminarTransaccion(id);
        await loadAllData();
        showMessage('transaccion-message', 'Transacción eliminada.', 'success');
      } catch (error) {
        showMessage('transaccion-message', error.message);
      }
    }

    if (action === 'edit-transaccion') {
      const transaccion = state.transacciones.find((item) => item.id === id);
      if (transaccion) {
        document.getElementById('transaccion-monto').value = transaccion.monto;
        document.getElementById('transaccion-tipo').value = transaccion.tipo;
        document.getElementById('transaccion-descripcion').value = transaccion.descripcion || '';
        state.selectedCuentaId = transaccion.cuenta_id;
        populateCuentaActivaSelect();
        syncTransactionFormAvailability();
        document.getElementById('transaccion-categoria').value = transaccion.categoria_id;
        document.getElementById('transaccion-fecha').value = transaccion.fecha ? transaccion.fecha.split('T')[0] : '';
        state.transaccionEditandoId = id;
        document.getElementById('btn-transaccion').textContent = 'Guardar cambios';
      }
    }

    if (action === 'delete-presupuesto') {
      try {
        await eliminarPresupuesto(id);
        await loadAllData();
        showMessage('presupuesto-message', 'Presupuesto eliminado.', 'success');
      } catch (error) {
        showMessage('presupuesto-message', error.message);
      }
    }

    if (action === 'edit-presupuesto') {
      const presupuesto = state.presupuestos.find((item) => item.id === id);
      if (presupuesto) {
        document.getElementById('presupuesto-categoria').value = presupuesto.categoria_id;
        document.getElementById('presupuesto-monto').value = presupuesto.monto_limite;
        document.getElementById('presupuesto-periodo').value = presupuesto.periodo;
        state.presupuestoEditandoId = id;
        document.getElementById('btn-presupuesto').textContent = 'Guardar cambios';
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }

  if (document.getElementById('dashboard-page')) {
    initDashboard();
  }
});
