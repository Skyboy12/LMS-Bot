let currentSessionId = null;

document.addEventListener('DOMContentLoaded', function() {
    const getSessionIdBtn = document.getElementById('getSessionIdBtn');
    const debugBtn = document.getElementById('debugBtn');
    const copyBtn = document.getElementById('copyBtn');
    const resultDiv = document.getElementById('result');

    getSessionIdBtn.addEventListener('click', getSessionId);
    debugBtn.addEventListener('click', debugInfo);
    copyBtn.addEventListener('click', copySessionId);
});

async function debugInfo() {
    const resultDiv = document.getElementById('result');
    
    try {
        const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
        
        // Lấy tất cả cookies
        const cookies = await chrome.cookies.getAll({
            url: tab.url
        });
        
        // Inject script để lấy thông tin debug
        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            function: () => {
                return {
                    url: window.location.href,
                    cookies: document.cookie,
                    localStorage: Object.keys(localStorage).map(key => `${key}=${localStorage.getItem(key)}`),
                    sessionStorage: Object.keys(sessionStorage).map(key => `${key}=${sessionStorage.getItem(key)}`)
                };
            }
        });
        
        const debugData = results[0].result;
        const debugText = `
URL: ${debugData.url}
Cookies: ${debugData.cookies || 'Không có'}
LocalStorage: ${debugData.localStorage.join(', ') || 'Không có'}
SessionStorage: ${debugData.sessionStorage.join(', ') || 'Không có'}
Chrome Cookies Count: ${cookies.length}
Chrome Cookies: ${cookies.map(c => `${c.name}=${c.value.substring(0, 20)}...`).join(', ')}
        `;
        
        showResult(debugText, 'success');
        
    } catch (error) {
        showResult('Lỗi debug: ' + error.message, 'error');
    }
}


async function getSessionId() {
    const resultDiv = document.getElementById('result');
    const copyBtn = document.getElementById('copyBtn');
    try {
        // Lấy tab hiện tại
        const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
        if (!tab.url.includes('lms.ptit.edu.vn')) {
            showResult('Vui lòng truy cập trang web lms.ptit.edu.vn trước!', 'error');
            copyBtn.style.display = 'none';
            return;
        }

        // Lấy cookie session_id đúng domain và path
        chrome.cookies.get({
            url: 'https://lms.ptit.edu.vn/',
            name: 'session_id'
        }, function(cookie) {
            if (cookie && cookie.value) {
                currentSessionId = cookie.value;
                showResult(`Session ID: ${currentSessionId}`, 'success');
                copyBtn.style.display = 'block';
            } else {
                showResult('Không tìm thấy session_id (HttpOnly) trong cookie.\nHãy chắc chắn đã đăng nhập LMS và thử lại.', 'error');
                copyBtn.style.display = 'none';
            }
        });
    } catch (error) {
        showResult('Lỗi khi lấy session_id: ' + error.message, 'error');
        copyBtn.style.display = 'none';
    }
}

// Hàm này sẽ được inject vào trang web để lấy cookie
function extractSessionIdFromPage() {
    console.log('Extracting session ID from page...');
    console.log('Current URL:', window.location.href);
    console.log('All cookies:', document.cookie);
    
    // Thử nhiều cách để lấy session_id
    const methods = [
        // Method đơn giản nhất - lấy trực tiếp
        () => {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.split('=');
                if (name && name.trim() === 'session_id' && value) {
                    const result = value.trim();
                    console.log('Method 0 (simple):', result);
                    return result;
                }
            }
            return null;
        },
        // Từ document.cookie - tìm session_id
        () => {
            const match = document.cookie.match(/session_id=([^;]+)/);
            let result = null;
            if (match) {
                result = match[1].trim();
                // Thử decode nếu cần
                try {
                    const decoded = decodeURIComponent(result);
                    if (decoded !== result && decoded.length > 0) {
                        result = decoded;
                    }
                } catch (e) {
                    // Giữ nguyên giá trị gốc nếu decode lỗi
                }
            }
            console.log('Method 1 (session_id):', result);
            return result;
        },
        // Từ document.cookie - tìm PHPSESSID
        () => {
            const match = document.cookie.match(/PHPSESSID=([^;]+)/);
            const result = match ? decodeURIComponent(match[1]) : null;
            console.log('Method 2 (PHPSESSID):', result);
            return result;
        },
        // Từ localStorage
        () => {
            try {
                const result = localStorage.getItem('session_id') || localStorage.getItem('PHPSESSID');
                console.log('Method 3 (localStorage):', result);
                return result;
            } catch (e) {
                return null;
            }
        },
        // Từ sessionStorage  
        () => {
            try {
                const result = sessionStorage.getItem('session_id') || sessionStorage.getItem('PHPSESSID');
                console.log('Method 4 (sessionStorage):', result);
                return result;
            } catch (e) {
                return null;
            }
        },
        // Tìm trong tất cả cookies với các pattern khác nhau
        () => {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name && (name.toLowerCase().includes('session') || name === 'PHPSESSID')) {
                    const result = decodeURIComponent(value || '');
                    console.log(`Method 5 (${name}):`, result);
                    return result;
                }
            }
            return null;
        },
        // Tìm trong meta tags
        () => {
            const meta = document.querySelector('meta[name="csrf-token"]') || 
                        document.querySelector('meta[name="session-id"]');
            const result = meta ? meta.getAttribute('content') : null;
            console.log('Method 6 (meta tags):', result);
            return result;
        },
        // Method cuối - sử dụng function getCookie đơn giản
        () => {
            function getCookie(name) {
                const value = "; " + document.cookie;
                const parts = value.split("; " + name + "=");
                if (parts.length === 2) return parts.pop().split(";").shift();
                return null;
            }
            const result = getCookie('session_id');
            console.log('Method 7 (getCookie):', result);
            return result;
        }
    ];

    for (let i = 0; i < methods.length; i++) {
        try {
            const result = methods[i]();
            if (result && result.length > 5 && result !== 'null' && result !== 'undefined') {
                console.log(`✅ Found session ID using method ${i + 1}:`, result);
                return result;
            }
        } catch (e) {
            console.log(`Method ${i + 1} failed:`, e);
        }
    }

    console.log('❌ No session ID found');
    return null;
}

function showResult(message, type) {
    const resultDiv = document.getElementById('result');
    resultDiv.textContent = message;
    resultDiv.className = `result ${type}`;
}

async function copySessionId() {
    if (currentSessionId) {
        try {
            await navigator.clipboard.writeText(currentSessionId);
            showResult(`Session ID đã được copy: ${currentSessionId}`, 'success');
        } catch (error) {
            // Fallback cho các trình duyệt không hỗ trợ clipboard API
            const textarea = document.createElement('textarea');
            textarea.value = currentSessionId;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            showResult(`Session ID đã được copy: ${currentSessionId}`, 'success');
        }
    }
}