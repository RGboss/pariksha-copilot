import React, { useState, useEffect } from 'react';
import { 
  CheckSquare, 
  Square, 
  Plus, 
  Trash2, 
  Flame, 
  Target, 
  Clock, 
  Play, 
  Pause, 
  RotateCcw, 
  CheckCircle2, 
  AlertCircle,
  Calendar,
  Sparkles
} from 'lucide-react';

export default function DailyPlanner({ token, targetExam }) {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({ total_tasks: 0, completed_tasks: 0, completion_rate: 0, streak_days: 4 });
  const [loading, setLoading] = useState(false);

  // New Task Form
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState('Revision');
  const [newPriority, setNewPriority] = useState('High');

  // Pomodoro Focus Timer State
  const [pomoMinutes, setPomoMinutes] = useState(25);
  const [pomoSeconds, setPomoSeconds] = useState(0);
  const [pomoActive, setPomoActive] = useState(false);
  const [pomoMode, setPomoMode] = useState('focus'); // 'focus' (25m) or 'break' (5m)

  const fetchPlannerData = async () => {
    setLoading(true);
    try {
      const [tasksRes, statsRes] = await Promise.all([
        fetch('/api/planner/tasks', { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch('/api/planner/stats', { headers: { 'Authorization': `Bearer ${token}` } })
      ]);
      if (tasksRes.ok) {
        const tData = await tasksRes.json();
        setTasks(tData.tasks || []);
      }
      if (statsRes.ok) {
        const sData = await statsRes.json();
        setStats(sData);
      }
    } catch (err) {
      console.error('Failed to load planner data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlannerData();
  }, []);

  // Pomodoro Timer Effect
  useEffect(() => {
    let interval = null;
    if (pomoActive) {
      interval = setInterval(() => {
        if (pomoSeconds > 0) {
          setPomoSeconds(prev => prev - 1);
        } else if (pomoMinutes > 0) {
          setPomoMinutes(prev => prev - 1);
          setPomoSeconds(59);
        } else {
          // Timer finished
          setPomoActive(false);
          if (pomoMode === 'focus') {
            setPomoMode('break');
            setPomoMinutes(5);
            setPomoSeconds(0);
          } else {
            setPomoMode('focus');
            setPomoMinutes(25);
            setPomoSeconds(0);
          }
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [pomoActive, pomoMinutes, pomoSeconds, pomoMode]);

  const handleAddTask = async (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    try {
      const res = await fetch('/api/planner/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: newTitle.trim(),
          category: newCategory,
          priority: newPriority
        })
      });
      if (res.ok) {
        setNewTitle('');
        await fetchPlannerData();
      }
    } catch (err) {
      console.error('Task creation failed:', err);
    }
  };

  const handleToggleTask = async (taskId) => {
    try {
      const res = await fetch(`/api/planner/tasks/${taskId}/toggle`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        await fetchPlannerData();
      }
    } catch (err) {
      console.error('Toggle failed:', err);
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      const res = await fetch(`/api/planner/tasks/${taskId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        await fetchPlannerData();
      }
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const resetTimer = (mode) => {
    setPomoActive(false);
    setPomoMode(mode);
    setPomoMinutes(mode === 'focus' ? 25 : 5);
    setPomoSeconds(0);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-400/10 text-emerald-400 border border-emerald-400/20 mb-2">
            <Target className="w-3.5 h-3.5" />
            <span>Daily Discipline & Habit Tracker</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100">Study Planner & Focus Desk</h2>
          <p className="text-xs text-slate-400 mt-1">
            Track daily syllabus milestones, active revision tasks, and structured Pomodoro deep-work blocks.
          </p>
        </div>

        {/* Study Streak Badge */}
        <div className="flex items-center space-x-3 bg-slate-950 border border-slate-800 rounded-2xl p-3 px-4">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Flame className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400">Preparation Streak</div>
            <div className="text-base font-bold text-amber-300 font-mono">
              {stats.streak_days || 4} Days Consecutive
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Daily Revision Checklist */}
        <div className="lg:col-span-2 space-y-6">
          {/* New Task Form */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
              <CheckSquare className="w-4 h-4 text-amber-400" />
              <span>Add Revision Milestone</span>
            </h3>

            <form onSubmit={handleAddTask} className="space-y-3">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="e.g. Master Indian Polity Articles 14 to 32 & case laws"
                  value={newTitle}
                  onChange={e => setNewTitle(e.target.value)}
                  className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-amber-500"
                />
                <button
                  type="submit"
                  className="px-4 py-2.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 inline-flex items-center space-x-1.5 transition-all shrink-0"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Task</span>
                </button>
              </div>

              <div className="flex items-center gap-3 text-xs">
                <div className="flex items-center space-x-1.5">
                  <span className="text-slate-400 text-[11px]">Category:</span>
                  <select
                    value={newCategory}
                    onChange={e => setNewCategory(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-slate-200 text-xs focus:outline-none focus:border-amber-500"
                  >
                    <option value="Revision">Revision</option>
                    <option value="PYQ Practice">PYQ Practice</option>
                    <option value="Answer Writing">Answer Writing</option>
                    <option value="Current Affairs">Current Affairs</option>
                    <option value="Mock Test">Mock Test</option>
                  </select>
                </div>

                <div className="flex items-center space-x-1.5">
                  <span className="text-slate-400 text-[11px]">Priority:</span>
                  <select
                    value={newPriority}
                    onChange={e => setNewPriority(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-slate-200 text-xs focus:outline-none focus:border-amber-500"
                  >
                    <option value="High">High Priority</option>
                    <option value="Medium">Medium Priority</option>
                    <option value="Low">Low Priority</option>
                  </select>
                </div>
              </div>
            </form>
          </div>

          {/* Tasks List */}
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400 px-1">
              <span>Today's Milestones ({tasks.length})</span>
              <span>{stats.completed_tasks} / {stats.total_tasks} Completed</span>
            </div>

            {loading ? (
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-8 text-center text-slate-400 text-xs animate-pulse">
                Loading tasks...
              </div>
            ) : tasks.length === 0 ? (
              <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-8 text-center space-y-2">
                <Calendar className="w-8 h-8 mx-auto text-slate-600" />
                <div className="text-xs font-semibold text-slate-300">No Pending Tasks</div>
                <div className="text-[11px] text-slate-500">Add high-yield syllabus tasks above to structure your day.</div>
              </div>
            ) : (
              <div className="space-y-2">
                {tasks.map(t => (
                  <div
                    key={t.id}
                    className={`group bg-slate-900 border rounded-xl p-3.5 flex items-center justify-between transition-all ${
                      t.is_completed
                        ? 'border-slate-800/60 opacity-60 bg-slate-950/40'
                        : 'border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3 flex-1 min-w-0 pr-3">
                      <button
                        onClick={() => handleToggleTask(t.id)}
                        className="text-slate-400 hover:text-amber-400 transition-colors shrink-0"
                      >
                        {t.is_completed ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                        ) : (
                          <Square className="w-5 h-5 text-slate-600" />
                        )}
                      </button>

                      <div className="min-w-0 flex-1">
                        <div
                          className={`text-xs md:text-sm font-medium truncate ${
                            t.is_completed ? 'line-through text-slate-400' : 'text-slate-200'
                          }`}
                        >
                          {t.title}
                        </div>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                            {t.category}
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                              t.priority === 'High'
                                ? 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
                                : t.priority === 'Medium'
                                ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                                : 'bg-slate-800 text-slate-400'
                            }`}
                          >
                            {t.priority}
                          </span>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => handleDeleteTask(t.id)}
                      className="text-slate-600 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-all p-1.5"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Col: Pomodoro Timer & Progress Stats */}
        <div className="space-y-6">
          {/* Pomodoro Focus Timer */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6 text-center">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
                <Clock className="w-4 h-4 text-amber-400" />
                <span>Deep Work Focus</span>
              </span>

              <div className="flex space-x-1">
                <button
                  onClick={() => resetTimer('focus')}
                  className={`px-2.5 py-1 rounded-lg text-[10px] font-bold ${
                    pomoMode === 'focus' ? 'bg-amber-500 text-slate-950' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  25m Focus
                </button>
                <button
                  onClick={() => resetTimer('break')}
                  className={`px-2.5 py-1 rounded-lg text-[10px] font-bold ${
                    pomoMode === 'break' ? 'bg-emerald-500 text-slate-950' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  5m Break
                </button>
              </div>
            </div>

            {/* Timer Digits */}
            <div className="py-4">
              <div className="text-5xl font-black font-mono text-slate-100 tracking-wider">
                {pomoMinutes.toString().padStart(2, '0')}:{pomoSeconds.toString().padStart(2, '0')}
              </div>
              <div className="text-xs text-slate-400 mt-2 font-medium">
                {pomoMode === 'focus' ? '🎯 High-Concentration Study Block' : '☕ Rest & Hydration Interval'}
              </div>
            </div>

            {/* Timer Controls */}
            <div className="flex items-center justify-center space-x-3">
              <button
                onClick={() => setPomoActive(!pomoActive)}
                className={`px-6 py-2.5 rounded-xl text-xs font-bold inline-flex items-center space-x-2 transition-all shadow-md ${
                  pomoActive
                    ? 'bg-amber-500 hover:bg-amber-400 text-slate-950'
                    : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950'
                }`}
              >
                {pomoActive ? (
                  <>
                    <Pause className="w-4 h-4" />
                    <span>Pause Session</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    <span>Start Focus</span>
                  </>
                )}
              </button>

              <button
                onClick={() => resetTimer(pomoMode)}
                className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Daily Progress Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Syllabus Completion Index
            </h4>

            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300">Daily Milestone Target:</span>
              <span className="font-bold text-amber-400 font-mono">{stats.completion_rate}%</span>
            </div>

            <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-800">
              <div
                className="h-full bg-gradient-to-r from-amber-500 to-emerald-400 transition-all duration-700"
                style={{ width: `${stats.completion_rate}%` }}
              />
            </div>

            <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-500 leading-relaxed">
              Discipline benchmark: Consistently completing &gt;75% of scheduled daily tasks correlates directly with Prelims clearance.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
