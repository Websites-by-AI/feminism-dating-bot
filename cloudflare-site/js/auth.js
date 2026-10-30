// Unified Authentication, Safe Storage & Multi-Edge API System
// سیستم یکپارچه احراز هویت با پشتیبانی از دامنه اختصاصی ضد فیلتر + پشتیبان ابری

(function () {
    const memStore = {};
    window.safeStorage = {
        getItem(k) {
            try { return localStorage.getItem(k); } catch (e) { return Object.prototype.hasOwnProperty.call(memStore, k) ? memStore[k] : null; }
        },
        setItem(k, v) {
            memStore[k] = String(v);
            try { localStorage.setItem(k, String(v)); } catch (e) {}
        },
        removeItem(k) {
            delete memStore[k];
            try { localStorage.removeItem(k); } catch (e) {}
        }
    };

    const host = (typeof window !== 'undefined' && window.location && window.location.hostname) || '';
    const isPagesOrCustom = host === 'dating.atikova.org' || host.endsWith('.pages.dev');
    // Same-origin first on Cloudflare Pages / dating.atikova.org (never blocked by workers.dev filters!)
    window.FEMINISM_API_BASE = isPagesOrCustom ? '' : 'https://dating.atikova.org';
    window.FEMINISM_API_ENDPOINTS = isPagesOrCustom
        ? ['', 'https://dating.atikova.org', 'https://feminism-dating-api.elasa2next.workers.dev']
        : ['https://dating.atikova.org', 'https://feminism-dating-api.elasa2next.workers.dev'];

    window.feminismApiFetch = async function (path, options) {
        let lastErr = null;
        for (const base of window.FEMINISM_API_ENDPOINTS) {
            try {
                const resp = await fetch(base + path, options);
                if (resp.ok || resp.status === 400 || resp.status === 401 || resp.status === 409) {
                    return resp;
                }
            } catch (e) {
                lastErr = e;
            }
        }
        if (lastErr) throw lastErr;
        return fetch(window.FEMINISM_API_BASE + path, options);
    };
})();

class AuthService {
    constructor() {
        this.apiBase = window.FEMINISM_API_BASE;
        this.users = this.loadUsers();
        this.currentUser = this.loadCurrentUser();
    }

    normalizeUser(u) {
        if (!u) return null;
        const firstName = u.firstName || (u.name ? u.name.split(' ')[0] : u.username || 'کاربر');
        const lastName = u.lastName !== undefined ? u.lastName : (u.name ? u.name.split(' ').slice(1).join(' ') : '');
        const fullName = u.name || `${firstName} ${lastName}`.trim();
        return {
            ...u,
            id: u.id || 1,
            telegram_id: u.telegram_id || (100000 + (u.id || 1)),
            firstName,
            lastName,
            name: fullName,
            role: u.role || 'user',
            safety_score: u.safety_score !== undefined ? u.safety_score : 100
        };
    }

    loadUsers() {
        try {
            const raw = window.safeStorage.getItem('feminism_dating_users');
            if (raw) return JSON.parse(raw);
        } catch (e) {}

        const demoUsers = [
            {
                id: 1,
                telegram_id: 100001,
                firstName: 'سارا',
                lastName: 'احمدی',
                name: 'سارا احمدی',
                email: 'sara@feminism-dating.org',
                username: 'sara123',
                password: 'demo123',
                age: 26,
                gender: 'female',
                city: 'تهران',
                relationship_mode: 'serious',
                mbti_type: 'INFJ',
                safety_score: 100,
                role: 'user',
                createdAt: new Date().toISOString()
            },
            {
                id: 2,
                telegram_id: 100002,
                firstName: 'مریم',
                lastName: 'کریمی',
                name: 'مریم کریمی',
                email: 'maryam@feminism-dating.org',
                username: 'maryam123',
                password: 'demo123',
                age: 29,
                gender: 'female',
                city: 'اصفهان',
                relationship_mode: 'startup',
                mbti_type: 'ENTJ',
                safety_score: 98,
                role: 'user',
                createdAt: new Date().toISOString()
            },
            {
                id: 99,
                telegram_id: 100099,
                firstName: 'مدیر',
                lastName: 'سیستم',
                name: 'مدیر سیستم',
                email: 'admin@feminism-dating.com',
                username: 'admin',
                password: 'admin123',
                age: 34,
                gender: 'female',
                city: 'تهران',
                relationship_mode: 'serious',
                safety_score: 100,
                role: 'admin',
                createdAt: new Date().toISOString()
            }
        ];
        window.safeStorage.setItem('feminism_dating_users', JSON.stringify(demoUsers));
        return demoUsers;
    }

