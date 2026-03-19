// --- Configuration ---
const CONFIG = {
    // OpenClaw Gateway (local only)
    OPENCLAW_WS_URL: 'ws://localhost:18789',
    
    // n8n Webhook URLs (update these with your actual webhook IDs)
    N8N_WEBHOOKS: {
        APPROVE_POST: 'http://localhost:5678/webhook/approve-post',
        REJECT_POST: 'http://localhost:5678/webhook/reject-post',
        GET_AGENTS: 'http://localhost:5678/webhook/get-agents',
        GET_QUEUE: 'http://localhost:5678/webhook/get-queue',
        GET_PIPELINE: 'http://localhost:5678/webhook/get-pipeline',
        GET_ANALYTICS: 'http://localhost:5678/webhook/get-analytics',
        SEND_COMMAND: 'http://localhost:5678/webhook/agent-command'
    },
    
    // Refresh intervals (ms)
    REFRESH_INTERVAL: 30000,
    WS_RECONNECT_DELAY: 5000
};

// --- State Management ---
const state = {
    ws: null,
    isLocalhost: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1',
    agents: [],
    queue: [],
    pipeline: [],
    analytics: {},
    notifications: [],
    lastRefresh: null
};

// --- Utilities ---
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

const showToast = (message, type = 'success') => {
    const container = $('#toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const iconMap = {
        success: 'check-circle',
        error: 'x-circle',
        warning: 'alert-triangle',
        info: 'info'
    };
    
    toast.innerHTML = `<i data-lucide="${iconMap[type] || 'info'}"></i> <span>${message}</span>
    `;
    container.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
};

const formatCurrency = (value) => {
    if (value === null || value === undefined) return '--';
    return '€' + parseFloat(value).toFixed(2);
};

const formatNumber = (value) => {
    if (value === null || value === undefined) return '--';
    return value.toLocaleString('de-DE');
};

const timeAgo = (date) => {
    if (!date) return '--';
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
};

// --- API Functions ---
async function fetchFromN8N(endpoint, payload = {}) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return null;
    }
}

// --- Data Fetching ---
async function loadAgents() {
    const data = await fetchFromN8N(CONFIG.N8N_WEBHOOKS.GET_AGENTS);
    if (!data) return;
    
    state.agents = data.agents || [];
    renderAgents();
    updateMetrics(data.metrics);
}

async function loadQueue() {
    const data = await fetchFromN8N(CONFIG.N8N_WEBHOOKS.GET_QUEUE);
    if (!data) return;
    
    state.queue = data.queue || [];
    renderQueue();
    renderScheduled(data.scheduled || []);
}

async function loadPipeline() {
    const data = await fetchFromN8N(CONFIG.N8N_WEBHOOKS.GET_PIPELINE);
    if (!data) return;
    
    state.pipeline = data.leads || [];
    renderPipeline();
    updatePipelineStats(data.stats);
}

async function loadAnalytics(period = '7d') {
    const data = await fetchFromN8N(CONFIG.N8N_WEBHOOKS.GET_ANALYTICS, { period });
    if (!data) return;
    
    state.analytics = data;
    renderAnalytics();
}

