import { FormEvent, useCallback, useEffect, useState } from 'react'
import { api, Task, User } from './api'

type Session = { token: string; user: User }
type TaskView = 'mine' | 'all'

const seededAccessibilityDefects = import.meta.env.VITE_SEEDED_ACCESSIBILITY_DEFECTS === 'true'

function readSession(): Session | null {
  const raw = localStorage.getItem('workboard-session')
  if (!raw) return null
  try {
    return JSON.parse(raw) as Session
  } catch {
    localStorage.removeItem('workboard-session')
    return null
  }
}

export default function App() {
  const [session, setSession] = useState<Session | null>(readSession)
  const [registering, setRegistering] = useState(false)
  const [email, setEmail] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [profileName, setProfileName] = useState('')
  const [password, setPassword] = useState('')
  const [tasks, setTasks] = useState<Task[]>([])
  const [taskView, setTaskView] = useState<TaskView>('mine')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [search, setSearch] = useState('')
  const [state, setState] = useState('all')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)

  const loadTasks = useCallback(async () => {
    if (!session) return
    try {
      const result = taskView === 'all' && session.user.role === 'admin'
        ? await api.allTasks(session.token)
        : await api.tasks(session.token, search, state)
      setTasks(result)
      setError('')
    } catch (reason) {
      if (reason instanceof Error && reason.message === 'Invalid or expired token') {
        localStorage.removeItem('workboard-session')
        setSession(null)
        setTasks([])
        setMessage('Your session expired. Please sign in again.')
        return
      }
      setError(reason instanceof Error ? reason.message : 'Unable to load tasks')
    }
  }, [session, search, state, taskView])

  useEffect(() => {
    void loadTasks()
  }, [loadTasks])

  useEffect(() => {
    setProfileName(session?.user.display_name ?? '')
  }, [session])

  function saveSession(next: Session) {
    localStorage.setItem('workboard-session', JSON.stringify(next))
    setSession(next)
  }

  async function authenticate(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const result = registering
        ? await api.register(email, displayName, password)
        : await api.login(email, password)
      saveSession({ token: result.access_token, user: result.user })
      setPassword('')
      setMessage(`Welcome, ${result.user.display_name}`)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Authentication failed')
    } finally {
      setBusy(false)
    }
  }

  async function saveProfile(event: FormEvent) {
    event.preventDefault()
    if (!session) return
    setBusy(true)
    setError('')
    try {
      const user = await api.updateProfile(session.token, profileName)
      saveSession({ ...session, user })
      setMessage('Profile updated')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to update profile')
    } finally {
      setBusy(false)
    }
  }

  async function addTask(event: FormEvent) {
    event.preventDefault()
    if (!session) return
    setBusy(true)
    setError('')
    try {
      await api.createTask(session.token, title, description)
      setTitle('')
      setDescription('')
      setMessage('Task created')
      await loadTasks()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to create task')
    } finally {
      setBusy(false)
    }
  }

  async function toggleTask(task: Task) {
    if (!session) return
    try {
      await api.updateTask(session.token, task.id, { completed: !task.completed })
      setMessage(task.completed ? 'Task reopened' : 'Task completed')
      await loadTasks()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to update task')
    }
  }

  async function editTask(task: Task) {
    if (!session) return
    const nextTitle = window.prompt('Task title', task.title)
    if (nextTitle === null) return
    const nextDescription = window.prompt('Task description', task.description)
    if (nextDescription === null) return
    try {
      await api.updateTask(session.token, task.id, { title: nextTitle, description: nextDescription })
      setMessage('Task updated')
      await loadTasks()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to update task')
    }
  }

  async function removeTask(task: Task) {
    if (!session || !window.confirm(`Delete "${task.title}"?`)) return
    try {
      await api.deleteTask(session.token, task.id)
      setMessage('Task deleted')
      await loadTasks()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to delete task')
    }
  }

  function logout() {
    localStorage.removeItem('workboard-session')
    setSession(null)
    setTasks([])
    setTaskView('mine')
    setMessage('Signed out')
  }

  const feedback = error
    ? <div className="alert error" role={seededAccessibilityDefects ? undefined : 'alert'}>{error}</div>
    : message
      ? <div className="alert success" role={seededAccessibilityDefects ? undefined : 'status'}>{message}</div>
      : null

  if (!session) {
    return (
      <main className={`auth-shell ${seededAccessibilityDefects ? 'seeded-focus-defect' : ''}`}>
        <section className="card auth-card">
          <p className="eyebrow">WorkBoard</p>
          <h1>{registering ? 'Create your account' : 'Welcome back'}</h1>
          <p>Manage a focused list of work from one place.</p>
          {feedback}
          <form onSubmit={authenticate}>
            {registering && <label>Display name<input data-testid="display-name" value={displayName} onChange={(event) => setDisplayName(event.target.value)} minLength={2} required /></label>}
            <label>Email<input data-testid="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
            <label>Password<input data-testid="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required /></label>
            <button data-testid="auth-submit" disabled={busy}>{busy ? 'Please wait...' : registering ? 'Create account' : 'Sign in'}</button>
          </form>
          <button data-testid="toggle-auth-mode" className="link-button" onClick={() => setRegistering((value) => !value)}>
            {registering ? 'Already have an account? Sign in' : 'Need an account? Register'}
          </button>
        </section>
      </main>
    )
  }

  const canChangeTask = (task: Task) => task.owner_id === session.user.id

  return (
    <div className={`app-shell ${seededAccessibilityDefects ? 'seeded-focus-defect' : ''}`}>
      <header>
        <div><p className="eyebrow">WorkBoard</p><h1>{taskView === 'all' ? 'Team tasks' : 'Your tasks'}</h1></div>
        <div className="profile"><span>{session.user.display_name} · {session.user.role}</span><button className="secondary" onClick={logout}>Sign out</button></div>
      </header>
      <main className="workspace">
        <aside className="sidebar-stack">
          <section className="card composer">
            <h2>Create a task</h2>
            {feedback}
            <form onSubmit={addTask}>
              <label>Title<input data-testid="task-title" value={title} onChange={(event) => setTitle(event.target.value)} maxLength={120} required /></label>
              <label>Description<textarea data-testid="task-description" value={description} onChange={(event) => setDescription(event.target.value)} maxLength={1000} /></label>
              <button data-testid="create-task" disabled={busy}>Add task</button>
            </form>
          </section>
          <section className="card profile-card">
            <h2>Profile</h2>
            <form onSubmit={saveProfile}>
              <label>Display name<input data-testid="profile-name" value={profileName} onChange={(event) => setProfileName(event.target.value)} minLength={2} required /></label>
              <button className="secondary" disabled={busy}>Save profile</button>
            </form>
          </section>
        </aside>
        <section className="task-area">
          {session.user.role === 'admin' && (
            <div className="view-switcher" aria-label="Task view">
              <button className={taskView === 'mine' ? '' : 'secondary'} onClick={() => setTaskView('mine')}>My tasks</button>
              <button className={taskView === 'all' ? '' : 'secondary'} onClick={() => setTaskView('all')}>All users' tasks</button>
            </div>
          )}
          {taskView === 'mine' ? (
            <div className="toolbar">
              {seededAccessibilityDefects ? (
                <div><span className="field-text">Search tasks</span><input className="seeded-low-contrast" data-testid="task-search" type="search" placeholder="Search" value={search} onChange={(event) => setSearch(event.target.value)} /></div>
              ) : (
                <label>Search tasks<input data-testid="task-search" type="search" value={search} onChange={(event) => setSearch(event.target.value)} /></label>
              )}
              <label>Status<select data-testid="task-filter" value={state} onChange={(event) => setState(event.target.value)}><option value="all">All</option><option value="active">Active</option><option value="completed">Completed</option></select></label>
            </div>
          ) : <p className="view-note">Administrator oversight is read-only for tasks owned by other users.</p>}
          <div className="task-list" data-testid="task-list">
            {tasks.length === 0 ? <div className="empty"><h2>No tasks found</h2><p>Create a task or change the current filters.</p></div> : tasks.map((task) => (
              <article className={`card task ${task.completed ? 'done' : ''}`} key={task.id}>
                <div>
                  {seededAccessibilityDefects ? <h3>{task.title}</h3> : <h2>{task.title}</h2>}
                  {task.owner_name && <p className="owner">Owner: {task.owner_name} ({task.owner_email})</p>}
                  <p>{task.description || 'No description'}</p>
                </div>
                {canChangeTask(task) && (
                  <div className="task-actions">
                    <button className="secondary" onClick={() => void toggleTask(task)}>{task.completed ? 'Reopen' : 'Complete'}</button>
                    <button className="secondary" onClick={() => void editTask(task)}>Edit</button>
                    {seededAccessibilityDefects ? (
                      <button className="danger" onClick={() => void removeTask(task)}><span aria-hidden="true">×</span></button>
                    ) : (
                      <button className="danger" onClick={() => void removeTask(task)}>Delete</button>
                    )}
                  </div>
                )}
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}
