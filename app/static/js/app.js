// Shared client helpers: API calls with JWT, auth guard, nav, toasts, escaping.
const DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд'];
const TYPE_NAMES = { cardio: 'Кардіо', strength: 'Силові', yoga: 'Йога' };
const DIFF_NAMES = { easy: 'Легко', medium: 'Середньо', hard: 'Важко' };
const GOAL_NAMES = { lose_weight: 'Схуднення', gain_muscle: 'Набір маси', endurance: 'Витривалість' };
const STATUS_NAMES = { upcoming: 'Скоро', active: 'Триває', finished: 'Завершено' };
const METRIC_NAMES = { sessions: 'тренувань', calories: 'ккал', minutes: 'хв' };

const store = {
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
  del(k) { try { localStorage.removeItem(k); } catch (e) {} },
};

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function toast(message, type = 'ok') {
  const box = document.getElementById('toast');
  const el = document.createElement('div');
  if (type === 'err') el.className = 'err';
  el.textContent = message;
  box.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

async function api(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  const token = store.get('token');
  if (token) headers.Authorization = 'Bearer ' + token;
  const res = await fetch('/api' + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  if (res.status === 401 && !location.pathname.startsWith('/login')) {
    logout();
    return new Promise(() => {});
  }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    let msg = data.error || data.msg || 'Помилка запиту';
    if (data.details) msg += ': ' + Object.entries(data.details).map(([k, v]) => k + ' — ' + [].concat(v).join(', ')).join('; ');
    throw new Error(msg);
  }
  return data;
}

// Wraps an async handler so any failure is shown as a toast.
function safe(fn) {
  return async (...args) => { try { await fn(...args); } catch (e) { toast(e.message, 'err'); } };
}

function logout() {
  store.del('token'); store.del('role'); store.del('email');
  location.href = '/login';
}

async function requireAuth({ admin = false } = {}) {
  if (!store.get('token')) { location.href = '/login'; return new Promise(() => {}); }
  if (!store.get('role')) {
    const me = await api('/users/me');
    store.set('role', me.role); store.set('email', me.email);
  }
  if (admin && store.get('role') !== 'admin') { location.href = '/'; return new Promise(() => {}); }
}

function renderNav() {
  const links = [['/', 'Головна'], ['/workouts', 'Тренування'], ['/plans', 'Програми'], ['/social', 'Досягнення'], ['/reminders', 'Нагадування'], ['/profile', 'Профіль']];
  if (store.get('role') === 'admin') links.push(['/admin', 'Адмін']);
  const nav = document.getElementById('nav');
  if (!store.get('token')) { nav.innerHTML = '<div class="inner"><span class="brand">💪 FitTrack</span></div>'; return; }
  nav.innerHTML = '<div class="inner"><span class="brand">💪 FitTrack</span>' +
    links.map(([href, text]) => `<a class="link ${location.pathname === href ? 'active' : ''}" href="${href}">${text}</a>`).join('') +
    `<span class="spacer"></span><span class="muted">${esc(store.get('email'))}</span><button class="ghost small" id="logout">Вийти</button></div>`;
  document.getElementById('logout').onclick = logout;
}

const fmtDate = iso => new Date(iso).toLocaleString('uk-UA', { dateStyle: 'short', timeStyle: 'short' });
const todayISO = () => new Date().toISOString().slice(0, 10);
const daysAgoISO = n => new Date(Date.now() - n * 864e5).toISOString().slice(0, 19);

const charts = {};
function drawChart(id, config) {
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart(document.getElementById(id), config);
}

function optionsHtml(items, valueKey, labelFn, selected) {
  return items.map(i => `<option value="${esc(i[valueKey])}" ${String(i[valueKey]) === String(selected) ? 'selected' : ''}>${esc(labelFn(i))}</option>`).join('');
}