// --- Rendering ---
function renderAgents() {
    const container = $('#agent-list');
    
    if (state.agents.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i data-lucide="server-off"></i>
                <p>No active agents</p>
            </div>
        `;
    } else {
        container.innerHTML = state.agents.map(agent => `
            <div class="agent-card" data-id="${agent.id}">
                <div class="agent-icon bg-${agent.color || 'blue'}">
                    <i data-lucide="${agent.icon || 'cpu'}"></i>
                </div>
                <div class="agent-info">
                    <h4>${agent.name}</h4>
                    <p>${agent.status === 'running' ? agent.task : 'Idle'}</p>
                </div>
                <div class="status-badge ${agent.status}">
                    ${agent.status === 'running' ? '<i data-lucide="loader" class="spin"></i>' : ''}
                    ${agent.status}
                </div>
            </div>
        `).join('');
    }
    
    lucide.createIcons();
}

function updateMetrics(metrics = {}) {
    $('#metric-cost').textContent = formatCurrency(metrics.apiCost);
    $('#metric-jobs').textContent = formatNumber(metrics.activeJobs);
    $('#metric-pending').textContent = formatNumber(metrics.pendingReviews);
    $('#api-cost').textContent = formatCurrency(metrics.apiCost);
    $('#cron-count').textContent = formatNumber(metrics.cronJobs);
}

function renderQueue() {
    const container = $('#approval-queue');
    const countBadge = $('#queue-count');
    
    countBadge.textContent = state.queue.length;
    countBadge.style.display = state.queue.length > 0 ? 'inline-flex' : 'none';
    
    if (state.queue.length === 0) {
        container.innerHTML = `
            <div class="empty-state small">
                <i data-lucide="inbox"></i>
                <p>No drafts pending approval</p>
            </div>
        `;
    } else {
        container.innerHTML = state.queue.map(item => `
            <div class="draft-card" data-id="${item.id}">
                <div class="platform-icon ${item.platform}">
                    <i data-lucide="${item.platform}"></i>
                </div>
                <div class="draft-content">
                    <p class="draft-meta">${item.platform} • ${timeAgo(item.createdAt)}</p>
                    <p class="draft-text">${escapeHtml(item.content)}</p>
                    <div class="draft-actions">
                        <button class="btn btn-outline deny-btn" data-id="${item.id}">
                            <i data-lucide="x"></i> Reject
                        </button>
                        <button class="btn btn-primary approve-btn" data-id="${item.id}">
                            <i data-lucide="check"></i> Approve
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Add event listeners
        container.querySelectorAll('.approve-btn').forEach(btn => {
            btn.addEventListener('click', () => approvePost(btn.dataset.id));
        });
        container.querySelectorAll('.deny-btn').forEach(btn => {
            btn.addEventListener('click', () => rejectPost(btn.dataset.id));
        });
    }
    
    lucide.createIcons();
}

function renderScheduled(scheduled) {
    const container = $('#scheduled-posts');
    
    if (scheduled.length === 0) {
        container.innerHTML = `
            <div class="empty-state small">
                <i data-lucide="calendar"></i>
                <p>No scheduled posts</p>
            </div>
        `;
    } else {
        container.innerHTML = scheduled.map(post => `
            <div class="scheduled-item">
                <div class="scheduled-platform">
                    <i data-lucide="${post.platform}"></i>
                </div>
                <div class="scheduled-info">
                    <p class="scheduled-text">${escapeHtml(post.content.substring(0, 60))}...</p>
                    <p class="scheduled-time">${formatDateTime(post.scheduledFor)}</p>
                </div>
            </div>
        `).join('');
    }
    
    lucide.createIcons();
}

