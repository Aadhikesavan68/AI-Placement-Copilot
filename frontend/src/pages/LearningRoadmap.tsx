import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { ArrowLeft, Clock, ExternalLink, PlayCircle } from 'lucide-react';

const LearningRoadmap = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const res = await api.get(`/analysis/history/${id}`);
        setAnalysis(res.data);
      } catch (error) {
        console.error('Failed to fetch analysis', error);
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchAnalysis();
  }, [id]);

  if (loading) return <div className="p-10 flex justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div></div>;
  if (!analysis) return <div className="p-10 text-center text-red-500">Analysis not found.</div>;

  const roadmap = analysis.roadmap || [];

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8 animate-fade-in">
      <div className="flex justify-between items-center">
        <button onClick={() => navigate(`/analysis/${id}`)} className="flex items-center text-gray-500 hover:text-indigo-600 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
        </button>
      </div>

      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Your Learning Roadmap</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-2">A personalized step-by-step plan to bridge your skill gaps for {analysis.company_name || 'this role'}.</p>
      </div>

      {roadmap.length === 0 ? (
        <div className="bg-green-50 text-green-800 p-8 rounded-2xl border border-green-200 text-center">
          <h3 className="text-lg font-semibold mb-2">No missing skills detected!</h3>
          <p>You already have all the required skills. Focus on practicing interview questions.</p>
        </div>
      ) : (
        <div className="relative border-l-4 border-indigo-200 dark:border-indigo-900 ml-4 space-y-10 py-4">
          {roadmap.map((week: any, idx: number) => (
            <div key={idx} className="relative pl-8">
              {/* Timeline marker */}
              <div className="absolute -left-[14px] top-1 w-6 h-6 bg-indigo-600 rounded-full border-4 border-white dark:border-gray-900 shadow-sm"></div>
              
              <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
                <div className="flex items-center gap-3 mb-2">
                  <span className="px-3 py-1 bg-indigo-100 text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300 text-sm font-bold rounded-lg uppercase tracking-wide">
                    Week {week.week}
                  </span>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">{week.topic}</h3>
                </div>
                <p className="text-gray-600 dark:text-gray-300 mb-6">{week.description}</p>
                
                {/* Resources */}
                <div className="space-y-3">
                  <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Recommended Resources</h4>
                  {week.resources.map((res: any, i: number) => (
                    <a 
                      key={i}
                      href={res.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block p-4 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-indigo-400 dark:hover:border-indigo-500 hover:shadow-md transition-all group bg-gray-50 dark:bg-gray-750"
                    >
                      <div className="flex justify-between items-start md:items-center flex-col md:flex-row gap-4">
                        <div className="flex items-center gap-4">
                          <div className="p-3 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-lg group-hover:scale-110 transition-transform">
                            <PlayCircle className="w-6 h-6" />
                          </div>
                          <div>
                            <h5 className="font-semibold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{res.course_name}</h5>
                            <p className="text-sm text-gray-500 flex items-center gap-2 mt-1">
                              <span>{res.provider}</span> • 
                              <span className="flex items-center"><Clock className="w-3 h-3 mr-1" /> {res.estimated_duration}</span> • 
                              <span className={`px-2 py-0.5 rounded text-xs ${res.difficulty === 'Beginner' ? 'bg-green-100 text-green-800' : res.difficulty === 'Advanced' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>{res.difficulty}</span>
                            </p>
                          </div>
                        </div>
                        <ExternalLink className="w-5 h-5 text-gray-400 group-hover:text-indigo-600" />
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LearningRoadmap;
