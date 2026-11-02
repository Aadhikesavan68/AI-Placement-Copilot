import { useState, useEffect } from 'react';
import api from '../services/api';
import { Filter, Bookmark, ExternalLink, Copy, Check } from 'lucide-react';
import toast from 'react-hot-toast';

interface Question {
  id: string;
  title: string;
  difficulty: string;
  topic: string;
  leetcode_link: string;
  bookmarked: boolean;
  completed: boolean;
}

interface QuestionViewerProps {
  companyName: string;
}

const QuestionViewer: React.FC<QuestionViewerProps> = ({ companyName }) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const [difficultyFilter, setDifficultyFilter] = useState('');
  const [topicFilter, setTopicFilter] = useState('');
  const [topics, setTopics] = useState<{topic: string, count: number}[]>([]);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const limit = 20;

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const res = await api.get(`/company/${companyName}/topics`);
        setTopics(res.data);
      } catch (error) {
        console.error("Failed to fetch topics");
      }
    };
    fetchTopics();
  }, [companyName]);

  useEffect(() => {
    const fetchQuestions = async () => {
      setLoading(true);
      try {
        let url = `/company/${companyName}/questions?skip=${page * limit}&limit=${limit}`;
        if (difficultyFilter) url += `&difficulty=${difficultyFilter}`;
        if (topicFilter) url += `&topic=${topicFilter}`;
        
        const res = await api.get(url);
        setQuestions(res.data.questions);
        setTotal(res.data.total);
      } catch (error) {
        toast.error("Failed to fetch questions");
      } finally {
        setLoading(false);
      }
    };
    fetchQuestions();
  }, [companyName, page, difficultyFilter, topicFilter]);

  const toggleBookmark = async (id: string) => {
    try {
      const res = await api.post(`/company/questions/${id}/bookmark`);
      setQuestions(questions.map(q => q.id === id ? { ...q, bookmarked: res.data.bookmarked } : q));
      if (res.data.bookmarked) {
        toast.success("Saved to bookmarks");
      } else {
        toast.success("Removed from bookmarks");
      }
    } catch (error) {
      toast.error("Failed to update bookmark");
    }
  };

  const copyLink = (link: string, id: string) => {
    navigator.clipboard.writeText(link);
    setCopiedId(id);
    toast.success("Link copied!");
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getDifficultyColor = (diff: string) => {
    switch(diff.toLowerCase()) {
      case 'easy': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 border-green-200 dark:border-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 border-red-200 dark:border-red-800';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 flex flex-wrap gap-4 items-center">
        <div className="flex items-center text-gray-500 font-medium">
          <Filter className="w-5 h-5 mr-2" /> Filters
        </div>
        
        <select 
          className="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none text-gray-700 dark:text-gray-200"
          value={difficultyFilter}
          onChange={(e) => { setDifficultyFilter(e.target.value); setPage(0); }}
        >
          <option value="">All Difficulties</option>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>

        <select 
          className="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none text-gray-700 dark:text-gray-200 max-w-xs"
          value={topicFilter}
          onChange={(e) => { setTopicFilter(e.target.value); setPage(0); }}
        >
          <option value="">All Topics</option>
          {topics.map(t => (
            <option key={t.topic} value={t.topic}>{t.topic} ({t.count})</option>
          ))}
        </select>

        <div className="ml-auto text-sm text-gray-500">
          Showing {questions.length} of {total}
        </div>
      </div>

      {/* Questions List */}
      <div className="space-y-4">
        {loading ? (
           <div className="flex justify-center p-10"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div></div>
        ) : questions.length === 0 ? (
          <div className="text-center py-10 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700">
            <p className="text-gray-500">No questions found for the selected filters.</p>
          </div>
        ) : (
          questions.map(q => (
            <div key={q.id} className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-700 transition-colors flex flex-col md:flex-row gap-4 justify-between md:items-center">
              
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{q.title}</h3>
                  <span className={`text-xs px-2 py-1 rounded-md border font-medium uppercase tracking-wider ${getDifficultyColor(q.difficulty)}`}>
                    {q.difficulty}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <span className="bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-1 rounded">
                    {q.topic}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button 
                  onClick={() => toggleBookmark(q.id)}
                  className={`p-2 rounded-lg transition-colors ${q.bookmarked ? 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/40 dark:text-indigo-400' : 'bg-gray-50 text-gray-400 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600'}`}
                  title="Bookmark"
                >
                  <Bookmark className="w-5 h-5" fill={q.bookmarked ? "currentColor" : "none"} />
                </button>
                
                {q.leetcode_link && (
                  <>
                    <button 
                      onClick={() => copyLink(q.leetcode_link, q.id)}
                      className="p-2 rounded-lg bg-gray-50 text-gray-400 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 transition-colors"
                      title="Copy Link"
                    >
                      {copiedId === q.id ? <Check className="w-5 h-5 text-green-500" /> : <Copy className="w-5 h-5" />}
                    </button>
                    
                    <a 
                      href={q.leetcode_link} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                      Solve <ExternalLink className="w-4 h-4" />
                    </a>
                  </>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {!loading && total > limit && (
        <div className="flex justify-center gap-2 pt-4">
          <button 
            disabled={page === 0}
            onClick={() => setPage(p => p - 1)}
            className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 disabled:opacity-50 text-gray-700 dark:text-gray-200"
          >
            Previous
          </button>
          <button 
            disabled={(page + 1) * limit >= total}
            onClick={() => setPage(p => p + 1)}
            className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 disabled:opacity-50 text-gray-700 dark:text-gray-200"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default QuestionViewer;
