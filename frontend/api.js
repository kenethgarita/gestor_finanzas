const API_URL = 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('token');
}

function clearSession() {
  localStorage.removeItem('token');
}

function redirectToLogin() {
  window.location.href = 'login.html';
}

function buildHeaders(extra = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(extra || {}) };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: buildHeaders(options.headers || {}),
    ...options,
  });

  if (response.status === 401) {
    clearSession();
    redirectToLogin();
    throw new Error('Sesión expirada. Inicia sesión nuevamente.');
  }

  const contentType = response.headers.get('content-type') || '';
  let payload = null;

  if (contentType.includes('application/json')) {
    const text = await response.text();
    payload = text ? JSON.parse(text) : null;
  } else {
    payload = await response.text();
  }

  if (!response.ok) {
    const detail = typeof payload === 'object' && payload && payload.detail
      ? payload.detail
      : 'No se pudo completar la solicitud.';
    throw new Error(detail);
  }

  return payload;
}

async function login(email, password) {
  return request('/usuarios/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

async function registerUser(nombre, email, password) {
  return request('/usuarios/', {
    method: 'POST',
    body: JSON.stringify({ nombre, email, password }),
  });
}

async function getMe() {
  return request('/usuarios/me');
}

async function getCuentas() {
  return request('/cuentas/');
}

async function crearCuenta(data) {
  return request('/cuentas/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

async function actualizarCuenta(id, data) {
  return request(`/cuentas/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

async function eliminarCuenta(id) {
  return request(`/cuentas/${id}`, { method: 'DELETE' });
}

async function getCategorias() {
  return request('/categorias/');
}

async function crearCategoria(data) {
  return request('/categorias/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

async function actualizarCategoria(id, data) {
  return request(`/categorias/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

async function eliminarCategoria(id) {
  return request(`/categorias/${id}`, { method: 'DELETE' });
}

async function getTransacciones() {
  return request('/transacciones/');
}

async function crearTransaccion(data) {
  return request('/transacciones/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

async function actualizarTransaccion(id, data) {
  return request(`/transacciones/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

async function eliminarTransaccion(id) {
  return request(`/transacciones/${id}`, { method: 'DELETE' });
}

async function getPresupuestos() {
  return request('/presupuestos/');
}

async function crearPresupuesto(data) {
  return request('/presupuestos/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

async function actualizarPresupuesto(id, data) {
  return request(`/presupuestos/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

async function eliminarPresupuesto(id) {
  return request(`/presupuestos/${id}`, { method: 'DELETE' });
}
