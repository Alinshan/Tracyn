// ── TRACYN Dashboard JS ──────────────────────────────────────────────

const API = '';  // same origin

// ── Navigation ──────────────────────────────────────────────────────
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById(`page-${id}`)?.classList.add('active');
  document.querySelector(`.nav-item[data-page="${id}"]`)?.classList.add('active');
  loaders[id]?.();
}

const loaders = {
  dashboard: loadDashboard,
  monitor: loadMonitor,
  files: loadFiles,
  events: loadEvents,
  incidents: loadIncidents,
  baselines: loadBaselines,
  reports: () => {},
  demo: () => {},
  settings: () => {}
};

document.querySelectorAll('.nav-item').forEach(el => {
  el.addEventListener('click', () => showPage(el.dataset.page));
});

// ── Utils ────────────────────────────────────────────────────────────
function fmt_time(iso) {
  if (!iso) return '-';
  const d = new Date(iso + (iso.endsWith('Z') ? '' : 'Z'));
  return d.toLocaleTimeString();
}

function fmt_datetime(iso) {
  if (!iso) return '-';
  const d = new Date(iso + (iso.endsWith('Z') ? '' : 'Z'));
  return d.toLocaleString();
}

function severity_badge(sev) {
  const s = (sev || 'low').toLowerCase();
  return `<span class="badge ${s}">${sev}</span>`;
}

function event_type_badge(t) {
  const s = (t || '').toLowerCase().replace('_', '_');
  return `<span class="badge ${s}">${t}</span>`;
}

function risk_bar(score) {
  let color = '#22c55e';
  if (score >= 75) color = '#ef4444';
  else if (score >= 50) color = '#f59e0b';
  else if (score >= 25) color = '#3b82f6';
  return `<div class="risk-bar-wrap"><div class="risk-bar"><div class="risk-bar-fill" style="width:${score}%;background:${color}"></div></div><span style="font-size:0.75rem;width:30px;text-align:right;color:#94a3b8">${score}</span></div>`;
}

function toast(msg, type = 'success', duration = 4000) {
  const c = document.getElementById('toast-container');
  const t = document.createElement('div');
  t.className = `toast ${(type || 'success').toLowerCase()}`;
  t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => t.remove(), duration);
}

async function api(path, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  if (!res.ok) throw new Error(`${res.status}: ${res.statusText}`);
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) return res.json();
  return res.text();
}

// ── Dashboard ────────────────────────────────────────────────────────
async function loadDashboard() {
  try {
    const s = await api('/api/dashboard/summary');
    document.getElementById('stat-files').textContent = s.total_files;
    document.getElementById('stat-modified').textContent = s.modified_files;
    document.getElementById('stat-new').textContent = s.new_files;
    document.getElementById('stat-deleted').textContent = s.deleted_files;
    document.getElementById('stat-incidents').textContent = s.open_incidents;
    document.getElementById('stat-critical').textContent = s.critical_alerts;
    document.getElementById('stat-high').textContent = s.high_alerts;
    document.getElementById('stat-risk').textContent = s.current_risk_level;
    const dot = document.getElementById('monitor-dot');
    const lbl = document.getElementById('monitor-label');
    if (s.monitor_status === 'ACTIVE') {
      dot.classList.remove('inactive');
      lbl.textContent = 'SYSTEM ONLINE';
    } else {
      dot.classList.add('inactive');
      lbl.textContent = 'MONITOR INACTIVE';
    }
  } catch (e) { console.error(e); }

  try {
    const events = await api('/api/events?limit=10');
    const tb = document.getElementById('dash-recent-events');
    if (!events.length) {
      tb.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#475569;padding:1.5rem">No events yet. Create a baseline and start monitoring.</td></tr>';
      return;
    }
    tb.innerHTML = events.map(e => `
      <tr onclick="openEventDetail('${e.event_id}')" style="cursor:pointer">
        <td class="mono" style="font-size:0.75rem;color:#475569">${fmt_time(e.timestamp)}</td>
        <td>${event_type_badge(e.event_type)}</td>
        <td class="path-cell">${e.path}</td>
        <td>${severity_badge(e.severity)}</td>
        <td>${risk_bar(e.risk_score)}</td>
      </tr>`).join('');
  } catch (e) { console.error(e); }
}

// ── Monitor ──────────────────────────────────────────────────────────
let monitorStarted = false;

