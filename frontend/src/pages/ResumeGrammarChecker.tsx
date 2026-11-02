import { useState } from 'react';
import { Check, CheckCircle2, Download, FileText, Loader2, RotateCcw, Sparkles, Upload, X } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../services/api';

interface Correction {
  id: string;
  before: string;
  after: string;
  category: 'grammar' | 'spelling';
  message: string;
  accepted: boolean;
}

interface AnalysisResult {
  id: string;
  original_filename: string;
  total_sentences: number;
  grammar_issue_count: number;
  spelling_issue_count: number;
  corrected_sentence_count: number;
  correction_summary: string;
  original_text: string;
  corrected_text: string;
  corrections: Correction[];
}

const ResumeGrammarChecker = () => {
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const chooseFile = (selected: File | undefined) => {
    if (!selected) return;
    if (!['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(selected.type) && !/\.(pdf|docx)$/i.test(selected.name)) {
      toast.error('Upload a PDF or DOCX resume');
      return;
    }
    if (selected.size > 10 * 1024 * 1024) {
      toast.error('Resume must be smaller than 10 MB');
      return;
    }
    setFile(selected);
    setAnalysis(null);
  };

  const analyze = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/resume-grammar/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setAnalysis(response.data);
      toast.success('Resume analysis completed');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Could not analyze this resume');
    } finally {
      setLoading(false);
    }
  };

  const updateCorrection = async (id: string, accepted: boolean, after?: string) => {
    if (!analysis) return;
    const corrections = analysis.corrections.map((item) => item.id === id ? { ...item, accepted, after: after ?? item.after } : item);
    try {
      const response = await api.post(`/resume-grammar/${analysis.id}/review`, { corrections });
      setAnalysis({ ...analysis, ...response.data });
    } catch {
      toast.error('Could not save this review decision');
    }
  };

  const acceptAll = async () => {
    if (!analysis) return;
    const corrections = analysis.corrections.map((item) => ({ ...item, accepted: true }));
    try {
      const response = await api.post(`/resume-grammar/${analysis.id}/review`, { corrections });
      setAnalysis({ ...analysis, ...response.data });
      toast.success('All corrections accepted');
    } catch {
      toast.error('Could not save your review');
    }
  };

  const download = async () => {
    if (!analysis) return;
    setDownloading(true);
    try {
      const response = await api.post(`/resume-grammar/${analysis.id}/generate-pdf`, {}, { responseType: 'blob' });
      const url = URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${analysis.original_filename.replace(/\.(pdf|docx)$/i, '')}_Corrected_Resume.pdf`;
      link.click();
      URL.revokeObjectURL(url);
      toast.success('Your corrected resume is ready');
    } catch {
      toast.error('Could not generate the corrected PDF');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-900 p-6 md:p-10 text-slate-900 dark:text-slate-50">
      <div className="max-w-6xl mx-auto space-y-8">
        <header className="space-y-2">
          <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
            <Sparkles className="w-4 h-4" /> AI writing review
          </div>
          <h1 className="text-3xl font-black">AI Resume Grammar Checker</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Review grammar and spelling improvements before generating your interview-ready PDF.</p>
        </header>

        <section className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 space-y-5">
          <label className="flex min-h-32 cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-600 hover:border-emerald-500 transition-colors">
            <Upload className="w-7 h-7 text-emerald-600" />
            <span className="text-sm font-bold">Upload PDF or DOCX resume</span>
            <span className="text-xs text-slate-400">Maximum 10 MB</span>
            <input type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" className="hidden" onChange={(event) => chooseFile(event.target.files?.[0])} />
          </label>
          {file && (
            <div className="flex items-center justify-between rounded-xl bg-slate-50 dark:bg-slate-900 p-3 text-xs">
              <span className="flex items-center gap-2 font-semibold"><FileText className="w-4 h-4 text-indigo-500" /> {file.name} <span className="font-normal text-slate-400">({(file.size / 1024).toFixed(0)} KB)</span></span>
              <button type="button" title="Remove file" onClick={() => { setFile(null); setAnalysis(null); }} className="text-slate-400 hover:text-red-500"><X className="w-4 h-4" /></button>
            </div>
          )}
          <button type="button" onClick={analyze} disabled={!file || loading} className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-3 text-sm font-bold text-white disabled:opacity-50">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {loading ? 'Analyzing resume...' : 'Analyze Resume'}
          </button>
        </section>

        {analysis && (
          <>
            <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                ['Sentences analyzed', analysis.total_sentences],
                ['Grammar issues', analysis.grammar_issue_count],
                ['Spelling issues', analysis.spelling_issue_count],
                ['Corrections', analysis.corrections.length],
              ].map(([label, value]) => <div key={label} className="rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-4"><p className="text-xs text-slate-500">{label}</p><p className="mt-1 text-2xl font-black text-indigo-600">{value}</p></div>)}
            </section>

            <section className="rounded-2xl border border-emerald-200 dark:border-emerald-900/60 bg-white dark:bg-slate-800 p-6 space-y-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div><h2 className="text-lg font-bold">Review corrections</h2><p className="text-xs text-slate-500 mt-1">{analysis.correction_summary}</p></div>
                <button type="button" onClick={acceptAll} className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-3 py-2 text-xs font-bold text-white"><Check className="w-4 h-4" /> Accept all</button>
              </div>
              <div className="space-y-3">
                {analysis.corrections.length === 0 && <p className="rounded-xl bg-emerald-50 p-4 text-sm text-emerald-800">No grammar or spelling corrections were found.</p>}
                {analysis.corrections.map((item) => <div key={item.id} className="grid gap-3 md:grid-cols-[1fr_auto_1fr_auto] items-center rounded-xl border border-slate-200 dark:border-slate-700 p-3 text-xs">
                  <div><p className="mb-1 font-bold text-slate-500">Original</p><p className="text-red-600 line-through">{item.before}</p></div>
                  <span className="text-slate-400">→</span>
                  <div><p className="mb-1 font-bold text-slate-500">Corrected</p><input value={item.after} onChange={(event) => updateCorrection(item.id, item.accepted, event.target.value)} className="w-full rounded border border-emerald-200 bg-emerald-50 px-2 py-1 text-emerald-700" /></div>
                  <div className="flex gap-1"><button type="button" title="Accept correction" onClick={() => updateCorrection(item.id, true)} className={`rounded-lg p-2 ${item.accepted ? 'bg-emerald-100 text-emerald-700' : 'text-slate-400 hover:text-emerald-600'}`}><CheckCircle2 className="w-4 h-4" /></button><button type="button" title="Reject correction" onClick={() => updateCorrection(item.id, false)} className={`rounded-lg p-2 ${!item.accepted ? 'bg-red-100 text-red-700' : 'text-slate-400 hover:text-red-600'}`}><X className="w-4 h-4" /></button></div>
                </div>)}
              </div>
            </section>

            <section className="grid gap-5 lg:grid-cols-2">
              <div className="rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-5"><h2 className="mb-3 text-sm font-bold">Original Resume Content</h2><pre className="max-h-96 overflow-auto whitespace-pre-wrap text-xs leading-relaxed text-slate-500">{analysis.original_text}</pre></div>
              <div className="rounded-2xl bg-white dark:bg-slate-800 border border-emerald-200 p-5"><h2 className="mb-3 text-sm font-bold text-emerald-700">Corrected Resume Content</h2><pre className="max-h-96 overflow-auto whitespace-pre-wrap text-xs leading-relaxed text-slate-700 dark:text-slate-300">{analysis.corrected_text}</pre></div>
            </section>

            <section className="flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-indigo-950 p-5 text-white">
              <div><p className="font-bold">Your corrected resume is ready!</p><p className="text-xs text-indigo-200 mt-1">Generate a reviewed PDF for your interview applications.</p></div>
              <div className="flex gap-2"><button type="button" onClick={() => { setAnalysis(null); setFile(null); }} className="inline-flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-xs font-bold"><RotateCcw className="w-4 h-4" /> Start new analysis</button><button type="button" onClick={download} disabled={downloading} className="inline-flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-xs font-bold disabled:opacity-50">{downloading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />} Download Corrected Resume (PDF)</button></div>
            </section>
          </>
        )}
      </div>
    </main>
  );
};

export default ResumeGrammarChecker;
