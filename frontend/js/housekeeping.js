/**
 * Housekeeping Management Module
 * Handles housekeeping tasks, room status, and staff performance
 */

// ==================== API Functions ====================

/**
 * Fetch housekeeping dashboard statistics
 */
async function fetchHousekeepingDashboard() {
  try {
    const response = await fetch(`${API_BASE_URL}/reports/housekeeping/dashboard`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch dashboard');
    return await response.json();
  } catch (error) {
    console.error('Error fetching housekeeping dashboard:', error);
    showMessage('housekeeping-message', 'Failed to load dashboard', 'error');
    return null;
  }
}

/**
 * Fetch all housekeeping tasks with optional filters
 */
async function fetchHousekeepingTasks(filters = {}) {
  try {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.priority) params.append('priority', filters.priority);
    if (filters.task_type) params.append('task_type', filters.task_type);
    if (filters.room_id) params.append('room_id', filters.room_id);
    
    const url = `${API_BASE_URL}/housekeeping/tasks/${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch tasks');
    return await response.json();
  } catch (error) {
    console.error('Error fetching tasks:', error);
    showMessage('housekeeping-message', 'Failed to load tasks', 'error');
    return [];
  }
}

/**
 * Create a new housekeeping task
 */
async function createHousekeepingTask(taskData) {
  try {
    const response = await fetch(`${API_BASE_URL}/housekeeping/tasks/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(taskData),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create task');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating task:', error);
    throw error;
  }
}

/**
 * Assign a task to a user
 */
async function assignTask(taskId, userId) {
  try {
    const response = await fetch(`${API_BASE_URL}/housekeeping/tasks/${taskId}/assign`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ assigned_to: userId }),
    });
    if (!response.ok) throw new Error('Failed to assign task');
    return await response.json();
  } catch (error) {
    console.error('Error assigning task:', error);
    throw error;
  }
}

/**
 * Start a task
 */
async function startTask(taskId) {
  try {
    const response = await fetch(`${API_BASE_URL}/housekeeping/tasks/${taskId}/start`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to start task');
    return await response.json();
  } catch (error) {
    console.error('Error starting task:', error);
    throw error;
  }
}

/**
 * Complete a task
 */
async function completeTask(taskId, completionData) {
  try {
    const response = await fetch(`${API_BASE_URL}/housekeeping/tasks/${taskId}/complete`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(completionData),
    });
    if (!response.ok) throw new Error('Failed to complete task');
    return await response.json();
  } catch (error) {
    console.error('Error completing task:', error);
    throw error;
  }
}

/**
 * Verify a completed task
 */
async function verifyTask(taskId, verificationData) {
  try {
    const response = await fetch(`${API_BASE_URL}/housekeeping/tasks/${taskId}/verify`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(verificationData),
    });
    if (!response.ok) throw new Error('Failed to verify task');
    return await response.json();
  } catch (error) {
    console.error('Error verifying task:', error);
    throw error;
  }
}

/**
 * Fetch room status grid
 */
async function fetchRoomStatusGrid() {
  try {
    const response = await fetch(`${API_BASE_URL}/reports/housekeeping/room-status-grid`, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) throw new Error('Failed to fetch room status grid');
    return await response.json();
  } catch (error) {
    console.error('Error fetching room grid:', error);
    showMessage('housekeeping-message', 'Failed to load room grid', 'error');
    return null;
  }
}

// ==================== UI Functions ====================

/**
 * Initialize housekeeping tab
 */
async function initHousekeeping() {
  await loadHousekeepingDashboard();
  await loadHousekeepingTasks();
  
  // Set default date to today
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('hk-scheduled-date').value = today;
  
  // Event listeners
  document.getElementById('btn-refresh-housekeeping').addEventListener('click', refreshHousekeeping);
  document.getElementById('btn-create-task').addEventListener('click', handleCreateTask);
  document.getElementById('btn-apply-filters').addEventListener('click', applyFilters);
  document.getElementById('btn-clear-filters').addEventListener('click', clearFilters);
  document.getElementById('btn-view-room-grid').addEventListener('click', showRoomGrid);
}

/**
 * Refresh all housekeeping data
 */
async function refreshHousekeeping() {
  await loadHousekeepingDashboard();
  await loadHousekeepingTasks();
  showMessage('housekeeping-message', 'Data refreshed', 'success');
}

/**
 * Load and display dashboard statistics
 */
