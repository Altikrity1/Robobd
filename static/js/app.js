document.addEventListener('DOMContentLoaded', function () {
    const chatBox = document.getElementById('chat-box');
    const queryInput = document.getElementById('query-input');
    const sendBtn = document.getElementById('send-btn');

    function appendMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');
        messageDiv.innerHTML = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function sendMessage() {
        const query = queryInput.value.trim();
        if (!query) return;

        appendMessage(query, 'user');
        queryInput.value = '';

        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('message', 'bot-message', 'typing-indicator');
        typingIndicator.innerHTML = 'Thinking...';
        chatBox.appendChild(typingIndicator);
        chatBox.scrollTop = chatBox.scrollHeight;

        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `query=${encodeURIComponent(query)}`
        })
        .then(response => response.json())
        .then(data => {
            chatBox.removeChild(typingIndicator);
            appendMessage(data.response, 'bot');
        })
        .catch(error => {
            console.error('Error:', error);
            chatBox.removeChild(typingIndicator);
            appendMessage('An error occurred. Please try again.', 'bot');
        });
    }

    sendBtn.addEventListener('click', sendMessage);
    queryInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') sendMessage();
    });
});
