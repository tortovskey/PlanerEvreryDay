const accessToken4 = localStorage.getItem('access_token') || '';
function headers4(){return accessToken4?{'Authorization':`Bearer ${accessToken4}`}:{}};
async function api4(url, opts={}){const res=await fetch(url,{...opts, headers:{'Content-Type':'application/json', ...(opts.headers||{}), ...headers4()}}); const data=await res.json(); if(!res.ok) throw new Error(data.error||'Ошибка API'); return data;}
async function initSettings(){
  const data = await api4('/api/settings');
  document.getElementById('settingsTheme').value = data.theme || 'nebula';
  document.getElementById('settingsTimezone').value = data.timezone || 'Europe/Paris';
  document.getElementById('settingsStartHour').value = data.start_hour || 9;
  document.getElementById('settingsEndHour').value = data.end_hour || 18;
  document.getElementById('settingsFocusMinutes').value = data.focus_minutes || 50;
  document.getElementById('settingsBreakMinutes').value = data.break_minutes || 10;
  document.getElementById('settingsEmailNotifications').checked = !!data.email_notifications;
  document.getElementById('settingsWeeklyDigest').checked = !!data.weekly_digest;
  document.getElementById('settingsAiMode').value = data.ai_mode || 'planner';
}
document.getElementById('settingsForm').addEventListener('submit', async (e)=>{
  e.preventDefault();
  const payload = {
    theme: document.getElementById('settingsTheme').value,
    timezone: document.getElementById('settingsTimezone').value,
    start_hour: Number(document.getElementById('settingsStartHour').value),
    end_hour: Number(document.getElementById('settingsEndHour').value),
    focus_minutes: Number(document.getElementById('settingsFocusMinutes').value),
    break_minutes: Number(document.getElementById('settingsBreakMinutes').value),
    email_notifications: document.getElementById('settingsEmailNotifications').checked,
    weekly_digest: document.getElementById('settingsWeeklyDigest').checked,
    ai_mode: document.getElementById('settingsAiMode').value,
  };
  const msg = document.getElementById('settingsMessage');
  try {
    await api4('/api/settings', {method:'PUT', body: JSON.stringify(payload)});
    localStorage.setItem('planner_theme', payload.theme);
    document.documentElement.setAttribute('data-theme', payload.theme);
    msg.textContent = 'Настройки сохранены';
  } catch (err) { msg.textContent = err.message; }
});
initSettings();
