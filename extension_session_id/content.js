// Content script chạy trên trang LMS PTIT
console.log('LMS PTIT Session ID Extension loaded');

// Hàm lấy session_id từ cookie
function getSessionIdFromCookie() {
    const match = document.cookie.match(/session_id=([^;]+)/);
    return match ? match[1] : null;
}

// Gửi session_id đến background script khi trang load
document.addEventListener('DOMContentLoaded', function() {
    const sessionId = getSessionIdFromCookie();
    if (sessionId) {
        console.log('Found session_id:', sessionId);
        // Có thể gửi đến background script nếu cần
        chrome.runtime.sendMessage({
            action: 'session_id_found',
            sessionId: sessionId
        });
    }
});

// Theo dõi thay đổi cookie
let lastSessionId = getSessionIdFromCookie();
setInterval(() => {
    const currentSessionId = getSessionIdFromCookie();
    if (currentSessionId !== lastSessionId) {
        lastSessionId = currentSessionId;
        if (currentSessionId) {
            console.log('Session ID updated:', currentSessionId);
            chrome.runtime.sendMessage({
                action: 'session_id_updated',
                sessionId: currentSessionId
            });
        }
    }
}, 1000); // Kiểm tra mỗi giây