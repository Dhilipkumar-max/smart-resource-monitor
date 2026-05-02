document.addEventListener('DOMContentLoaded', () => {
    // Configuration
    // Change this to your Railway app URL for production, e.g., 'https://your-app-production.up.railway.app/api'
    const API_BASE = 'http://localhost:5000/api';
    const UPDATE_INTERVAL = 2000; // 2 seconds
    const CHART_MAX_POINTS = 30; // Last 60 seconds

    // State
    const state = {
        cpuHistory: new Array(CHART_MAX_POINTS).fill(0),
        memoryHistory: new Array(CHART_MAX_POINTS).fill(0),
        labels: new Array(CHART_MAX_POINTS).fill(''),
        systemUptime: 0, // Mocked for now or fetched
        lastUpdate: null
    };

    // --- Chart Initialization ---
    // Dark theme sensitive defaults
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = '#334155';

    const ctxCpu = document.getElementById('cpuChart').getContext('2d');
    const ctxMem = document.getElementById('memoryChart').getContext('2d');
    const ctxDist = document.getElementById('distChart').getContext('2d');

    // Gradients
    const gradientCpu = ctxCpu.createLinearGradient(0, 0, 0, 400);
    gradientCpu.addColorStop(0, 'rgba(59, 130, 246, 0.5)'); // Blue
    gradientCpu.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

    const gradientMem = ctxMem.createLinearGradient(0, 0, 0, 400);
    gradientMem.addColorStop(0, 'rgba(139, 92, 246, 0.5)'); // Purple
    gradientMem.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

    const gradientDist = ctxDist.createLinearGradient(0, 0, 0, 400);
    gradientDist.addColorStop(0, 'rgba(34, 197, 94, 0.5)'); // Green
    gradientDist.addColorStop(1, 'rgba(34, 197, 94, 0.0)');

    const chartConfig = (label, color, gradient) => ({
        type: 'line',
        data: {
            labels: state.labels,
            datasets: [{
                label: label,
                data: [],
                borderColor: color,
                backgroundColor: gradient,
                borderWidth: 2,
                tension: 0.4, // Smooth curves
                fill: true,
                pointRadius: 0, // Clean look
                pointHoverRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1e293b',
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    borderColor: '#334155',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    display: false, // Hide X axis labels for cleaner look
                    grid: { display: false }
                },
                y: {
                    min: 0,
                    max: 100,
                    ticks: {
                        callback: function (value) { return value + '%' }
                    },
                    grid: {
                        color: '#334155',
                        borderDash: [5, 5]
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });

    const cpuChart = new Chart(ctxCpu, chartConfig('CPU Usage', '#3b82f6', gradientCpu));
    const memoryChart = new Chart(ctxMem, chartConfig('Memory Usage', '#8b5cf6', gradientMem));

    // Dist Chart (Multi-line) - Enhanced to match CPU chart style
    const distChart = new Chart(ctxDist, {
        type: 'line',
        data: {
            labels: state.labels,
            datasets: [
                {
                    label: 'System Load',
                    data: [],
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34, 197, 94, 0.2)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: 'App Load',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1e293b',
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    borderColor: '#334155',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    display: false,
                    grid: { display: false }
                },
                y: {
                    min: 0,
                    max: 100,
                    ticks: {
                        callback: function (value) { return value + '%'; },
                        color: Chart.defaults.color
                    },
                    grid: {
                        color: '#334155',
                        borderDash: [5, 5]
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            elements: { point: { radius: 0 } }
        }
    });


    // --- Data Fetching ---

    async function fetchData() {
        try {
            // 1. System Metrics
            const sysRes = await fetch(`${API_BASE}/system/current`);
            const sysData = await sysRes.json();

            updateSystemStats(sysData);
            updateCharts(sysData);

            // 2. Applications
            const appRes = await fetch(`${API_BASE}/apps/current`);
            const appData = await appRes.json();

            updateAppTable(appData);
            updateTopAppsList(appData);
            updateDistChart(sysData, appData);

            // 3. Recommendations
            const recRes = await fetch(`${API_BASE}/recommendations`);
            const recData = await recRes.json();

            updateRecommendations(recData);

            // Status Indicator
            document.getElementById('connection-status').classList.add('connected');
            document.getElementById('connection-status').classList.remove('disconnected');

        } catch (error) {
            console.error('Fetch error:', error);
            document.getElementById('connection-status').classList.remove('connected');
            document.getElementById('connection-status').classList.add('disconnected');
        }
    }

    // --- UI Update Helpers ---

    function updateSystemStats(data) {
        if (!data) return;

        // CPU
        const cpuVal = (typeof data.cpu_usage === 'number') ? data.cpu_usage.toFixed(1) : data.cpu_usage;
        document.getElementById('cpu-stat-val').innerText = `${cpuVal}%`;

        // Memory
        const memVal = (typeof data.memory_usage === 'number') ? data.memory_usage.toFixed(1) : data.memory_usage;
        document.getElementById('mem-stat-val').innerText = `${memVal}%`;

        // Available / Total Memory (Estimated Total based on Avail + (Used% -> UsedAmt)
        // Total = Available / (1 - (Used%/100))
        const availGB = parseFloat(data.available_memory); // GB
        const usedPercent = parseFloat(memVal) / 100;
        // avoid div by zero
        let totalGB = 16; // default fallback
        if (usedPercent < 1) {
            totalGB = availGB / (1 - usedPercent);
        }

        const usedGB = totalGB * usedPercent;
        document.getElementById('mem-total-display').innerText = `${usedGB.toFixed(1)} GB / ${totalGB.toFixed(0)} GB`;

        // Uptime Simulation (Simple incrementer since page load + base offset)
        // For real uptime, we'd need backend to send "boot_time".
        // Use a mock counter for visual effect
        state.systemUptime += UPDATE_INTERVAL / 1000;
        const uptimeStr = formatUptime(state.systemUptime);
        document.getElementById('uptime-display').innerText = uptimeStr;
    }

    function formatUptime(seconds) {
        const d = Math.floor(seconds / (3600 * 24));
        const h = Math.floor(seconds % (3600 * 24) / 3600);
        const m = Math.floor(seconds % 3600 / 60);
        return `${d}d ${h}h ${m}m`;
    }

    // Mock uptime init
    state.systemUptime = 3600 * 4 + 1800; // start at 4h 30m

    function updateCharts(data) {
        if (!data) return;

        // Push new data
        const cpu = parseFloat(data.cpu_usage);
        const mem = parseFloat(data.memory_usage);

        state.cpuHistory.push(cpu);
        state.cpuHistory.shift();

        state.memoryHistory.push(mem);
        state.memoryHistory.shift();

        // Update charts
        cpuChart.data.datasets[0].data = state.cpuHistory;
        cpuChart.update('none'); // 'none' for performance

        memoryChart.data.datasets[0].data = state.memoryHistory;
        memoryChart.update('none');
    }

    function updateAppTable(apps) {
        const tbody = document.getElementById('app-table-body');
        tbody.innerHTML = ''; // Clear

        // Show all apps as requested
        const topApps = apps;

        // Identify Top Resource Consumer (Max CPU)
        if (apps.length > 0) {
            // Find max CPU app
            const top = apps.reduce((prev, current) => (prev.cpu_usage > current.cpu_usage) ? prev : current);

            const topCard = document.getElementById('top-usage-content');
            if (topCard) {
                const colorClass = top.cpu_usage > 50 ? 'text-red' : (top.cpu_usage > 20 ? 'text-orange' : 'text-blue');
                topCard.innerHTML = `
                    <span style="font-size:1.1rem; font-weight:600; color:var(--text-primary)">${top.app_name}</span>
                    <div style="margin-top:4px; font-size:0.9rem; color:var(--text-secondary)">
                        Consuming <span class="${colorClass}" style="font-weight:bold">${top.cpu_usage}%</span> CPU
                    </div>
                `;
            }
        }

        let highPriorityCount = 0;

        topApps.forEach(app => {
            const tr = document.createElement('tr');

            // Priority Logic
            let priorityClass = 'tag-low';
            let priorityText = 'Normal';

            if (app.cpu_usage > 15 || app.memory_usage > 1000) {
                priorityClass = 'tag-high';
                priorityText = 'High Priority';
                highPriorityCount++;
            } else if (app.cpu_usage > 5 || app.memory_usage > 500) {
                priorityClass = 'tag-med';
                priorityText = 'Medium';
            }

            tr.innerHTML = `
                <td>
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:30px; height:30px; background:#334155; border-radius:6px; display:flex; align-items:center; justify-content:center;">
                            <span style="font-weight:bold; color:#fff;">${app.app_name.charAt(0).toUpperCase()}</span>
                        </div>
                        <div>
                            <div style="font-weight:500; color:#f8fafc;">${app.app_name}</div>
                            <div style="font-size:0.75rem; color:#94a3b8;">PID: ${app.pid}</div>
                        </div>
                    </div>
                </td>
                <td>
                     <div class="progress-bar-container" style="width: 100px; height: 6px; background: #334155; border-radius: 3px; position: relative;">
                        <div style="width: ${Math.min(app.cpu_usage, 100)}%; background: var(--accent-blue); height: 100%; border-radius: 3px;"></div>
                     </div>
                     <span style="font-size:0.8rem;">${app.cpu_usage}%</span>
                </td>
                <td>${app.memory_usage.toFixed(0)} MB</td>
                <td><span class="priority-tag ${priorityClass}">${priorityText}</span></td>
                <td>
                    <button class="action-btn" title="Stop Process"><i class="fa-solid fa-ban"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Update active apps count in header stats
        document.getElementById('process-count').innerText = apps.length;
        document.getElementById('high-priority-count').innerText = `${highPriorityCount} High Priority`;
    }

    function updateRecommendations(data) {
        const container = document.getElementById('recommendations-container');
        container.innerHTML = '';

        if (!data.recommendations || data.recommendations.length === 0) {
            container.innerHTML = `
                <div class="insight-card info">
                    <div class="insight-header">
                        <i class="fa-solid fa-check-circle text-green"></i>
                        <h4>System Optimized</h4>
                    </div>
                    <p>No critical issues detected. Performance is optimal.</p>
                </div>
            `;
            return;
        }

        data.recommendations.forEach(rec => {
            const card = document.createElement('div');
            card.className = `insight-card ${rec.severity === 'critical' ? 'critical' : 'warning'}`;

            const icon = rec.severity === 'critical'
                ? '<i class="fa-solid fa-triangle-exclamation text-red"></i>'
                : '<i class="fa-solid fa-circle-exclamation text-orange"></i>';

            card.innerHTML = `
                <div class="insight-header">
                    ${icon}
                    <h4>${rec.app_name} Impact</h4>
                </div>
                <p>High ${rec.metric} Usage: <strong>${rec.value}</strong></p>
                <p style="font-size:0.8rem; margin-top:4px;">${rec.suggestion}</p>
            `;
            container.appendChild(card);
        });
    }

    function updateTopAppsList(apps) {
        const container = document.getElementById('top-apps-list');
        if (!container) return;

        container.innerHTML = '';

        // Take top 4 by CPU
        const topApps = apps.slice(0, 4);

        topApps.forEach((app, index) => {
            const cpu = parseFloat(app.cpu_usage);

            let color = 'bar-blue';
            if (index === 0) color = 'bar-red';
            else if (index === 1) color = 'bar-orange';
            else if (index === 2) color = 'bar-yellow';

            const item = document.createElement('div');
            item.className = 'top-app-item';

            item.innerHTML = `
                <div class="app-name-col">${app.app_name}</div>
                <div class="app-bar-wrapper">
                    <div class="app-bar-fill ${color}" style="width: ${Math.min(cpu, 100)}%"></div>
                </div>
                <div class="percent-label">${cpu.toFixed(1)}%</div>
            `;
            container.appendChild(item);
        });
    }

    function updateDistChart(sysData, apps) {
        if (!sysData || !apps) return;

        const sysMem = parseFloat(sysData.memory_usage);

        // Calculate total app memory usage in MB
        const totalAppMem = apps.reduce((acc, app) => acc + app.memory_usage, 0);
        // Convert to GB to match System total (approx 16GB) or just use % of system
        // Let's approximate App Load % = (Total App MB / (Total RAM MB)) * 100
        // We know sysData.available_memory (GB) and sysMem (%).
        // Total RAM = Available / (1 - Used%)

        let appLoadPercent = 0;
        const availGB = parseFloat(sysData.available_memory);
        const usedPercentDecimal = sysMem / 100;

        if (usedPercentDecimal < 0.99 && usedPercentDecimal > 0) {
            const totalGB = availGB / (1 - usedPercentDecimal);
            const totalMB = totalGB * 1024;
            if (totalMB > 0) {
                appLoadPercent = (totalAppMem / totalMB) * 100;
            }
        } else {
            // Fallback if near 100% or 0%
            appLoadPercent = (totalAppMem / 16384) * 100; // Asume 16GB
        }

        // Ensure App Load matches visualization expectation (App is part of System, or Comparison?)
        // Let's show: Line 1 = Total System Load. Line 2 = App Load.

        // Push data
        // We need history for this too? "distChart" has labels from state.
        // We need to store history for dist chart or just push to existing chart datasets if using same labels state.
        // Yes, labels are shared.

        // distChart datasets[0] -> System
        // distChart datasets[1] -> App

        const d0 = distChart.data.datasets[0].data;
        const d1 = distChart.data.datasets[1].data;

        d0.push(sysMem);
        if (d0.length > CHART_MAX_POINTS) d0.shift();

        d1.push(appLoadPercent);
        if (d1.length > CHART_MAX_POINTS) d1.shift();

        distChart.update('none');
    }

    // --- Theme Toggle ---
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            document.body.classList.toggle('light-theme');
            const isLight = document.body.classList.contains('light-theme');
            const icon = themeBtn.querySelector('i');
            if (isLight) {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
                Chart.defaults.color = '#475569';
                Chart.defaults.borderColor = '#e2e8f0';
            } else {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
                Chart.defaults.color = '#94a3b8';
                Chart.defaults.borderColor = '#334155';
            }
            // Update charts color dynamically
            cpuChart.options.scales.x.grid.color = Chart.defaults.borderColor;
            cpuChart.options.scales.y.grid.color = Chart.defaults.borderColor;
            memoryChart.options.scales.x.grid.color = Chart.defaults.borderColor;
            memoryChart.options.scales.y.grid.color = Chart.defaults.borderColor;
            distChart.options.scales.x.grid.color = Chart.defaults.borderColor;
            distChart.options.scales.y.grid.color = Chart.defaults.borderColor;
            distChart.options.scales.y.ticks.color = Chart.defaults.color;
            cpuChart.update();
            memoryChart.update();
            distChart.update();
        });
    }

    // Start
    fetchData();
    setInterval(fetchData, UPDATE_INTERVAL);
});
