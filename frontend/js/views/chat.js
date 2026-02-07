import Api from '../api.js';
import Utils from '../utils.js';
import Auth from '../auth.js';
import Components from '../components.js';

class ChatView {
    constructor() {
        this.currentSessionId = null;
        this.sessions = [];
        this.isStreaming = false;
        this.abortController = null; // For stop streaming
        this.isLoadingSession = false;
    }

    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                <!-- Sidebar: Session List -->
                <div id="chat-sidebar" style="width: 280px; background: rgba(0,0,0,0.4); border-right: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; overflow: hidden;">
                    <!-- New Chat Button -->
                    <div style="padding: 1rem;">
                        <button id="new-chat-btn" class="btn" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                            <i class="material-symbols-outlined" style="font-size: 1.2rem;">add</i>
                            NEW CHAT
                        </button>
                    </div>
                    
                    <!-- Session List -->
                    <div id="session-list" style="flex: 1; overflow-y: auto; padding: 0 0.5rem;">
                        <div style="color: var(--text-muted); text-align: center; padding: 2rem 0.5rem; font-size: 0.8rem;">
                            Loading sessions...
                        </div>
                    </div>
                    
                    <!-- Ollama Status -->
                    <div id="ollama-status" style="padding: 0.8rem; border-top: 1px solid rgba(255,255,255,0.05); font-size: 0.7rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #666;"></span>
                        <span>Checking Ollama...</span>
                    </div>
                </div>
                
