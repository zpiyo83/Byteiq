// ByteIQ Web GUI JavaScript

class ByteIQApp {
    constructor() {
        this.socket = null;
        this.sessionId = null;
        this.currentTab = 'chat';
        this.config = {};
        this.todos = [];
        
        this.init();
    }
    
    init() {
        this.initSocket();
        this.loadSettings();
        this.loadTodos();
        this.bindEvents();
        this.showTab('chat');
    }
    
    initSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('session_created', (data) => {
            this.sessionId = data.session_id;
        });
        
        this.socket.on('ai_processing', (data) => {
            this.showLoading(true);
            this.addMessage('system', data.message);
        });
        
        this.socket.on('ai_response', (data) => {
            this.showLoading(false);
            this.addMessage('ai', data.response);
        });
        
        this.socket.on('ai_error', (data) => {
            this.showLoading(false);
            this.showNotification('error', data.message);
        });
    }
    
    bindEvents() {
        // 导航按钮事件
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.closest('.nav-btn').getAttribute('onclick').match(/showTab\('(.+)'\)/)[1];
                this.showTab(tab);
            });
        });
        
        // 聊天输入框回车事件
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // 模态框关闭事件
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });
    }
    
    showTab(tabName) {
        // 更新导航按钮状态
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
        
        // 显示对应标签页
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        this.currentTab = tabName;
        
        // 根据标签页加载相应数据
        if (tabName === 'todos') {
            this.loadTodos();
        } else if (tabName === 'settings') {
            this.loadSettings();
        }
    }
    
    // 聊天功能
    sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // 显示用户消息
        this.addMessage('user', message);
        input.value = '';
        
        // 发送到AI
        this.socket.emit('ai_message', {
            message: message,
            session_id: this.sessionId
        });
    }
    
    addMessage(type, content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        let icon = '';
        switch(type) {
            case 'user':
                icon = '<i class="fas fa-user"></i>';
                break;
            case 'ai':
                icon = '<i class="fas fa-robot"></i>';
                break;
            case 'system':
                icon = '<i class="fas fa-info-circle"></i>';
                break;
        }
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${icon}
                <span>${this.formatMessage(content)}</span>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    formatMessage(content) {
        // 简单的Markdown格式化
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }
    
    clearChat() {
        if (confirm('确定要清除所有对话记录吗？')) {
            document.getElementById('chatMessages').innerHTML = `
                <div class="message system-message">
                    <div class="message-content">
                        <i class="fas fa-robot"></i>
                        <span>对话已清除。我是ByteIQ AI助手，请告诉我你需要什么帮助？</span>
                    </div>
                </div>
            `;
            this.showNotification('success', '对话已清除');
        }
    }
    
    // TODO管理功能
    async loadTodos() {
        try {
            const response = await fetch('/api/todos');
            const todos = await response.json();
            
            if (Array.isArray(todos)) {
                this.todos = todos;
                this.renderTodos();
                this.renderTodoStats();
            }
        } catch (error) {
            this.showNotification('error', '加载TODO列表失败: ' + error.message);
        }
    }
    
    renderTodos() {
        const container = document.getElementById('todosList');
        
        if (this.todos.length === 0) {
            container.innerHTML = `
                <div class="info-card">
                    <h3>暂无任务</h3>
                    <p>点击"添加任务"按钮创建你的第一个任务。</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.todos.map(todo => `
            <div class="todo-item">
                <div class="todo-header">
                    <h3 class="todo-title">${this.escapeHtml(todo.title)}</h3>
                    <span class="todo-priority priority-${todo.priority}">${this.getPriorityText(todo.priority)}</span>
                </div>
                
                ${todo.description ? `<p class="todo-description">${this.escapeHtml(todo.description)}</p>` : ''}
                
                <div class="todo-status">
                    <label>状态:</label>
                    <select class="status-select" onchange="app.updateTodoStatus('${todo.id}', this.value)">
                        <option value="pending" ${todo.status === 'pending' ? 'selected' : ''}>待办</option>
                        <option value="in_progress" ${todo.status === 'in_progress' ? 'selected' : ''}>进行中</option>
                        <option value="completed" ${todo.status === 'completed' ? 'selected' : ''}>已完成</option>
                        <option value="cancelled" ${todo.status === 'cancelled' ? 'selected' : ''}>已取消</option>
                    </select>
                    <span>进度: ${todo.progress || 0}%</span>
                </div>
                
                <div class="todo-actions">
                    <button class="btn btn-danger" onclick="app.deleteTodo('${todo.id}')">
                        <i class="fas fa-trash"></i> 删除
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    renderTodoStats() {
        const stats = this.calculateTodoStats();
        const container = document.getElementById('todosStats');
        
        container.innerHTML = `
            <div class="stat-card">
                <h3>${stats.total}</h3>
                <p>总任务</p>
            </div>
            <div class="stat-card">
                <h3>${stats.pending}</h3>
                <p>待办</p>
            </div>
            <div class="stat-card">
                <h3>${stats.in_progress}</h3>
                <p>进行中</p>
            </div>
            <div class="stat-card">
                <h3>${stats.completed}</h3>
                <p>已完成</p>
            </div>
            <div class="stat-card">
                <h3>${stats.completion_rate}%</h3>
                <p>完成率</p>
            </div>
        `;
    }
    
    calculateTodoStats() {
        const stats = {
            total: this.todos.length,
            pending: 0,
            in_progress: 0,
            completed: 0,
            cancelled: 0
        };
        
        this.todos.forEach(todo => {
            stats[todo.status]++;
        });
        
        stats.completion_rate = stats.total > 0 ? 
            Math.round((stats.completed / stats.total) * 100) : 0;
        
        return stats;
    }
    
    showAddTodoModal() {
        document.getElementById('addTodoModal').style.display = 'block';
        document.getElementById('todoTitle').focus();
    }
    
    async addTodo() {
        const title = document.getElementById('todoTitle').value.trim();
        const description = document.getElementById('todoDescription').value.trim();
        const priority = document.getElementById('todoPriority').value;
        
        if (!title) {
            this.showNotification('error', '任务标题不能为空');
            return;
        }
        
        try {
            const response = await fetch('/api/todos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title, description, priority })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', result.message);
                this.closeModal('addTodoModal');
                this.clearAddTodoForm();
                this.loadTodos();
            } else {
                this.showNotification('error', result.message);
            }
        } catch (error) {
            this.showNotification('error', '添加任务失败: ' + error.message);
        }
    }
    
    async updateTodoStatus(todoId, status) {
        try {
            const response = await fetch(`/api/todos/${todoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    status, 
                    progress: status === 'completed' ? 100 : 0 
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', result.message);
                this.loadTodos();
            } else {
                this.showNotification('error', result.message);
            }
        } catch (error) {
            this.showNotification('error', '更新任务失败: ' + error.message);
        }
    }
    
    async deleteTodo(todoId) {
        if (!confirm('确定要删除这个任务吗？')) return;
        
        try {
            const response = await fetch(`/api/todos/${todoId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', result.message);
                this.loadTodos();
            } else {
                this.showNotification('error', result.message);
            }
        } catch (error) {
            this.showNotification('error', '删除任务失败: ' + error.message);
        }
    }
    
    clearAddTodoForm() {
        document.getElementById('todoTitle').value = '';
        document.getElementById('todoDescription').value = '';
        document.getElementById('todoPriority').value = 'medium';
    }
    
    // 项目分析功能
    async analyzeProject() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', result.message);
                this.displayProjectAnalysis(result.analysis);
            } else {
                this.showNotification('error', result.message);
            }
        } catch (error) {
            this.showNotification('error', '项目分析失败: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    displayProjectAnalysis(analysis) {
        const container = document.getElementById('projectInfo');
        
        container.innerHTML = `
            <div class="info-card">
                <h3>项目分析结果</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
                    <div>
                        <strong>项目类型:</strong> ${analysis.project_type}
                    </div>
                    <div>
                        <strong>技术栈:</strong> ${analysis.tech_stack.join(', ')}
                    </div>
                    <div>
                        <strong>文件总数:</strong> ${analysis.total_files}
                    </div>
                    <div>
                        <strong>项目大小:</strong> ${analysis.project_size} MB
                    </div>
                    <div>
                        <strong>编程语言:</strong> ${analysis.languages.join(', ')}
                    </div>
                    <div>
                        <strong>使用框架:</strong> ${analysis.frameworks.join(', ')}
                    </div>
                </div>
                <p style="margin-top: 1rem; color: var(--text-muted);">
                    分析完成！BYTEIQ.md 配置文件已生成，AI助手将根据此配置提供更精准的帮助。
                </p>
            </div>
        `;
    }
    
    // 设置管理
    async loadSettings() {
        try {
            const response = await fetch('/api/config');
            const config = await response.json();
            
            this.config = config;
            
            // 更新设置界面
            document.getElementById('aiModel').value = config.model || 'gpt-3.5-turbo';
            document.getElementById('language').value = config.language || 'zh-CN';
            document.getElementById('theme').value = config.theme || 'dark';
            
            // 更新状态栏
            document.getElementById('apiStatus').textContent = 
                `API: ${config.api_key_set ? '已设置' : '未设置'}`;
        } catch (error) {
            this.showNotification('error', '加载设置失败: ' + error.message);
        }
    }
    
    async saveSettings() {
        const apiKey = document.getElementById('apiKey').value.trim();
        const model = document.getElementById('aiModel').value;
        const language = document.getElementById('language').value;
        const theme = document.getElementById('theme').value;
        
        const settings = { model, language, theme };
        if (apiKey) {
            settings.api_key = apiKey;
        }
        
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', result.message);
                this.loadSettings();
                
                // 清除API密钥输入框
                document.getElementById('apiKey').value = '';
            } else {
                this.showNotification('error', result.message);
            }
        } catch (error) {
            this.showNotification('error', '保存设置失败: ' + error.message);
        }
    }
    
    // 上下文管理
    async showContextStatus() {
        try {
            const response = await fetch('/api/context');
            const stats = await response.json();
            
            const modalBody = document.getElementById('contextModalBody');
            modalBody.innerHTML = `
                <div style="display: grid; gap: 1rem;">
                    <div><strong>总Token数:</strong> ${stats.total_tokens?.toLocaleString() || 0} / ${stats.max_tokens?.toLocaleString() || 0}</div>
                    <div><strong>利用率:</strong> ${stats.utilization_percent || 0}%</div>
                    <div><strong>对话消息:</strong> ${stats.conversation_messages || 0}</div>
                    <div><strong>项目上下文:</strong> ${stats.project_contexts || 0}</div>
                    <div><strong>代码上下文:</strong> ${stats.code_contexts || 0}</div>
                    <div><strong>会话摘要:</strong> ${stats.has_summary ? '是' : '否'}</div>
                    
                    <div style="margin-top: 1rem;">
                        <div style="background: var(--bg-color); border-radius: 8px; padding: 0.5rem;">
                            <div style="background: var(--primary-color); height: 20px; border-radius: 4px; width: ${stats.utilization_percent || 0}%; transition: width 0.3s ease;"></div>
                        </div>
                        <div style="text-align: center; margin-top: 0.5rem; color: var(--text-muted);">
                            ${stats.utilization_percent || 0}% 已使用
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('contextModal').style.display = 'block';
        } catch (error) {
            this.showNotification('error', '获取上下文状态失败: ' + error.message);
        }
    }
    
    async clearContext() {
        if (!confirm('确定要清除所有上下文吗？这将删除所有对话历史和项目上下文。')) return;
        
        try {
            const response = await fetch('/api/context/clear', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('success', result.message);
                this.closeModal('contextModal');
                this.clearChat();
            } else {
                this.showNotification('error', result.message);
            }
        } catch (error) {
            this.showNotification('error', '清除上下文失败: ' + error.message);
        }
    }
    
    // 工具函数
    closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }
    
    showLoading(show) {
        document.getElementById('loadingIndicator').style.display = show ? 'block' : 'none';
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (connected) {
            statusElement.innerHTML = '<i class="fas fa-circle text-success"></i> 已连接';
        } else {
            statusElement.innerHTML = '<i class="fas fa-circle text-danger"></i> 连接断开';
        }
    }
    
    showNotification(type, message) {
        const container = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: inherit; cursor: pointer; font-size: 1.2rem;">&times;</button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // 自动移除通知
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    getPriorityText(priority) {
        const map = {
            'low': '低',
            'medium': '中',
            'high': '高',
            'urgent': '紧急'
        };
        return map[priority] || priority;
    }
}

// 全局函数（供HTML调用）
let app;

window.addEventListener('DOMContentLoaded', () => {
    app = new ByteIQApp();
});

// 全局函数
function showTab(tabName) {
    app.showTab(tabName);
}

function sendMessage() {
    app.sendMessage();
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        app.sendMessage();
    }
}

function clearChat() {
    app.clearChat();
}

function showContextStatus() {
    app.showContextStatus();
}

function showAddTodoModal() {
    app.showAddTodoModal();
}

function addTodo() {
    app.addTodo();
}

function closeModal(modalId) {
    app.closeModal(modalId);
}

function analyzeProject() {
    app.analyzeProject();
}

function saveSettings() {
    app.saveSettings();
}

function loadSettings() {
    app.loadSettings();
}

function clearContext() {
    app.clearContext();
}
