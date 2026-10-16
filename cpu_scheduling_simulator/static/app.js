const sampleProcesses = [
  { pid: 'P1', arrival_time: 0, burst_time: 5 },
  { pid: 'P2', arrival_time: 1, burst_time: 3 },
  { pid: 'P3', arrival_time: 2, burst_time: 8 },
  { pid: 'P4', arrival_time: 3, burst_time: 6 },
];

const processColors = [
  { bg: '#203950', border: '#3b6688', color: '#a1d6ff' },
  { bg: '#30294e', border: '#625194', color: '#c8b8ff' },
  { bg: '#1c403a', border: '#347b6b', color: '#8ef0d5' },
  { bg: '#4a3327', border: '#946447', color: '#ffd0a1' },
  { bg: '#46273b', border: '#8b4c70', color: '#ffb3da' },
  { bg: '#263a47', border: '#4c7589', color: '#b5eaff' },
  { bg: '#3b3b25', border: '#787745', color: '#e4e7a3' },
  { bg: '#3b2c2c', border: '#865454', color: '#ffc0b6' },
];

const $ = (selector) => document.querySelector(selector);
const processRows = $('#processRows');
const addProcessBtn = $('#addProcessBtn');
const sampleBtn = $('#sampleBtn');
const simulateBtn = $('#simulateBtn');
const errorBox = $('#errorBox');
const resultsSection = $('#results');
const comparisonSection = $('#comparison');
let nextPid = 5;

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);
}

function makeProcessRow(process, index) {
  const row = document.createElement('tr');
  row.innerHTML = `
    <td><input class="pid-input" type="text" maxlength="12" aria-label="Process ID ${index + 1}" data-field="pid" value="${escapeHTML(process.pid)}"></td>
    <td><input type="number" min="0" max="10000" step="1" aria-label="Arrival time ${index + 1}" data-field="arrival_time" value="${process.arrival_time}"></td>
    <td><input type="number" min="1" max="10000" step="1" aria-label="Burst time ${index + 1}" data-field="burst_time" value="${process.burst_time}"></td>
    <td><button class="remove-btn" type="button" aria-label="Remove process ${index + 1}" title="Remove process">×</button></td>`;
  row.querySelector('.remove-btn').addEventListener('click', () => {
    if (processRows.children.length <= 1) return;
    row.remove();
    refreshRowAccessibility();
  });
  return row;
}

function renderProcessRows(processes) {
  processRows.replaceChildren();
  processes.forEach((process, index) => processRows.appendChild(makeProcessRow(process, index)));
  refreshRowAccessibility();
}

function refreshRowAccessibility() {
  const rows = [...processRows.querySelectorAll('tr')];
  rows.forEach((row, index) => {
    row.querySelectorAll('input').forEach((input) => {
      const names = { pid: 'Process ID', arrival_time: 'Arrival time', burst_time: 'Burst time' };
      input.setAttribute('aria-label', `${names[input.dataset.field]} ${index + 1}`);
    });
    const remove = row.querySelector('.remove-btn');
    remove.disabled = rows.length <= 1;
    remove.setAttribute('aria-label', `Remove process ${index + 1}`);
  });
}

