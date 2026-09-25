const API_URL = '/api/v1';
const S3_BASE_URL = 'http://localhost:9000/mediapulse-storage'; // Налаштуйте під ваш S3/MinIO

let currentFilter = 'all';
let pollingTimer = null;

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    initUploadZone();
    initEasterEggs();
    initKonamiCode();

    // --- Перемикання Вхід / Реєстрація ---
    document.getElementById('show-register')?.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('login-form-container')?.classList.add('hidden');
        document.getElementById('register-form-container')?.classList.remove('hidden');
    });

    document.getElementById('show-login')?.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('register-form-container')?.classList.add('hidden');
        document.getElementById('login-form-container')?.classList.remove('hidden');
    });

    // --- Фільтри Галереї ---
    document.getElementById('filter-all')?.addEventListener('click', (e) => {
        setActiveFilter(e.target);
        loadMyTasks('all');
    });
    document.getElementById('filter-public')?.addEventListener('click', (e) => {
        setActiveFilter(e.target);
        loadMyTasks('public');
    });
    document.getElementById('filter-private')?.addEventListener('click', (e) => {
        setActiveFilter(e.target);
        loadMyTasks('private');
    });

    // --- Авторизація ---
    document.getElementById('login-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);

        try {
            const res = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error('Невірний логін або пароль');

            const data = await res.json();
            localStorage.setItem('token', data.access_token);
            showToast('Успішний вхід у систему!');
            checkAuth();
        } catch (err) {
            showToast(`Помилка: ${err.message}`);
        }
    });

    // --- Реєстрація ---
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

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || 'Помилка реєстрації');
            }

            showToast('Реєстрація успішна! Увійдіть в акаунт.');
            document.getElementById('show-login')?.click();
        } catch (err) {
            showToast(`Помилка: ${err.message}`);
        }
    });

    // --- Вихід ---
    document.getElementById('logout-btn')?.addEventListener('click', () => {
        localStorage.removeItem('token');
        document.body.classList.remove('matrix-mode');
        showToast('Ви вийшли з системи');
        checkAuth();
    });
});

// --- ПАСХАЛКА 1 і 2: Matrix Mode & Triple-click Console Log ---
function initEasterEggs() {
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
                '%c🚀 MediaPulse Dev Mode Enabled!\n%cArchitecture: FastAPI + Celery + Redis + PostgreSQL + S3/MinIO.\nBuilt for Cloud-Native Engineers.',
                'color: #3b82f6; font-size: 16px; font-weight: bold;',
                'color: #94a3b8; font-size: 12px;'
            );

            showToast('✨ Dev Mode Unlocked! Inspect F12 Console.');
            clickCount = 0;
        } else {
            clickTimer = setTimeout(() => { clickCount = 0; }, 400);
        }
    });
}

// --- ПАСХАЛКА 3: Konami Code (↑ ↑ ↓ ↓ ← → ← → B A) ---
function initKonamiCode() {
    const konamiCode = [
        'ArrowUp', 'ArrowUp', 
        'ArrowDown', 'ArrowDown', 
        'ArrowLeft', 'ArrowRight', 
        'ArrowLeft', 'ArrowRight', 
        'KeyB', 'KeyA'
    ];
    let konamiIndex = 0;

    document.addEventListener('keydown', (e) => {
        const reqKey = konamiCode[konamiIndex];
        if (e.code === reqKey || e.key === reqKey) {
            konamiIndex++;
            if (konamiIndex === konamiCode.length) {
                activateKonamiGodMode();
                konamiIndex = 0;
            }
        } else {
            konamiIndex = 0;
        }
    });
}

function activateKonamiGodMode() {
    document.body.classList.add('matrix-mode');
    showToast('🎮 KONAMI CODE ACTIVATED: GOD MODE ENABLED!');
    console.log(
        '%c🎮 KONAMI CODE UNLOCKED!\n%c+30 Lives Granted. All S3 Buckets Unlocked.',
        'color: #ef4444; font-size: 20px; font-weight: bold;',
        'color: #10b981; font-size: 14px;'
    );
}

// --- Завантаження файлів ---
function initUploadZone() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');

    if (!uploadZone || !fileInput) return;

    uploadZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

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

    uploadZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
}

async function handleFileUpload(file) {
    const token = localStorage.getItem('token');
    if (!token) {
        showToast('Помилка: ви не авторизовані');
        return;
    }

    const isPublic = confirm("Зробити файл публічним?");

    const formData = new FormData();
    formData.append('file', file);
    formData.append('is_public', isPublic);

    showToast(`Завантаження: ${file.name}...`);

    try {
        const res = await fetch(`${API_URL}/tasks/`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Помилка завантаження');
        }

        showToast('Файл успішно відправлено на інверсію!');
        loadMyTasks(currentFilter);
    } catch (err) {
        showToast(`Помилка: ${err.message}`);
    }
}

