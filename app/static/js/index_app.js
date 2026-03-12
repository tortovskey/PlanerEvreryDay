const accessToken = localStorage.getItem('access_token') || '';
function authHeaders(){return accessToken ? {'Authorization': `Bearer ${accessToken}`} : {}};
function escapeHtml(value){return String(value).replace(/[&<>"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));}
function message(role, text){
  const div = document.createElement('div');
  div.className = `assistant-message ${role}`;
  div.textContent = text;
  document.getElementById('assistantMessages').appendChild(div);
}
function taskCard(task){
  return `<div class="task-item"><div class="task-title">${escapeHtml(task.title)}</div><div class="task-meta">${task.task_date} ${task.task_time || 'без времени'} · <span class="priority-${task.priority}">${task.priority}</span></div>${task.description ? `<div class="task-meta">${escapeHtml(task.description)}</div>` : ''}</div>`;
}
async function api(url, opts={}){
  const res = await fetch(url, {...opts, headers: {'Content-Type':'application/json', ...(opts.headers||{}), ...authHeaders()}});
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Ошибка API');
  return data;
}
async function loadDashboard(){
  const [stats, upcoming] = await Promise.all([api('/api/stats'), api('/api/tasks/upcoming?limit=8')]);
  document.getElementById('statTotal').textContent = stats.total_tasks || 0;
  document.getElementById('statDone').textContent = stats.done_tasks || 0;
  document.getElementById('statToday').textContent = stats.today_tasks || 0;
  document.getElementById('statUpcoming').textContent = stats.upcoming_tasks || 0;
  document.getElementById('statHigh').textContent = stats.high_priority_open || 0;
  const upcomingList = document.getElementById('upcomingList');
  upcomingList.className = upcoming.length ? 'task-list' : 'task-list empty-block';
  upcomingList.innerHTML = upcoming.length ? upcoming.map(taskCard).join('') : 'Ближайших задач пока нет';
}
document.getElementById('quickDate').value = new Date().toISOString().split('T')[0];
document.getElementById('quickTaskForm').addEventListener('submit', async (e)=>{
  e.preventDefault();
  const payload = {
    title: document.getElementById('quickTitle').value.trim(),
    description: document.getElementById('quickDescription').value.trim(),
    task_date: document.getElementById('quickDate').value,
    task_time: document.getElementById('quickTime').value,
    priority: document.getElementById('quickPriority').value,
    duration_minutes: document.getElementById('quickDuration').value,
  };
  const msg = document.getElementById('quickMessage');
  try {
    await api('/api/tasks', {method:'POST', body: JSON.stringify(payload)});
    msg.textContent = 'Задача сохранена';
    e.target.reset();
    document.getElementById('quickDate').value = new Date().toISOString().split('T')[0];
    document.getElementById('quickDuration').value = 60;
    await loadDashboard();
  } catch (err) { msg.textContent = err.message; }
});
document.getElementById('searchBtn').addEventListener('click', async ()=>{
  const q = document.getElementById('searchInput').value.trim();
  const box = document.getElementById('searchResults');
  if (!q) { box.className='task-list empty-block'; box.textContent='Начни вводить запрос.'; return; }
  try {
    const data = await api(`/api/tasks/search?q=${encodeURIComponent(q)}`);
    box.className = data.length ? 'task-list' : 'task-list empty-block';
    box.innerHTML = data.length ? data.map(taskCard).join('') : 'Ничего не найдено';
  } catch(err){ box.textContent = err.message; }
});
document.querySelectorAll('.prompt-btn').forEach(btn=>btn.addEventListener('click',()=>{
  document.getElementById('assistantInput').value = btn.dataset.prompt;
  document.getElementById('assistantForm').requestSubmit();
}));
document.getElementById('assistantForm').addEventListener('submit', async (e)=>{
  e.preventDefault();
  const input = document.getElementById('assistantInput');
  const text = input.value.trim();
  if (!text) return;
  message('user', text); input.value='';
  try {
    const data = await api('/api/assistant', {method:'POST', body: JSON.stringify({message:text})});
    message('bot', data.reply || 'Пустой ответ. Ассистент философствует.');
    await loadDashboard();
  } catch(err){ message('bot', err.message); }
});
message('bot','Я готов: могу создать задачу, показать задачи на сегодня и составить план дня.');
loadDashboard();