async function loadMonitor() {
  try {
    const s = await api('/api/monitor/status');
    updateMonitorUI(s.status);
  } catch(e) {}
}

function updateMonitorUI(status) {
  const btn = document.getElementById('btn-monitor-toggle');
  const lbl = document.getElementById('monitor-status-label');
  if (status === 'ACTIVE') {
    btn.textContent = '⏹ Stop Monitor';
    btn.className = 'btn btn-danger';
    lbl.innerHTML = '<span class="badge low">ACTIVE</span>';
    monitorStarted = true;
  } else {
    btn.textContent = '▶ Start Monitor';
    btn.className = 'btn btn-primary';
    lbl.innerHTML = '<span class="badge unknown">INACTIVE</span>';
    monitorStarted = false;
  }
}

document.getElementById('btn-monitor-toggle')?.addEventListener('click', async () => {
  try {
    if (monitorStarted) {
      await api('/api/monitor/stop', 'POST');
      updateMonitorUI('INACTIVE');
      toast('Monitor stopped', 'medium');
    } else {
      await api('/api/monitor/start', 'POST');
      updateMonitorUI('ACTIVE');
      startSSE();
      toast('Real-time monitor ACTIVE', 'success');
    }
  } catch(e) { toast('Error: ' + e.message, 'critical'); }
});

document.getElementById('btn-scan-now')?.addEventListener('click', async () => {
  toast('Running integrity scan...', 'medium');
  try {
    const res = await api('/api/scan', 'POST');
    toast(`Scan complete. ${res.changes_detected} change(s) detected.`, res.changes_detected > 0 ? 'high' : 'success');
    loadMonitor();
  } catch(e) { toast('Scan error: ' + e.message, 'critical'); }
});

// SSE Live Feed
function startSSE() {
  if (window._sseSource) window._sseSource.close();
  const es = new EventSource('/api/events/stream');
  window._sseSource = es;
  es.onmessage = (ev) => {
    try {
      const event = JSON.parse(ev.data);
      appendFeedItem(event);
      if (['CRITICAL', 'HIGH'].includes(event.severity)) {
        toast(`[${event.severity}] ${event.event_type}: ${event.path.split('/').pop()}`, event.severity.toLowerCase());
      }
      loadDashboard();
    } catch(e) {}
  };
}

function appendFeedItem(event) {
  const feed = document.getElementById('live-feed');
  const item = document.createElement('div');
  item.className = 'feed-item';
  item.innerHTML = `
    <span class="feed-time mono">${fmt_time(event.timestamp)}</span>
    ${event_type_badge(event.event_type)}
    <span class="feed-path">${event.path}</span>
    ${severity_badge(event.severity)}
    <span class="feed-risk" style="font-size:0.75rem">${event.risk_score}</span>`;
  item.onclick = () => openEventDetail(event.event_id);
  feed.insertBefore(item, feed.firstChild);
  // Keep max 100 items
  while (feed.children.length > 100) feed.removeChild(feed.lastChild);
}

// ── Events Page ──────────────────────────────────────────────────────
async function loadEvents() {
  try {
    const events = await api('/api/events?limit=200');
    const tb = document.getElementById('events-tbody');
    if (!events.length) {
      tb.innerHTML = '<tr><td colspan="6" class="empty-state">No events recorded yet.</td></tr>';
      return;
    }
    tb.innerHTML = events.map(e => `
      <tr onclick="openEventDetail('${e.event_id}')" style="cursor:pointer">
        <td class="mono" style="font-size:0.75rem;color:#475569">${fmt_time(e.timestamp)}</td>
        <td>${event_type_badge(e.event_type)}</td>
        <td class="path-cell">${e.path}</td>
        <td>${severity_badge(e.severity)}</td>
        <td>${risk_bar(e.risk_score)}</td>
        <td style="font-size:0.72rem;color:#475569">${e.status}</td>
      </tr>`).join('');
  } catch(e) { console.error(e); }
}

