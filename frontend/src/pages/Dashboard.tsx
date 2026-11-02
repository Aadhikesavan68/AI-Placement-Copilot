import { useState, useEffect, useRef } from 'react';
import ResumeUpload from '../components/ResumeUpload';
import JobDescriptionUpload from '../components/JobDescriptionUpload';
import ProfileCard from '../components/ProfileCard';
import JobDescriptionCard from '../components/JobDescriptionCard';
import type { JobDescriptionData } from '../components/JobDescriptionCard';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';
import {
  FileText, Briefcase, ArrowRight, Sparkles, CheckCircle2,
  TrendingUp, Award, Search, BookOpen, Compass, History, CheckCheck
  , Brain
} from 'lucide-react';
import { motion } from 'framer-motion';

const Dashboard = () => {
  const navigate = useNavigate();
  const [latestResume, setLatestResume] = useState<any>(null);
  const [latestJD, setLatestJD] = useState<JobDescriptionData | null>(null);
  const [activeViewTab, setActiveViewTab] = useState<'both' | 'resume' | 'jd'>('both');
  const uploadSectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchLatestResume();
    fetchLatestJD();
  }, []);

  const fetchLatestResume = async () => {
    try {
      const response = await api.get('/resume/history');
      if (response.data && response.data.length > 0) {
        setLatestResume(response.data[0]);
      }
    } catch (error) {
      console.error('Failed to fetch resume history', error);
    }
  };

  const fetchLatestJD = async () => {
    try {
      const response = await api.get('/job/latest');
      if (response.data) {
        setLatestJD(response.data);
      } else {
        setLatestJD(null);
      }
    } catch (error) {
      console.error('Failed to fetch latest job description', error);
    }
  };

  const handleResumeUploadSuccess = (data: any) => {
    setLatestResume(data);
  };

  const handleJDUploadSuccess = (data: any) => {
    setLatestJD(data);
  };

  const handleJDDelete = () => {
    fetchLatestJD();
  };

  const scrollToUpload = () => {
    uploadSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 8 Feature Cards
  const features = [
    {
      icon: Award,
      title: 'ATS Resume Score',
      desc: '12-factor evaluation including formatting, contact info, action verbs, and section completeness.',
      color: 'from-blue-500 to-indigo-600',
      tag: 'ATS 95%+'
    },
    {
      icon: TrendingUp,
      title: 'Resume vs JD Match Score',
      desc: 'Real-time semantic & keyword match calculation between your skills and job requirements.',
      color: 'from-indigo-500 to-purple-600',
      tag: 'AI Matching'
    },
    {
      icon: Search,
      title: 'Missing Skills Detection',
      desc: 'Categorized breakdown into Critical, Important, and Optional skills with priority rankings.',
      color: 'from-purple-500 to-pink-600',
      tag: 'Skill Gap'
    },
    {
      icon: CheckCheck,
      title: 'Keyword Analysis',
      desc: 'Pinpoint missing industry keywords, tool names, and recruiter buzzwords to optimize your CV.',
      color: 'from-pink-500 to-rose-600',
      tag: 'Keywords'
    },
    {
      icon: Sparkles,
      title: 'Resume Suggestions',
      desc: 'Actionable suggestions with quantified metrics and power verbs to boost interview callbacks.',
      color: 'from-amber-500 to-orange-600',
      tag: 'Actionable'
    },
    {
      icon: BookOpen,
      title: 'Learning Roadmap',
      desc: 'Structured 4-week timeline with curated tutorials, courses, and project milestones.',
      color: 'from-emerald-500 to-teal-600',
      tag: '4 Weeks'
    },
    {
      icon: Compass,
      title: 'Company Interview Prep',
      desc: 'Targeted technical & behavioral interview questions tailored to the company stack.',
      color: 'from-cyan-500 to-blue-600',
      tag: 'STAR Method'
    },
    {
      icon: History,
      title: 'Analysis History',
      desc: 'Store, filter, sort, and track match scores across all applied companies and positions.',
      color: 'from-slate-600 to-slate-800',
      tag: 'Tracking'
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-50">
      <div className="max-w-7xl mx-auto p-6 md:p-10 space-y-12">
        {/* Hero Section */}
        <section className="relative overflow-hidden bg-gradient-to-br from-indigo-900 via-indigo-950 to-slate-950 text-white rounded-3xl p-8 md:p-12 shadow-xl border border-indigo-800/40">
          <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
          
          <div className="relative z-10 max-w-3xl space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
              <Sparkles className="w-3.5 h-3.5" /> Next-Gen AI Resume & Job Matcher
            </div>

            <h1 className="text-3xl md:text-5xl font-black tracking-tight leading-tight">
              Optimize your resume for <span className="bg-gradient-to-r from-indigo-300 via-purple-300 to-pink-300 bg-clip-text text-transparent">ATS & dream roles</span> in seconds.
            </h1>

            <p className="text-slate-300 text-sm md:text-base leading-relaxed max-w-2xl">
              Evaluate your placement readiness against real job descriptions like top SaaS products. Uncover missing skills, boost ATS scoring, generate 4-week learning roadmaps, and practice tailored interview questions.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                onClick={scrollToUpload}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-sm font-bold rounded-xl shadow-lg hover:shadow-indigo-500/30 transition-all cursor-pointer"
              >
                <FileText className="w-4 h-4" />
                Upload Resume
              </button>

              <button
                onClick={scrollToUpload}
                className="flex items-center gap-2 px-6 py-3 bg-white/10 hover:bg-white/20 text-white text-sm font-bold rounded-xl border border-white/20 transition-all cursor-pointer"
              >
                <Briefcase className="w-4 h-4" />
                Upload Job Description
              </button>

              <button
                onClick={() => navigate('/analysis')}
                className="flex items-center gap-2 px-6 py-3 bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-bold rounded-xl shadow-lg hover:shadow-emerald-500/30 transition-all cursor-pointer"
              >
                <Sparkles className="w-4 h-4" />
                Analyze Match
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                onClick={() => navigate('/resume-grammar')}
                className="flex items-center gap-2 px-6 py-3 bg-white/10 hover:bg-white/20 text-white text-sm font-bold rounded-xl border border-white/20 transition-all cursor-pointer"
              >
                <Sparkles className="w-4 h-4" />
                AI Grammar Checker
              </button>

              <button
                onClick={() => navigate('/skill-assessment')}
                className="flex items-center gap-2 px-6 py-3 bg-amber-500 hover:bg-amber-600 text-white text-sm font-bold rounded-xl shadow-lg transition-all cursor-pointer"
              >
                <Brain className="w-4 h-4" />
                Assess Skills
              </button>
            </div>
          </div>
        </section>

        {/* 8 Feature Showcase Cards */}
        <section className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-500" />
                Intelligent Analysis Capabilities
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Everything you need to beat the ATS algorithms and land interviews
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {features.map((feat, idx) => {
              const Icon = feat.icon;
              return (
                <motion.div
                  key={idx}
                  whileHover={{ y: -4 }}
                  className="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200 dark:border-slate-700/80 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className={`w-10 h-10 rounded-xl bg-gradient-to-tr ${feat.color} flex items-center justify-center text-white shadow-sm`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300">
                        {feat.tag}
                      </span>
                    </div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                      {feat.title}
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                      {feat.desc}
                    </p>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </section>

        {/* Upload Section */}
        <section ref={uploadSectionRef} className="space-y-6">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-700 pb-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-500" />
                Upload Documents for AI Analysis
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Upload both candidate resume & target job description to generate your ATS score
              </p>
            </div>
            
            {latestResume && (
              <button
                onClick={() => navigate('/analysis')}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-xl text-xs font-bold shadow-md hover:shadow-lg transition-all cursor-pointer shrink-0"
              >
                <Sparkles className="w-4 h-4" />
                Run AI Match
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
            {/* Left: Resume Upload */}
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xs border border-slate-200 dark:border-slate-700 p-5 md:p-6">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-700 pb-4 mb-4">
                <div>
                  <h3 className="text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                    <FileText className="w-4 h-4 text-indigo-500" />
                    Resume / CV
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    Supports PDF and DOCX formats
                  </p>
                </div>
                {latestResume && (
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Uploaded
                  </span>
                )}
              </div>
              <ResumeUpload onUploadSuccess={handleResumeUploadSuccess} />
            </div>

            {/* Right: Job Description Upload */}
            <JobDescriptionUpload onUploadSuccess={handleJDUploadSuccess} />
          </div>
        </section>

        {/* Live Parsed Documents Area */}
        <section className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-700 pb-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">Parsed Documents & Extraction</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Review extracted skills, competencies, qualifications, and requirements
              </p>
            </div>

            {/* View Selector */}
            <div className="flex bg-slate-200/80 dark:bg-slate-800 p-1 rounded-xl">
              <button
                onClick={() => setActiveViewTab('both')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeViewTab === 'both'
                    ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                All Documents
              </button>
              <button
                onClick={() => setActiveViewTab('resume')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeViewTab === 'resume'
                    ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Candidate Profile
              </button>
              <button
                onClick={() => setActiveViewTab('jd')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeViewTab === 'jd'
                    ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Target JD
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
            {/* Left: Resume Profile Card */}
            {(activeViewTab === 'both' || activeViewTab === 'resume') && (
              <div className={activeViewTab === 'resume' ? 'lg:col-span-2' : ''}>
                {latestResume ? (
                  <ProfileCard resume={latestResume} />
                ) : (
                  <div className="h-full min-h-[300px] flex flex-col items-center justify-center p-8 bg-slate-100/50 dark:bg-slate-800/30 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-700 text-center">
                    <FileText className="w-12 h-12 text-slate-400 mb-3" />
                    <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                      No resume uploaded yet
                    </p>
                    <p className="text-xs text-slate-500 mt-1 max-w-xs">
                      Upload your resume above to view parsed candidate details.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Right: Job Description Card */}
            {(activeViewTab === 'both' || activeViewTab === 'jd') && (
              <div className={activeViewTab === 'jd' ? 'lg:col-span-2' : ''}>
                {latestJD ? (
                  <JobDescriptionCard job={latestJD} onDelete={handleJDDelete} />
                ) : (
                  <div className="h-full min-h-[300px] flex flex-col items-center justify-center p-8 bg-slate-100/50 dark:bg-slate-800/30 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-700 text-center">
                    <Briefcase className="w-12 h-12 text-slate-400 mb-3" />
                    <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                      No Job Description uploaded yet
                    </p>
                    <p className="text-xs text-slate-500 mt-1 max-w-xs">
                      Upload or paste a target JD above to match your skills.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
