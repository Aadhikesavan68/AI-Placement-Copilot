import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import toast from 'react-hot-toast';
import {
  FileText, Briefcase, Sparkles, ArrowRight, CheckCircle2,
  Loader2, ArrowLeft, Zap, Download
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Analysis = () => {
  const [resumes, setResumes] = useState<any[]>([]);
  const [jobDescriptions, setJobDescriptions] = useState<any[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState('');
  const [targetType, setTargetType] = useState<'existing_jd' | 'paste_jd'>('existing_jd');
  const [selectedJdId, setSelectedJdId] = useState('');
  const [jdText, setJdText] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [improving, setImproving] = useState(false);
  const [improvement, setImprovement] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchResumesAndJDs();
  }, []);

  const fetchResumesAndJDs = async () => {
    try {
      const [resumeRes, jdRes] = await Promise.all([
        api.get('/resume/history'),
        api.get('/job/history')
      ]);
      setResumes(resumeRes.data || []);
      if (resumeRes.data && resumeRes.data.length > 0) {
        setSelectedResumeId(resumeRes.data[0].id);
      }

      setJobDescriptions(jdRes.data || []);
      if (jdRes.data && jdRes.data.length > 0) {
        setSelectedJdId(jdRes.data[0].id);
      } else {
        setTargetType('paste_jd');
      }
    } catch (error) {
      console.error('Failed to fetch resumes or JDs', error);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedResumeId) {
      toast.error('Please select a resume first');
      return;
    }

    if (targetType === 'existing_jd' && !selectedJdId) {
      toast.error('Please select a Job Description or paste one');
      return;
    }

    if (targetType === 'paste_jd' && !jdText.trim()) {
      toast.error('Please paste a target Job Description');
      return;
    }

    setLoading(true);
    setLoadingStep(1);

    const stepInterval = setInterval(() => {
      setLoadingStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 1200);

    try {
      const payload: any = { resume_id: selectedResumeId };
      if (targetType === 'existing_jd') {
        payload.jd_id = selectedJdId;
      } else {
        payload.job_description = jdText.trim();
      }

      const res = await api.post('/analysis/compare', payload);
      clearInterval(stepInterval);
      toast.success('Analysis completed successfully!');
      navigate(`/analysis/${res.data.id}`);
    } catch (error: any) {
      clearInterval(stepInterval);
      console.error('Analysis error:', error);
      toast.error(error.response?.data?.detail?.message || error.response?.data?.detail || 'Failed to run analysis. Please try again.');
    } finally {
      setLoading(false);
      setLoadingStep(0);
    }
  };

  const handleImproveResume = async () => {
    if (!selectedResumeId) {
      toast.error('Please select a resume first');
      return;
    }

    setImproving(true);
    try {
      const res = await api.post(`/resume/${selectedResumeId}/improve`);
      setImprovement(res.data);
      setResumes((current) => current.map((resume) => (
        resume.id === selectedResumeId ? res.data.resume : resume
      )));
      toast.success('Resume corrected and updated successfully');
    } catch (error: any) {
      console.error('Resume improvement error:', error);
      toast.error(error.response?.data?.detail?.message || error.response?.data?.detail || 'Failed to improve resume. Please try again.');
    } finally {
      setImproving(false);
    }
  };

  const handleDownloadResume = async () => {
    if (!selectedResumeId) return;
    try {
      const response = await api.get(`/resume/${selectedResumeId}/download`, { responseType: 'blob' });
      const url = URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      const selectedResume = resumes.find((resume) => resume.id === selectedResumeId);
      const extension = selectedResume?.resume_name?.toLowerCase().endsWith('.pdf') ? 'pdf' : 'docx';
      link.download = `corrected_candidate_resume.${extension}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error('Failed to download the corrected resume');
    }
  };

  const steps = [
    'Parsing resume credentials and target job description...',
    'Evaluating 12-factor ATS compliance & section scores...',
    'Running semantic skill match & keyword density check...',
    'Generating 4-week learning roadmap & tailored interview questions...'
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-50 p-6 md:p-10">
      <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
        
        {/* Navigation & Header */}
        <div className="flex items-center justify-between">
          <Link
            to="/dashboard"
            className="inline-flex items-center text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-1.5" /> Back to Dashboard
          </Link>

          <Link
            to="/analysis-history"
            className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline"
          >
            View History ↗
          </Link>
        </div>

        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
            <Sparkles className="w-3.5 h-3.5" /> AI Matching Engine
          </div>
          <h1 className="text-2xl md:text-3xl font-bold">Compare Resume vs Job Description</h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm">
            Select your uploaded resume and target job posting to generate an instant ATS match score and learning roadmap.
          </p>
        </div>

        {/* Wizard Card */}
        <div className="bg-white dark:bg-slate-800 rounded-3xl p-6 md:p-8 shadow-xs border border-slate-200 dark:border-slate-700 space-y-8">
          
          {/* Step 1: Resume Selection */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-indigo-100 dark:bg-indigo-900/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xs font-bold">
                  1
                </span>
                Select Candidate Resume
              </label>
              <Link to="/dashboard" className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline">
                + Upload New Resume
              </Link>
            </div>

            {resumes.length === 0 ? (
              <div className="p-5 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-2xl text-xs text-amber-800 dark:text-amber-300 flex items-center justify-between">
                <span>No resumes found. Please upload a resume first on the dashboard.</span>
                <Link to="/dashboard" className="px-3 py-1.5 bg-amber-600 text-white rounded-lg font-bold">
                  Upload Resume
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                {resumes.map((r) => {
                  const isSelected = selectedResumeId === r.id;
                  return (
                    <div
                      key={r.id}
                      onClick={() => setSelectedResumeId(r.id)}
                      className={`p-4 rounded-2xl border-2 cursor-pointer transition-all flex items-start justify-between ${
                        isSelected
                          ? 'border-indigo-600 bg-indigo-50/70 dark:bg-indigo-950/40 shadow-xs'
                          : 'border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-slate-600'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-xl ${isSelected ? 'bg-indigo-600 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'}`}>
                          <FileText className="w-5 h-5" />
                        </div>
                        <div>
                          <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                            {r.name && r.name !== "Not Found" ? r.name : r.resume_name}
                          </h4>
                          <p className="text-[11px] text-slate-400 mt-0.5">
                            {r.skills?.length || 0} skills • {new Date(r.upload_date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>

                      {isSelected && (
                        <CheckCircle2 className="w-5 h-5 text-indigo-600 dark:text-indigo-400 shrink-0" />
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/60">
            <div>
              <p className="text-sm font-bold text-emerald-900 dark:text-emerald-200">Polish this resume</p>
              <p className="text-xs text-emerald-700 dark:text-emerald-300 mt-1">Check grammar, spelling, clarity, and bullet presentation while preserving facts.</p>
            </div>
            <button
              type="button"
              onClick={handleImproveResume}
              disabled={improving || !selectedResumeId}
              className="shrink-0 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {improving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              {improving ? 'Correcting...' : 'Correct & structure resume'}
            </button>
          </div>

          {improvement && (
            <div className="space-y-5 p-5 rounded-2xl border border-emerald-200 dark:border-emerald-900/60 bg-white dark:bg-slate-900">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <h2 className="text-base font-bold text-slate-900 dark:text-white">Final structured resume</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    {improvement.issues_found} section{improvement.issues_found === 1 ? '' : 's'} improved using {improvement.provider} editing.
                  </p>
                </div>
                <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-700 dark:text-emerald-300">
                  <CheckCircle2 className="w-4 h-4" /> Saved to candidate resume
                </span>
              </div>

              <button
                type="button"
                onClick={handleDownloadResume}
                className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-colors"
              >
                <Download className="w-4 h-4" /> Download corrected resume
              </button>

              {improvement.issues?.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wide text-slate-500">Corrections made</h3>
                  {improvement.issues.map((issue: any) => (
                    <div key={issue.section} className="grid grid-cols-1 md:grid-cols-2 gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800 text-xs">
                      <div><p className="font-bold text-slate-500 mb-1">{issue.section} before</p><p className="text-slate-600 dark:text-slate-300 line-clamp-3">{Array.isArray(issue.before) ? issue.before.join(' • ') : issue.before || 'Not provided'}</p></div>
                      <div><p className="font-bold text-emerald-600 dark:text-emerald-400 mb-1">{issue.section} after</p><p className="text-slate-700 dark:text-slate-200 line-clamp-3">{Array.isArray(issue.after) ? issue.after.join(' • ') : issue.after || 'Not provided'}</p></div>
                    </div>
                  ))}
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {['summary', 'skills', 'experience', 'projects', 'education', 'certifications'].map((field) => {
                  const value = improvement.resume?.[field];
                  if (!value || (Array.isArray(value) && value.length === 0)) return null;
                  return (
                    <section key={field} className="space-y-1.5">
                      <h3 className="text-xs font-bold uppercase tracking-wide text-indigo-600 dark:text-indigo-400">{field.replace('_', ' ')}</h3>
                      {Array.isArray(value) ? value.map((item: string, index: number) => <p key={`${field}-${index}`} className="text-xs leading-relaxed text-slate-700 dark:text-slate-300">• {item}</p>) : <p className="text-xs leading-relaxed text-slate-700 dark:text-slate-300">{value}</p>}
                    </section>
                  );
                })}
              </div>
            </div>
          )}

          {/* Step 2: Target JD Selection */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-purple-100 dark:bg-purple-900/60 text-purple-600 dark:text-purple-400 flex items-center justify-center text-xs font-bold">
                  2
                </span>
                Target Job Description
              </label>

              {/* Toggle Switch */}
              <div className="flex bg-slate-100 dark:bg-slate-900 p-1 rounded-xl">
                <button
                  type="button"
                  onClick={() => setTargetType('existing_jd')}
                  disabled={jobDescriptions.length === 0}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all disabled:opacity-40 ${
                    targetType === 'existing_jd'
                      ? 'bg-white dark:bg-slate-800 text-purple-600 dark:text-purple-400 shadow-xs'
                      : 'text-slate-600 dark:text-slate-400'
                  }`}
                >
                  Saved JDs ({jobDescriptions.length})
                </button>
                <button
                  type="button"
                  onClick={() => setTargetType('paste_jd')}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                    targetType === 'paste_jd'
                      ? 'bg-white dark:bg-slate-800 text-purple-600 dark:text-purple-400 shadow-xs'
                      : 'text-slate-600 dark:text-slate-400'
                  }`}
                >
                  Paste New JD
                </button>
              </div>
            </div>

            {targetType === 'existing_jd' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                {jobDescriptions.map((jd) => {
                  const isSelected = selectedJdId === jd.id;
                  const title = jd.extracted_data?.role || jd.extracted_data?.job_title || jd.jd_name;
                  const comp = jd.extracted_data?.company_name || 'Target Company';
                  return (
                    <div
                      key={jd.id}
                      onClick={() => setSelectedJdId(jd.id)}
                      className={`p-4 rounded-2xl border-2 cursor-pointer transition-all flex items-start justify-between ${
                        isSelected
                          ? 'border-purple-600 bg-purple-50/70 dark:bg-purple-950/40 shadow-xs'
                          : 'border-slate-200 dark:border-slate-700 hover:border-purple-300 dark:hover:border-slate-600'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-xl ${isSelected ? 'bg-purple-600 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'}`}>
                          <Briefcase className="w-5 h-5" />
                        </div>
                        <div>
                          <h4 className="text-sm font-bold text-slate-900 dark:text-white">{title}</h4>
                          <p className="text-[11px] text-slate-400 mt-0.5">
                            {comp} • {jd.extracted_data?.required_skills?.length || 0} req skills
                          </p>
                        </div>
                      </div>

                      {isSelected && (
                        <CheckCircle2 className="w-5 h-5 text-purple-600 dark:text-purple-400 shrink-0" />
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="space-y-2">
                <textarea
                  rows={6}
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  placeholder="Paste the job description text here (e.g. Senior Full Stack Engineer at Stripe, requirements, responsibilities)..."
                  className="w-full p-4 text-xs font-mono bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-slate-900 dark:text-white placeholder-slate-400 resize-none leading-relaxed"
                />
                <p className="text-[11px] text-slate-400">
                  {jdText.length} characters entered
                </p>
              </div>
            )}
          </div>

          {/* Submit Action */}
          <div className="pt-2">
            <button
              onClick={handleAnalyze}
              disabled={loading || resumes.length === 0}
              className="w-full py-4 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-700 hover:to-pink-700 text-white rounded-2xl font-bold text-base shadow-lg hover:shadow-indigo-500/25 transition-all flex items-center justify-center gap-2.5 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing Match...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Perform AI Resume & JD Analysis
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>

          {/* Animated Progress Stages */}
          <AnimatePresence>
            {loading && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="p-5 bg-slate-50 dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-700 space-y-3"
              >
                <div className="flex items-center justify-between text-xs font-bold text-indigo-600 dark:text-indigo-400">
                  <span className="flex items-center gap-1.5">
                    <Zap className="w-4 h-4 animate-pulse" />
                    Analyzing Placement Match
                  </span>
                  <span>Step {loadingStep} of 4</span>
                </div>

                <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-600"
                    initial={{ width: '15%' }}
                    animate={{ width: `${loadingStep * 25}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>

                <p className="text-xs text-slate-600 dark:text-slate-300 font-medium">
                  {steps[loadingStep - 1] || 'Running analysis...'}
                </p>
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </div>
    </div>
  );
};

export default Analysis;