    saveUsers() {
        window.safeStorage.setItem('feminism_dating_users', JSON.stringify(this.users));
    }

    loadCurrentUser() {
        try {
            const raw = window.safeStorage.getItem('feminism_dating_current_user') || window.safeStorage.getItem('user');
            if (!raw) return null;
            return this.normalizeUser(JSON.parse(raw));
        } catch (e) {
            return null;
        }
    }

    saveCurrentUser(user) {
        if (user) {
            const norm = this.normalizeUser(user);
            const str = JSON.stringify(norm);
            window.safeStorage.setItem('feminism_dating_current_user', str);
            window.safeStorage.setItem('user', str);
            this.currentUser = norm;
        } else {
            window.safeStorage.removeItem('feminism_dating_current_user');
            window.safeStorage.removeItem('user');
            this.currentUser = null;
        }
    }

    register(userData) {
        if (this.users.find(u => u.username.toLowerCase() === userData.username.toLowerCase())) {
            return { success: false, message: 'این نام کاربری قبلاً ثبت شده است' };
        }
        if (this.users.find(u => u.email.toLowerCase() === userData.email.toLowerCase())) {
            return { success: false, message: 'این ایمیل قبلاً ثبت شده است' };
        }
        const nextId = Math.max(...this.users.map(u => u.id || 0), 10) + 1;
        const newUser = this.normalizeUser({
            id: nextId,
            telegram_id: 200000 + nextId,
            firstName: userData.firstName,
            lastName: userData.lastName,
            name: `${userData.firstName || ''} ${userData.lastName || ''}`.trim(),
            email: userData.email,
            username: userData.username,
            password: userData.password,
            age: userData.age,
            gender: userData.gender,
            city: userData.city,
            relationship_mode: userData.relationship_mode || 'serious',
            role: 'user',
            createdAt: new Date().toISOString()
        });
        this.users.push(newUser);
        this.saveUsers();
        return { success: true, message: 'ثبت‌نام با موفقیت انجام شد', user: newUser };
    }