                <!-- Main Chat Area -->
                <div style="flex: 1; display: flex; flex-direction: column; overflow: hidden;">
                    <!-- Chat Header -->
                    <div id="chat-header" style="padding: 1rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <a href="#/dashboard" class="btn-outline btn-sm" style="display: flex; align-items: center; justify-content: center; padding: 0.5rem; border: none; color: var(--text-muted);" title="Go to Dashboard">
                                <i class="material-symbols-outlined" style="font-size: 1.5rem;">home</i>
                            </a>
                            <div>
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    <h2 id="chat-title" style="margin: 0; font-size: 1.1rem; color: var(--text);">AI Assistant</h2>
                                    <button id="edit-title-btn" class="btn-outline btn-sm" style="padding: 2px; border: none; color: var(--text-muted); display: none;" title="Edit Title">
                                        <i class="material-symbols-outlined" style="font-size: 1rem;">edit</i>
                                    </button>
                                </div>
                                <div id="chat-subtitle" style="font-size: 0.75rem; color: var(--text-muted);">Powered by Koffan/Cybiz</div>
                            </div>
                        </div>
                        <button id="delete-session-btn" class="btn-outline btn-sm" style="display: none;">
                            <i class="material-symbols-outlined" style="font-size: 1rem;">delete</i>
                        </button>
                    </div>

                    
                    <!-- Messages Container -->
                    <div id="messages-container" style="flex: 1; overflow-y: auto; padding: 1.5rem;">
                        <div id="messages-list" style="max-width: 800px; margin: 0 auto;">
                            <!-- Welcome message when empty -->
                            <div id="welcome-message" style="text-align: center; padding: 3rem; color: var(--text-muted);">
                                <i class="material-symbols-outlined" style="font-size: 4rem; color: var(--primary); opacity: 0.5;">smart_toy</i>
                                <h3 style="margin-top: 1rem; color: var(--text);">Welcome to Cybiz AI</h3>
                                <p style="font-size: 0.9rem;">Start a conversation or select a previous chat from the sidebar.</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Input Area -->
                    <div style="padding: 1rem 1.5rem; border-top: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
                        <form id="chat-form" style="max-width: 800px; margin: 0 auto; display: flex; gap: 0.8rem; align-items: flex-end;">
                            <textarea id="message-input" placeholder="Type your message..." style="flex: 1; background: rgba(0, 20, 10, 0.6); border: 1px solid var(--primary); border-radius: 8px; padding: 0.8rem; color: var(--primary); resize: none; font-family: 'JetBrains Mono', monospace; line-height: 1.5; min-height: 48px; max-height: 150px; caret-color: var(--primary);" rows="1"></textarea>
                            <button type="submit" id="send-btn" class="btn" style="padding: 0.8rem 1.5rem; height: 48px;">
                                <i class="material-symbols-outlined" style="font-size: 1.2rem;">send</i>
                            </button>
                            <button type="button" id="stop-btn" class="btn" style="padding: 0.8rem 1.5rem; display: none; background: #ff4757; height: 48px;">
                                <i class="material-symbols-outlined" style="font-size: 1.2rem;">stop</i>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());

        // Load sessions and check Ollama
        await this.loadSessions();
        await this.checkOllamaStatus();

        // Event Listeners
        document.getElementById('new-chat-btn').addEventListener('click', () => this.createNewChat());

        const form = document.getElementById('chat-form');
        const input = document.getElementById('message-input');

        // Handle form submit (click)
        form.addEventListener('submit', (e) => this.handleSendMessage(e));

        // Handle Enter/Shift+Enter
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                // Dispatch submit event to handle sending
                const submitEvent = new Event('submit', { cancelable: true });
                form.dispatchEvent(submitEvent);
            }
        });

        // Auto-resize textarea
        input.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            if (this.value === '') this.style.height = '48px';
        });

        document.getElementById('delete-session-btn').addEventListener('click', () => this.deleteCurrentSession());
        document.getElementById('edit-title-btn').addEventListener('click', () => this.editTitle());
        document.getElementById('stop-btn').addEventListener('click', () => this.stopStreaming());
    }

    async loadSessions() {
        try {
            const response = await Api.get('/chat/sessions');
            this.sessions = response || [];
            this.renderSessionList();
        } catch (error) {
            console.error('Failed to load sessions:', error);
            document.getElementById('session-list').innerHTML = `
                <div style="color: #ff4757; padding: 1rem; font-size: 0.8rem;">Failed to load sessions</div>
            `;
        }
    }

    renderSessionList() {
        const container = document.getElementById('session-list');

        if (this.sessions.length === 0) {
            container.innerHTML = `
                <div style="color: var(--text-muted); text-align: center; padding: 2rem 0.5rem; font-size: 0.8rem;">
                    No conversations yet.<br>Start a new chat!
                </div>
            `;
            return;
        }

        container.innerHTML = this.sessions.map(s => `
            <div class="session-item ${s.id === this.currentSessionId ? 'active' : ''}" 
                 data-session-id="${s.id}"
                 style="padding: 0.8rem; margin: 0.3rem 0; border-radius: 8px; cursor: pointer; background: ${s.id === this.currentSessionId ? 'rgba(0, 255, 157, 0.1)' : 'rgba(255,255,255,0.02)'}; border-left: 3px solid ${s.id === this.currentSessionId ? 'var(--primary)' : 'transparent'}; transition: all 0.2s; display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1; overflow: hidden;">
                    <div style="font-size: 0.85rem; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${Utils.escapeHtml(s.title)}</div>
                    <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.2rem;">${s.message_count} messages</div>
                </div>
                <button class="delete-session-item" data-session-id="${s.id}" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 0.25rem; opacity: 0.5;" title="Delete">
                    <i class="material-symbols-outlined" style="font-size: 1rem;">close</i>
                </button>
            </div>
        `).join('');

        // Add click listeners for session selection
        container.querySelectorAll('.session-item').forEach(item => {
            item.addEventListener('click', (e) => {
                // Don't select if clicking delete button
                if (e.target.closest('.delete-session-item')) return;
                const sessionId = item.dataset.sessionId;
                this.loadSession(sessionId);
            });
        });

        // Add click listeners for delete buttons
        container.querySelectorAll('.delete-session-item').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const sessionId = btn.dataset.sessionId;
                this.showDeleteModal(sessionId);
            });
        });
    }

    async loadSession(sessionId) {
        // Prevent duplicate loading
        if (this.isLoadingSession) return;
        this.isLoadingSession = true;

        try {
            const session = await Api.get(`/chat/sessions/${sessionId}`);
            if (!session || !session.messages) {
                throw new Error('Invalid session data');
            }

            this.currentSessionId = sessionId;
            this.renderSessionList();
            this.renderMessages(session.messages);

            document.getElementById('chat-title').textContent = session.title;
            document.getElementById('delete-session-btn').style.display = 'block';
            document.getElementById('edit-title-btn').style.display = 'block';
            const welcome = document.getElementById('welcome-message');
            if (welcome) welcome.style.display = 'none';
        } catch (error) {
            console.error('Session load error:', error);
            Utils.showToast('Failed to load session', 'error');
        } finally {
            this.isLoadingSession = false;
        }
    }

    renderMessages(messages) {
        const container = document.getElementById('messages-list');

        if (messages.length === 0) {
            container.innerHTML = `<div id="welcome-message" style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <i class="material-symbols-outlined" style="font-size: 4rem; color: var(--primary); opacity: 0.5;">chat</i>
                <p style="margin-top: 1rem;">This conversation is empty. Send a message to begin.</p>
            </div>`;
            return;
        }

        container.innerHTML = messages.map((m, i) => this.renderSingleMessage(m, i, i === messages.length - 1)).join('');
        this.scrollToBottom();

        // Attach event listeners for edit/retry buttons dynamically
        this.attachMessageEventListeners();
    }

    attachMessageEventListeners() {
        document.querySelectorAll('.edit-msg-btn').forEach(btn => {
            btn.onclick = (e) => {
                const msgId = btn.dataset.messageId;
                const content = btn.dataset.content;
                this.enableEditMode(msgId, content, btn.closest('.message-bubble'));
            };
        });

        document.querySelectorAll('.retry-msg-btn').forEach(btn => {
            btn.onclick = (e) => {
                const msgId = btn.dataset.messageId;
                const content = btn.dataset.content;
                this.handleRetry(msgId, content);
            };
        });
    }

    renderSingleMessage(message, index, isLast) {
        const isUser = message.role === 'user';
        const formattedContent = this.formatMessageContent(message.content);
        const messageId = message.id || `temp-${index}`;

        return `
            <div id="msg-${messageId}" class="chat-message ${isUser ? 'user' : 'assistant'}" style="margin-bottom: 1.5rem; display: flex; gap: 1rem; flex-direction: ${isUser ? 'row-reverse' : 'row'}; group">
                <div class="avatar" style="width: 36px; height: 36px; border-radius: 50%; background: ${isUser ? 'var(--primary)' : 'var(--secondary)'}; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <i class="material-symbols-outlined" style="font-size: 1.2rem; color: #000;">${isUser ? 'person' : 'smart_toy'}</i>
                </div>
                <div class="message-content" style="flex: 1; max-width: 85%;">
                    <div class="message-bubble" style="background: ${isUser ? 'rgba(0, 255, 157, 0.1)' : 'rgba(255,255,255,0.03)'}; padding: 1rem; border-radius: 12px; border-top-${isUser ? 'right' : 'left'}-radius: 4px; position: relative;">
                        <div class="message-text" style="line-height: 1.6; font-size: 0.9rem;">${formattedContent}</div>
                        <div class="message-actions" style="position: absolute; top: 0.5rem; right: 0.5rem; display: flex; gap: 0.5rem; opacity: 0; transition: opacity 0.2s;">
                            ${isUser ? `
                            <button class="edit-msg-btn" data-message-id="${messageId}" data-content="${Utils.escapeHtml(message.content)}" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 2px;" title="Edit">
                                <i class="material-symbols-outlined" style="font-size: 1rem;">edit</i>
                            </button>
                            ${isLast ? `
                            <button class="retry-msg-btn" data-message-id="${messageId}" data-content="${Utils.escapeHtml(message.content)}" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 2px;" title="Retry">
                                <i class="material-symbols-outlined" style="font-size: 1rem;">refresh</i>
                            </button>` : ''}
                            ` : ''}
                            <button class="copy-btn" onclick="copyMessage(this)" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer;" title="Copy">
                                <i class="material-symbols-outlined" style="font-size: 1rem;">content_copy</i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <style>
                .chat-message:hover .message-actions { opacity: 1 !important; }
            </style>
        `;
    }

    enableEditMode(messageId, currentContent, bubbleEl) {
        if (this.isStreaming) return;

        // Decode HTML entities if any
        const decodedContent = new DOMParser().parseFromString(currentContent, 'text/html').documentElement.textContent;

        bubbleEl.innerHTML = `
            <div class="edit-mode" style="width: 100%;">
                <textarea id="edit-input-${messageId}" style="width: 100%; background: rgba(0,0,0,0.3); border: 1px solid var(--primary); border-radius: 6px; padding: 0.5rem; color: var(--text-main); font-family: inherit; font-size: 0.9rem; resize: vertical; min-height: 60px;">${decodedContent}</textarea>
                <div style="display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: 0.5rem;">
                    <button class="btn-cancel-edit" style="background: transparent; border: 1px solid rgba(255,255,255,0.2); color: var(--text-muted); padding: 0.3rem 0.8rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">Cancel</button>
                    <button class="btn-save-edit" style="background: var(--primary); border: none; color: #000; padding: 0.3rem 0.8rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">Save & Submit</button>
                </div>
            </div>
        `;

        const textarea = bubbleEl.querySelector('textarea');
        textarea.focus();

        // Event handlers
        bubbleEl.querySelector('.btn-cancel-edit').onclick = () => {
            // Reload to restore original UI
            this.loadSession(this.currentSessionId);
        };

        bubbleEl.querySelector('.btn-save-edit').onclick = () => {
            const newContent = textarea.value.trim();
            if (newContent && newContent !== decodedContent) {
                this.handleEditSubmit(messageId, newContent);
            } else {
                this.loadSession(this.currentSessionId);
            }
        };
    }

    async handleEditSubmit(messageId, newContent) {
        try {
            this.isStreaming = true;
            document.getElementById('send-btn').disabled = true;

            // Clear all messages after the edited one visually
            const allMessages = Array.from(document.querySelectorAll('.chat-message'));
            const editedMsgEl = document.getElementById(`msg-${messageId}`);

            if (!editedMsgEl) {
                throw new Error("Message element not found. Please refresh.");
            }

            const index = allMessages.indexOf(editedMsgEl);

            // Update the edited message UI
            // Restore message UI structure
            const bubbleEl = editedMsgEl.querySelector('.message-bubble');
            const isUser = true; // We only edit user messages
            const isLast = index === allMessages.length - 1; // Check if it was the last message (though we are about to delete subsequent ones anyway)
            // Actually, since we delete subsequent messages, this edited message becomes the last user message potentially?
            // But wait, we delete subsequent messages *after* this block. 
            // In the final state, this will be the last user message before the new AI response.
            // So we can just render the standard inner structure.

            bubbleEl.innerHTML = `
                <div class="message-text" style="line-height: 1.6; font-size: 0.9rem;">${this.formatMessageContent(newContent)}</div>
                <div class="message-actions" style="position: absolute; top: 0.5rem; right: 0.5rem; display: flex; gap: 0.5rem; opacity: 0; transition: opacity 0.2s;">
                    <button class="edit-msg-btn" data-message-id="${messageId}" data-content="${Utils.escapeHtml(newContent)}" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 2px;" title="Edit">
                        <i class="material-symbols-outlined" style="font-size: 1rem;">edit</i>
                    </button>
                    <button class="retry-msg-btn" data-message-id="${messageId}" data-content="${Utils.escapeHtml(newContent)}" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 2px;" title="Retry">
                        <i class="material-symbols-outlined" style="font-size: 1rem;">refresh</i>
                    </button>
                    <button class="copy-btn" onclick="copyMessage(this)" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer;" title="Copy">
                        <i class="material-symbols-outlined" style="font-size: 1rem;">content_copy</i>
                    </button>
                </div>
            `;

            // Remove subsequent messages from DOM
            if (index !== -1) {
                for (let i = index + 1; i < allMessages.length; i++) {
                    allMessages[i].remove();
                }
            } else {
                // Should not happen check above
                return;
            }

            this.abortController = new AbortController();
            document.getElementById('send-btn').style.display = 'none';
            document.getElementById('stop-btn').style.display = 'block';

            // Add assistant placeholder
            const assistantId = 'assistant-' + Date.now();
            document.getElementById('messages-list').insertAdjacentHTML('beforeend', `
                <div id="${assistantId}" class="chat-message assistant" style="margin-bottom: 1.5rem; display: flex; gap: 1rem;">
                    <div class="avatar" style="width: 36px; height: 36px; border-radius: 50%; background: var(--secondary); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                        <i class="material-symbols-outlined" style="font-size: 1.2rem; color: #000;">smart_toy</i>
                    </div>
                    <div class="message-content" style="flex: 1; max-width: 85%;">
                        <div class="message-bubble" style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 12px; border-top-left-radius: 4px;">
                            <div class="message-text streaming" style="line-height: 1.6; font-size: 0.9rem;">
                                <span class="typing-indicator">●●●</span>
                            </div>
                        </div>
                    </div>
                </div>
            `);

            const token = localStorage.getItem('access_token');
            const response = await fetch(`${Api.baseUrl}/chat/sessions/${this.currentSessionId}/messages/${messageId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    new_content: newContent
                }),
                signal: this.abortController.signal
            });

            await this.processStreamResponse(response, assistantId);

        } catch (error) {
            if (error.name !== 'AbortError') {
                Utils.showToast('Failed to edit message: ' + error.message, 'error');
                await this.loadSession(this.currentSessionId); // Reload on error to restore state
            }
        } finally {
            this.cleanupStreamingState();
        }
    }

    async handleRetry(messageId, content) {
        this.handleEditSubmit(messageId, content);
    }

    // Extracted streaming logic to reuse for Send and Edit
    async processStreamResponse(response, assistantId) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const messageTextEl = document.querySelector(`#${assistantId} .message-text`);
        let fullContent = '';

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const text = decoder.decode(value);
                const lines = text.split('\n').filter(line => line.startsWith('data: '));

                for (const line of lines) {
                    try {
                        const data = JSON.parse(line.slice(6));

                        if (data.session_id && data.type === 'session_created') {
                            this.currentSessionId = data.session_id;
                            document.getElementById('delete-session-btn').style.display = 'block';
                            document.getElementById('edit-title-btn').style.display = 'block';
                            await this.loadSessions();
                        }

                        if (data.content) {
                            fullContent += data.content;
                            messageTextEl.innerHTML = this.formatMessageContent(fullContent);
                            this.scrollToBottom();
                        }

                        if (data.error) {
                            messageTextEl.innerHTML = `<span style="color: #ff4757;"><i class="material-symbols-outlined" style="vertical-align: middle;">error</i> ${data.error}</span>`;
                        }

                        if (data.type === 'done') {
                            // Add copy button implementation if needed
                            const bubble = messageTextEl.parentElement;
                            // Remove existing copy btn if any
                            const existingBtn = bubble.querySelector('.copy-btn');
                            if (existingBtn) existingBtn.remove();

                            const copyBtn = document.createElement('button');
                            copyBtn.className = 'copy-btn';
                            copyBtn.innerHTML = '<i class="material-symbols-outlined" style="font-size: 1rem;">content_copy</i>';
                            copyBtn.onclick = () => window.copyMessage(copyBtn);
                            copyBtn.style.cssText = 'position: absolute; top: 0.5rem; right: 0.5rem; background: transparent; border: none; color: var(--text-muted); cursor: pointer; opacity: 0.5;';
                            bubble.appendChild(copyBtn);
                        }
                    } catch (err) {
                        console.error('Parse error:', err);
                    }
                }
            }
        } catch (err) {
            throw err;
        } finally {
            // CRITICAL: Reload session to sync message IDs (temp ID -> real ID)
            await this.loadSessions(); // Updates sidebar
            if (this.currentSessionId) {
                await this.loadSession(this.currentSessionId); // Updates messages with real IDs
            }
        }
    }

    cleanupStreamingState() {
        this.isStreaming = false;
        this.abortController = null;
        const sendBtn = document.getElementById('send-btn');
        if (sendBtn) {
            sendBtn.style.display = 'block';
            sendBtn.disabled = false;
        }
        const stopBtn = document.getElementById('stop-btn');
        if (stopBtn) {
            stopBtn.style.display = 'none';
        }

        // Re-attach listeners to new elements
        this.attachMessageEventListeners();
    }

    formatMessageContent(content) {
        // Escape HTML first
        let formatted = Utils.escapeHtml(content);

        // Code blocks (```language...```)
        formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
            return `<pre class="code-block" style="background: rgba(0,0,0,0.4); padding: 1rem; border-radius: 8px; overflow-x: auto; margin: 0.5rem 0; position: relative;"><code class="language-${lang || 'plaintext'}">${code.trim()}</code><button onclick="copyCode(this)" style="position: absolute; top: 0.5rem; right: 0.5rem; background: rgba(255,255,255,0.1); border: none; color: var(--text-muted); padding: 0.3rem 0.5rem; border-radius: 4px; cursor: pointer; font-size: 0.7rem;">COPY</button></pre>`;
        });

        // Inline code (before other formatting to preserve backticks)
        formatted = formatted.replace(/`([^`]+)`/g, '<code style="background: rgba(255,255,255,0.1); padding: 0.2rem 0.4rem; border-radius: 4px; font-family: JetBrains Mono, monospace;">$1</code>');

        // Headings (must process before line breaks)
        formatted = formatted.replace(/^#### (.+)$/gm, '<h4 class="markdown-content" style="font-size: 1.1rem; font-weight: 600; margin: 1rem 0 0.5rem 0; color: var(--text-main);">$1</h4>');
        formatted = formatted.replace(/^### (.+)$/gm, '<h3 class="markdown-content" style="font-size: 1.25rem; font-weight: 600; margin: 1.25rem 0 0.75rem 0; color: var(--text-main);">$1</h3>');
        formatted = formatted.replace(/^## (.+)$/gm, '<h2 class="markdown-content" style="font-size: 1.5rem; font-weight: 600; margin: 1.5rem 0 0.75rem 0; color: var(--text-main);">$1</h2>');
        formatted = formatted.replace(/^# (.+)$/gm, '<h1 class="markdown-content" style="font-size: 1.75rem; font-weight: 700; margin: 1.5rem 0 0.75rem 0; color: var(--primary); border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem;">$1</h1>');

        // Bold & Italic
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // Lists
        formatted = formatted.replace(/^- (.+)$/gm, '<li style="margin-left: 1rem; list-style-type: disc;">$1</li>');
        formatted = formatted.replace(/^\* (.+)$/gm, '<li style="margin-left: 1rem; list-style-type: disc;">$1</li>');
        formatted = formatted.replace(/^(\d+)\. (.+)$/gm, '<li style="margin-left: 1rem; list-style-type: decimal;">$2</li>');

        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');

        return formatted;
    }

    async handleSendMessage(e) {
        e.preventDefault();

        const input = document.getElementById('message-input');
        const message = input.value.trim();

        if (!message || this.isStreaming) return;

        input.value = '';
        input.style.height = '48px'; // Reset height
        this.isStreaming = true;
        document.getElementById('send-btn').disabled = true;

        // Hide welcome message
        const welcome = document.getElementById('welcome-message');
        if (welcome) welcome.style.display = 'none';

        // Add user message to UI
        const messagesContainer = document.getElementById('messages-list');
        // Temp ID for immediate display
        const tempId = 'temp-' + Date.now();

        messagesContainer.insertAdjacentHTML('beforeend', this.renderSingleMessage({
            role: 'user',
            content: message,
            id: tempId
        }, 0, true)); // true = isLast

        // Add assistant placeholder
        const assistantId = 'assistant-' + Date.now();
        messagesContainer.insertAdjacentHTML('beforeend', `
            <div id="${assistantId}" class="chat-message assistant" style="margin-bottom: 1.5rem; display: flex; gap: 1rem;">
                <div class="avatar" style="width: 36px; height: 36px; border-radius: 50%; background: var(--secondary); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <i class="material-symbols-outlined" style="font-size: 1.2rem; color: #000;">smart_toy</i>
                </div>
                <div class="message-content" style="flex: 1; max-width: 85%;">
                    <div class="message-bubble" style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 12px; border-top-left-radius: 4px;">
                        <div class="message-text streaming" style="line-height: 1.6; font-size: 0.9rem;">
                            <span class="typing-indicator">●●●</span>
                        </div>
                    </div>
                </div>
            </div>
        `);
        this.scrollToBottom();

        // Send to API with SSE
        this.abortController = new AbortController();
        document.getElementById('send-btn').style.display = 'none';
        document.getElementById('stop-btn').style.display = 'block';

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${Api.baseUrl}/chat/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    session_id: this.currentSessionId,
                    message: message
                }),
                signal: this.abortController.signal
            });

            await this.processStreamResponse(response, assistantId);

        } catch (error) {
            if (error.name !== 'AbortError') {
                Utils.showToast('Failed to send message: ' + error.message, 'error');
            }
        } finally {
            this.cleanupStreamingState();
        }
    }

    stopStreaming() {
        if (this.abortController) {
            this.abortController.abort();
        }
    }

    async createNewChat() {
        this.currentSessionId = null;
        this.renderSessionList();

        document.getElementById('chat-title').textContent = 'New Conversation';
        document.getElementById('delete-session-btn').style.display = 'none';
        document.getElementById('edit-title-btn').style.display = 'none';
        document.getElementById('messages-list').innerHTML = `
            <div id="welcome-message" style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <i class="material-symbols-outlined" style="font-size: 4rem; color: var(--primary); opacity: 0.5;">smart_toy</i>
                <h3 style="margin-top: 1rem; color: var(--text);">Start a New Conversation</h3>
                <p style="font-size: 0.9rem;">Type your message below to begin chatting with Cybiz AI.</p>
            </div>
        `;
    }

    async editTitle() {
        if (!this.currentSessionId) return;

        const titleEl = document.getElementById('chat-title');
        const currentTitle = titleEl.textContent;
        const editBtn = document.getElementById('edit-title-btn');

        // Already editing
        if (titleEl.querySelector('input')) return;

        // Create inline input
        const input = document.createElement('input');
        input.type = 'text';
        input.value = currentTitle;
        input.className = 'inline-edit-input';
        input.style.cssText = 'background: rgba(0,0,0,0.4); border: 1px solid var(--primary); border-radius: 4px; color: var(--text-main); padding: 0.25rem 0.5rem; font-family: inherit; font-size: inherit; width: 200px; outline: none;';

        // Replace title with input
        titleEl.textContent = '';
        titleEl.appendChild(input);
        input.focus();
        input.select();

        // Hide edit button during editing
        editBtn.style.display = 'none';

        const saveTitle = async () => {
            const newTitle = input.value.trim();
            if (newTitle && newTitle !== currentTitle) {
                try {
                    await Api.put(`/chat/sessions/${this.currentSessionId}/title`, { title: newTitle });
                    titleEl.textContent = newTitle;
                    await this.loadSessions();
                    Utils.showToast('Title updated', 'success');
                } catch (error) {
                    titleEl.textContent = currentTitle;
                    Utils.showToast('Failed to update title', 'error');
                }
            } else {
                titleEl.textContent = currentTitle;
            }
            editBtn.style.display = 'block';
        };

        // Save on Enter, cancel on Escape
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveTitle();
            } else if (e.key === 'Escape') {
                titleEl.textContent = currentTitle;
                editBtn.style.display = 'block';
            }
        });

        // Save on blur
        input.addEventListener('blur', saveTitle);
    }

    showDeleteModal(sessionId) {
        // Create modal container
        const modal = document.createElement('div');
        modal.id = 'delete-modal';
        modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); z-index: 2000; display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.3s;';

        modal.innerHTML = `
            <div class="glass" style="width: 100%; max-width: 400px; padding: 2rem; border-radius: 12px; border: 1px solid var(--danger); transform: scale(0.9); transition: transform 0.3s; box-shadow: 0 10px 40px rgba(0,0,0,0.5);">
                <div style="display: flex; flex-direction: column; align-items: center; text-align: center; gap: 1rem;">
                    <div style="width: 60px; height: 60px; border-radius: 50%; background: rgba(255, 71, 87, 0.1); display: flex; align-items: center; justify-content: center; color: var(--danger);">
                        <i class="material-symbols-outlined" style="font-size: 2rem;">delete_forever</i>
                    </div>
                    
                    <h3 style="font-size: 1.5rem; color: var(--text-main);">Delete Chat?</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem; line-height: 1.5;">Are you sure you want to delete this conversation? This action cannot be undone.</p>
                    
                    <div style="display: flex; gap: 1rem; width: 100%; margin-top: 1rem;">
                        <button id="cancel-delete-btn" class="btn" style="flex: 1; background: transparent; border: 1px solid rgba(255,255,255,0.2); color: var(--text-main);">Cancel</button>
                        <button id="confirm-delete-btn" class="btn" style="flex: 1; background: var(--danger); color: white; border: none;">Delete</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Animate in
        requestAnimationFrame(() => {
            modal.style.opacity = '1';
            modal.querySelector('.glass').style.transform = 'scale(1)';
        });

        // Handlers
        const closeModal = () => {
            modal.style.opacity = '0';
            modal.querySelector('.glass').style.transform = 'scale(0.9)';
            setTimeout(() => modal.remove(), 300);
        };

        modal.querySelector('#cancel-delete-btn').onclick = closeModal;
        modal.onclick = (e) => {
            if (e.target === modal) closeModal();
        };

        modal.querySelector('#confirm-delete-btn').onclick = async () => {
            try {
                const btn = document.getElementById('confirm-delete-btn');
                btn.innerHTML = '<span class="material-symbols-outlined" style="animation: spin 1s linear infinite; font-size: 1.2rem;">sync</span>';

                await Api.delete(`/chat/sessions/${sessionId}`);

                if (this.currentSessionId === sessionId) {
                    this.currentSessionId = null;
                    this.createNewChat();
                }

                await this.loadSessions();
                Utils.showToast('Conversation deleted', 'success');
                closeModal();
            } catch (err) {
                console.error(err);
                Utils.showToast('Failed to delete conversation', 'error');
                closeModal();
            }
        };
    }

    async deleteCurrentSession() {
        if (!this.currentSessionId) return;
        this.showDeleteModal(this.currentSessionId);
    }

    async checkOllamaStatus() {
        const statusEl = document.getElementById('ollama-status');
        try {
            const data = await Api.get('/chat/health');
            if (data.ollama_connected && data.model_available) {
                statusEl.innerHTML = `
                    <span class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: var(--primary);"></span>
                    <span style="color: var(--primary);">AI: Ready</span>
                `;
            } else if (data.ollama_connected && !data.model_available) {
                statusEl.innerHTML = `
                    <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #ffa502;"></span>
                            <span style="color: #ffa502;">Model Missing</span>
                        </div>
                        <div style="font-size: 0.6rem; color: var(--text-muted); opacity: 0.8;">Check Ollama models</div>
                    </div>
                `;
            } else {
                statusEl.innerHTML = `
                    <span class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #ff4757;"></span>
                    <span style="color: #ff4757;">Ollama Offline</span>
                `;
            }
        } catch {
            statusEl.innerHTML = `
                <span class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #666;"></span>
                <span style="color: #666;">Status Unknown</span>
            `;
        }
    }

    scrollToBottom() {
        const container = document.getElementById('messages-container');
        container.scrollTop = container.scrollHeight;
    }
}

// Global functions for copy buttons
window.copyMessage = function (btn) {
    const text = btn.parentElement.parentElement.querySelector('.message-text').innerText;
    navigator.clipboard.writeText(text).then(() => {
        btn.innerHTML = '<i class="material-symbols-outlined" style="font-size: 1rem;">check</i>';
        setTimeout(() => {
            btn.innerHTML = '<i class="material-symbols-outlined" style="font-size: 1rem;">content_copy</i>';
        }, 2000);
    });
};

window.copyCode = function (btn) {
    const code = btn.parentElement.querySelector('code').innerText;
    navigator.clipboard.writeText(code).then(() => {
        btn.textContent = 'COPIED!';
        setTimeout(() => { btn.textContent = 'COPY'; }, 2000);
    });
};

export default new ChatView();