// --- Завантаження та рендеринг списку задач ---
async function loadMyTasks(filterType = 'all') {
    currentFilter = filterType;
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const res = await fetch(`${API_URL}/tasks/my?filter_type=${filterType}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) return;

        const tasks = await res.json();
        renderTaskList(tasks);
        checkPendingTasks(tasks);
    } catch (err) {
        console.error('Помилка завантаження задач:', err);
    }
}

async function loadPublicGallery() {
    if (localStorage.getItem('token')) return;

    try {
        const res = await fetch(`${API_URL}/tasks/public`);
        if (!res.ok) return;

        const tasks = await res.json();
        renderTaskList(tasks);
        checkPendingTasks(tasks);
    } catch (err) {
        console.error('Помилка завантаження публічної галереї:', err);
    }
}

// Перевіряє, чи є завдання у статусі PENDING, та запускає оновлення
function checkPendingTasks(tasks) {
    clearTimeout(pollingTimer);
    const hasPending = tasks.some(t => t.status?.toLowerCase() === 'pending');
    if (hasPending) {
        pollingTimer = setTimeout(() => {
            if (localStorage.getItem('token')) {
                loadMyTasks(currentFilter);
            } else {
                loadPublicGallery();
            }
        }, 2000);
    }
}

function renderTaskList(tasks) {
    const tasksList = document.getElementById('tasks-list');
    if (!tasksList) return;

    if (!tasks || tasks.length === 0) {
        tasksList.innerHTML = '<p style="color: var(--text-muted); font-size: 0.875rem; margin-top: 1rem; text-align: center;">Медіафайлів поки немає</p>';
        return;
    }

    const token = localStorage.getItem('token');

    tasksList.innerHTML = tasks.map(t => {
        // Формуємо URL зображення: якщо шлях вже є повноцінним URL (S3/MinIO), використовуємо його, інакше додаємо локальний префікс /
        const formatUrl = (path) => {
            if (!path) return '';
            if (path.startsWith('http://') || path.startsWith('https://')) return path;
            return path.startsWith('/') ? path : `/${path}`;
        };

        const origUrl = formatUrl(t.storage_path);
        const procUrl = t.processed_path ? formatUrl(t.processed_path) : origUrl;
        const currentDisplayUrl = t.processed_path ? procUrl : origUrl;

        // Відображаємо назву файлу з original_filename
        const fileName = t.original_filename || t.user_filename || 'Завантажений файл';

        return `
            <div id="task-${t.id}" style="background: rgba(15,23,42,0.6); padding: 1rem; border-radius: 8px; margin-top: 0.75rem; border: 1px solid var(--card-border, #1e293b);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 0.95rem; font-weight: 600;">📄 ${fileName}</span>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 0.7rem; padding: 0.2rem 0.4rem; border-radius: 4px; background: ${t.is_public ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}; color: ${t.is_public ? '#34d399' : '#f87171'};">
                            ${t.is_public ? 'Публічний' : 'Приватний'}
                        </span>
                        <span style="font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 4px; background: rgba(59, 130, 246, 0.2); color: #60a5fa;">${t.status}</span>
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <div style="display: flex; gap: 0.5rem;">
                        <button onclick="switchView('${t.id}', '${origUrl}')" style="font-size: 0.75rem; padding: 4px 8px; background: #334155; border: none; color: white; border-radius: 4px; cursor: pointer;">Оригінал</button>
                        ${t.processed_path ? `<button onclick="switchView('${t.id}', '${procUrl}')" style="font-size: 0.75rem; padding: 4px 8px; background: #3b82f6; border: none; color: white; border-radius: 4px; cursor: pointer;">Інверсія</button>` : ''}
                    </div>
                    ${token ? `<button onclick="deleteTask('${t.id}')" style="font-size: 0.75rem; padding: 4px 8px; background: #ef4444; border: none; color: white; border-radius: 4px; cursor: pointer;">Видалити</button>` : ''}
                </div>

                <div style="margin-top: 0.75rem; text-align: center;">
                    <img id="img-preview-${t.id}" src="${currentDisplayUrl}" alt="${fileName}" style="max-width: 100%; max-height: 250px; border-radius: 6px; object-fit: contain;">
                </div>
            </div>
        `;
    }).join('');
}

function switchView(taskId, url) {
    const img = document.getElementById(`img-preview-${taskId}`);
    if (img) img.src = url;
}

async function deleteTask(taskId) {
    if (!confirm("Ви дійсно бажаєте видалити цей файл?")) return;

    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.ok) {
            showToast('Файл успішно видалено!');
            loadMyTasks(currentFilter);
        } else {
            const err = await res.json();
            showToast(`Помилка: ${err.detail || 'Не вдалося видалити файл'}`);
        }
    } catch (err) {
        showToast(`Помилка: ${err.message}`);
    }
}

function checkAuth() {
    const token = localStorage.getItem('token');
    const authSection = document.getElementById('auth-section');
    const appSection = document.getElementById('app-section');
    const userBadge = document.getElementById('user-badge');
    const logoutBtn = document.getElementById('logout-btn');
    const galleryFilters = document.getElementById('gallery-filters');

    if (token) {
        authSection?.classList.add('hidden');
        appSection?.classList.remove('hidden');
        logoutBtn?.classList.remove('hidden');
        galleryFilters?.classList.remove('hidden');
        if (userBadge) userBadge.innerText = 'Авторизований';
        loadMyTasks('all');
    } else {
        authSection?.classList.remove('hidden');
        appSection?.classList.add('hidden');
        logoutBtn?.classList.add('hidden');
        galleryFilters?.classList.add('hidden');
        if (userBadge) userBadge.innerText = 'Не авторизований';
        loadPublicGallery();
    }
}

function setActiveFilter(targetBtn) {
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    targetBtn.classList.add('active');
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