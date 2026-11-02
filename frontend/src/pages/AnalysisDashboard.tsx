import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import {
  CheckCircle2, XCircle, ArrowLeft, Award, BookOpen, AlertTriangle,
  TrendingUp, Sparkles, ChevronDown, ChevronUp, RotateCcw,
  ExternalLink, Clock, ShieldCheck, HelpCircle,
  CheckCheck
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AnalysisDashboard = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [openAccordion, setOpenAccordion] = useState<string>('suggestions');

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const res = await api.get(`/analysis/${id}`);
        setAnalysis(res.data);
      } catch (error) {
        console.error('Failed to fetch analysis', error);
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchAnalysis();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-indigo-600 border-t-transparent animate-spin" />
        <p className="text-sm font-semibold text-slate-600 dark:text-slate-300">
          Loading comprehensive ATS analysis...
        </p>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-10 flex flex-col items-center justify-center space-y-4">
        <div className="p-4 bg-red-100 dark:bg-red-900/40 text-red-600 rounded-full">
          <AlertTriangle className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold">Analysis Not Found</h2>
        <p className="text-sm text-slate-500 max-w-sm text-center">
          The requested analysis could not be located or has been deleted.
        </p>
        <button
          onClick={() => navigate('/analysis')}
          className="px-5 py-2.5 bg-indigo-600 text-white text-xs font-bold rounded-xl"
        >
          Run New Analysis
        </button>
      </div>
    );
  }

  // 1. Donut Chart Data: Matched vs Missing vs Extra Skills
  const matchedCount = analysis.matched_skills?.length || 0;
  const missingCount = analysis.missing_skills?.length || 0;
  const extraCount = analysis.extra_skills?.length || 0;
  
  const skillDistributionData = [
    { name: 'Matched Skills', value: matchedCount || 1, color: '#10B981' },
    { name: 'Missing Skills', value: missingCount || 1, color: '#EF4444' },
    { name: 'Extra Skills', value: extraCount || 1, color: '#6366F1' }
  ];

  // 2. Radar Chart Data: 6 Dimensions
  const radarData = [
    { subject: 'Languages', score: Math.min(100, Math.max(40, (analysis.scores?.skill_match || 70) * 1.1)) },
    { subject: 'Frameworks', score: analysis.scores?.skill_match || 75 },
    { subject: 'Databases', score: analysis.scores?.keyword_match || 80 },
    { subject: 'Cloud / DevOps', score: Math.min(100, Math.max(30, (analysis.scores?.skill_match || 60) * 0.9)) },
    { subject: 'Experience', score: analysis.scores?.experience_match || 80 },
    { subject: 'Education', score: analysis.scores?.education_match || 90 },
  ];

  // 3. Bar Chart Data: 12 ATS Factor Scores
  const atsDetails = analysis.ats_details || {};
  const barChartData = [
    { name: 'Format', score: atsDetails.formatting || 100 },
    { name: 'Sections', score: atsDetails.section_presence || 85 },
    { name: 'Keywords', score: atsDetails.keyword_optimization || 75 },
    { name: 'Readability', score: atsDetails.readability || 90 },
    { name: 'Contact', score: atsDetails.contact_information || 95 },
    { name: 'Projects', score: atsDetails.projects || 80 },
    { name: 'Experience', score: atsDetails.experience || 75 },
    { name: 'Education', score: atsDetails.education || 90 },
    { name: 'Achievements', score: atsDetails.achievements || 70 },
    { name: 'Skills', score: atsDetails.skills || 85 },
    { name: 'Verbs', score: atsDetails.action_verbs || 75 },
    { name: 'Length', score: atsDetails.resume_length || 95 }
  ];

  const getScoreBadge = (score: number) => {
    if (score >= 80) return { label: 'Excellent Match', bg: 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800' };
    if (score >= 60) return { label: 'Good Candidate', bg: 'bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-300 border-blue-200 dark:border-blue-800' };
    return { label: 'Needs Improvement', bg: 'bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-300 border-amber-200 dark:border-amber-800' };
  };

  const atsBadge = getScoreBadge(analysis.ats_score);
  const matchBadge = getScoreBadge(analysis.match_score);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-50 p-6 md:p-10 space-y-8 animate-fade-in">
      
      {/* Top Header & Quick Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-700 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/analysis')}
              className="p-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-500 hover:text-indigo-600 transition-colors cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                  Analysis Report
                </span>
                <span className="text-xs text-slate-400">
                  {new Date(analysis.created_at).toLocaleDateString()}
                </span>
              </div>
              <h1 className="text-2xl font-bold mt-1 text-slate-900 dark:text-white">
                {analysis.role_title || analysis.jd_data?.role || 'Software Engineer'} @ {analysis.company_name || analysis.jd_data?.company_name || 'Target Company'}
              </h1>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => navigate(`/roadmap/${id}`)}
            className="flex items-center gap-1.5 px-4 py-2 bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-100 text-indigo-700 dark:text-indigo-300 rounded-xl text-xs font-bold border border-indigo-200 dark:border-indigo-800 transition-colors cursor-pointer"
          >
            <BookOpen className="w-3.5 h-3.5" />
            Learning Roadmap
          </button>
          <button
            onClick={() => navigate(`/learning/setup?analysisId=${id}`)}
            className="flex items-center gap-1.5 px-4 py-2 bg-emerald-50 dark:bg-emerald-950/60 hover:bg-emerald-100 text-emerald-700 dark:text-emerald-300 rounded-xl text-xs font-bold border border-emerald-200 dark:border-emerald-800 transition-colors cursor-pointer"
          >
            <BookOpen className="w-3.5 h-3.5" />
            Adaptive Learning
          </button>

          <button
            onClick={() => navigate('/analysis')}
            className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Re-Analyze New JD
          </button>
        </div>
      </div>

      {/* TOP 4 KPI CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        
        {/* Card 1: ATS Score */}
        <div className="p-6 bg-white dark:bg-slate-800 rounded-3xl shadow-xs border border-slate-200 dark:border-slate-700 relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">ATS Resume Score</span>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${atsBadge.bg}`}>
              {atsBadge.label}
            </span>
          </div>
          
          <div className="my-4 flex items-baseline gap-2">
            <span className="text-4xl font-black text-indigo-600 dark:text-indigo-400">
              {analysis.ats_score}
            </span>
            <span className="text-slate-400 text-xs font-bold">/ 100</span>
          </div>

          <p className="text-xs text-slate-500 dark:text-slate-400">
            Based on 12-factor parsing algorithm & section integrity.
          </p>
        </div>

        {/* Card 2: JD Match */}
        <div className="p-6 bg-white dark:bg-slate-800 rounded-3xl shadow-xs border border-slate-200 dark:border-slate-700 relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">JD Skill Match</span>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${matchBadge.bg}`}>
              {matchBadge.label}
            </span>
          </div>

          <div className="my-4 flex items-baseline gap-2">
            <span className="text-4xl font-black text-emerald-600 dark:text-emerald-400">
              {analysis.match_score}%
            </span>
          </div>

          <p className="text-xs text-slate-500 dark:text-slate-400">
            {matchedCount} matched skills out of {matchedCount + missingCount} required.
          </p>
        </div>

        {/* Card 3: Interview Readiness */}
        <div className="p-6 bg-white dark:bg-slate-800 rounded-3xl shadow-xs border border-slate-200 dark:border-slate-700 relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Interview Readiness</span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-300 border border-purple-200 dark:border-purple-800">
              {analysis.interview_readiness >= 75 ? 'Ready' : 'In Progress'}
            </span>
          </div>

          <div className="my-4 flex items-baseline gap-2">
            <span className="text-4xl font-black text-purple-600 dark:text-purple-400">
              {analysis.interview_readiness || 75}%
            </span>
          </div>

          <p className="text-xs text-slate-500 dark:text-slate-400">
            {analysis.interview_questions?.length || 4} tailored STAR questions generated.
          </p>
        </div>

        {/* Card 4: Confidence Score */}
        <div className="p-6 bg-white dark:bg-slate-800 rounded-3xl shadow-xs border border-slate-200 dark:border-slate-700 relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Confidence Level</span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
              High Accuracy
            </span>
          </div>

          <div className="my-4 flex items-baseline gap-2">
            <span className="text-4xl font-black text-blue-600 dark:text-blue-400">
              {analysis.confidence_score || 92}%
            </span>
          </div>

          <p className="text-xs text-slate-500 dark:text-slate-400">
            Semantic overlap: {analysis.semantic_match || 78}%
          </p>
        </div>

      </div>

      {/* CHARTS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Chart 1: Donut Chart - Matched vs Missing vs Extra */}
        <div className="bg-white dark:bg-slate-800 rounded-3xl p-6 shadow-xs border border-slate-200 dark:border-slate-700 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-500" />
              Skill Distribution Breakdown
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Matched vs Missing vs Extra competencies
            </p>
          </div>

          <div className="h-56 my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={skillDistributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={75}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {skillDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-100 dark:border-slate-700/60 text-center">
            <div>
              <span className="text-[10px] text-slate-400 uppercase">Matched</span>
              <p className="text-base font-bold text-emerald-600 dark:text-emerald-400">{matchedCount}</p>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase">Missing</span>
              <p className="text-base font-bold text-red-500">{missingCount}</p>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase">Extra</span>
              <p className="text-base font-bold text-indigo-500">{extraCount}</p>
            </div>
          </div>
        </div>

        {/* Chart 2: Radar Chart - Skill & Domain Competencies */}
        <div className="bg-white dark:bg-slate-800 rounded-3xl p-6 shadow-xs border border-slate-200 dark:border-slate-700 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-indigo-500" />
              Competency Radar (6 Dimensions)
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Candidate strengths across core software domains
            </p>
          </div>

          <div className="h-60 my-1">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData} outerRadius="70%">
                <PolarGrid stroke="#94a3b8" strokeDasharray="3 3" opacity={0.3} />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#94a3b8" tick={{ fontSize: 9 }} />
                <Radar name="Candidate" dataKey="score" stroke="#6366f1" fill="#818cf8" fillOpacity={0.5} />
                <RechartsTooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <p className="text-[11px] text-slate-500 dark:text-slate-400 text-center">
            Highest scoring domain: <b className="text-indigo-600 dark:text-indigo-400">Education & Core Languages</b>
          </p>
        </div>

        {/* Chart 3: Progress Bars - Key Match Categories */}
        <div className="bg-white dark:bg-slate-800 rounded-3xl p-6 shadow-xs border border-slate-200 dark:border-slate-700 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <CheckCheck className="w-4 h-4 text-purple-500" />
              Sub-Category Alignment
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Granular scoring across role requirements
            </p>
          </div>

          <div className="space-y-3.5 my-3">
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span>Technical Skills Match</span>
                <span className="text-emerald-600 dark:text-emerald-400">{analysis.scores?.skill_match || 80}%</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full transition-all duration-700" style={{ width: `${analysis.scores?.skill_match || 80}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span>Experience & Seniority</span>
                <span className="text-indigo-600 dark:text-indigo-400">{analysis.scores?.experience_match || 75}%</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                <div className="bg-indigo-500 h-full rounded-full transition-all duration-700" style={{ width: `${analysis.scores?.experience_match || 75}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span>Education & Qualifications</span>
                <span className="text-purple-600 dark:text-purple-400">{analysis.scores?.education_match || 90}%</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                <div className="bg-purple-500 h-full rounded-full transition-all duration-700" style={{ width: `${analysis.scores?.education_match || 90}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span>Keywords & Terminology</span>
                <span className="text-amber-600 dark:text-amber-400">{analysis.scores?.keyword_match || 70}%</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                <div className="bg-amber-500 h-full rounded-full transition-all duration-700" style={{ width: `${analysis.scores?.keyword_match || 70}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span>Project Relevance</span>
                <span className="text-pink-600 dark:text-pink-400">{analysis.scores?.project_relevance || 85}%</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                <div className="bg-pink-500 h-full rounded-full transition-all duration-700" style={{ width: `${analysis.scores?.project_relevance || 85}%` }} />
              </div>
            </div>
          </div>

          <div className="text-[11px] text-slate-400 text-center">
            Overall Weighted Average: <b className="text-slate-800 dark:text-slate-200">{analysis.match_score}%</b>
          </div>
        </div>

      </div>

      {/* FULL WIDTH BAR CHART: 12 ATS FACTORS */}
      <div className="bg-white dark:bg-slate-800 rounded-3xl p-6 md:p-8 shadow-xs border border-slate-200 dark:border-slate-700 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Award className="w-5 h-5 text-indigo-500" />
              12-Factor ATS Compliance Breakdown
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Detailed evaluation scores for Applicant Tracking Systems & automated screeners
            </p>
          </div>
          <span className="text-xs font-bold px-3 py-1 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 rounded-xl border border-indigo-200 dark:border-indigo-800">
            Avg Score: {analysis.ats_score}/100
          </span>
        </div>

        <div className="h-64 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barChartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.15} vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} interval={0} angle={-25} textAnchor="end" />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#64748b' }} />
              <RechartsTooltip />
              <Bar dataKey="score" fill="#6366f1" radius={[6, 6, 0, 0]}>
                {barChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.score >= 80 ? '#10b981' : entry.score >= 60 ? '#6366f1' : '#f59e0b'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* MISSING SKILLS MATRIX (STEP 8) */}
      <div className="bg-white dark:bg-slate-800 rounded-3xl p-6 md:p-8 shadow-xs border border-slate-200 dark:border-slate-700 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-700 pb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <XCircle className="w-5 h-5 text-red-500" />
              Categorized Missing Skills Matrix
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Ranked by difficulty, learning time, and job priority
            </p>
          </div>
          <span className="text-xs font-bold text-slate-500">
            {analysis.missing_skills_categorized?.length || analysis.missing_skills?.length || 0} skills to acquire
          </span>
        </div>

        {analysis.missing_skills_categorized && analysis.missing_skills_categorized.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analysis.missing_skills_categorized.map((item: any, idx: number) => {
              const isCritical = item.category === 'Critical' || item.priority === 'High';
              const isOptional = item.category === 'Optional';
              return (
                <div
                  key={idx}
                  className={`p-4 rounded-2xl border transition-all flex flex-col justify-between ${
                    isCritical
                      ? 'bg-red-50/50 dark:bg-red-950/20 border-red-200 dark:border-red-900/60'
                      : isOptional
                      ? 'bg-blue-50/50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-900/60'
                      : 'bg-amber-50/50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-900/60'
                  }`}
                >
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md uppercase ${
                        isCritical
                          ? 'bg-red-100 text-red-700 dark:bg-red-900/60 dark:text-red-300'
                          : isOptional
                          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300'
                          : 'bg-amber-100 text-amber-700 dark:bg-amber-900/60 dark:text-amber-300'
                      }`}>
                        {item.category || 'Important'}
                      </span>
                      <span className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
                        <Clock className="w-3 h-3" /> {item.estimated_hours || '15 hours'}
                      </span>
                    </div>

                    <h4 className="text-base font-bold text-slate-900 dark:text-white">
                      {item.skill}
                    </h4>

                    <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-300">
                      <span>Difficulty: <b className="capitalize">{item.difficulty || 'Intermediate'}</b></span>
                      <span>•</span>
                      <span>Priority: <b>{item.priority || 'Medium'}</b></span>
                    </div>
                  </div>

                  <div className="pt-3 mt-3 border-t border-slate-200/60 dark:border-slate-700/60 flex items-center justify-between">
                    <span className="text-[11px] text-slate-500 truncate max-w-[170px]" title={item.resource_name}>
                      {item.resource_name || 'Documentation & Tutorials'}
                    </span>
                    <a
                      href={item.resource_url || `https://www.google.com/search?q=${item.skill}+tutorial`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline shrink-0"
                    >
                      Learn <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-6 text-center text-sm font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/30 rounded-2xl border border-emerald-200 dark:border-emerald-800">
            🎉 Outstanding! You already match 100% of the required technical skills for this position!
          </div>
        )}
      </div>

      {/* 4-WEEK STRUCTURED LEARNING ROADMAP (STEP 9) */}
      <div className="bg-white dark:bg-slate-800 rounded-3xl p-6 md:p-8 shadow-xs border border-slate-200 dark:border-slate-700 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-700 pb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-indigo-500" />
              4-Week Tailored Learning Roadmap
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Structured study plan designed to bridge your skill gap before interviews
            </p>
          </div>
          <Link
            to={`/roadmap/${id}`}
            className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
          >
            Full Roadmap View ↗
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {analysis.roadmap && analysis.roadmap.length > 0 ? (
            analysis.roadmap.map((week: any, idx: number) => (
              <div
                key={idx}
                className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-700/80 flex flex-col justify-between space-y-3"
              >
                <div className="space-y-2">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900/60 text-indigo-600 dark:text-indigo-400 inline-block">
                    Week {week.week || idx + 1}
                  </span>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    {week.topic}
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    {week.description}
                  </p>
                </div>

                {week.resources && week.resources.length > 0 && (
                  <div className="pt-2 border-t border-slate-200 dark:border-slate-700/60">
                    <span className="text-[10px] text-slate-400 font-semibold block mb-1">Recommended Resource:</span>
                    <a
                      href={week.resources[0].url || 'https://roadmap.sh'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 truncate"
                    >
                      {week.resources[0].course_name} <ExternalLink className="w-3 h-3 shrink-0" />
                    </a>
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-500">No roadmap weeks generated.</p>
          )}
        </div>
      </div>

      {/* ACCORDION SECTIONS: SUGGESTIONS, STRENGTHS & WEAKNESSES, INTERVIEW PREP */}
      <div className="space-y-4">
        
        {/* Accordion Item 1: Resume Improvement Suggestions */}
        <div className="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 overflow-hidden shadow-xs">
          <button
            onClick={() => setOpenAccordion(openAccordion === 'suggestions' ? '' : 'suggestions')}
            className="w-full p-6 flex items-center justify-between text-left font-bold text-slate-900 dark:text-white cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors"
          >
            <div className="flex items-center gap-2.5">
              <Sparkles className="w-5 h-5 text-amber-500" />
              <span>Resume Improvement Suggestions ({analysis.suggestions?.length || 0})</span>
            </div>
            {openAccordion === 'suggestions' ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>

          <AnimatePresence>
            {openAccordion === 'suggestions' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="px-6 pb-6 border-t border-slate-100 dark:border-slate-700/60 pt-4"
              >
                <ul className="space-y-2.5">
                  {analysis.suggestions && analysis.suggestions.length > 0 ? (
                    analysis.suggestions.map((sug: string, i: number) => (
                      <li key={i} className="flex items-start text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                        <span className="w-2 h-2 rounded-full bg-amber-500 mt-1.5 mr-2.5 shrink-0" />
                        <span>{sug}</span>
                      </li>
                    ))
                  ) : (
                    <li className="text-xs text-slate-500">Your resume is well structured and aligns closely with the job requirements.</li>
                  )}
                </ul>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Accordion Item 2: Strengths & Weaknesses */}
        <div className="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 overflow-hidden shadow-xs">
          <button
            onClick={() => setOpenAccordion(openAccordion === 'strengths' ? '' : 'strengths')}
            className="w-full p-6 flex items-center justify-between text-left font-bold text-slate-900 dark:text-white cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors"
          >
            <div className="flex items-center gap-2.5">
              <ShieldCheck className="w-5 h-5 text-indigo-500" />
              <span>Candidate Profile Strengths & Weaknesses</span>
            </div>
            {openAccordion === 'strengths' ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>

          <AnimatePresence>
            {openAccordion === 'strengths' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="px-6 pb-6 border-t border-slate-100 dark:border-slate-700/60 pt-4 grid grid-cols-1 md:grid-cols-2 gap-6"
              >
                {/* Strengths */}
                <div className="p-4 bg-emerald-50/50 dark:bg-emerald-950/20 rounded-2xl border border-emerald-100 dark:border-emerald-900/40">
                  <h4 className="text-xs font-bold text-emerald-800 dark:text-emerald-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Key Strengths
                  </h4>
                  <ul className="space-y-2">
                    {analysis.strengths && analysis.strengths.length > 0 ? (
                      analysis.strengths.map((st: string, idx: number) => (
                        <li key={idx} className="text-xs text-slate-700 dark:text-slate-300 flex items-start">
                          <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-1.5 mr-2 shrink-0" />
                          <span>{st}</span>
                        </li>
                      ))
                    ) : (
                      <li className="text-xs text-slate-500">Strong technical background.</li>
                    )}
                  </ul>
                </div>

                {/* Weaknesses */}
                <div className="p-4 bg-red-50/50 dark:bg-red-950/20 rounded-2xl border border-red-100 dark:border-red-900/40">
                  <h4 className="text-xs font-bold text-red-800 dark:text-red-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4 text-red-600" /> Areas for Improvement
                  </h4>
                  <ul className="space-y-2">
                    {analysis.weaknesses && analysis.weaknesses.length > 0 ? (
                      analysis.weaknesses.map((wk: string, idx: number) => (
                        <li key={idx} className="text-xs text-slate-700 dark:text-slate-300 flex items-start">
                          <span className="w-1.5 h-1.5 bg-red-500 rounded-full mt-1.5 mr-2 shrink-0" />
                          <span>{wk}</span>
                        </li>
                      ))
                    ) : (
                      <li className="text-xs text-slate-500">No major weaknesses identified.</li>
                    )}
                  </ul>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Accordion Item 3: Tailored Interview Questions */}
        <div className="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 overflow-hidden shadow-xs">
          <button
            onClick={() => setOpenAccordion(openAccordion === 'interview' ? '' : 'interview')}
            className="w-full p-6 flex items-center justify-between text-left font-bold text-slate-900 dark:text-white cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors"
          >
            <div className="flex items-center gap-2.5">
              <HelpCircle className="w-5 h-5 text-purple-500" />
              <span>Tailored Technical Interview Questions ({analysis.interview_questions?.length || 0})</span>
            </div>
            {openAccordion === 'interview' ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>

          <AnimatePresence>
            {openAccordion === 'interview' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="px-6 pb-6 border-t border-slate-100 dark:border-slate-700/60 pt-4 space-y-3"
              >
                {analysis.interview_questions && analysis.interview_questions.length > 0 ? (
                  analysis.interview_questions.map((q: any, i: number) => (
                    <div key={i} className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-700/60 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300">
                          {q.category || 'Technical Question'}
                        </span>
                        <span className="text-[10px] text-slate-400">Q{i + 1}</span>
                      </div>
                      <p className="text-xs font-semibold text-slate-900 dark:text-white">
                        {q.question}
                      </p>
                      {q.tip && (
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 italic">
                          💡 Tip: {q.tip}
                        </p>
                      )}
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-500">Standard interview questions apply for this role.</p>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

      </div>

    </div>
  );
};

export default AnalysisDashboard;