function renderPipeline() {
    const container = $('#lead-feed');
    
    if (state.pipeline.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i data-lucide="users"></i>
                <p>No active leads in pipeline</p>
            </div>
        `;
    } else {
        container.innerHTML = state.pipeline.map(lead => `
            <div class="lead-item" data-id="${lead.id}">
                <div class="lead-avatar" style="background: ${lead.avatarColor || 'linear-gradient(135deg, #3b82f6, #8b5cf6)'}">
                    ${lead.initials || lead.name.substring(0, 2).toUpperCase()}
                </div>
                <div class="lead-details">
                    <h4>${escapeHtml(lead.name)}</h4>
                    <p class="lead-summary">${escapeHtml(lead.business)} • ${lead.recommendation}</p>
                    <div class="automation-steps">
                        ${renderSteps(lead.steps)}
                    </div>
                </div>
                <button class="btn btn-sm btn-outline view-lead-btn" data-id="${lead.id}">
                    View
                </button>
            </div>
        `).join('');
        
        container.querySelectorAll('.view-lead-btn').forEach(btn => {
            btn.addEventListener('click', () => viewLead(btn.dataset.id));
        });
    }
    
    lucide.createIcons();
}

function renderSteps(steps = []) {
    return steps.map(step => `
        <span class="step ${step.status}" title="${step.name}"></span>
    `).join('');
}

function updatePipelineStats(stats = {}) {
    $('#stage-leads').textContent = formatNumber(stats.leads || 0);
    $('#stage-discovery').textContent = formatNumber(stats.discovery || 0);
    $('#stage-proposal').textContent = formatNumber(stats.proposal || 0);
    $('#stage-active').textContent = formatNumber(stats.active || 0);
}

function renderAnalytics() {
    const data = state.analytics;
    if (!data) return;
    
    $('#stat-visits').textContent = formatNumber(data.visits);
    $('#stat-forms').textContent = formatNumber(data.forms);
    $('#stat-conversion').textContent = data.conversion ? `${data.conversion}%` : '--';
    $('#stat-social').textContent = formatNumber(data.social);
    
    updateChangeIndicator('change-visits', data.visitsChange);
    updateChangeIndicator('change-forms', data.formsChange);
    updateChangeIndicator('change-conversion', data.conversionChange);
    updateChangeIndicator('change-social', data.socialChange);
}

function updateChangeIndicator(id, value) {
    const el = $(`#${id}`);
    if (!el || value === undefined) return;
    
    const isPositive = value >= 0;
    el.textContent = `${isPositive ? '+' : ''}${value}%`;
    el.className = `change ${isPositive ? 'positive' : 'negative'}`;
}

// --- Actions ---
async function approvePost(id) {
    const card = $(`.draft-card[data-id="${id}"]`);
    if (!card) return;
    
    const btn = card.querySelector('.approve-btn');
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader" class="spin"></i> Processing...';
    lucide.createIcons();
    
    const result = await fetchFromN8N(CONFIG.N8N_WEBHOOKS.APPROVE_POST, { id });
    
    if (result?.success) {
        showToast('Post approved and scheduled', 'success');
        card.remove();
        loadQueue();
    } else {
        showToast('Failed to approve post', 'error');
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="check"></i> Approve';
        lucide.createIcons();
    }
}

async function rejectPost(id) {
    const card = $(`.draft-card[data-id="${id}"]`);
    if (!card) return;
    
    const result = await fetchFromN8N(CONFIG.N8N_WEBHOOKS.REJECT_POST, { id });
    
    if (result?.success) {
        showToast('Post rejected', 'info');
        card.remove();
        loadQueue();
    } else {
        showToast('Failed to reject post', 'error');
    }
}

function viewLead(id) {
    const lead = state.pipeline.find(l => l.id === id);
    if (!lead) return;
    
    // Could open a modal or navigate to detail view
    showToast(`Viewing ${lead.name}'s profile`, 'info');
}

// --- Chat Interface ---
function appendMessage(content, sender = 'user') {
    const history = $('#chat-history');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    
    const isHtml = content.includes('<');
    const avatarIcon = sender === 'user' ? 'user' : 'cpu';
    const avatarClass = sender === 'hitl-alert' ? 'avatar bg-warning' : 'avatar';
    
    msgDiv.innerHTML = `
        <div class="${avatarClass}"><i data-lucide="${avatarIcon}"></i></div>
        <div class="msg-content">${isHtml ? content : `<p>${content}</p>`}</div>
    `;
    
    history.appendChild(msgDiv);
    lucide.createIcons();
    history.scrollTop = history.scrollHeight;
}

function showTyping() {
    const history = $('#chat-history');
    if ($('#typing-indicator')) return;
    
    const typing = document.createElement('div');
    typing.id = 'typing-indicator';
    typing.className = 'message system typing-indicator';
    typing.innerHTML = `
        <div class="avatar"><i data-lucide="loader" class="spin"></i></div>
        <div class="msg-content"><p class="text-muted">Processing...</p></div>
    `;
    history.appendChild(typing);
    lucide.createIcons();
    history.scrollTop = history.scrollHeight;
}

function hideTyping() {
    const typing = $('#typing-indicator');
    if (typing) typing.remove();
}

async function sendCommand(message) {
    appendMessage(message, 'user');
    showTyping();
    
    // Try WebSocket first if connected
    if (state.ws?.readyState === WebSocket.OPEN) {
        state.ws.send(JSON.stringify({ type: 'chat', content: message }));
        return;
    }
    
    // Fallback to HTTP
    const result = await fetchFromN8N(CONFIG.N8N_WEBHOOKS.SEND_COMMAND, { command: message });
    hideTyping();
    
    if (result?.response) {
        appendMessage(result.response, 'system');
    } else {
        appendMessage('Command processed. Check your n8n workflows for results.', 'system');
    }
}

// --- WebSocket ---
function connectWebSocket() {
    if (!state.isLocalhost) {
        updateConnectionStatus('http');
        return;
    }
    
    try {
        state.ws = new WebSocket(CONFIG.OPENCLAW_WS_URL);
        
        state.ws.onopen = () => {
            console.log('WebSocket connected');
            updateConnectionStatus('connected');
            showToast('Connected to OpenClaw Gateway', 'success');
        };
        
        state.ws.onclose = () => {
            updateConnectionStatus('disconnected');
            setTimeout(connectWebSocket, CONFIG.WS_RECONNECT_DELAY);
        };
        
        state.ws.onerror = (err) => {
            console.error('WebSocket error:', err);
            updateConnectionStatus('error');
        };
        
        state.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            } catch (e) {
                appendMessage(event.data, 'system');
            }
        };
    } catch (err) {
        console.error('Failed to connect WebSocket:', err);
        updateConnectionStatus('error');
    }
}

