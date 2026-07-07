document.addEventListener('DOMContentLoaded', () => {
    // ── Chatbot Overlay Interactions ───────────────────────────────
    const chatbotIcon = document.getElementById('chatbotIcon');
    const chatbotWindow = document.getElementById('chatbotWindow');
    const closeChatbot = document.getElementById('closeChatbot');
    const chatInput = document.getElementById('chatInput');
    const sendChat = document.getElementById('sendChat');
    const chatMessages = document.getElementById('chatMessages');

    // Toggle Window with Animation
    chatbotIcon.addEventListener('click', () => {
        chatbotWindow.classList.toggle('hidden');
        chatbotWindow.classList.add('animate-zoom-in');
    });

    closeChatbot.addEventListener('click', () => {
        chatbotWindow.classList.add('hidden');
    });

    // Send Logic
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // User Message UI
        appendMessage(message, 'user-msg');
        chatInput.value = '';

        // Typing indicator or delay
        const typingId = appendMessage("AI is typing...", 'bot-msg', true);

        try {
            const response = await fetch('/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            const data = await response.json();
            
            // Remove typing indicator and add final response
            document.getElementById(typingId).remove();
            appendMessage(data.response, 'bot-msg');
        } catch (error) {
            document.getElementById(typingId).remove();
            appendMessage("🤖 Connection error. Please try again later.", 'bot-msg');
        }
    }

    function appendMessage(text, className, isTemp = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = className + ' animate-fade-in';
        msgDiv.textContent = text;
        const id = 'msg-' + Date.now();
        if (isTemp) msgDiv.id = id;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    sendChat.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // ── Page-Level Micro-interactions ──────────────────────────────
    // Add hover sound/glow effect placeholders or general utility
    const cards = document.querySelectorAll('.dashboard-card, .feature-card, .q-card, .coding-card, .hr-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
             // Future extension: add subtle audio or haptic feedback
        });
    });

    // Flash Message Auto-fadeout
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-20px)';
            flash.style.transition = 'opacity 0.6s, transform 0.6s';
            setTimeout(() => flash.remove(), 600);
        }, 5000);
    });
});
