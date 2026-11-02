import { useEffect, useState } from 'react';
import api from '../services/api';
import { Trash2, Eye, Calendar, FileText, Download } from 'lucide-react';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';

const ResumeHistory = () => {
  const [resumes, setResumes] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await api.get('/resume/history');
      setResumes(response.data);
    } catch (error) {
      toast.error('Failed to load resume history');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this resume?')) return;
    
    try {
      await api.delete(`/resume/${id}`);
      setResumes(resumes.filter((r) => r.id !== id));
      toast.success('Resume deleted successfully');
    } catch (error) {
      toast.error('Failed to delete resume');
    }
  };

  const handleDownload = async (id: string) => {
    try {
      const response = await api.get(`/resume/${id}/download`, { responseType: 'blob' });
      const url = URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      const resume = resumes.find((item) => item.id === id);
      const extension = resume?.resume_name?.toLowerCase().endsWith('.pdf') ? 'pdf' : 'docx';
      link.download = `corrected_candidate_resume.${extension}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error('Failed to download the corrected resume');
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center animate-pulse">Loading history...</div>;
  }

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Resume History</h2>
      
      {resumes.length === 0 ? (
        <div className="text-center p-12 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700">
          <FileText className="w-12 h-12 mx-auto text-slate-400 mb-4" />
          <p className="text-slate-500">No resumes uploaded yet.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {resumes.map((resume, index) => (
            <motion.div 
              key={resume.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center justify-between p-5 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg text-indigo-600 dark:text-indigo-400">
                  <FileText className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">{resume.resume_name}</h3>
                  <div className="flex items-center text-sm text-slate-500 mt-1">
                    <Calendar className="w-4 h-4 mr-1" />
                    {new Date(resume.upload_date).toLocaleDateString()}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-6">
                <div className="text-center hidden sm:block">
                  <span className="block text-xs text-slate-500 uppercase tracking-wider">Score</span>
                  <span className="font-semibold text-indigo-600 dark:text-indigo-400">{resume.completion_score}%</span>
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleDownload(resume.id)}
                    title="Download corrected resume"
                    className="p-2 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
                  >
                    <Download className="w-5 h-5" />
                  </button>
                  <button 
                    onClick={() => toast('View functionality coming soon', { icon: '👀' })}
                    className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                  >
                    <Eye className="w-5 h-5" />
                  </button>
                  <button 
                    onClick={() => handleDelete(resume.id)}
                    className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ResumeHistory;
