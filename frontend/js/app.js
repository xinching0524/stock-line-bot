let currentUser = localStorage.getItem('temple_user');
let selectedAmount = 100;

// DOM Elements
const loginScreen = document.getElementById('login-screen');
const mainScreen = document.getElementById('main-screen');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('login-btn');
const registerBtn = document.getElementById('register-btn');
const authError = document.getElementById('auth-error');
const displayName = document.getElementById('display-name');
const navBtns = document.querySelectorAll('.nav-btn');
const tabSections = document.querySelectorAll('.tab-section');
const logoutBtn = document.getElementById('logout-btn');

// Draw Elements
const drawBtn = document.getElementById('draw-btn');
const questionInput = document.getElementById('question');
const poemResult = document.getElementById('poem-result');

// Donate Elements
const amountBtns = document.querySelectorAll('.amount-btn');
const donateBtn = document.getElementById('donate-btn');
const donateMsgInput = document.getElementById('donate-message');
const donateSuccess = document.getElementById('donate-success');

// History Elements
const historyList = document.getElementById('history-list');

// Initialization
if (currentUser) {
    showMainScreen(currentUser);
}

// Event Listeners
async function handleAuth(isRegister) {
    const name = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    if (!name || password.length < 4) {
        authError.innerText = "請輸入名稱與至少 4 碼密碼";
        authError.classList.remove('hidden');
        return;
    }
    authError.classList.add('hidden');
    loginBtn.disabled = true;
    if(registerBtn) registerBtn.disabled = true;

    try {
        const endpoint = isRegister ? '/api/auth/register' : '/api/auth/login';
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: name, password: password })
        });
        const data = await res.json();
        if(res.ok) {
            if(isRegister) {
                authError.innerText = "註冊成功，請登入！";
                authError.style.color = "#4caf50";
                authError.classList.remove('hidden');
            } else {
                currentUser = name;
                localStorage.setItem('temple_user', name);
                showMainScreen(name);
                passwordInput.value = '';
            }
        } else {
            authError.innerText = data.detail || "發生錯誤";
            authError.style.color = "var(--red)";
            authError.classList.remove('hidden');
        }
    } catch (err) {
        authError.innerText = "連線失敗";
        authError.classList.remove('hidden');
    }
    loginBtn.disabled = false;
    if(registerBtn) registerBtn.disabled = false;
}

loginBtn.addEventListener('click', () => handleAuth(false));
registerBtn.addEventListener('click', () => handleAuth(true));

logoutBtn.addEventListener('click', () => {
    currentUser = null;
    localStorage.removeItem('temple_user');
    mainScreen.classList.remove('active');
    loginScreen.classList.add('active');
    poemResult.classList.add('hidden');
});

navBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        navBtns.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        const targetId = e.target.getAttribute('data-target');
        tabSections.forEach(sec => {
            sec.classList.remove('active');
            if (sec.id === targetId) sec.classList.add('active');
        });

        if (targetId === 'history-section') {
            loadHistory();
        }
    });
});

amountBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        amountBtns.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        selectedAmount = parseInt(e.target.getAttribute('data-amount'));
    });
});

drawBtn.addEventListener('click', async () => {
    drawBtn.disabled = true;
    drawBtn.innerText = "搖動中...";
    poemResult.classList.add('hidden');

    try {
        const res = await fetch('/api/draw', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser, question: questionInput.value })
        });
        const data = await res.json();
        if(res.ok) {
            document.getElementById('poem-title').innerText = data.poem.title;
            document.getElementById('poem-type').innerText = data.poem.fortune_type;
            document.getElementById('poem-content').innerText = data.poem.content;
            document.getElementById('poem-explanation').innerText = data.poem.explanation;
            poemResult.classList.remove('hidden');
        } else {
            alert(data.detail || "發生錯誤");
        }
    } catch (err) {
        alert("連線失敗");
    }
    
    drawBtn.disabled = false;
    drawBtn.innerText = "搖動籤筒";
});

donateBtn.addEventListener('click', async () => {
    donateBtn.disabled = true;
    try {
        const res = await fetch('/api/donation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser, amount: selectedAmount, message: donateMsgInput.value })
        });
        if(res.ok) {
            donateSuccess.classList.remove('hidden');
            setTimeout(() => donateSuccess.classList.add('hidden'), 3000);
            donateMsgInput.value = "";
        }
    } catch (err) { }
    donateBtn.disabled = false;
});

function showMainScreen(name) {
    loginScreen.classList.remove('active');
    mainScreen.classList.add('active');
    displayName.innerText = name;
}

async function loadHistory() {
    historyList.innerHTML = "載入中...";
    try {
        const [drawRes, donateRes] = await Promise.all([
            fetch(`/api/history?username=${currentUser}`),
            fetch(`/api/donation/history?username=${currentUser}`)
        ]);
        
        let draws = [];
        let donations = [];
        if(drawRes.ok) draws = await drawRes.json();
        if(donateRes.ok) donations = await donateRes.json();

        let combined = [...draws.map(d => ({...d, _type: 'draw'})), ...donations.map(d => ({...d, _type: 'donation'}))];
        combined.sort((a,b) => new Date(b.created_at) - new Date(a.created_at));

        if (combined.length === 0) {
            historyList.innerHTML = "<p>尚無任何紀錄</p>";
            return;
        }

        historyList.innerHTML = "";
        combined.forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item';
            const dateTxt = new Date(item.created_at).toLocaleString('zh-TW');
            
            if (item._type === 'draw') {
                div.innerHTML = `
                    <div class="history-date">${dateTxt}</div>
                    <div class="history-msg">
                        <span class="history-type">線上求籤</span>
                        ${item.poem.title} / ${item.poem.fortune_type}
                        ${item.question ? `<br><small>所求：${item.question}</small>` : ''}
                    </div>`;
            } else {
                div.innerHTML = `
                    <div class="history-date">${dateTxt}</div>
                    <div class="history-msg">
                        <span class="history-type">香油捐獻</span>
                        NT$ ${item.amount}
                        ${item.message ? `<br><small>祈願：${item.message}</small>` : ''}
                    </div>`;
            }
            historyList.appendChild(div);
        });
    } catch(err) {
        historyList.innerHTML = "載入失敗";
    }
}
