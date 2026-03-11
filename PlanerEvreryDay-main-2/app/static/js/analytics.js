// ================== ЛОКАЛИЗАЦИЯ ==================
const translations = {
    ru: {
        // Общее
        'appName': 'Planer EveryDay',
        'addTask': 'Добавить задачу',
        'editTask': 'Редактировать задачу',
        'deleteTask': 'Удалить задачу',
        'confirm': 'Подтвердить',
        'cancel': 'Отмена',
        'close': 'Закрыть',
        'save': 'Сохранить',
        'today': 'Сегодня',
        'tasks': 'задачи',
        'task': 'задача',
        'tasks_plural': 'задач',
        'noTasks': 'Нет задач',
        'emptyToday': 'На сегодня всё пусто',
        'upcoming': 'Предстоящее',
        'notifications': 'Уведомления',
        'markAllRead': 'Отметить все как прочитанные',
        'clearAll': 'Очистить все',
        'all': 'Все',
        'unread': 'Непрочитанные',
        'read': 'Прочитанные',
        'new': 'Новое',
        'sync': 'Синхронизация',
        'settings': 'Настройки',
        'logout': 'Выйти из аккаунта',
        'welcome': 'Добро пожаловать в Planer Everyday',
        'loginPrompt': 'Войти или зарегистрироваться',
        'or': 'или',
        'email': 'Email',
        'password': 'Пароль',
        'registerViaEmail': 'Зарегистрироваться через Email',
        'agreement': 'Используя для входа Google, Яндекс, VK или Email-адрес, вы соглашаетесь с Условиями использования и Политикой конфиденциальности',
        'alreadyHaveAccount': 'Уже есть аккаунт? Тогда войдите',
        'tasksToday': 'задачи сегодня',
        'completed': 'выполнено',
        'daysInApp': 'дней в приложении',
        'lastSync': 'Последняя синхронизация:',
        'syncNow': 'Синхронизировать',
        'justNow': 'только что',
        'minutesAgo_one': 'минуту назад',
        'minutesAgo_few': 'минуты назад',
        'minutesAgo_many': 'минут назад',
        'notificationsEnabled': 'Уведомления',
        'darkTheme': 'Тёмная тема',
        'sounds': 'Звуки',
        'language': 'Язык',
        'dateFormat': 'Формат даты',
        // Календарь
        'calendar': 'Календарь задач',
        'month': 'Месяц',
        'year': 'Год',
        'weekdays_short': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
        'months': ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
        'months_short': ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'],
        // Профиль
        'profile': 'Профиль пользователя',
        'aiHelper': 'ИИ помощник',
        'reminder': 'Напоминание',
        // Чаты
        'chatPlaceholder': 'Введите сообщение... (Enter для отправки)',
        'chatWelcome': '👋 Здравствуйте! Я ваш персональный ИИ помощник. Могу помочь с задачами, напоминаниями и ответить на вопросы.',
        // Уведомления
        'notificationSuccess': '✅ Успешно',
        'notificationWarning': '⚠️ Внимание',
        'notificationError': '❌ Ошибка',
        'notificationInfo': 'ℹ️ Информация',
        // Звуки не переводим
    },
    en: {
        // General
        'appName': 'Planer EveryDay',
        'addTask': 'Add task',
        'editTask': 'Edit task',
        'deleteTask': 'Delete task',
        'confirm': 'Confirm',
        'cancel': 'Cancel',
        'close': 'Close',
        'save': 'Save',
        'today': 'Today',
        'tasks': 'tasks',
        'task': 'task',
        'tasks_plural': 'tasks',
        'noTasks': 'No tasks',
        'emptyToday': 'Nothing for today',
        'upcoming': 'Upcoming',
        'notifications': 'Notifications',
        'markAllRead': 'Mark all as read',
        'clearAll': 'Clear all',
        'all': 'All',
        'unread': 'Unread',
        'read': 'Read',
        'new': 'New',
        'sync': 'Synchronization',
        'settings': 'Settings',
        'logout': 'Log out',
        'welcome': 'Welcome to Planer Everyday',
        'loginPrompt': 'Sign in or register',
        'or': 'or',
        'email': 'Email',
        'password': 'Password',
        'registerViaEmail': 'Register via Email',
        'agreement': 'By using Google, Yandex, VK or Email to log in, you agree to the Terms of Use and Privacy Policy',
        'alreadyHaveAccount': 'Already have an account? Log in',
        'tasksToday': 'tasks today',
        'completed': 'completed',
        'daysInApp': 'days in app',
        'lastSync': 'Last sync:',
        'syncNow': 'Sync now',
        'justNow': 'just now',
        'minutesAgo_one': 'minute ago',
        'minutesAgo_other': 'minutes ago',
        'notificationsEnabled': 'Notifications',
        'darkTheme': 'Dark theme',
        'sounds': 'Sounds',
        'language': 'Language',
        'dateFormat': 'Date format',
        // Calendar
        'calendar': 'Task calendar',
        'month': 'Month',
        'year': 'Year',
        'weekdays_short': ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
        'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        'months_short': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        // Profile
        'profile': 'User profile',
        'aiHelper': 'AI assistant',
        'reminder': 'Reminder',
        // Chat
        'chatPlaceholder': 'Type a message... (Enter to send)',
        'chatWelcome': '👋 Hello! I am your personal AI assistant. I can help with tasks, reminders and answer questions.',
        // Notifications
        'notificationSuccess': '✅ Success',
        'notificationWarning': '⚠️ Warning',
        'notificationError': '❌ Error',
        'notificationInfo': 'ℹ️ Info',
    }
};