async function loadHousekeepingDashboard() {
  const dashboard = await fetchHousekeepingDashboard();
  if (!dashboard) return;
  
  // Update stat cards
  document.getElementById('hk-total-tasks').textContent = dashboard.total_tasks;
  document.getElementById('hk-pending-tasks').textContent = dashboard.pending_tasks;
  document.getElementById('hk-in-progress-tasks').textContent = dashboard.in_progress_tasks;
  document.getElementById('hk-completed-tasks').textContent = dashboard.tasks_completed_today;
  document.getElementById('hk-urgent-tasks').textContent = dashboard.urgent_tasks;
  document.getElementById('hk-rooms-maintenance').textContent = dashboard.rooms_in_maintenance;
  
  // Update room status summary
  document.getElementById('rooms-available-count').textContent = dashboard.rooms_available;
  document.getElementById('rooms-maintenance-count').textContent = dashboard.rooms_in_maintenance;
  document.getElementById('rooms-out-of-service-count').textContent = dashboard.rooms_out_of_service;
}

/**
 * Load and display housekeeping tasks
 */
async function loadHousekeepingTasks(filters = {}) {
  const tasks = await fetchHousekeepingTasks(filters);
  const tbody = document.getElementById('housekeeping-task-list');
  tbody.innerHTML = '';
  
  if (!tasks || tasks.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No tasks found</td></tr>';
    return;
  }
  
  tasks.forEach(task => {
    const row = createTaskRow(task);
    tbody.appendChild(row);
  });
}

/**
 * Create a table row for a task
 */
function createTaskRow(task) {
  const tr = document.createElement('tr');
  
  // Priority and status badges
  const priorityClass = `priority-${task.priority}`;
  const statusClass = `status-${task.status}`;
  
  tr.innerHTML = `
    <td>${task.id}</td>
    <td>Room ${task.room_number || task.room_id}</td>
    <td>${task.task_type}</td>
    <td><span class="badge ${priorityClass}">${task.priority}</span></td>
    <td><span class="badge ${statusClass}">${task.status}</span></td>
    <td>${formatDate(task.scheduled_date)} ${task.scheduled_time || ''}</td>
    <td>${task.assigned_to_username || 'Unassigned'}</td>
    <td class="action-buttons">
      ${getTaskActionButtons(task)}
    </td>
  `;
  
  return tr;
}

/**
 * Get action buttons based on task status and user permissions
 */
function getTaskActionButtons(task) {
  const buttons = [];
  
  // Start button (pending -> in_progress)
  if (task.status === 'pending' && task.assigned_to) {
    buttons.push(`<button class="btn-icon" onclick="handleStartTask(${task.id})" title="Start Task">▶️</button>`);
  }
  
  // Complete button (in_progress -> completed)
  if (task.status === 'in_progress') {
    buttons.push(`<button class="btn-icon" onclick="handleCompleteTask(${task.id})" title="Complete Task">✅</button>`);
  }
  
  // Verify button (completed -> verified)
  if (task.status === 'completed') {
    buttons.push(`<button class="btn-icon" onclick="handleVerifyTask(${task.id})" title="Verify Task">🔍</button>`);
  }
  
  // Assign button (if unassigned)
  if (!task.assigned_to) {
    buttons.push(`<button class="btn-icon" onclick="handleAssignTask(${task.id})" title="Assign Task">👤</button>`);
  }
  
  // View details
  buttons.push(`<button class="btn-icon" onclick="viewTaskDetails(${task.id})" title="View Details">ℹ️</button>`);
  
  return buttons.join('');
}

/**
 * Handle task creation
 */
async function handleCreateTask() {
  const taskData = {
    room_id: parseInt(document.getElementById('hk-room-id').value),
    task_type: document.getElementById('hk-task-type').value,
    priority: document.getElementById('hk-priority').value,
    scheduled_date: document.getElementById('hk-scheduled-date').value,
    scheduled_time: document.getElementById('hk-scheduled-time').value,
    notes: document.getElementById('hk-notes').value,
    estimated_duration_minutes: parseInt(document.getElementById('hk-duration').value),
  };
  
  try {
    await createHousekeepingTask(taskData);
    showMessage('housekeeping-message', 'Task created successfully', 'success');
    document.getElementById('housekeeping-task-form').reset();
    
    // Reset defaults
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('hk-scheduled-date').value = today;
    document.getElementById('hk-scheduled-time').value = '10:00';
    document.getElementById('hk-duration').value = '30';
    
    await refreshHousekeeping();
  } catch (error) {
    showMessage('housekeeping-message', error.message, 'error');
  }
}

/**
 * Handle task assignment
 */
