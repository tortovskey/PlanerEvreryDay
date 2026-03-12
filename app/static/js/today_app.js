const todayIso = new Date().toISOString().split('T')[0];
const accessToken3 = localStorage.getItem('access_token') || '';
function headers3(){return accessToken3?{'Authorization':`Bearer ${accessToken3}`}:{}};
async function api3(url, opts={}){const res=await fetch(url,{...opts, headers:{'Content-Type':'application/json', ...(opts.headers||{}), ...headers3()}}); const data=await res.json(); if(!res.ok) throw new Error(data.error||'Ошибка API'); return data;}
function escapeHtml(v){return String(v).replace(/[&<>"]/g, ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));}
document.getElementById('todayDateTitle').textContent = `Сегодня — ${todayIso}`;
function card(task){return `<div class="task-item"><div class="task-title">${escapeHtml(task.title)}</div><div class="task-meta">${task.task_time || 'без времени'} · ${task.duration_minutes || 60} мин · <span class="priority-${task.priority}">${task.priority}</span></div>${task.description?`<div class="task-meta">${escapeHtml(task.description)}</div>`:''}<div class="task-actions"><button class="mini-btn" onclick="toggleToday(${task.id}, '${task.status==='done'?'pending':'done'}')">${task.status==='done'?'Вернуть':'Готово'}</button></div></div>`;}
window.toggleToday=async(id,status)=>{await api3(`/api/tasks/${id}/status`,{method:'PATCH', body:JSON.stringify({status})}); loadToday();};
async function loadToday(){
  const [tasks, plan] = await Promise.all([
    api3(`/api/tasks?date=${todayIso}`),
    api3('/api/assistant', {method:'POST', body: JSON.stringify({message:'спланируй день на сегодня'})})
  ]);
  document.getElementById('todayCount').textContent = `${tasks.length} задач`;
  const done = tasks.filter(t=>t.status==='done').length;
  const high = tasks.filter(t=>t.priority==='high' && t.status!=='done').length;
  const percent = tasks.length ? Math.round(done/tagsafe(tasks.length)*100) : 0;
  document.getElementById('progressText').textContent = `${percent}%`;
  document.getElementById('progressFill').style.width = `${percent}%`;
  document.getElementById('todayStats').textContent = `${high} важных открытых`;
  document.getElementById('focusTip').textContent = plan.reply || 'Пусто';
  const list = document.getElementById('todayTasks');
  list.className = tasks.length ? 'task-list' : 'task-list empty-block';
  list.innerHTML = tasks.length ? tasks.map(card).join('') : 'На сегодня задач пока нет';
}
function tagsafe(n){return n||1}
loadToday();
