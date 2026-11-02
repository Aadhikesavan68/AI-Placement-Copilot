import { useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CalendarDays, Clock3, Sparkles } from 'lucide-react';
import api from '../services/api';

const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const LearningSetup = () => {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const analysisId = params.get('analysisId') || '';
  const [dailyMinutes, setDailyMinutes] = useState(60);
  const [days, setDays] = useState([0, 1, 2, 3, 4, 5]);
  const [startDate, setStartDate] = useState(new Date().toISOString().slice(0, 10));
  const [targetDate, setTargetDate] = useState(() => {
    const target = new Date();
    target.setDate(target.getDate() + 28);
    return target.toISOString().slice(0, 10);
  });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const toggleDay = (day: number) => {
    setDays((current) => current.includes(day) ? current.filter((value) => value !== day) : [...current, day].sort());
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    if (!analysisId) {
      setError('Open this setup from an analysis so missing skills can be used.');
      return;
    }
    if (!days.length) {
      setError('Select at least one learning day.');
      return;
    }
    setSaving(true);
    try {
      const response = await api.post('/learning/plans', {
        analysis_id: analysisId,
        daily_minutes: dailyMinutes,
        learning_days: days,
        start_date: startDate,
        target_date: targetDate,
      });
      navigate(`/learning/${response.data.id}`);
    } catch (requestError: any) {
      if (requestError.response?.status === 409) {
        try {
          const existing = await api.get(`/learning/plans/by-analysis/${analysisId}`);
          navigate(`/learning/${existing.data.id}`);
          return;
        } catch {
          // Keep the original API error below when the existing plan cannot be loaded.
        }
      }
      const detail = requestError.response?.data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((item: any) => item.msg).join(', ')
        : detail;
      setError(message || `Could not create your learning plan (${requestError.response?.status || 'network error'}).`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-900 p-6 md:p-10">
      <form onSubmit={submit} className="max-w-3xl mx-auto bg-white dark:bg-slate-800 rounded-3xl p-8 shadow-sm border border-slate-200 dark:border-slate-700 space-y-8">
        <div>
          <div className="inline-flex items-center gap-2 text-indigo-600 text-xs font-bold uppercase"><Sparkles className="w-4 h-4" /> Adaptive Skill Learning & Progress Tracker</div>
          <h1 className="text-3xl font-black mt-3">Personalize your learning plan</h1>
          <p className="text-slate-500 mt-2">Your plan uses only the time and days you choose. It can be updated after each task or mock test.</p>
        </div>
        <label className="block">
          <span className="flex items-center gap-2 font-bold mb-2"><Clock3 className="w-4 h-4 text-indigo-600" /> Daily learning time</span>
          <div className="flex flex-wrap gap-2">
            {[30, 60, 120, 180].map((minutes) => (
              <button type="button" key={minutes} onClick={() => setDailyMinutes(minutes)} className={`px-4 py-2 rounded-xl border text-sm font-semibold ${dailyMinutes === minutes ? 'bg-indigo-600 text-white border-indigo-600' : 'border-slate-200 text-slate-600'}`}>{minutes >= 60 ? `${minutes / 60} hour${minutes > 60 ? 's' : ''}` : `${minutes} minutes`}</button>
            ))}
            <input aria-label="Custom daily minutes" type="number" min="15" max="720" value={dailyMinutes} onChange={(event) => setDailyMinutes(Number(event.target.value))} className="w-28 px-3 py-2 rounded-xl border border-slate-200" />
          </div>
        </label>
        <fieldset>
          <legend className="font-bold mb-3">Learning days</legend>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {weekdays.map((day, index) => (
              <label key={day} className={`cursor-pointer p-3 rounded-xl border text-sm ${days.includes(index) ? 'bg-indigo-50 border-indigo-400 text-indigo-700' : 'border-slate-200 text-slate-600'}`}>
                <input type="checkbox" checked={days.includes(index)} onChange={() => toggleDay(index)} className="mr-2" />{day}
              </label>
            ))}
          </div>
        </fieldset>
        <div className="grid sm:grid-cols-2 gap-4">
          <label className="font-bold"><span className="flex items-center gap-2 mb-2"><CalendarDays className="w-4 h-4 text-indigo-600" /> Start date</span><input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} className="w-full px-3 py-2 rounded-xl border border-slate-200" /></label>
          <label className="font-bold"><span className="flex items-center gap-2 mb-2"><CalendarDays className="w-4 h-4 text-indigo-600" /> Target completion date</span><input type="date" value={targetDate} onChange={(event) => setTargetDate(event.target.value)} className="w-full px-3 py-2 rounded-xl border border-slate-200" /></label>
        </div>
        {error && <p className="text-sm text-red-600 bg-red-50 rounded-xl p-3">{error}</p>}
        <button disabled={saving} className="w-full py-3 rounded-xl bg-indigo-600 text-white font-bold disabled:opacity-60">{saving ? 'Building adaptive plan...' : 'Generate adaptive roadmap'}</button>
      </form>
    </main>
  );
};

export default LearningSetup;