let currentLanguage = 'ru'; // язык по умолчанию

// Функция применения языка ко всем элементам с data-i18n
function applyLanguage(lang) {
    currentLanguage = lang;
    const t = translations[lang];

    // Обновляем все элементы с атрибутом data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key]) {
            el.textContent = t[key];
        }
    });

    // Обновляем плейсхолдеры
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (t[key]) {
            el.placeholder = t[key];
        }
    });

    // Обновляем дни недели в календаре
    const weekdays = document.querySelectorAll('.weekday');
    if (weekdays.length) {
        t.weekdays_short.forEach((day, index) => {
            if (weekdays[index]) weekdays[index].textContent = day;
        });
    }

    // Обновляем заголовок месяца/года в календаре (будет обновлено при renderMonth/Year)
    // Динамические обновления делаем в renderMonth/renderYear

    // Обновляем статистику профиля (текст, который зависит от числа)
    updateProfileStatsText();

    // Обновляем текст синхронизации
    updateSyncTimeText();

    // Обновляем текст количества задач в календаре и списках
    if (typeof renderTasks === 'function') renderTasks();
    if (typeof renderUpcomingTasks === 'function') renderUpcomingTasks();
    if (typeof renderMonth === 'function') renderMonth();
    if (typeof renderYear === 'function') renderYear();
}

// Функция для обновления текста статистики профиля (задачи сегодня, выполнено, дней)
function updateProfileStatsText() {
    const t = translations[currentLanguage];
    const taskCountEl = document.querySelector('.profile-stat-label[data-i18n="tasksToday"]');
    if (taskCountEl) taskCountEl.textContent = t.tasksToday;
    const completedLabel = document.querySelector('.profile-stat-label[data-i18n="completed"]');
    if (completedLabel) completedLabel.textContent = t.completed;
    const daysLabel = document.querySelector('.profile-stat-label[data-i18n="daysInApp"]');
    if (daysLabel) daysLabel.textContent = t.daysInApp;
}

// Функция для обновления текста последней синхронизации
function updateSyncTimeText() {
    const syncEl = document.getElementById('lastSyncText');
    if (!syncEl) return;
    const diff = Math.floor((Date.now() - lastSyncTime) / 1000 / 60);
    const t = translations[currentLanguage];
    let timeText = '';
    if (diff < 1) {
        timeText = t.lastSync + ' ' + t.justNow;
    } else if (diff === 1) {
        timeText = t.lastSync + ' 1 ' + (currentLanguage === 'ru' ? 'минуту назад' : 'minute ago');
    } else {
        if (currentLanguage === 'ru') {
            // Склонение для русского
            let word = 'минут';
            if (diff % 10 === 1 && diff % 100 !== 11) word = 'минуту';
            else if (diff % 10 >= 2 && diff % 10 <= 4 && (diff % 100 < 10 || diff % 100 >= 20)) word = 'минуты';
            timeText = `${t.lastSync} ${diff} ${word} назад`;
        } else {
            timeText = `${t.lastSync} ${diff} ${diff === 1 ? 'minute' : 'minutes'} ago`;
        }
    }
    syncEl.textContent = timeText;
}

// Переопределяем существующую функцию changeLanguage
window.changeLanguage = function(lang) {
    currentUser.settings.language = lang;
    applyLanguage(lang);
    addNotification(translations[lang].language + ' changed to ' + (lang === 'ru' ? 'Russian' : 'English'), 'info');
};