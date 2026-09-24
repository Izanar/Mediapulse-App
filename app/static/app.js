const API_URL = '/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    initUploadZone();

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

    // --- Пасхалка №1: SRE Matrix Mode ---
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

    // --- Пасхалка №2: Тройной клик по логотипу ---
    let clickCount = 0;
    let clickTimer = null;
    const logo = document.getElementById('logo');

    logo?.addEventListener('click', () => {
        clickCount++;
        clearTimeout(clickTimer);

        if (clickCount === 3) {
            logo.classList.add('spin-anim');
            setTimeout(() => logo.classList.remove('spin-anim'), 1000);

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

    // --- Вход ---
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

// Инициализация зоны загрузки файлов
function initUploadZone() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');

    if (!uploadZone || !fileInput) return;

    // Клик по всей зоне триггерит выбор файла
    uploadZone.addEventListener('click', () => fileInput.click());

    // Выбор файла через диалоговое окно
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // Drag & Drop подсветка
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.style.borderColor = '#3b82f6';
            uploadZone.style.background = 'rgba(59, 130, 246, 0.15)';
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.style.borderColor = '';
            uploadZone.style.background = '';
        });
    });

    // Сброс файла
    uploadZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
}

// Отправка файла на сервер
async function handleFileUpload(file) {
    const token = localStorage.getItem('token');
    if (!token) {
        showToast('Ошибка: вы не авторизованы');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showToast(`Загрузка: ${file.name}...`);

    try {
        const res = await fetch(`${API_URL}/tasks/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Ошибка загрузки');
        }

        showToast('Файл успешно загружен!');
        loadTasks();
    } catch (err) {
        showToast(`Ошибка: ${err.message}`);
    }
}

// Получение и вывод списка задач
async function loadTasks() {
    const token = localStorage.getItem('token');
    const tasksList = document.getElementById('tasks-list');
    if (!token || !tasksList) return;

    try {
        const res = await fetch(`${API_URL}/tasks/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) return;

        const tasks = await res.json();
        if (tasks.length === 0) {
            tasksList.innerHTML = '<p style="color: var(--text-muted); font-size: 0.875rem; margin-top: 1rem; text-align: center;">Загруженных файлов пока нет</p>';
            return;
        }

        tasksList.innerHTML = tasks.map(t => `
            <div id="task-${t.id}" style="background: rgba(15,23,42,0.6); padding: 0.75rem 1rem; border-radius: 8px; margin-top: 0.5rem; display: flex; justify-content: space-between; align-items: center; border: 1px solid var(--card-border);">
                <div style="display: flex; align-items: center; gap: 0.5rem; overflow: hidden; max-width: 250px;">
                    <span style="font-size: 0.9rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">📄 ${t.original_filename}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 4px; background: rgba(59, 130, 246, 0.2); color: #60a5fa;">${t.status}</span>
                    <button onclick="deleteTask('${t.id}')" title="Видалити" style="background: transparent; border: none; color: #ff5c5c; font-size: 16px; cursor: pointer; padding: 2px 6px; border-radius: 4px; transition: background 0.2s;">✕</button>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error('Ошибка загрузки задач:', err);
    }
}

// Удаление задачи по её ID
async function deleteTask(taskId) {
    const token = localStorage.getItem('token');
    if (!token) {
        showToast('Ошибка: вы не авторизованы');
        return;
    }

    try {
        const res = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!res.ok && res.status !== 204) {
            const err = await res.json();
            throw new Error(err.detail || 'Ошибка удаления');
        }

        showToast('Файл успешно удален');
        
        // Удаляем элемент из DOM без перезагрузки всей страницы
        const taskElement = document.getElementById(`task-${taskId}`);
        if (taskElement) {
            taskElement.remove();
        }
        
        // Если список стал пустым, выведем заглушку
        const tasksList = document.getElementById('tasks-list');
        if (tasksList && tasksList.children.length === 0) {
            tasksList.innerHTML = '<p style="color: var(--text-muted); font-size: 0.875rem; margin-top: 1rem; text-align: center;">Загруженных файлов пока нет</p>';
        }

    } catch (err) {
        showToast(`Ошибка: ${err.message}`);
    }
}

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
        loadTasks();
    } else {
        authSection?.classList.remove('hidden');
        appSection?.classList.add('hidden');
        logoutBtn?.classList.add('hidden');
        if (userBadge) userBadge.innerText = 'Не авторизован';
    }
}

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