class ChatApp {
    constructor() {
        this.authBtn = document.getElementById('auth-btn');
        this.loginBtn = document.getElementById('login-btn');
        this.usernameInput = document.getElementById('username');
        this.passwordInput = document.getElementById('password');
        this.authContainer = document.getElementById('auth-container');
        this.userMenu = document.getElementById('user-menu');
        this.userList = document.getElementById('user-list');
        this.chatContainer = document.getElementById('chat-container');
        this.messagesDiv = document.getElementById('messages');
        this.messageForm = document.getElementById('message-form');
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('sendBtn');
        this.connectTGBtn = document.getElementById('connectTelegramBtn');
        this.backBtn = document.getElementById('backBtn');

        this.userId = null;
        this.username = null;
        this.selectedUserId = null;
        this.token = null;
        this.ws = null;

        this.bindEvents();
    }

    bindEvents() {
        this.authBtn.addEventListener('click', () => this.handleAuth('register'));
        this.loginBtn.addEventListener('click', () => this.handleAuth('login'));
        this.backBtn.addEventListener('click', () => this.goBack());
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.connectTGBtn.addEventListener('click', () => this.connectTelegram());
    }

    async handleAuth(action) {
        const usernameValue = this.usernameInput.value;
        const passwordValue = this.passwordInput.value;

        if (!usernameValue || !passwordValue) {
            alert("Please enter both username and password.");
            return;
        }

        const endpoint = action === 'register' ? '/api/users/register/' : '/api/users/login/';
        const formData = new URLSearchParams();
        formData.append('username', usernameValue);
        formData.append('password', passwordValue);

        try {
            const response = await this.postData(endpoint, formData);

            if (response.ok) {
                const data = await response.json();
                if (data.status === 'bad request') {
                    alert(action === 'register' ? 'Registration failed.' : 'Login failed.');
                } else {
                    this.handleAuthSuccess(data.data, action);
                }
            } else {
                alert(action === 'register' ? 'Registration failed.' : 'Login failed.');
            }
        } catch (error) {
            console.error('Error during authentication:', error);
            alert('Error during authentication.');
        }
    }

    async postData(url, data) {
        return await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: data,
        });
    }

    handleAuthSuccess(data, action) {
        this.userId = data.user_id;
        this.token = data.token;
        this.username = this.usernameInput.value;

        alert(action === 'register' ? 'Registration successful!' : 'Login successful!');
        this.usernameInput.value = '';
        this.passwordInput.value = '';
        this.loadUserList();
        this.authContainer.style.display = 'none';
        this.userMenu.style.display = 'flex';
        this.connectTGBtn.style.display = 'block';
    }

    async loadUserList() {
        try {
            const response = await fetch('/api/users/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });

            if (response.ok) {
                const users = await response.json();
                this.updateUserList(users);
            }
        } catch (error) {
            console.error('Error loading user list:', error);
        }
    }

    updateUserList(users) {
        this.userList.innerHTML = '';
        users.forEach(user => {
            if (user.id !== this.userId) {
                const userBtn = document.createElement('button');
                userBtn.textContent = user.username;
                userBtn.onclick = () => this.startChat(user.id);
                this.userList.appendChild(userBtn);
            }
        });
    }

    startChat(receiverId) {
        this.selectedUserId = receiverId;
        this.userMenu.style.display = 'none';
        this.chatContainer.style.display = 'flex';
        this.connectToWebSocket(this.userId, receiverId);
    }

    connectToWebSocket(senderId, receiverId) {
        if (this.ws) {
            this.ws.close();
        }
        this.ws = new WebSocket(`ws://${window.location.host}/ws/chat/ws/${senderId}/${receiverId}`);

        this.ws.onmessage = (event) => {
            const message = document.createElement('div');
            message.textContent = event.data;
            this.messagesDiv.appendChild(message);
            this.messagesDiv.scrollTop = this.messagesDiv.scrollHeight;
        };
    }

    goBack() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.messagesDiv.innerHTML = '';
        this.chatContainer.style.display = 'none';
        this.userMenu.style.display = 'block';
    }

    sendMessage() {
        const message = this.messageInput.value.trim();

        if (message && this.ws && this.ws.readyState === WebSocket.OPEN) {
            const messageElement = document.createElement('div');
            messageElement.textContent = `${this.username}: ${message}`;
            this.messagesDiv.appendChild(messageElement);

            this.ws.send(message);
            this.messageInput.value = "";
        }
    }

    async getEnvVariables() {
        try {
            const response = await fetch('/front-api/env');
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('Error fetching environment variables:', error);
            return {};
        }
    }

    async connectTelegram() {
        const env = await this.getEnvVariables();
        const botUsername = env.BOT_USERNAME;
        const telegramLink = `https://t.me/${botUsername}?start=${this.userId}`;
        window.open(telegramLink, '_blank');
    }
}

const chatApp = new ChatApp();
