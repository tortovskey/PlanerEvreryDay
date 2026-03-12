const accessToken5 = localStorage.getItem('access_token') || '';
function headers5(){return accessToken5?{'Authorization':`Bearer ${accessToken5}`}:{}};
async function api5(url, opts={}){const res=await fetch(url,{...opts, headers:{'Content-Type':'application/json', ...(opts.headers||{}), ...headers5()}}); const data=await res.json(); if(!res.ok) throw new Error(data.error||'Ошибка API'); return data;}
document.getElementById('profileForm').addEventListener('submit', async (e)=>{
  e.preventDefault();
  const payload = {
    display_name: document.getElementById('profileName').value.trim(),
    avatar_url: document.getElementById('profileAvatar').value.trim(),
  };
  const msg = document.getElementById('profileMessage');
  try {
    await api5('/api/profile', {method:'PUT', body: JSON.stringify(payload)});
    msg.textContent = 'Профиль сохранён. Перезагрузи страницу, чтобы увидеть обновление в шапке.';
  } catch (err) { msg.textContent = err.message; }
});