function updateConnectionStatus(status) {
    const ping = $('#ws-ping');
    const text = $('#ws-status');
    const gatewayStatus = $('#gateway-status');
    const gatewayText = $('#gateway-text');
    
    const statusMap = {
        connected: { class: 'online', text: 'Connected' },
        disconnected: { class: '', text: 'Disconnected' },
        error: { class: '', text: 'Error' },
        http: { class: '', text: 'HTTP Mode' }
    };
    
    const config = statusMap[status] || statusMap.disconnected;
    
    ping.className = `ping ${config.class}`;
    text.textContent = config.text;
    
    if (gatewayStatus) {
        gatewayStatus.className = `status-indicator ${config.class}`;
        gatewayText.textContent = status === 'connected' ? 'OpenClaw Gateway Live' : config.text;
    }
}

function handleWebSocketMessage(data) {
    hideTyping();
    
    switch (data.type) {
        case 'agent_reply':
            appendMessage(data.content, 'system');
            break;
        case 'hitl_required':
            appendHitlAlert(data);
            break;
        case 'agent_update':
            loadAgents();
            break;
        case 'queue_update':
            loadQueue();
            break;
        default:
            appendMessage(JSON.stringify(data), 'system');
    }
}

function appendHitlAlert(data) {
    const history = $('#chat-history');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message hitl-alert';
    msgDiv.innerHTML = `
        <div class="avatar bg-warning"><i data-lucide="alert-triangle"></i></div>
        <div class="msg-content">
            <p><strong>Human-in-the-Loop Required:</strong> ${data.message}</p>
            <div class="msg-actions">
                <button class="btn btn-sm btn-outline hitl-review" data-id="${data.id}">Review</button>
                <button class="btn btn-sm btn-primary hitl-approve" data-id="${data.id}">Approve</button>
            </div>
        </div>
    `;
    history.appendChild(msgDiv);
    lucide.createIcons();
    history.scrollTop = history.scrollHeight;
}

// --- Helpers ---
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDateTime(date) {
    if (!date) return '--';
    return new Date(date).toLocaleString('de-DE', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', () => {
    // Initialize
    lucide.createIcons();
    connectWebSocket();
    
    // Load initial data
    loadAgents();
    loadQueue();
    loadPipeline();
    loadAnalytics();
    
    // Refresh timer
    setInterval(() => {
        loadAgents();
        loadQueue();
        loadPipeline();
    }, CONFIG.REFRESH_INTERVAL);
    
    // Update timer display
    let timeLeft = 30;
    setInterval(() => {
        timeLeft--;
        if (timeLeft <= 0) timeLeft = 30;
        const timer = $('#fleet-timer');
        if (timer) timer.textContent = `Refresh in ${timeLeft}s`;
    }, 1000);
    
    // Chat form
    $('#chat-form')?.addEventListener('submit', (e) => {
        e.preventDefault();
        const input = $('#chat-input');
        const msg = input.value.trim();
        if (!msg) return;
        input.value = '';
        sendCommand(msg);
    });
    
    // Refresh button
    $('#refresh-btn')?.addEventListener('click', () => {
        showToast('Refreshing data...', 'info');
        loadAgents();
        loadQueue();
        loadPipeline();
        loadAnalytics();
    });
    
    // Analytics period selector
    $('#analytics-period')?.addEventListener('change', (e) => {
        loadAnalytics(e.target.value);
    });
    
    // Create content button
    $('#create-content-btn')?.addEventListener('click', () => {
        showToast('Opening content creator...', 'info');
        // Could open modal or navigate
    });
});

// Expose for debugging
window.dashboardState = state;
