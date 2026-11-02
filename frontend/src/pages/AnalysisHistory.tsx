import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from "../services/api";
import {
  History, ArrowRight, Calendar,
  Search, Trash2, Sparkles, ArrowLeft,
  FileText
} from 'lucide-react';
import toast from 'react-hot-toast';

const AnalysisHistory = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterScore, setFilterScore] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [sortBy, setSortBy] = useState<string>('date_desc');
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, [sortBy]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/analysis/history?sort_by=${sortBy}`);
      setHistory(res.data || []);
    } catch (error) {
      console.error('Failed to fetch history', error);
      toast.error('Failed to load analysis history');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this analysis record?')) return;

    setDeletingId(id);
    try {
      await apiClient.delete(`/analysis/${id}`);
      toast.success('Analysis record deleted');
      setHistory(prev => prev.filter(item => item.id !== id));
    } catch (error) {
      console.error('Failed to delete analysis', error);
      toast.error('Failed to delete record');
    } finally {
      setDeletingId(null);
    }
  };

  // Client-side filtering by search term and score category
  const filteredHistory = history.filter((item) => {
    const resumeName = item.resume_name || item.resume_data?.name || '';
    const companyName = item.company_name || item.jd_data?.company_name || '';
    const roleTitle = item.role_title || item.jd_data?.role || '';
    const searchString = `${resumeName} ${companyName} ${roleTitle}`.toLowerCase();
    const matchesSearch = !searchTerm || searchString.includes(searchTerm.toLowerCase());

    const score = item.match_score || 0;
    let matchesFilter = true;
    if (filterScore === 'high') matchesFilter = score >= 80;
    else if (filterScore === 'medium') matchesFilter = score >= 50 && score < 80;
    else if (filterScore === 'low') matchesFilter = score < 50;

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-50 p-6 md:p-10 space-y-8 animate-fade-in">
      
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-700 pb-6">
        <div className="flex items-center gap-3">
          <Link
            to="/dashboard"
            className="p-2.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-500 hover:text-indigo-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                Placement History
              </span>
              <span className="text-xs text-slate-400">
                {history.length} Total Records
              </span>
            </div>
            <h1 className="text-2xl font-bold mt-1 text-slate-900 dark:text-white">
              Analysis & Comparison History
            </h1>
          </div>
        </div>

        <button
          onClick={() => navigate('/analysis')}
          className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-xl text-xs font-bold shadow-md hover:shadow-lg transition-all cursor-pointer shrink-0"
        >
          <Sparkles className="w-4 h-4" />
          Run New Analysis
        </button>
      </div>

      {/* SEARCH, FILTER & SORT TOOLBAR */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-white dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-xs">
        
        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search by resume, company, or role..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-900 dark:text-white placeholder-slate-400"
          />
        </div>

        {/* Filter by Score */}
        <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-900 p-1 rounded-xl">
          <button
            onClick={() => setFilterScore('all')}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              filterScore === 'all'
                ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-xs'
                : 'text-slate-600 dark:text-slate-400'
            }`}
          >
            All Scores
          </button>
          <button
            onClick={() => setFilterScore('high')}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              filterScore === 'high'
                ? 'bg-white dark:bg-slate-800 text-emerald-600 dark:text-emerald-400 shadow-xs'
                : 'text-slate-600 dark:text-slate-400'
            }`}
          >
            &gt;80% Match
          </button>
          <button
            onClick={() => setFilterScore('medium')}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              filterScore === 'medium'
                ? 'bg-white dark:bg-slate-800 text-amber-600 dark:text-amber-400 shadow-xs'
                : 'text-slate-600 dark:text-slate-400'
            }`}
          >
            50-80%
          </button>
          <button
            onClick={() => setFilterScore('low')}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              filterScore === 'low'
                ? 'bg-white dark:bg-slate-800 text-red-600 dark:text-red-400 shadow-xs'
                : 'text-slate-600 dark:text-slate-400'
            }`}
          >
            &lt;50%
          </button>
        </div>

        {/* Sort */}
        <div className="flex items-center gap-2">
          <label className="text-xs font-semibold text-slate-500 shrink-0">Sort:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="w-full py-2 px-3 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-900 dark:text-white cursor-pointer"
          >
            <option value="date_desc">Newest First</option>
            <option value="date_asc">Oldest First</option>
            <option value="match_desc">Highest Match Score</option>
            <option value="match_asc">Lowest Match Score</option>
            <option value="ats_desc">Highest ATS Score</option>
          </select>
        </div>

      </div>

      {/* HISTORY CARDS / TABLE */}
      {loading ? (
        <div className="py-20 flex justify-center">
          <div className="w-10 h-10 rounded-full border-4 border-indigo-600 border-t-transparent animate-spin" />
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="text-center py-20 bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 space-y-4">
          <History className="mx-auto w-12 h-12 text-slate-300 dark:text-slate-600" />
          <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">No Matching Analyses Found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            {searchTerm || filterScore !== 'all'
              ? 'Try changing your search keywords or score filters.'
              : "You haven't executed any resume vs job description comparisons yet."}
          </p>
          <button
            onClick={() => navigate('/analysis')}
            className="px-5 py-2.5 bg-indigo-600 text-white text-xs font-bold rounded-xl hover:bg-indigo-700 transition-colors"
          >
            Start First Analysis
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredHistory.map((item) => {
            const role = item.role_title || item.jd_data?.role || 'Software Engineer';
            const company = item.company_name || item.jd_data?.company_name || 'Target Company';
            const resumeName = item.resume_name || item.resume_data?.name || 'Resume Document';
            const matchScore = item.match_score || 0;
            const atsScore = item.ats_score || 0;
            const missingCount = item.missing_skills?.length || 0;

            return (
              <div
                key={item.id}
                onClick={() => navigate(`/analysis/${item.id}`)}
                className="bg-white dark:bg-slate-800 rounded-3xl p-6 shadow-xs hover:shadow-md border border-slate-200 dark:border-slate-700 transition-all cursor-pointer flex flex-col justify-between space-y-5 group"
              >
                {/* Header */}
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1 flex-1">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 inline-block">
                      {company}
                    </span>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                      {role}
                    </h3>
                    <p className="text-xs text-slate-400 flex items-center gap-1">
                      <FileText className="w-3 h-3" /> {resumeName}
                    </p>
                  </div>

                  <button
                    onClick={(e) => handleDelete(item.id, e)}
                    disabled={deletingId === item.id}
                    className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-xl transition-colors shrink-0 cursor-pointer"
                    title="Delete record"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                {/* Scores Row */}
                <div className="grid grid-cols-2 gap-3 p-3 bg-slate-50 dark:bg-slate-900/60 rounded-2xl border border-slate-100 dark:border-slate-700/60">
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Match Score</span>
                    <p className={`text-xl font-black ${
                      matchScore >= 80 ? 'text-emerald-600 dark:text-emerald-400' : matchScore >= 50 ? 'text-indigo-600 dark:text-indigo-400' : 'text-red-500'
                    }`}>
                      {matchScore}%
                    </p>
                  </div>

                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase">ATS Score</span>
                    <p className="text-xl font-black text-slate-800 dark:text-slate-200">
                      {atsScore} <span className="text-xs font-normal text-slate-400">/100</span>
                    </p>
                  </div>
                </div>

                {/* Footer Meta & View CTA */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-700/60 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" />
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                    {missingCount > 0 && (
                      <span className="text-[10px] text-red-500 bg-red-50 dark:bg-red-950/40 px-1.5 py-0.5 rounded font-medium">
                        {missingCount} missing
                      </span>
                    )}
                  </div>

                  <span className="font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                    View Report <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>

              </div>
            );
          })}
        </div>
      )}

    </div>
  );
};

export default AnalysisHistory;