async function openEventDetail(event_id) {
  try {
    const e = await api(`/api/events/${event_id}`);
    const modal = document.getElementById('event-modal');
    document.getElementById('modal-event-id').textContent = e.event_id;
    document.getElementById('modal-event-type').innerHTML = event_type_badge(e.event_type);
    document.getElementById('modal-event-path').textContent = e.path;
    document.getElementById('modal-event-time').textContent = fmt_datetime(e.timestamp);
    document.getElementById('modal-old-hash').textContent = e.old_hash || 'N/A';
    document.getElementById('modal-new-hash').textContent = e.new_hash || 'N/A';
    document.getElementById('modal-user').textContent = e.user || 'UNKNOWN';
    document.getElementById('modal-process').textContent = e.process || 'UNKNOWN';
    document.getElementById('modal-risk').textContent = e.risk_score;
    document.getElementById('modal-severity').innerHTML = severity_badge(e.severity);
    document.getElementById('modal-reason').innerHTML = (e.reason || '').replace(/\n/g, '<br>');
    modal.style.display = 'flex';
  } catch(e) { console.error(e); }
}

document.getElementById('modal-close')?.addEventListener('click', () => {
  document.getElementById('event-modal').style.display = 'none';
});

document.getElementById('event-modal')?.addEventListener('click', (ev) => {
  if (ev.target === document.getElementById('event-modal'))
    document.getElementById('event-modal').style.display = 'none';
});

// ── Files Page ───────────────────────────────────────────────────────
async function loadFiles() {
  try {
    const files = await api('/api/files');
    const tb = document.getElementById('files-tbody');
    if (!files.length) {
      tb.innerHTML = '<tr><td colspan="6" class="empty-state">No files tracked yet. Create a baseline first.</td></tr>';
      return;
    }
    tb.innerHTML = files.map(f => `
      <tr>
        <td class="path-cell">${f.path}</td>
        <td style="font-size:0.75rem;color:#475569">.${f.extension || '-'}</td>
        <td style="font-size:0.75rem">${f.size.toLocaleString()} B</td>
        <td class="hash-cell">${(f.sha256 || '').slice(0, 12)}...</td>
        <td>${severity_badge(f.criticality?.toLowerCase())}</td>
        <td class="mono" style="font-size:0.72rem;color:#475569">${fmt_datetime(f.last_seen)}</td>
      </tr>`).join('');
  } catch(e) { console.error(e); }
}

// ── Incidents Page ───────────────────────────────────────────────────
async function loadIncidents() {
  try {
    const incidents = await api('/api/incidents');
    const tb = document.getElementById('incidents-tbody');
    if (!incidents.length) {
      tb.innerHTML = '<tr><td colspan="6" class="empty-state">No incidents. System is clean.</td></tr>';
      return;
    }
    tb.innerHTML = incidents.map(i => `
      <tr onclick="openIncident('${i.incident_number}')" style="cursor:pointer">
        <td class="mono" style="color:#00ff88">${i.incident_number}</td>
        <td>${i.title}</td>
        <td>${severity_badge(i.severity)}</td>
        <td><span class="badge ${i.status.toLowerCase()}">${i.status}</span></td>
        <td style="font-size:0.75rem">${i.event_count}</td>
        <td class="mono" style="font-size:0.72rem;color:#475569">${fmt_datetime(i.created_at)}</td>
      </tr>`).join('');
  } catch(e) { console.error(e); }
}

async function openIncident(incident_number) {
  try {
    const inc = await api(`/api/incidents/${incident_number}`);
    const modal = document.getElementById('incident-modal');
    document.getElementById('inc-number').textContent = inc.incident_number;
    document.getElementById('inc-title').textContent = inc.title;
    document.getElementById('inc-severity').innerHTML = severity_badge(inc.severity);
    document.getElementById('inc-status').innerHTML = `<span class="badge ${inc.status.toLowerCase()}">${inc.status}</span>`;
    document.getElementById('inc-risk').textContent = inc.risk_score;
    document.getElementById('inc-events-count').textContent = inc.event_count;
    document.getElementById('inc-created').textContent = fmt_datetime(inc.created_at);
    document.getElementById('inc-notes').value = inc.analyst_notes || '';
    document.getElementById('inc-status-select').value = inc.status;

    const timeline = document.getElementById('inc-timeline');
    timeline.innerHTML = (inc.events || []).map(e => `
      <div class="timeline-item">
        <div class="timeline-time">${fmt_datetime(e.timestamp)}</div>
        <div class="timeline-path">${event_type_badge(e.event_type)} ${e.path}</div>
      </div>`).join('');

    document.getElementById('inc-save').onclick = async () => {
      try {
        const status = document.getElementById('inc-status-select').value;
        const notes = document.getElementById('inc-notes').value;
        await api(`/api/incidents/${incident_number}/status`, 'POST', { status, analyst_notes: notes });
        toast('Incident updated', 'success');
        loadIncidents();
      } catch(e) { toast('Error: ' + e.message, 'critical'); }
    };

    modal.style.display = 'flex';
  } catch(e) { console.error(e); }
}

