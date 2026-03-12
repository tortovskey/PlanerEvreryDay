async function submitAuth(formId, endpoint, payloadBuilder) {
  const form = document.getElementById(formId);
  if (!form) return;
  const messageEl = document.getElementById('authMessage');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    messageEl.textContent = 'Отправляю...';
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payloadBuilder()),
    });
    const data = await res.json();
    if (!res.ok) {
      messageEl.textContent = data.error || 'Ошибка';
      return;
    }
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    messageEl.textContent = 'Готово. Перехожу в приложение...';
    window.location.href = '/index';
  });
}

submitAuth('loginForm', '/api/auth/login', () => ({
  email: document.getElementById('loginEmail').value.trim(),
  password: document.getElementById('loginPassword').value,
}));

submitAuth('registerForm', '/api/auth/register', () => ({
  display_name: document.getElementById('registerName').value.trim(),
  email: document.getElementById('registerEmail').value.trim(),
  password: document.getElementById('registerPassword').value,
}));
