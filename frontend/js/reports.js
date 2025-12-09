// Report functionality and chart rendering

let currentReportChart = null;

// Fetch reports
async function fetchOccupancyReport() {
  const start = document.getElementById('report-start').value;
  const end = document.getElementById('report-end').value;
  if (!start || !end) {
    showMessage('reports-message', 'Select start and end dates', true);
    return;
  }

  const out = document.getElementById('report-output');
  out.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">Loading occupancy report...</div>';
  showMessage('reports-message', 'Fetching occupancy...');

  try {
    const data = await fetchOccupancyReportAPI(start, end);
    if (!data.daily || data.daily.length === 0) {
      out.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">No occupancy data available for selected date range.</div>';
      showMessage('reports-message', 'No data found', true);
      return;
    }
    renderOccupancyReport(data);
    showMessage('reports-message', '');
  } catch (e) {
    out.innerHTML = '';
    showMessage('reports-message', `Failed: ${e.message}`, true);
  }
}

async function fetchRevenueReport() {
  const start = document.getElementById('report-start').value;
  const end = document.getElementById('report-end').value;
  if (!start || !end) {
    showMessage('reports-message', 'Select start and end dates', true);
    return;
  }

  const out = document.getElementById('report-output');
  out.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">Loading revenue report...</div>';
  showMessage('reports-message', 'Fetching revenue...');

  try {
    const data = await fetchRevenueReportAPI(start, end);
    if (!data.daily || data.daily.length === 0) {
      out.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">No revenue data available for selected date range.</div>';
      showMessage('reports-message', 'No data found', true);
      return;
    }
    renderRevenueReport(data);
    showMessage('reports-message', '');
  } catch (e) {
    out.innerHTML = '';
    showMessage('reports-message', `Failed: ${e.message}`, true);
  }
}

async function fetchTrendsReport() {
  const start = document.getElementById('report-start').value;
  const end = document.getElementById('report-end').value;
  if (!start || !end) {
    showMessage('reports-message', 'Select start and end dates', true);
    return;
  }

  const out = document.getElementById('report-output');
  out.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">Loading trends report...</div>';
  showMessage('reports-message', 'Fetching trends...');

  try {
    const data = await fetchTrendsReportAPI(start, end);
    if (data.total_bookings === 0) {
      out.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-secondary);">No booking data available for selected date range.</div>';
      showMessage('reports-message', 'No data found', true);
      return;
    }
    renderTrendsReport(data);
    showMessage('reports-message', '');
  } catch (e) {
    out.innerHTML = '';
    showMessage('reports-message', `Failed: ${e.message}`, true);
  }
}

// Render reports
function renderOccupancyReport(data) {
  clearReportExports();
  const out = document.getElementById('report-output');
  out.innerHTML = '';
  const header = document.createElement('div');
  header.className = 'report-header';
  header.innerHTML = `<strong>Occupancy</strong> — ${fmtDate(data.start_date)} to ${fmtDate(data.end_date)}`;
  out.appendChild(header);

  // Chart section
  const chartSection = document.createElement('div');
  chartSection.id = 'report-chart-container';
  chartSection.style.height = '320px';
  const canvas = document.createElement('canvas');
  canvas.id = 'report-chart';
  chartSection.appendChild(canvas);
  out.appendChild(chartSection);

  // Summary section
  const summary = document.createElement('div');
  summary.className = 'report-summary';
  summary.appendChild(createStatCard('Average Occupancy', fmtPercent(data.average_occupancy)));
  summary.appendChild(createStatCard('Peak Occupancy', fmtPercent(data.max_occupancy)));
  summary.appendChild(createStatCard('Min Occupancy', fmtPercent(data.min_occupancy)));
  summary.appendChild(createStatCard('Total Room-Nights', safeText(data.total_room_nights)));
  out.appendChild(summary);

  // Render the actual chart
  setTimeout(() => renderOccupancyChart(data), 0);

  // Export buttons
  showExportButtons('occupancy', data);
}