document.getElementById('inc-modal-close')?.addEventListener('click', () => {
  document.getElementById('incident-modal').style.display = 'none';
});

document.getElementById('incident-modal')?.addEventListener('click', (ev) => {
  if (ev.target === document.getElementById('incident-modal'))
    document.getElementById('incident-modal').style.display = 'none';
});

// ── Baselines Page ───────────────────────────────────────────────────
async function loadBaselines() {
  try {
    const bl = await api('/api/baselines');
    const tb = document.getElementById('baselines-tbody');
    if (!bl.length) {
      tb.innerHTML = '<tr><td colspan="5" class="empty-state">No baseline created yet.</td></tr>';
      return;
    }
    tb.innerHTML = bl.map(b => `
      <tr>
        <td class="mono" style="color:#00ff88">${b.version}</td>
        <td style="font-size:0.75rem;color:#475569">${fmt_datetime(b.created_at)}</td>
        <td>${b.description || '-'}</td>
        <td><span class="badge ${b.status === 'ACTIVE' ? 'low' : 'unknown'}">${b.status}</span></td>
        <td>${b.file_count} files</td>
      </tr>`).join('');
  } catch(e) { console.error(e); }
}

document.getElementById('btn-create-baseline')?.addEventListener('click', async () => {
  toast('Creating baseline...', 'medium');
  try {
    const res = await api('/api/baselines', 'POST');
    toast(`Baseline created: ${res.version} (${res.files_count} files)`, 'success');
    loadBaselines();
  } catch(e) { toast('Error: ' + e.message, 'critical'); }
});

// ── Reports ──────────────────────────────────────────────────────────
document.getElementById('btn-report-json')?.addEventListener('click', async () => {
  try {
    const res = await api('/api/reports?fmt=json', 'POST');
    const blob = new Blob([res.content], { type: 'application/json' });
    download(blob, `tracyn-report-${res.report_id}.json`);
    toast('JSON report downloaded', 'success');
  } catch(e) { toast('Error: ' + e.message, 'critical'); }
});

document.getElementById('btn-report-csv')?.addEventListener('click', async () => {
  try {
    const res = await fetch('/api/reports?fmt=csv', { method: 'POST' });
    const text = await res.text();
    const blob = new Blob([text], { type: 'text/csv' });
    download(blob, `tracyn-report.csv`);
    toast('CSV report downloaded', 'success');
  } catch(e) { toast('Error: ' + e.message, 'critical'); }
});

document.getElementById('btn-report-html')?.addEventListener('click', async () => {
  try {
    const res = await fetch('/api/reports?fmt=html', { method: 'POST' });
    const html = await res.text();
    const w = window.open('', '_blank');
    w.document.write(html);
    toast('HTML report opened in new tab', 'success');
  } catch(e) { toast('Error: ' + e.message, 'critical'); }
});

function download(blob, filename) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
}

// ── Demo Mode ────────────────────────────────────────────────────────
async function runScenario(scenario) {
  try {
    toast(`Running: ${scenario.replace('_', ' ')}...`, 'medium');
    const res = await api(`/api/demo/${scenario}`, 'POST');
    toast(`Demo: ${res.scenario || scenario} → ${res.expected || 'done'}`, 'high');
    // Auto-scan after demo scenario
    setTimeout(async () => {
      await api('/api/scan', 'POST');
      loadDashboard();
      if (document.getElementById('page-monitor').classList.contains('active')) loadMonitor();
    }, 500);
  } catch(e) { toast('Demo error: ' + e.message, 'critical'); }
}

document.getElementById('btn-demo-reset')?.addEventListener('click', async () => {
  try {
    await api('/api/demo/reset', 'POST');
    toast('Demo environment reset', 'success');
  } catch(e) { toast('Error: ' + e.message, 'critical'); }
});

document.querySelectorAll('.scenario-card').forEach(card => {
  card.addEventListener('click', () => runScenario(card.dataset.scenario));
});

// ── Init ─────────────────────────────────────────────────────────────
showPage('dashboard');

// Auto-refresh dashboard every 15s
setInterval(() => {
  if (document.getElementById('page-dashboard').classList.contains('active')) {
    loadDashboard();
  }
}, 15000);
