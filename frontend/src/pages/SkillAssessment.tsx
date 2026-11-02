import { useEffect, useState } from 'react';
import { CheckCircle2, Brain, ArrowRight, RefreshCw, AlertTriangle } from 'lucide-react';
import api from '../services/api';

type Skill = {
  skill: string;
  category: string;
  current_level?: string;
  latest_score?: number;
};

type Question = {
  id: string;
  skill: string;
  topic: string;
  difficulty: string;
  question: string;
  options: string[];
  sequence: number;
};

type AssessmentResult = {
  skill: string;
  score: number;
  level: string;
  correct_answers: number;
  total_questions: number;
  weak_topics: string[];
  strong_topics: string[];
};

type SkillPriority = Skill & {
  priority: string;
  required_by_jd: boolean;
  weak_topics: string[];
};

type HistoryItem = Pick<AssessmentResult, 'skill' | 'score' | 'level'> & { created_at: string };

const SkillAssessment = () => {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [priorities, setPriorities] = useState<SkillPriority[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [assessmentId, setAssessmentId] = useState('');
  const [question, setQuestion] = useState<Question | null>(null);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [pendingSkills, setPendingSkills] = useState<string[]>([]);
  const [manualSkill, setManualSkill] = useState('');
  const [selfReportedLevel, setSelfReportedLevel] = useState<'Beginner' | 'Intermediate' | 'Advanced'>('Beginner');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const getRequestError = (requestError: any, fallback: string) => {
    if (requestError.response?.data?.detail) return requestError.response.data.detail;
    if (requestError.response?.status) return `${fallback} (HTTP ${requestError.response.status}).`;
    if (requestError.message === 'Network Error') return `${fallback} The backend is not reachable.`;
    return fallback;
  };

  const loadSkills = async () => {
    setError('');
    try {
      const response = await api.get('/skills');
      setSkills(response.data.skills);
      setSelected(response.data.skills.map((item: Skill) => item.skill));
      const priorityResponse = await api.get('/skill-profile/priorities');
      setPriorities(priorityResponse.data.skills);
      const historyResponse = await api.get('/skill-assessment/history');
      setHistory(historyResponse.data);
    } catch (requestError: any) {
      setError(getRequestError(requestError, 'Upload a resume to detect technical skills.'));
    }
  };

  useEffect(() => {
    loadSkills();
  }, []);

  const toggleSkill = (skill: string) => {
    setSelected((current) => current.includes(skill) ? current.filter((item) => item !== skill) : [...current, skill]);
  };

  const start = async (reassessment = false, requestedSkill?: string) => {
    const skill = requestedSkill || selected[0];
    if (!skill) {
      setError('Select at least one skill to assess.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const response = await api.post('/skill-assessment/start', {
        skill,
        self_reported_level: selfReportedLevel,
        reassessment,
      });
      setAssessmentId(response.data.assessment_id);
      setQuestion(response.data.question);
      setResult(null);
    } catch (requestError: any) {
      setError(getRequestError(requestError, 'Could not start the assessment.'));
    } finally {
      setLoading(false);
    }
  };

  const addManualSkill = async () => {
    const skill = manualSkill.trim();
    if (!skill) return;
    try {
      const response = await api.post('/skills', { skills: [skill] });
      setSkills(response.data.skills);
      setSelected((current) => [...new Set([...current, skill])]);
      setManualSkill('');
    } catch (requestError: any) {
      setError(getRequestError(requestError, 'Could not add that skill.'));
    }
  };

  const answer = async (option: number) => {
    if (!question || !assessmentId) return;
    setLoading(true);
    setError('');
    try {
      const response = await api.post(`/skill-assessment/${assessmentId}/answer`, {
        question_id: question.id,
        answer: option,
      });
      if (response.data.question) {
        setQuestion(response.data.question);
      } else {
          setQuestion(null);
        setResult(response.data);
        await loadSkills();
      }
    } catch (requestError: any) {
      setError(getRequestError(requestError, 'Could not submit this answer.'));
    } finally {
      setLoading(false);
    }
  };

  if (question && !result) {
    return (
      <main className="min-h-screen bg-slate-50 dark:bg-slate-900 p-6 md:p-10">
        <section className="max-w-3xl mx-auto bg-white dark:bg-slate-800 rounded-3xl p-8 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-bold uppercase text-indigo-600">{question.skill} assessment</p>
              <h1 className="text-2xl font-black mt-2">Question {question.sequence} of 10</h1>
            </div>
            <span className="px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-bold">{question.difficulty}</span>
          </div>
          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-indigo-600 transition-all" style={{ width: `${question.sequence * 10}%` }} />
          </div>
          <p className="text-xs text-slate-500">Topic: {question.topic}</p>
          <h2 className="text-xl font-bold">{question.question}</h2>
          <div className="grid gap-3">
            {question.options.map((option, index) => (
              <button key={option} disabled={loading} onClick={() => answer(index)} className="text-left p-4 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-950/30 transition-colors disabled:opacity-60">
                <span className="font-bold mr-3">{String.fromCharCode(65 + index)}.</span>{option}
              </button>
            ))}
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </section>
      </main>
    );
  }

  if (result) {
    return (
      <main className="min-h-screen bg-slate-50 dark:bg-slate-900 p-6 md:p-10">
        <section className="max-w-3xl mx-auto bg-white dark:bg-slate-800 rounded-3xl p-8 shadow-sm space-y-6">
          <div className="flex items-center gap-3 text-emerald-600"><CheckCircle2 /> Assessment complete</div>
          <h1 className="text-3xl font-black">{result.skill} result</h1>
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="rounded-2xl bg-indigo-50 p-5"><p className="text-xs font-bold uppercase text-indigo-600">Assessment-based level</p><p className="text-3xl font-black text-indigo-900 mt-2">{result.level}</p></div>
            <div className="rounded-2xl bg-slate-100 p-5"><p className="text-xs font-bold uppercase text-slate-600">Score</p><p className="text-3xl font-black mt-2">{result.score}%</p><p className="text-xs text-slate-500">{result.correct_answers} / {result.total_questions} correct</p></div>
          </div>
          <div><p className="font-bold mb-2">Strong topics</p><p className="text-slate-600">{result.strong_topics.length ? result.strong_topics.join(', ') : 'Keep practicing across topics.'}</p></div>
          <div><p className="font-bold mb-2 flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-amber-500" />Needs improvement</p><p className="text-slate-600">{result.weak_topics.length ? result.weak_topics.join(', ') : 'No weak topics detected in this attempt.'}</p></div>
          <div className="flex flex-wrap gap-3">
            {pendingSkills.length > 0 && <button onClick={() => { const [next, ...remaining] = pendingSkills; setPendingSkills(remaining); start(false, next); }} className="px-5 py-3 rounded-xl bg-indigo-600 text-white font-bold">Assess next selected skill</button>}
            <button onClick={() => { setResult(null); setQuestion(null); }} className="px-5 py-3 rounded-xl border border-slate-200 font-bold">Back to skills</button>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-900 p-6 md:p-10">
      <section className="max-w-4xl mx-auto space-y-8">
        <div><div className="inline-flex items-center gap-2 text-indigo-600 text-xs font-bold uppercase"><Brain className="w-4 h-4" /> Resume-based adaptive assessment</div><h1 className="text-3xl font-black mt-3">Verify your technical skills</h1><p className="text-slate-500 mt-2">Resume mentions are evidence to assess, not proof of proficiency. Questions adapt to your performance.</p></div>
        <div className="bg-white dark:bg-slate-800 rounded-3xl p-6 shadow-sm space-y-5">
          <div className="flex items-center justify-between"><h2 className="text-xl font-black">Skills detected from your resume</h2><button onClick={loadSkills} className="text-indigo-600"><RefreshCw className="w-4 h-4" /></button></div>
          {!skills.length && <p className="text-slate-500">No skills detected yet. Upload a resume from the dashboard, then return here.</p>}
          {priorities.length > 0 && <div className="rounded-2xl bg-slate-50 dark:bg-slate-900/40 p-4 space-y-3"><h3 className="font-bold">Assessment and JD priority</h3>{priorities.map((item) => <div key={item.skill} className="flex flex-wrap items-center justify-between gap-2 text-sm"><span className="font-semibold">{item.skill}{item.required_by_jd ? ' • required by latest JD' : ''}</span><span className={`px-2 py-1 rounded-full text-xs font-bold ${item.priority === 'High' ? 'bg-red-100 text-red-700' : item.priority === 'Medium' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}`}>{item.priority} priority</span></div>)}</div>}
          {history.length > 0 && <div className="rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-4 space-y-3"><h3 className="font-bold">Assessment history</h3>{history.slice(0, 8).map((item, index) => <div key={`${item.skill}-${item.created_at}-${index}`} className="flex items-center justify-between text-sm"><span><b>{item.skill}</b><span className="block text-xs text-slate-500">{new Date(item.created_at).toLocaleDateString()} · {item.level}</span></span><span className="font-black text-indigo-600">{item.score}%</span></div>)}</div>}
          <div className="grid sm:grid-cols-2 gap-3">
            {skills.map((item) => <label key={item.skill} className={`p-4 rounded-2xl border cursor-pointer ${selected.includes(item.skill) ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-950/30' : 'border-slate-200 dark:border-slate-700'}`}><input type="checkbox" checked={selected.includes(item.skill)} onChange={() => toggleSkill(item.skill)} className="mr-3" /><span className="font-bold">{item.skill}</span><span className="block text-xs text-slate-500 ml-6">{item.category}{item.current_level ? ` • ${item.current_level} • ${item.latest_score}%` : ''}</span></label>)}
          </div>
          <div className="flex flex-wrap gap-3">
            <input value={manualSkill} onChange={(event) => setManualSkill(event.target.value)} placeholder="Add a skill manually" className="px-4 py-3 rounded-xl border border-slate-200" />
            <button type="button" onClick={addManualSkill} className="px-4 py-3 rounded-xl border border-indigo-200 text-indigo-700 font-bold">Add skill</button>
          </div>
          <label className="block max-w-sm">
            <span className="block text-sm font-bold mb-2">How would you rate yourself?</span>
            <select value={selfReportedLevel} onChange={(event) => setSelfReportedLevel(event.target.value as typeof selfReportedLevel)} className="w-full px-4 py-3 rounded-xl border border-slate-200 bg-white">
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
            <span className="block text-xs text-slate-500 mt-1">This sets the starting question difficulty. Your final level is based on your answers.</span>
          </label>
          <button disabled={loading || !selected.length} onClick={() => { setPendingSkills(selected.slice(1)); start(); }} className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-indigo-600 text-white font-bold disabled:opacity-50">Start selected assessment <ArrowRight className="w-4 h-4" /></button>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>
      </section>
    </main>
  );
};

export default SkillAssessment;