function renderRevenueReport(data) {
  clearReportExports();
  const out = document.getElementById('report-output');
  out.innerHTML = '';
  const header = document.createElement('div');
  header.className = 'report-header';
  header.innerHTML = `<strong>Revenue</strong> — ${fmtDate(data.start_date)} to ${fmtDate(data.end_date)}`;
  out.appendChild(header);

  // Chart section
  const chartSection = document.createElement('div');
  chartSection.id = 'report-chart-container';
  chartSection.style.height = '520px';
  const canvas = document.createElement('canvas');
  canvas.id = 'report-chart';
  chartSection.appendChild(canvas);
  out.appendChild(chartSection);

  // Summary section
  const summary = document.createElement('div');
  summary.className = 'report-summary';
  summary.appendChild(createStatCard('Total Revenue', fmtCurrency(data.total_revenue)));
  summary.appendChild(createStatCard('Avg Daily Revenue', fmtCurrency(data.average_daily_revenue)));
  summary.appendChild(createStatCard('Max Daily Revenue', fmtCurrency(data.max_daily_revenue)));
  summary.appendChild(createStatCard('Min Daily Revenue', fmtCurrency(data.min_daily_revenue)));
  summary.appendChild(createStatCard('Paid Bookings', safeText(data.total_paid_bookings)));

  // Add room type breakdown
  if (data.room_type_breakdown && data.room_type_breakdown.length > 0) {
    const topRoomType = data.room_type_breakdown.reduce((max, rt) =>
      Number(rt.revenue) > Number(max.revenue) ? rt : max, data.room_type_breakdown[0]);
    summary.appendChild(createStatCard('Top Room Type', `${topRoomType.room_type} (${fmtCurrency(topRoomType.revenue)})`));
  }

  out.appendChild(summary);

  // Render the actual chart
  setTimeout(() => renderRevenueChart(data), 0);

  // Export buttons
  showExportButtons('revenue', data);
}

function renderTrendsReport(data) {
  clearReportExports();
  const out = document.getElementById('report-output');
  out.innerHTML = '';
  const header = document.createElement('div');
  header.className = 'report-header';
  header.innerHTML = `<strong>Booking Trends</strong> — ${fmtDate(data.start_date)} to ${fmtDate(data.end_date)}`;
  out.appendChild(header);

  // Chart section
  const chartSection = document.createElement('div');
  chartSection.id = 'report-chart-container';
  chartSection.style.height = '420px';
  chartSection.style.maxWidth = '80%';
  chartSection.style.margin = '0 auto';
  const canvas = document.createElement('canvas');
  canvas.id = 'report-chart';
  chartSection.appendChild(canvas);
  out.appendChild(chartSection);

  const grid = document.createElement('div');
  grid.className = 'report-summary';
  grid.appendChild(createStatCard('Total Bookings', data.total_bookings));
  grid.appendChild(createStatCard('Confirmed', data.confirmed_bookings));
  grid.appendChild(createStatCard('Cancellations', data.cancellations));
  grid.appendChild(createStatCard('No-shows', data.no_shows));
  grid.appendChild(createStatCard('Cancel Rate', fmtPercent(data.cancellation_rate)));
  grid.appendChild(createStatCard('No-show Rate', fmtPercent(data.no_show_rate)));
  grid.appendChild(createStatCard('Avg Lead Time', `${Math.round(data.avg_lead_time_days) || 0} days`));
  grid.appendChild(createStatCard('Avg Stay', `${Math.round(data.avg_length_of_stay_nights) || 0} nights`));
  out.appendChild(grid);

  // Chart - render after DOM is ready
  setTimeout(() => renderTrendsChart(data), 0);

  // Export buttons
  showExportButtons('trends', data);
}

