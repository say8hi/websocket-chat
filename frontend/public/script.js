const authBtn = document.getElementById('auth-btn');
const loginBtn = document.getElementById('login-btn');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const authContainer = document.getElementById('auth-container');
const userMenu = document.getElementById('user-menu');
const userList = document.getElementById('user-list');
const chatContainer = document.getElementById('chat-container');
const messagesDiv = document.getElementById('messages');
const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('sendBtn');
const connectTGBtn = document.getElementById('connectTelegramBtn');

const backBtn = document.getElementById('backBtn');

let userId = null;
let username = null;
let selectedUserId = null;

async function handleAuth(action) {
    const usernameValue = usernameInput.value;
    const passwordValue = passwordInput.value;

    if (!usernameValue || !passwordValue) {
        alert("Please enter both username and password.");
        return;
    }

    try {
        const endpoint = action === 'register' ? '/api/users/register/' : '/api/users/login/';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: usernameValue,
                password: passwordValue
            }),
        });

        if (response.ok) {
            const data = await response.json();
            userId = data.id;
            username = usernameInput.value;

            if (action === 'register') {
                alert('Registration successful! Please login.');
            } else {
                alert('Login successful!');
            }

            usernameInput.value = '';
            passwordInput.value = '';
            loadUserList();
            authContainer.style.display = 'none';
            userMenu.style.display = 'flex';
            connectTGBtn.style.display = 'block';
        } else {
            alert(action === 'register' ? 'Registration failed.' : 'Login failed.');
        }
    } catch (error) {
        console.error('Error during authentication:', error);
        alert('Error during authentication.');
    }
}

authBtn.addEventListener('click', () => handleAuth('register'));

loginBtn.addEventListener('click', () => handleAuth('login'))

async function loadUserList() {
    try {
        const response = await fetch('/api/users/');
        if (response.ok) {
            const users = await response.json();
            userList.innerHTML = '';
            users.forEach(user => {
                if (user.id !== userId) {
                    const userBtn = document.createElement('button');
                    userBtn.textContent = user.username;
                    userBtn.onclick = () => startChat(user.id);
                    userList.appendChild(userBtn);
                }
            });
        }
    } catch (error) {
        console.error('Error loading user list:', error);
    }
}


async function loadChatHistory(senderId, receiverId) {
    try {
        const response = await fetch(`/api/chat/history/${senderId}/${receiverId}`);
        if (response.ok) {
            const messages = await response.json();
            messagesDiv.innerHTML = '';
            messages.forEach(message => {
                const messageElement = document.createElement('div');
                messageElement.textContent = `${message.sender.username}: ${message.message}`;
                messagesDiv.appendChild(messageElement);
            });
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        } else {
            console.error('Error loading chat history.');
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

function startChat(receiverId) {
    selectedUserId = receiverId;
    userMenu.style.display = 'none';
    chatContainer.style.display = 'flex';
    connectToWebSocket(userId, receiverId);
}

let ws = null;

function connectToWebSocket(senderId, receiverId) {
    if (ws !== null) {
        ws.close();
    }
    ws = new WebSocket(`ws://${window.location.host}/ws/chat/ws/${userId}/${receiverId}`);

    ws.onmessage = function(event) {
        const message = document.createElement('div');
        message.textContent = event.data;
        messagesDiv.appendChild(message);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    };
}

function goBack() {
    if (ws) {
        ws.close();
        ws = null;
    }
    messagesDiv.innerHTML = '';
    chatContainer.style.display = 'none';
    userMenu.style.display = 'block';
}

function sendMessage() {
    const message = messageInput.value.trim();

    if (message && ws && ws.readyState === WebSocket.OPEN) {
        const messageElement = document.createElement('div');
        messageElement.textContent = `${username}: ${message}`;
        messagesDiv.appendChild(messageElement);

        ws.send(message);
        messageInput.value = "";
    }
}

async function getEnvVariables() {
    try {
    const response = await fetch('/front-api/env');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const envVariables = await response.json();
        return envVariables;
    } catch (error) {
        console.error('Error fetching environment variables:', error);
        return {};
    }
}

backBtn.addEventListener('click', goBack);
sendBtn.addEventListener('click', sendMessage);

async function connectTelegram() {
  const env = await getEnvVariables();
  const botUsername = env.BOT_USERNAME;
  const telegramLink = `https://t.me/${botUsername}?start=${userId}`;
    window.open(telegramLink, '_blank');
}

connectTGBtn.addEventListener('click', connectTelegram);