    async registerAsync(userData) {
        try {
            const resp = await window.feminismApiFetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });
            const data = await resp.json();
            if (data && data.success) {
                const synced = this.normalizeUser({ ...userData, ...data.user });
                const idx = this.users.findIndex(u => u.username === synced.username);
                if (idx === -1) this.users.push(synced);
                else this.users[idx] = synced;
                this.saveUsers();
                this.saveCurrentUser(synced);
                return { success: true, message: data.message || 'ثبت‌نام با موفقیت انجام شد', user: synced };
            }
            if (resp.status === 409 || resp.status === 400) {
                return { success: false, message: data.message || 'خطا در اطلاعات ورودی' };
            }
        } catch (err) {
            console.warn('Cloud API fallback to local register:', err);
        }
        const localRes = this.register(userData);
        if (localRes.success) this.saveCurrentUser(localRes.user);
        return localRes;
    }

    login(username, password) {
        const user = this.users.find(
            u => (u.username.toLowerCase() === username.toLowerCase() || (u.email && u.email.toLowerCase() === username.toLowerCase())) && u.password === password
        );
        if (!user) {
            return { success: false, message: 'نام کاربری یا رمز عبور اشتباه است' };
        }
        const norm = this.normalizeUser(user);
        this.saveCurrentUser(norm);
        return { success: true, user: norm };
    }

    async loginAsync(username, password) {
        try {
            const resp = await window.feminismApiFetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await resp.json();
            if (data && data.success && data.user) {
                const norm = this.normalizeUser(data.user);
                this.saveCurrentUser(norm);
                return { success: true, user: norm };
            }
        } catch (err) {
            console.warn('Cloud API fallback to local login:', err);
        }
        return this.login(username, password);
    }

    logout() {
        this.saveCurrentUser(null);
    }

    isLoggedIn() {
        return this.currentUser !== null;
    }

    isAdmin() {
        return this.currentUser && this.currentUser.role === 'admin';
    }

    getCurrentUser() {
        if (!this.currentUser) {
            this.currentUser = this.loadCurrentUser();
        }
        return this.currentUser;
    }

    async updateProfileAsync(userId, updates) {
        try {
            const resp = await window.feminismApiFetch(`/api/user/${encodeURIComponent(userId)}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });
            const data = await resp.json();
            if (data && data.success && data.user) {
                this.saveCurrentUser(data.user);
                return { success: true, user: this.currentUser };
            }
        } catch (err) {
            console.warn('Local profile update fallback:', err);
        }
        return this.updateProfile(userId, updates);
    }

    updateProfile(userId, updates) {
        const userIndex = this.users.findIndex(u => u.id === userId || u.telegram_id === userId);
        if (userIndex !== -1) {
            this.users[userIndex] = this.normalizeUser({ ...this.users[userIndex], ...updates });
            this.saveUsers();
        }
        if (this.currentUser) {
            this.saveCurrentUser({ ...this.currentUser, ...updates });
        }
        return { success: true, message: 'پروفایل با موفقیت به‌روزرسانی شد', user: this.currentUser };
    }

    getAllUsers() {
        return this.users;
    }
}

class DatabaseService {
    constructor() {
        this.initDatabase();
    }

    initDatabase() {
        if (!window.safeStorage.getItem('feminism_dating_initialized')) {
            const stats = {
                totalUsers: 7,
                activeUsers: 7,
                totalMatches: 128,
                safetyAlerts: 0,
                todayLogins: 4,
                avgRating: 4.9
            };
            window.safeStorage.setItem('feminism_dating_stats', JSON.stringify(stats));

            const activities = [
                { id: 1, user: 'سارا احمدی', action: 'ورود به سیستم و فعال‌سازی دوست مخفی', time: '۵ دقیقه پیش', type: 'login' },
                { id: 2, user: 'مریم کریمی', action: 'تکمیل تست شریک استارتاپی (۹۵٪)', time: '۱۵ دقیقه پیش', type: 'profile' },
                { id: 3, user: 'Elif Yılmaz', action: 'تنظیم حالت آشنایی بین‌المللی', time: '۳۰ دقیقه پیش', type: 'match' }
            ];
            window.safeStorage.setItem('feminism_dating_activities', JSON.stringify(activities));
            window.safeStorage.setItem('feminism_dating_initialized', 'true');
        }
    }

    getStatistics() {
        try {
            return JSON.parse(window.safeStorage.getItem('feminism_dating_stats') || 'null');
        } catch (e) {
            return null;
        }
    }

    getActivities() {
        try {
            return JSON.parse(window.safeStorage.getItem('feminism_dating_activities') || '[]');
        } catch (e) {
            return [];
        }
    }

    addActivity(activity) {
        const activities = this.getActivities();
        activity.id = activities.length + 1;
        activities.unshift(activity);
        window.safeStorage.setItem('feminism_dating_activities', JSON.stringify(activities.slice(0, 30)));
    }
}

class ThemeManager {
    constructor() {
        this.initTheme();
    }

    initTheme() {
        const theme = window.safeStorage.getItem('theme') || 'light';
        this.setTheme(theme);
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        window.safeStorage.setItem('theme', theme);
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        this.setTheme(currentTheme === 'dark' ? 'light' : 'dark');
    }
}

var authService = window.authService || new AuthService();
var dbService = window.dbService || new DatabaseService();
var themeManager = window.themeManager || new ThemeManager();
window.authService = authService;
window.dbService = dbService;
window.themeManager = themeManager;