// Chart rendering
function renderOccupancyChart(data) {
  const container = document.getElementById('report-chart-container');
  const canvas = document.getElementById('report-chart');
  if (!container || !canvas) return;

  let labels = (data.daily || []).map(d => fmtDate(d.date));
  let rates = (data.daily || []).map(d => Number(d.occupancy_rate) || 0);

  container.style.display = 'block';

  if (currentReportChart) currentReportChart.destroy();

  // Aggregate data for large date ranges
  const dayCount = labels.length;
  if (dayCount > 90) {
    const aggregateSize = dayCount > 180 ? 30 : 7; // Monthly for 180+ days, weekly for 90+ days
    const newLabels = [];
    const newRates = [];
    const monthFormatter = new Intl.DateTimeFormat('en', { month: 'short', year: '2-digit' });

    for (let i = 0; i < labels.length; i += aggregateSize) {
      const chunk = rates.slice(i, i + aggregateSize);
      const avgRate = chunk.length > 0 ? chunk.reduce((a, b) => a + b, 0) / chunk.length : 0;

      let label;
      if (dayCount > 180) {
        // Monthly: use month name
        const date = new Date(labels[i]);
        label = monthFormatter.format(date);
      } else {
        // Weekly: use date range
        label = labels[i] + ' to ' + labels[Math.min(i + aggregateSize - 1, labels.length - 1)];
      }

      newLabels.push(label);
      newRates.push(Number(avgRate.toFixed(2)));
    }
    labels = newLabels;
    rates = newRates;
  }

  currentReportChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Occupancy Rate (%)',
        data: rates,
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        tension: 0.4,
        fill: true,
        borderWidth: 2,
        pointRadius: dayCount > 90 ? 5 : 3
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false, position: 'top' } },
      scales: {
        y: { beginAtZero: true, max: 100, ticks: { callback: v => v + '%' } },
        x: { ticks: { maxRotation: 45, minRotation: 0 } }
      }
    }
  });
}

function renderRevenueChart(data) {
  const container = document.getElementById('report-chart-container');
  const canvas = document.getElementById('report-chart');
  if (!container || !canvas) return;

  let labels = (data.daily || []).map(d => fmtDate(d.date));
  let revenues = (data.daily || []).map(d => Number(d.revenue) || 0);

  container.style.display = 'block';

  if (currentReportChart) currentReportChart.destroy();

  // Aggregate data for large date ranges
  const dayCount = labels.length;
  if (dayCount > 90) {
    const aggregateSize = dayCount > 180 ? 30 : 7; // Monthly for 180+ days, weekly for 90+ days
    const newLabels = [];
    const newRevenues = [];
    const monthFormatter = new Intl.DateTimeFormat('en', { month: 'short', year: '2-digit' });

    for (let i = 0; i < labels.length; i += aggregateSize) {
      const chunk = revenues.slice(i, i + aggregateSize);
      const sumRevenue = chunk.reduce((a, b) => a + b, 0);

      let label;
      if (dayCount > 180) {
        // Monthly: use month name
        const date = new Date(labels[i]);
        label = monthFormatter.format(date);
      } else {
        // Weekly: use date range
        label = labels[i] + ' to ' + labels[Math.min(i + aggregateSize - 1, labels.length - 1)];
      }

      newLabels.push(label);
      newRevenues.push(Number(sumRevenue.toFixed(2)));
    }
    labels = newLabels;
    revenues = newRevenues;
  }

  currentReportChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: dayCount > 90 ? 'Period Revenue' : 'Daily Revenue',
        data: revenues,
        borderColor: 'rgba(52, 152, 219, 0.1)',
        backgroundColor: 'rgba(52, 152, 219, 0.2)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false, position: 'top' } },
      scales: {
        y: { beginAtZero: true },
        x: { ticks: { maxRotation: 45, minRotation: 0 } }
      }
    }
  });
}

function renderTrendsChart(data) {
  const container = document.getElementById('report-chart-container');
  const canvas = document.getElementById('report-chart');
  if (!container || !canvas) return;

  container.style.display = 'block';

  if (currentReportChart) currentReportChart.destroy();

  currentReportChart = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: ['Confirmed', 'Cancelled', 'No-shows'],
      datasets: [{
        data: [
          data.confirmed_bookings || 0,
          data.cancellations || 0,
          data.no_shows || 0
        ],
        backgroundColor: ['#27ae60', '#e74c3c', '#f39c12'],
        borderWidth: 2,
        borderColor: '#ecf0f1'
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true, position: 'right' } }
    }
  });
}

