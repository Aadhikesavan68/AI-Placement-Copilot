import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { CheckCircle2, Circle, Clock3, Target, Trophy } from 'lucide-react';
import api from '../services/api';

const LearningDashboard = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [plan, setPlan] = useState<any>(null);
  const [error, setError] = useState('');

  const load = async () => {
    try { setPlan((await api.get(`/learning/plans/${id}`)).data); }
    catch (requestError: any) { setError(requestError.response?.data?.detail || 'Could not load learning plan.'); }
  };
  useEffect(() => { if (id) load(); }, [id]);

  const updateTask = async (task: any) => {
    const status = task.status === 'completed' ? 'started' : 'completed';
    const response = await api.patch(`/learning/plans/${id}/tasks/${task.id}`, { status, actual_minutes: status === 'completed' ? task.planned_minutes : task.actual_minutes });
    setPlan(response.data);
  };

  if (error) return <div className="p-10 text-red-600">{error}</div>;
  if (!plan) return <div className="p-10 text-center">Loading adaptive plan...</div>;
  const grouped: Record<string, any[]> = plan.tasks.reduce((groups: Record<string, any[]>, task: any) => { (groups[task.date] ||= []).push(task); return groups; }, {});

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-900 p-6 md:p-10">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex flex-col md:flex-row justify-between gap-4">
          <div><p className="text-xs font-bold uppercase text-indigo-600">Adaptive Skill Learning</p><h1 className="text-3xl font-black mt-2">Your learning dashboard</h1><p className="text-slate-500 mt-1">{plan.start_date} to {plan.target_date} · {plan.daily_minutes} minutes on selected days</p></div>
          <button onClick={() => navigate(`/learning/setup?analysisId=${plan.analysis_id}`)} className="px-4 py-2 h-fit rounded-xl border border-indigo-200 text-indigo-700 font-bold">Create another plan</button>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[[Target, 'Progress', `${plan.progress_percent}%`], [Clock3, 'Completed time', `${plan.completed_minutes} min`], [Trophy, 'Streak', `${plan.streak_days} day${plan.streak_days === 1 ? '' : 's'}`], [CheckCircle2, 'Planned time', `${plan.total_planned_minutes} min`]].map(([Icon, label, value]: any) => <div key={label} className="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200 dark:border-slate-700"><Icon className="w-5 h-5 text-indigo-600" /><p className="text-xs text-slate-500 mt-3">{label}</p><p className="text-2xl font-black mt-1">{value}</p></div>)}
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700"><h2 className="font-bold mb-4">Skill progress</h2><div className="space-y-4">{plan.skills.map((skill: any) => <div key={skill.skill}><div className="flex justify-between text-sm font-semibold"><span>{skill.skill}</span><span>{skill.confidence}%</span></div><div className="h-2 bg-slate-100 rounded-full mt-2"><div className="h-2 bg-indigo-600 rounded-full" style={{ width: `${skill.confidence}%` }} /></div><p className="text-xs text-slate-500 mt-1">{skill.difficulty} · {skill.estimated_hours} estimated hours</p><button onClick={() => navigate(`/learning/${id}/test/${encodeURIComponent(skill.skill)}`)} className="text-xs text-indigo-600 font-bold mt-2">Take skill mock test</button></div>)}</div></div>
        <section><h2 className="text-xl font-bold mb-4">Daily tasks</h2><div className="space-y-4">{Object.entries(grouped).map(([date, tasks]) => <div key={date} className="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200 dark:border-slate-700"><h3 className="font-bold mb-3">{date}</h3>{tasks.map((task: any) => <button key={task.id} onClick={() => updateTask(task)} className="w-full flex items-center justify-between text-left p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50"><span className="flex items-center gap-3">{task.status === 'completed' ? <CheckCircle2 className="text-emerald-500" /> : <Circle className="text-slate-300" />}<span><b>{task.skill}</b><span className="block text-xs text-slate-500">{task.description}</span></span></span><span className="text-xs text-slate-500">{task.planned_minutes} min</span></button>)}</div>)}</div></section>
      </div>
    </main>
  );
};

export default LearningDashboard;
