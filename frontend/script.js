// Configuration
const API_URL = 'http://localhost:8000';
let conversationHistory = [];
let escalationTriggered = false;

// DOM Elements
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const messagesContainer = document.getElementById('messagesContainer');
const loadingIndicator = document.getElementById('loadingIndicator');
const toast = document.getElementById('toast');
const clearChatBtn = document.getElementById('clearChat');

// Handoff elements
const escalationBanner  = document.getElementById('escalationBanner');
const escalationBannerText = document.getElementById('escalationBannerText');
const btnTransfer       = document.getElementById('btnTransfer');
const handoffOverlay    = document.getElementById('handoffOverlay');
const handoffReason     = document.getElementById('handoffReason');
const handoffNote       = document.getElementById('handoffNote');
const handoffActions    = document.getElementById('handoffActions');
const handoffAgentCard  = document.getElementById('handoffAgentCard');
const handoffConfirm    = document.getElementById('handoffConfirm');
const handoffCancel     = document.getElementById('handoffCancel');
const chatInputArea     = document.querySelector('.chat-input-area');

// Navigation
const navItems = document.querySelectorAll('.nav-item');
const views = document.querySelectorAll('.view');

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

clearChatBtn.addEventListener('click', clearChat);

// Navigation handler
navItems.forEach(item => {
    item.addEventListener('click', () => {
        const viewId = item.getAttribute('data-view') + '-view';
        switchView(viewId);
    });
});

// Quick action buttons
document.querySelectorAll('.quick-action').forEach(btn => {
    btn.addEventListener('click', () => {
        const prompt = btn.getAttribute('data-prompt');
        userInput.value = prompt;
        userInput.focus();
    });
});

// Scenario buttons — auto send
document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const prompt = btn.getAttribute('data-prompt');
        userInput.value = prompt;
        sendMessage();
    });
});

// Functions
function switchView(viewId) {
    // Update nav items
    navItems.forEach(item => {
        const view = item.getAttribute('data-view') + '-view';
        item.classList.toggle('active', view === viewId);
    });

    // Update views
    views.forEach(view => {
        view.classList.remove('active');
    });
    document.getElementById(viewId).classList.add('active');
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to UI
    addMessageToUI('user', message);
    userInput.value = '';
    conversationHistory.push({ role: 'user', content: message });

    // Show loading
    showLoading(true);

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_history: conversationHistory
            })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        
        // Add agent response to UI
        addMessageToUI('agent', data.response);
        conversationHistory.push({ role: 'agent', content: data.response });

        // Show action summary if available
        if (data.action_summary) {
            showToast(data.action_summary, 'success');
        }

        // Check if escalation needed
        if (data.escalation_required && !escalationTriggered) {
            escalationTriggered = true;
            const reason = data.escalation_reason || 'This request requires specialist review.';
            triggerEscalationBanner(reason);
        }

    } catch (error) {
        console.error('Error:', error);
        addMessageToUI('agent', 
            '❌ Sorry, I encountered an error. Please try again or contact our support team.');
        showToast('Connection error. Please check your internet and try again.', 'error');
    } finally {
        showLoading(false);
        userInput.focus();
    }
}

function addMessageToUI(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = `avatar ${sender}-avatar`;
    avatar.textContent = sender === 'user' ? '👤' : '🤖';

    const content = document.createElement('div');
    content.className = 'message-content';

    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    
    // Parse message as HTML if it contains formatting (lists, bold, etc.)
    if (text.includes('\n') || text.includes('**') || text.includes('•')) {
        messageText.innerHTML = parseMarkdown(text);
    } else {
        messageText.textContent = text;
    }

    const time = document.createElement('span');
    time.className = 'message-time';
    time.textContent = getTimeString();

    content.appendChild(messageText);
    content.appendChild(time);

    if (sender === 'user') {
        messageDiv.appendChild(content);
        messageDiv.appendChild(avatar);
    } else {
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
    }

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function parseMarkdown(text) {
    // Simple markdown parser for our needs
    text = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/__(.*?)__/g, '<strong>$1</strong>')
        .replace(/•\s/g, '• ')
        .replace(/\n/g, '<br>');
    
    return text;
}

function getTimeString() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 0);
}

function showLoading(show) {
    if (show) {
        loadingIndicator.classList.add('active');
    } else {
        loadingIndicator.classList.remove('active');
    }
}

function showToast(message, type = 'info') {
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

function triggerEscalationBanner(reason) {
    escalationBannerText.textContent = reason;
    escalationBanner.style.display = 'flex';
    chatInputArea.classList.add('has-banner');

    // Add in-chat escalation message
    setTimeout(() => {
        addMessageToUI('agent',
            '⚠️ **Heads up** — this conversation has reached a point that needs human attention. ' +
            'You can continue chatting with me, or click **"Transfer to Human"** below to connect with a specialist right now.');
    }, 600);
}

function startHandoff(reason) {
    handoffReason.textContent = reason || 'This conversation requires specialist attention.';
    handoffNote.textContent = 'Transferring conversation history...';
    handoffActions.style.display = 'none';
    handoffAgentCard.classList.remove('show');
    handoffOverlay.classList.add('active');

    // Animate progress bar
    setTimeout(() => {
        document.querySelector('.handoff-bar').classList.add('go');
    }, 100);

    // Show agent card
    setTimeout(() => {
        handoffAgentCard.classList.add('show');
        handoffNote.textContent = 'Specialist found and ready to take over.';
    }, 1800);

    // Show action buttons
    setTimeout(() => {
        handoffActions.style.display = 'flex';
    }, 2200);
}

function completeHandoff() {
    handoffOverlay.classList.remove('active');
    escalationBanner.style.display = 'none';
    chatInputArea.classList.remove('has-banner');

    // Disable input
    userInput.disabled = true;
    sendBtn.disabled = true;
    userInput.placeholder = 'Chat transferred to human agent...';

    // Add final message
    addMessageToUI('agent',
        '✅ **You\'ve been connected to Rahul Sharma**, Senior Support Specialist.\n\n' +
        'He has your full conversation history and will reach out to you at your registered contact within **5 minutes**.\n\n' +
        '📧 priya.nair@example.com\n📞 +91-98xxxxxxx\n\n' +
        'Thank you for your patience.');

    showToast('Connected to human agent successfully', 'success');
}

// Handoff button listeners
btnTransfer.addEventListener('click', () => {
    startHandoff(escalationBannerText.textContent);
});

handoffConfirm.addEventListener('click', () => {
    completeHandoff();
});

handoffCancel.addEventListener('click', () => {
    handoffOverlay.classList.remove('active');
    showToast('Continuing with AI agent', 'info');
});

function clearChat() {
    const confirmed = confirm('Clear all messages? This cannot be undone.');
    if (confirmed) {
        messagesContainer.innerHTML = `
            <div class="message agent welcome-message">
                <div class="avatar agent-avatar">🤖</div>
                <div class="message-content">
                    <div class="message-text">
                        <h3>Welcome back! 👋</h3>
                        <p>Chat cleared. How can I help you today?</p>
                    </div>
                    <span class="message-time">just now</span>
                </div>
            </div>
        `;
        conversationHistory = [];
        escalationTriggered = false;
        escalationBanner.style.display = 'none';
        chatInputArea.classList.remove('has-banner');
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.placeholder = 'Type your booking ref or issue here...';
        showToast('Chat cleared successfully', 'success');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    userInput.focus();
    console.log('SkyAssist loaded and ready! 🚀');
});