function readProcesses() {
  return [...processRows.querySelectorAll('tr')].map((row) => {
    const values = {};
    row.querySelectorAll('input').forEach((input) => {
      values[input.dataset.field] = input.value.trim();
    });
    return {
      pid: values.pid,
      arrival_time: values.arrival_time === '' ? '' : Number(values.arrival_time),
      burst_time: values.burst_time === '' ? '' : Number(values.burst_time),
    };
  });
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function clearError() {
  errorBox.textContent = '';
  errorBox.hidden = true;
}

function formatTime(value) {
  return Number(value).toLocaleString('en-IN', { maximumFractionDigits: 2 });
}

function averageItem(label, value, suffix = '') {
  return `<div class="algo-stat"><span>${label}</span><strong>${formatTime(value)}${suffix}</strong></div>`;
}

function renderMetricCards(results, inputProcessCount, quantum) {
  const waitingWinner = results.reduce((best, result) => result.metrics.average_waiting_time < best.metrics.average_waiting_time ? result : best);
  const turnaroundWinner = results.reduce((best, result) => result.metrics.average_turnaround_time < best.metrics.average_turnaround_time ? result : best);
  const utilizationLeader = results.reduce((best, result) => result.metrics.cpu_utilization > best.metrics.cpu_utilization ? result : best);
  const cards = [
    { icon: '⌛', label: 'LOWEST AVG. WAITING', value: formatTime(waitingWinner.metrics.average_waiting_time), sub: waitingWinner.algorithm },
    { icon: '↔', label: 'LOWEST AVG. TURNAROUND', value: formatTime(turnaroundWinner.metrics.average_turnaround_time), sub: turnaroundWinner.algorithm },
    { icon: '◉', label: 'CPU UTILIZATION', value: `${formatTime(utilizationLeader.metrics.cpu_utilization)}%`, sub: `${utilizationLeader.algorithm} · highest in this run` },
    { icon: '▤', label: 'PROCESSES / QUANTUM', value: `${inputProcessCount} / ${quantum}`, sub: 'Quantum used for Round Robin' },
  ];
  $('#metricCards').innerHTML = cards.map((card) => `
    <article class="metric-card"><div class="metric-header"><span>${card.label}</span><span class="metric-icon">${card.icon}</span></div>
    <strong>${escapeHTML(card.value)}</strong><small>${escapeHTML(card.sub)}</small></article>`).join('');
}

function renderGantt(result, processIndex) {
  const total = result.metrics.finish_time;
  const timeline = result.timeline;
  const chartSegments = timeline.map((segment) => {
    let color;
    if (segment.pid === 'IDLE') {
      color = { bg: '#242a40', border: '#3a405a', color: '#929bb5' };
    } else {
      color = processColors[(processIndex[segment.pid] ?? 0) % processColors.length];
    }
    const start = formatTime(segment.start);
    const end = formatTime(segment.end);
    return `<div class="gantt-segment ${segment.pid === 'IDLE' ? 'idle' : ''}" style="--duration:${segment.duration};--seg-bg:${color.bg};--seg-border:${color.border};--seg-color:${color.color}" title="${escapeHTML(segment.pid)}: ${start} to ${end} (duration ${segment.duration})">
      <span class="seg-pid">${escapeHTML(segment.pid)}</span><span class="seg-time">${start}–${end}</span></div>`;
  }).join('');
  return `<div class="gantt-label"><strong>Gantt chart</strong><span>TIME UNITS · TOTAL ${formatTime(total)}</span></div>
    <div class="gantt-chart" role="img" aria-label="${escapeHTML(result.algorithm)} Gantt chart: ${timeline.map(s => `${s.pid} from ${s.start} to ${s.end}`).join(', ')}">${chartSegments}</div>
    <div class="gantt-time-axis"><span>START · ${formatTime(timeline[0]?.start ?? 0)}</span><span>FINISH · ${formatTime(total)}</span></div>`;
}

function renderProcessDetailTable(processes) {
  const rows = processes.map((p) => `<tr><td>${escapeHTML(p.pid)}</td><td>${p.arrival_time}</td><td>${p.burst_time}</td><td>${p.completion_time}</td><td>${p.turnaround_time}</td><td>${p.waiting_time}</td><td>${p.response_time}</td></tr>`).join('');
  return `<div class="detail-table-wrap"><table class="detail-table"><thead><tr><th>PID</th><th>AT</th><th>BT</th><th>CT</th><th>TAT</th><th>WT</th><th>RT</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

function renderAlgorithmCards(results, processes) {
  const processIndex = Object.fromEntries(processes.map((p, index) => [p.pid, index]));
  const meta = [
    { badge: 'F', cls: 'fcfs', subtitle: 'Non-preemptive · Arrival-order execution', tag: 'ARRIVAL ORDER' },
    { badge: 'S', cls: 'sjf', subtitle: 'Non-preemptive · Shortest ready burst first', tag: 'SHORTEST JOB FIRST' },
    { badge: 'R', cls: 'rr', subtitle: 'Preemptive · Circular ready-queue rotation', tag: 'TIME SLICING' },
  ];
  $('#algorithmResults').innerHTML = results.map((result, index) => {
    const m = result.metrics;
    const info = meta[index];
    return `<article class="algorithm-card">
      <div class="algorithm-card-head"><div class="algorithm-title"><div class="algorithm-badge ${info.cls}">${info.badge}</div><div><h3>${escapeHTML(result.algorithm)}</h3><p>${info.subtitle}</p></div></div><span class="algorithm-tag">${info.tag}</span></div>
      ${renderGantt(result, processIndex)}
      <div class="algorithm-lower"><div class="algo-stats">
        ${averageItem('AVERAGE WAITING TIME', m.average_waiting_time)}
        ${averageItem('AVERAGE TURNAROUND', m.average_turnaround_time)}
        ${averageItem('AVERAGE RESPONSE', m.average_response_time)}
        ${averageItem('CPU UTILIZATION', m.cpu_utilization, '%')}
      </div>${renderProcessDetailTable(result.processes)}</div>
    </article>`;
  }).join('');
}

function renderComparison(results) {
  const dots = ['#8dccff', '#c0b0ff', '#7be5c9'];
  $('#comparisonRows').innerHTML = results.map((result, index) => {
    const m = result.metrics;
    return `<tr><td><span class="algorithm-cell"><span class="tiny-algo" style="background:${dots[index]}"></span>${escapeHTML(result.algorithm)}</span></td>
    <td>${formatTime(m.average_waiting_time)}</td><td>${formatTime(m.average_turnaround_time)}</td><td>${formatTime(m.average_response_time)}</td><td>${formatTime(m.cpu_utilization)}%</td><td>${formatTime(m.throughput)}</td></tr>`;
  }).join('');
  const waitingWinner = results.reduce((best, result) => result.metrics.average_waiting_time < best.metrics.average_waiting_time ? result : best);
  const tatWinner = results.reduce((best, result) => result.metrics.average_turnaround_time < best.metrics.average_turnaround_time ? result : best);
  $('#insightText').innerHTML = `<strong>Run insight:</strong> ${escapeHTML(waitingWinner.algorithm)} has the lowest average waiting time (${formatTime(waitingWinner.metrics.average_waiting_time)} units), while ${escapeHTML(tatWinner.algorithm)} has the lowest average turnaround time (${formatTime(tatWinner.metrics.average_turnaround_time)} units). Results can change with different arrival times, burst times, and time quantum.`;
}

function revealResults() {
  resultsSection.hidden = false;
  comparisonSection.hidden = false;
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

addProcessBtn.addEventListener('click', () => {
  if (processRows.children.length >= 20) {
    showError('The simulator supports a maximum of 20 processes.');
    return;
  }
  clearError();
  processRows.appendChild(makeProcessRow({ pid: `P${nextPid++}`, arrival_time: 0, burst_time: 1 }, processRows.children.length));
  refreshRowAccessibility();
});

sampleBtn.addEventListener('click', () => {
  renderProcessRows(sampleProcesses);
  nextPid = 5;
  $('#timeQuantum').value = 2;
  clearError();
});

$('#quantumDown').addEventListener('click', () => {
  const input = $('#timeQuantum');
  input.value = Math.max(1, Number(input.value || 1) - 1);
});
$('#quantumUp').addEventListener('click', () => {
  const input = $('#timeQuantum');
  input.value = Math.min(10000, Number(input.value || 1) + 1);
});

simulateBtn.addEventListener('click', async () => {
  clearError();
  const processes = readProcesses();
  const timeQuantum = Number($('#timeQuantum').value);
  if (processes.some((p) => !p.pid || p.arrival_time === '' || p.burst_time === '' || !Number.isInteger(p.arrival_time) || !Number.isInteger(p.burst_time))) {
    showError('Complete every field using whole numbers. Process IDs cannot be blank.');
    return;
  }
  if (processes.some((p) => p.arrival_time < 0 || p.burst_time <= 0 || p.arrival_time > 10000 || p.burst_time > 10000)) {
    showError('Arrival time must be 0 or more; burst time must be greater than 0. Values must be 10,000 or less.');
    return;
  }
  if (!Number.isInteger(timeQuantum) || timeQuantum < 1 || timeQuantum > 10000) {
    showError('Time quantum must be a whole number from 1 to 10,000.');
    return;
  }
  if (processes.length > 20) {
    showError('The simulator supports a maximum of 20 processes.');
    return;
  }
  simulateBtn.disabled = true;
  simulateBtn.innerHTML = '<span class="spinner"></span> Simulating…';
  try {
    const response = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ processes, time_quantum: timeQuantum }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Simulation failed. Check your inputs.');
    renderMetricCards(data.results, processes.length, data.time_quantum);
    renderAlgorithmCards(data.results, processes);
    renderComparison(data.results);
    revealResults();
  } catch (error) {
    showError(error.message || 'Could not connect to the simulator. Make sure the local Flask server is running.');
  } finally {
    simulateBtn.disabled = false;
    simulateBtn.innerHTML = '<span>▶</span> Run simulation <span class="button-arrow">↗</span>';
  }
});

renderProcessRows(sampleProcesses);
