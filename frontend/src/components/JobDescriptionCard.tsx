import { useState } from 'react';
import {
  Briefcase,
  GraduationCap,
  Clock,
  Code2,
  Wrench,
  Key,
  CheckCircle2,
  Building2,
  Trash2,
  ChevronDown,
  ChevronUp,
  FileText,
  Sparkles
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import toast from 'react-hot-toast';

interface JDExtractedData {
  company_name?: string;
  job_title?: string;
  role?: string;
  required_skills: string[];
  preferred_skills: string[];
  responsibilities: string[];
  experience?: string;
  required_experience?: string;
  education: string[];
  keywords: string[];
  technologies: string[];
  tools: string[];
  soft_skills?: string[];
}

export interface JobDescriptionData {
  id: string;
  jd_name: string;
  jd_text: string;
  original_file?: string | null;
  upload_date: string;
  extracted_data?: JDExtractedData;
}

interface JobDescriptionCardProps {
  job: JobDescriptionData | null;
  onDelete?: () => void;
}

const JobDescriptionCard: React.FC<JobDescriptionCardProps> = ({ job, onDelete }) => {
  const [showRawText, setShowRawText] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  if (!job) return null;

  const data: JDExtractedData = job.extracted_data || {
    required_skills: [],
    preferred_skills: [],
    responsibilities: [],
    education: [],
    keywords: [],
    technologies: [],
    tools: [],
  };

  const jobTitle = data.job_title || data.role || job.jd_name || 'Target Role';
  const companyName = data.company_name || 'Target Company';
  const experience = data.experience || data.required_experience || '0-2 years';

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete "${job.jd_name}"?`)) return;

    setIsDeleting(true);
    try {
      await api.delete(`/job/${job.id}`);
      toast.success('Job description deleted successfully');
      if (onDelete) onDelete();
    } catch (error: any) {
      console.error('Delete JD error:', error);
      toast.error(error.response?.data?.detail?.message || error.response?.data?.detail || 'Failed to delete job description');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white dark:bg-slate-800 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden"
    >
      <div className="p-6 md:p-8 space-y-7">
        
        {/* Header & Meta */}
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 border-b border-slate-100 dark:border-slate-700/80 pb-6">
          <div className="space-y-2 flex-1">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800">
                <Sparkles className="w-3 h-3" /> Target Job
              </span>
              {job.original_file ? (
                <span className="text-xs text-slate-400 dark:text-slate-500">
                  via {job.jd_name}
                </span>
              ) : (
                <span className="text-xs text-slate-400 dark:text-slate-500">
                  via Pasted Text
                </span>
              )}
            </div>

            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
              {jobTitle}
            </h2>

            <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600 dark:text-slate-300 pt-1">
              <div className="flex items-center gap-1.5">
                <Building2 className="w-4 h-4 text-purple-500" />
                <span className="font-medium">{companyName}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-indigo-500" />
                <span>{experience}</span>
              </div>
              {job.upload_date && (
                <span className="text-xs text-slate-400">
                  Uploaded: {new Date(job.upload_date).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowRawText(!showRawText)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white bg-slate-100 dark:bg-slate-700/60 rounded-xl hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              <FileText className="w-3.5 h-3.5" />
              {showRawText ? 'Hide Text' : 'View Text'}
              {showRawText ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-colors disabled:opacity-50"
              title="Delete this Job Description"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Collapsible Raw JD Text */}
        <AnimatePresence>
          {showRawText && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden bg-slate-50 dark:bg-slate-900/90 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
            >
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                Original Job Description Text
              </h4>
              <pre className="text-xs text-slate-700 dark:text-slate-300 whitespace-pre-wrap font-mono max-h-60 overflow-y-auto leading-relaxed">
                {job.jd_text}
              </pre>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 9 Extracted Sections */}
        <div className="space-y-6">

          {/* 1. Required Skills & Preferred Skills */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Required Skills */}
            <div className="p-4 bg-indigo-50/60 dark:bg-indigo-950/20 rounded-xl border border-indigo-100 dark:border-indigo-900/40">
              <h3 className="flex items-center text-sm font-bold text-indigo-900 dark:text-indigo-300 mb-3">
                <CheckCircle2 className="w-4 h-4 mr-1.5 text-indigo-600 dark:text-indigo-400" />
                Required Skills ({data.required_skills?.length || 0})
              </h3>
              {data.required_skills && data.required_skills.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {data.required_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 text-xs font-semibold bg-white dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-200 rounded-lg shadow-2xs border border-indigo-200 dark:border-indigo-800"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">None specified.</p>
              )}
            </div>

            {/* Preferred Skills */}
            <div className="p-4 bg-purple-50/60 dark:bg-purple-950/20 rounded-xl border border-purple-100 dark:border-purple-900/40">
              <h3 className="flex items-center text-sm font-bold text-purple-900 dark:text-purple-300 mb-3">
                <Sparkles className="w-4 h-4 mr-1.5 text-purple-600 dark:text-purple-400" />
                Preferred Skills ({data.preferred_skills?.length || 0})
              </h3>
              {data.preferred_skills && data.preferred_skills.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {data.preferred_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 text-xs font-semibold bg-white dark:bg-purple-900/60 text-purple-700 dark:text-purple-200 rounded-lg shadow-2xs border border-purple-200 dark:border-purple-800"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No secondary skills specified.</p>
              )}
            </div>
          </div>

          {/* 2. Technologies & Tools */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Technologies */}
            <div>
              <h3 className="flex items-center text-sm font-bold text-slate-800 dark:text-slate-200 mb-2.5">
                <Code2 className="w-4 h-4 mr-2 text-indigo-500" />
                Technologies & Frameworks
              </h3>
              {data.technologies && data.technologies.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {data.technologies.map((tech, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-0.5 text-xs bg-slate-100 dark:bg-slate-700/60 text-slate-700 dark:text-slate-200 rounded-md"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">None extracted.</p>
              )}
            </div>

            {/* Tools */}
            <div>
              <h3 className="flex items-center text-sm font-bold text-slate-800 dark:text-slate-200 mb-2.5">
                <Wrench className="w-4 h-4 mr-2 text-amber-500" />
                Developer Tools & Platforms
              </h3>
              {data.tools && data.tools.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {data.tools.map((tool, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-0.5 text-xs bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800/50 rounded-md"
                    >
                      {tool}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">Standard tools apply.</p>
              )}
            </div>
          </div>

          {/* 3. Responsibilities */}
          {data.responsibilities && data.responsibilities.length > 0 && (
            <div>
              <h3 className="flex items-center text-sm font-bold text-slate-800 dark:text-slate-200 mb-2.5">
                <Briefcase className="w-4 h-4 mr-2 text-indigo-500" />
                Key Responsibilities
              </h3>
              <ul className="space-y-1.5">
                {data.responsibilities.map((resp, idx) => (
                  <li
                    key={idx}
                    className="flex items-start text-xs text-slate-600 dark:text-slate-300 leading-relaxed"
                  >
                    <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 mr-2 shrink-0" />
                    <span>{resp}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 4. Education & Experience */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            <div>
              <h3 className="flex items-center text-sm font-bold text-slate-800 dark:text-slate-200 mb-2">
                <GraduationCap className="w-4 h-4 mr-2 text-indigo-500" />
                Education Requirements
              </h3>
              <ul className="space-y-1 text-xs text-slate-600 dark:text-slate-300">
                {data.education && data.education.length > 0 ? (
                  data.education.map((edu, idx) => (
                    <li key={idx} className="flex items-center gap-1.5">
                      <span className="w-1 h-1 bg-slate-400 rounded-full" />
                      {edu}
                    </li>
                  ))
                ) : (
                  <li>Bachelor's Degree in Computer Science or related field</li>
                )}
              </ul>
            </div>

            <div>
              <h3 className="flex items-center text-sm font-bold text-slate-800 dark:text-slate-200 mb-2">
                <Clock className="w-4 h-4 mr-2 text-indigo-500" />
                Experience Requirement
              </h3>
              <p className="text-xs text-slate-700 dark:text-slate-300 font-medium bg-slate-50 dark:bg-slate-700/40 px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700">
                {experience}
              </p>
            </div>
          </div>

          {/* 5. Keywords & Concepts */}
          {data.keywords && data.keywords.length > 0 && (
            <div className="pt-2">
              <h3 className="flex items-center text-sm font-bold text-slate-800 dark:text-slate-200 mb-2">
                <Key className="w-4 h-4 mr-2 text-emerald-500" />
                Target Keywords & Concepts ({data.keywords.length})
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {data.keywords.map((kw, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 text-[11px] bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-300 rounded font-mono"
                  >
                    #{kw}
                  </span>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </motion.div>
  );
};

export default JobDescriptionCard;