// Export functions
function clearReportExports() {
  const container = document.getElementById('report-export-buttons');
  if (container) container.innerHTML = '';
  const chartContainer = document.getElementById('report-chart-container');
  if (chartContainer) chartContainer.style.display = 'none';
}

function showExportButtons(reportType, data) {
  const container = document.getElementById('report-export-buttons');
  if (!container) return;

  container.innerHTML = '';

  const csvBtn = document.createElement('button');
  csvBtn.className = 'btn btn-secondary btn-sm';
  csvBtn.textContent = '📥 CSV';
  csvBtn.addEventListener('click', () => exportCSV(reportType, data));
  container.appendChild(csvBtn);

  const pdfBtn = document.createElement('button');
  pdfBtn.className = 'btn btn-secondary btn-sm';
  pdfBtn.textContent = '📄 PDF';
  pdfBtn.addEventListener('click', () => exportPDF(reportType, data));
  container.appendChild(pdfBtn);
}

function exportCSV(reportType, data) {
  let csv = '';
  const timestamp = new Date().toISOString().slice(0, 10);

  if (reportType === 'occupancy') {
    csv = 'Occupancy Report\n';
    csv += `Period: ${fmtDate(data.start_date)} to ${fmtDate(data.end_date)}\n`;
    csv += `Average Occupancy: ${fmtPercent(data.average_occupancy)}\n\n`;
    csv += 'Date,Occupied,Total Rooms,Occupancy Rate\n';
    (data.daily || []).forEach(d => {
      csv += `${fmtDate(d.date)},${d.occupied},${d.total_rooms},${d.occupancy_rate}%\n`;
    });
  } else if (reportType === 'revenue') {
    csv = 'Revenue Report\n';
    csv += `Period: ${fmtDate(data.start_date)} to ${fmtDate(data.end_date)}\n`;
    csv += `Total Revenue: ${fmtCurrency(data.total_revenue)}\n\n`;
    csv += 'Date,Revenue\n';
    (data.daily || []).forEach(d => {
      csv += `${fmtDate(d.date)},${d.revenue}\n`;
    });
  } else if (reportType === 'trends') {
    csv = 'Booking Trends Report\n';
    csv += `Period: ${fmtDate(data.start_date)} to ${fmtDate(data.end_date)}\n\n`;
    csv += 'Metric,Value\n';
    csv += `Total Bookings,${data.total_bookings}\n`;
    csv += `Cancellations,${data.cancellations}\n`;
    csv += `No-shows,${data.no_shows}\n`;
    csv += `Cancellation Rate,${data.cancellation_rate}%\n`;
    csv += `No-show Rate,${data.no_show_rate}%\n`;
  }

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${reportType}-report-${timestamp}.csv`;
  link.click();
}

function exportPDF(reportType, data) {
  // Simple PDF export by printing to PDF
  const element = document.getElementById('report-output');
  if (!element) return;

  // Create a new window for printing
  const printWindow = window.open('', '', 'width=900,height=600');
  printWindow.document.write('<html><head><title>');
  printWindow.document.write(reportType + ' Report - ' + new Date().toISOString().slice(0, 10));
  printWindow.document.write('</title><style>');
  printWindow.document.write(`
    body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th { background: #3498db; color: white; padding: 10px; text-align: left; }
    td { padding: 8px; border-bottom: 1px solid #ddd; }
    tr:nth-child(even) { background: #f9f9f9; }
    .report-header { font-size: 20px; font-weight: bold; margin: 20px 0 10px 0; border-bottom: 2px solid #3498db; }
    .report-summary { margin: 20px 0; }
    dt { font-weight: bold; margin-top: 10px; }
    dd { margin-left: 20px; font-size: 16px; }
  `);
  printWindow.document.write('</style></head><body>');
  printWindow.document.write(element.innerHTML);
  printWindow.document.write('</body></html>');
  printWindow.document.close();

  // Trigger print dialog
  setTimeout(() => {
    printWindow.print();
  }, 250);
}
