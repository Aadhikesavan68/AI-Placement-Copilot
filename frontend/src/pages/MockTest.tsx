import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../services/api';

const MockTest = () => {
  const { id, skill } = useParams();
  const navigate = useNavigate();
  const [test, setTest] = useState<any>(null);
  const [answers, setAnswers] = useState<number[]>([]);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id || !skill) return;
    api.post(`/learning/plans/${id}/tests/${encodeURIComponent(skill)}`).then((response) => setTest(response.data)).catch((requestError) => setError(requestError.response?.data?.detail || 'Could not start test.'));
  }, [id, skill]);

  const submit = async () => {
    if (!test || answers.length !== test.questions.length) { setError('Answer every question before submitting.'); return; }
    try { setResult((await api.post(`/learning/tests/${test.id}/submit`, { answers })).data); } catch (requestError: any) { setError(requestError.response?.data?.detail || 'Could not submit test.'); }
  };
  if (error) return <div className="p-10 text-red-600">{error}</div>;
  if (result) return <main className="max-w-2xl mx-auto p-10 text-center space-y-4"><h1 className="text-3xl font-black">Test complete</h1><p className="text-5xl font-black text-indigo-600">{result.score}%</p><p className="text-slate-500">{result.weak_topics.length ? `Review: ${result.weak_topics.join(', ')}` : 'No weak topics detected in this attempt.'}</p><button onClick={() => navigate(`/learning/${id}`)} className="px-5 py-3 rounded-xl bg-indigo-600 text-white font-bold">Back to dashboard</button></main>;
  if (!test) return <div className="p-10 text-center">Preparing mock test...</div>;
  return <main className="min-h-screen bg-slate-50 dark:bg-slate-900 p-6 md:p-10"><div className="max-w-2xl mx-auto bg-white dark:bg-slate-800 rounded-3xl p-8 space-y-6"><h1 className="text-2xl font-black">{skill} mock test</h1>{test.questions.map((question: any, index: number) => <fieldset key={question.question} className="space-y-2"><legend className="font-bold">{index + 1}. {question.question}</legend>{question.options.map((option: string, optionIndex: number) => <label key={option} className="block p-3 rounded-xl border border-slate-200 cursor-pointer"><input type="radio" name={`question-${index}`} checked={answers[index] === optionIndex} onChange={() => setAnswers((current) => { const next = [...current]; next[index] = optionIndex; return next; })} className="mr-2" />{option}</label>)}</fieldset>)}<button onClick={submit} className="w-full py-3 rounded-xl bg-indigo-600 text-white font-bold">Submit test</button></div></main>;
};

export default MockTest;