async function handleAssignTask(taskId) {
  const userId = prompt('Enter User ID to assign:');
  if (!userId) return;
  
  try {
    await assignTask(taskId, parseInt(userId));
    showMessage('housekeeping-message', 'Task assigned successfully', 'success');
    await loadHousekeepingTasks();
  } catch (error) {
    showMessage('housekeeping-message', 'Failed to assign task', 'error');
  }
}

/**
 * Handle starting a task
 */
async function handleStartTask(taskId) {
  try {
    await startTask(taskId);
    showMessage('housekeeping-message', 'Task started', 'success');
    await refreshHousekeeping();
  } catch (error) {
    showMessage('housekeeping-message', 'Failed to start task', 'error');
  }
}

/**
 * Handle completing a task
 */
async function handleCompleteTask(taskId) {
  const notes = prompt('Completion notes (optional):');
  const duration = prompt('Actual duration in minutes:');
  
  const completionData = {
    completion_notes: notes || '',
    actual_duration_minutes: duration ? parseInt(duration) : null,
  };
  
  try {
    await completeTask(taskId, completionData);
    showMessage('housekeeping-message', 'Task completed', 'success');
    await refreshHousekeeping();
  } catch (error) {
    showMessage('housekeeping-message', 'Failed to complete task', 'error');
  }
}

/**
 * Handle verifying a task
 */
async function handleVerifyTask(taskId) {
  const notes = prompt('Verification notes (optional):');
  
  const verificationData = {
    verification_notes: notes || '',
  };
  
  try {
    await verifyTask(taskId, verificationData);
    showMessage('housekeeping-message', 'Task verified', 'success');
    await refreshHousekeeping();
  } catch (error) {
    showMessage('housekeeping-message', 'Failed to verify task', 'error');
  }
}

/**
 * View task details (placeholder)
 */
function viewTaskDetails(taskId) {
  // TODO: Implement detailed task view modal
  alert(`View details for task #${taskId}`);
}

/**
 * Apply filters
 */
async function applyFilters() {
  const filters = {
    status: document.getElementById('hk-filter-status').value,
    priority: document.getElementById('hk-filter-priority').value,
    task_type: document.getElementById('hk-filter-type').value,
  };
  
  await loadHousekeepingTasks(filters);
}

/**
 * Clear all filters
 */
async function clearFilters() {
  document.getElementById('hk-filter-status').value = '';
  document.getElementById('hk-filter-priority').value = '';
  document.getElementById('hk-filter-type').value = '';
  await loadHousekeepingTasks();
}

/**
 * Show room status grid
 */
async function showRoomGrid() {
  const gridData = await fetchRoomStatusGrid();
  if (!gridData) return;
  
  // Create modal for room grid
  let html = `
    <div class="modal modal-active" id="room-grid-modal">
      <div class="modal-content" style="max-width: 90%; max-height: 90%; overflow-y: auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h2>Room Status Grid - ${gridData.as_of_date}</h2>
          <button onclick="closeRoomGridModal()" class="btn btn-secondary">Close</button>
        </div>
        <div class="room-grid">
  `;
  
  gridData.rooms.forEach(room => {
    const statusClass = room.maintenance_status.toLowerCase();
    const hasTasks = room.has_pending_tasks || room.has_in_progress_tasks;
    const nextBooking = room.next_booking_checkin ? `Next: ${room.next_booking_checkin}` : 'No upcoming booking';
    
    html += `
      <div class="room-card status-${statusClass} ${hasTasks ? 'has-tasks' : ''}">
        <div class="room-number">${room.room_number}</div>
        <div class="room-type">${room.room_type}</div>
        <div class="room-status">${room.maintenance_status}</div>
        ${hasTasks ? '<div class="room-tasks">📋 Has tasks</div>' : ''}
        <div class="room-booking">${nextBooking}</div>
      </div>
    `;
  });
  
  html += `
        </div>
      </div>
    </div>
  `;
  
  const container = document.createElement('div');
  container.innerHTML = html;
  document.body.appendChild(container.firstElementChild);
}

/**
 * Close room grid modal
 */
function closeRoomGridModal() {
  const modal = document.getElementById('room-grid-modal');
  if (modal) modal.remove();
}

/**
 * Format date for display
 */
function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString();
}

// Initialize when tab is selected
document.addEventListener('DOMContentLoaded', () => {
  // Initialize only when housekeeping tab is clicked
  const housekeepingTab = document.querySelector('[data-tab="housekeeping"]');
  if (housekeepingTab) {
    let initialized = false;
    housekeepingTab.addEventListener('click', () => {
      if (!initialized) {
        initHousekeeping();
        initialized = true;
      }
    });
  }
});
