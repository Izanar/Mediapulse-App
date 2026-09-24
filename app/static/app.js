const API_URL = '/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();

    // --- Переключение Вход / Регистрация ---
    document.getElementById('show-register')?.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('login-form-container').classList.add('hidden');
        document.getElementById('register-form-container').classList.remove('hidden');
    });

    document.getElementById('show-login')?.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('register-form-container').classList.add('hidden');
        document.getElementById('login-form-container').classList.remove('hidden');
    });

    // --- 🤫 ПАСХАЛКА №1: SRE Matrix Mode (мгновенное переключение при вводе 'matrix' или 'sudo') ---
    const loginInput = document.getElementById('login-username');
    loginInput?.addEventListener('input', (e) => {
        const val = e.target.value.toLowerCase().trim();
        if (val === 'matrix' || val === 'sudo') {
            document.body.classList.add('matrix-mode');
            showToast('🟢 SRE Matrix Mode activated!');
        } else {
            document.body.classList.remove('matrix-mode');
        }
    });

    // --- 🤫 ПАСХАЛКА №2: Быстрый тройной клик по логотипу MediaPulse ---
    let clickCount = 0;
    let clickTimer = null;
    const logo = document.getElementById('logo');

    logo?.addEventListener('click', () => {
        clickCount++;
        clearTimeout(clickTimer);

        if (clickCount === 3) {
            // Запуск вращения
            logo.classList.add('spin-anim');
            setTimeout(() => logo.classList.remove('spin-anim'), 1000);

            // Сообщение в консоль разработчика (F12)
            console.log(
                '%c🚀 MediaPulse Dev Mode Enabled!\n%cWelcome, Engineer. Built with FastAPI & SQLAlchemy.',
                'color: #3b82f6; font-size: 16px; font-weight: bold;',
                'color: #94a3b8; font-size: 12px;'
            );

            showToast('✨ Secrets unlocked! Check F12 console.');
            clickCount = 0;
        } else {
            clickTimer = setTimeout(() => { clickCount = 0; }, 400);
        }
    });

    // --- Авторизация ---
    document.getElementById('login-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);

        try {
            const res = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error('Неверный логин или пароль');

            const data = await res.json();
            localStorage.setItem('token', data.access_token);
            showToast('Успешный вход!');
            checkAuth();
        } catch (err) {
            showToast(`Ошибка: ${err.message}`);
        }
    });

    // --- Регистрация ---
    document.getElementById('register-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const password = document.getElementById('reg-password').value;

        try {
            const res = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!res.ok) throw new Error('Ошибка регистрации');

            showToast('Регистрация успешна! Войдите в аккаунт.');
            document.getElementById('show-login').click();
        } catch (err) {
            showToast(`Ошибка: ${err.message}`);
        }
    });

    // --- Выход ---
    document.getElementById('logout-btn')?.addEventListener('click', () => {
        localStorage.removeItem('token');
        document.body.classList.remove('matrix-mode');
        showToast('Вы вышли из системы');
        checkAuth();
    });
});

function checkAuth() {
    const token = localStorage.getItem('token');
    const authSection = document.getElementById('auth-section');
    const appSection = document.getElementById('app-section');
    const userBadge = document.getElementById('user-badge');
    const logoutBtn = document.getElementById('logout-btn');

    if (token) {
        authSection?.classList.add('hidden');
        appSection?.classList.remove('hidden');
        logoutBtn?.classList.remove('hidden');
        if (userBadge) userBadge.innerText = 'Авторизован';
    } else {
        authSection?.classList.remove('hidden');
        appSection?.classList.add('hidden');
        logoutBtn?.classList.add('hidden');
        if (userBadge) userBadge.innerText = 'Не авторизован';
    }
}

// Показ notification-тостов
function showToast(message) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerText = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}