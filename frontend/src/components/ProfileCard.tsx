import { Mail, Phone, MapPin, Globe, GraduationCap, Briefcase, Code2, Award, Layers, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';

export interface ResumeData {
  id: string;
  resume_name: string;
  name?: string;
  email?: string;
  phone?: string;
  college?: string;
  degree?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  portfolio?: string;
  skills: string[];
  languages_prog?: string[];
  frameworks?: string[];
  databases?: string[];
  cloud?: string[];
  tools?: string[];
  soft_skills?: string[];
  education: string[];
  projects: string[];
  experience: string[];
  internships?: string[];
  certifications: string[];
  achievements?: string[];
  languages?: string[];
  summary?: string;
  completion_score: number;
}

interface ProfileCardProps {
  resume: ResumeData | null;
}

const ProfileCard: React.FC<ProfileCardProps> = ({ resume }) => {
  if (!resume) return null;

  const renderOrNotFound = (val?: string) => {
    if (!val || val === "Not Found" || val.trim() === "") {
      return <span className="text-slate-400 italic text-xs">Not Found</span>;
    }
    return <span className="text-slate-700 dark:text-slate-300 text-xs font-medium">{val}</span>;
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white dark:bg-slate-800 rounded-2xl shadow-xs border border-slate-200 dark:border-slate-700 overflow-hidden"
    >
      <div className="p-6 md:p-8 space-y-6">
        
        {/* Header & Basic Info */}
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 pb-6 border-b border-slate-100 dark:border-slate-700">
          <div className="space-y-3 flex-1">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                <CheckCircle2 className="w-3 h-3" /> Extracted Candidate
              </span>
              <span className="text-xs text-slate-400">via {resume.resume_name}</span>
            </div>

            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
              {resume.name && resume.name !== "Not Found" ? resume.name : "Candidate Profile"}
            </h2>

            {/* Quick Contact & Education Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
              <div className="flex items-center gap-2 text-xs">
                <Mail className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                <span className="text-slate-500 dark:text-slate-400">Email:</span>
                {renderOrNotFound(resume.email)}
              </div>

              <div className="flex items-center gap-2 text-xs">
                <Phone className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                <span className="text-slate-500 dark:text-slate-400">Phone:</span>
                {renderOrNotFound(resume.phone)}
              </div>

              <div className="flex items-center gap-2 text-xs">
                <GraduationCap className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                <span className="text-slate-500 dark:text-slate-400">Degree:</span>
                {renderOrNotFound(resume.degree)}
              </div>

              <div className="flex items-center gap-2 text-xs">
                <MapPin className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                <span className="text-slate-500 dark:text-slate-400">College:</span>
                {renderOrNotFound(resume.college)}
              </div>
            </div>
            
            {/* Social Links */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              {resume.linkedin && resume.linkedin !== "Not Found" && (
                <a href={resume.linkedin.startsWith('http') ? resume.linkedin : `https://${resume.linkedin}`} target="_blank" rel="noopener noreferrer" className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline">
                  LinkedIn ↗
                </a>
              )}
              {resume.github && resume.github !== "Not Found" && (
                <a href={resume.github.startsWith('http') ? resume.github : `https://${resume.github}`} target="_blank" rel="noopener noreferrer" className="text-xs font-medium text-slate-700 dark:text-slate-300 hover:underline">
                  GitHub ↗
                </a>
              )}
              {resume.portfolio && resume.portfolio !== "Not Found" && (
                <a href={resume.portfolio.startsWith('http') ? resume.portfolio : `https://${resume.portfolio}`} target="_blank" rel="noopener noreferrer" className="text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-1">
                  <Globe className="w-3 h-3" /> Portfolio ↗
                </a>
              )}
            </div>
          </div>
          
          {/* Profile Completion Score */}
          <div className="flex flex-col items-center justify-center p-4 bg-slate-50 dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-700/80 shrink-0">
            <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Completeness</span>
            <div className="relative flex items-center justify-center w-16 h-16">
              <svg className="w-16 h-16 transform -rotate-90">
                <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="6" fill="transparent" className="text-slate-200 dark:text-slate-700" />
                <circle 
                  cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="6" fill="transparent" 
                  strokeDasharray={175.9} strokeDashoffset={175.9 - (175.9 * (resume.completion_score || 50)) / 100}
                  className={`${(resume.completion_score || 50) >= 70 ? 'text-emerald-500' : (resume.completion_score || 50) >= 40 ? 'text-amber-500' : 'text-red-500'} transition-all duration-1000 ease-out`} 
                />
              </svg>
              <span className="absolute text-sm font-bold text-slate-800 dark:text-slate-100">{resume.completion_score || 0}%</span>
            </div>
          </div>
        </div>

        {/* Categorized Skills Breakdown */}
        <div className="space-y-4">
          <h3 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Code2 className="w-4 h-4 text-indigo-500" />
            Extracted Technical Competencies
          </h3>

          {/* Languages & Frameworks */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="p-3 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-100 dark:border-slate-700/60">
              <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block mb-1.5">Languages:</span>
              <div className="flex flex-wrap gap-1">
                {resume.languages_prog && resume.languages_prog.length > 0 ? (
                  resume.languages_prog.map((l, i) => (
                    <span key={i} className="px-2 py-0.5 text-[11px] bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 rounded-md shadow-2xs border border-indigo-100 dark:border-indigo-900/40 font-mono">
                      {l}
                    </span>
                  ))
                ) : (
                  <span className="text-[11px] text-slate-400 italic">None extracted</span>
                )}
              </div>
            </div>

            <div className="p-3 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-100 dark:border-slate-700/60">
              <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block mb-1.5">Frameworks & Libraries:</span>
              <div className="flex flex-wrap gap-1">
                {resume.frameworks && resume.frameworks.length > 0 ? (
                  resume.frameworks.map((f, i) => (
                    <span key={i} className="px-2 py-0.5 text-[11px] bg-white dark:bg-slate-800 text-purple-600 dark:text-purple-400 rounded-md shadow-2xs border border-purple-100 dark:border-purple-900/40">
                      {f}
                    </span>
                  ))
                ) : (
                  <span className="text-[11px] text-slate-400 italic">None extracted</span>
                )}
              </div>
            </div>
          </div>

          {/* Databases, Cloud & Tools */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-100 dark:border-slate-700/60">
              <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block mb-1">Databases:</span>
              <div className="flex flex-wrap gap-1">
                {resume.databases && resume.databases.length > 0 ? (
                  resume.databases.map((d, i) => <span key={i} className="px-2 py-0.5 text-[10px] bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 rounded">{d}</span>)
                ) : <span className="text-[10px] text-slate-400 italic">None</span>}
              </div>
            </div>

            <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-100 dark:border-slate-700/60">
              <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block mb-1">Cloud / DevOps:</span>
              <div className="flex flex-wrap gap-1">
                {resume.cloud && resume.cloud.length > 0 ? (
                  resume.cloud.map((c, i) => <span key={i} className="px-2 py-0.5 text-[10px] bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 rounded">{c}</span>)
                ) : <span className="text-[10px] text-slate-400 italic">None</span>}
              </div>
            </div>

            <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-100 dark:border-slate-700/60">
              <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block mb-1">Developer Tools:</span>
              <div className="flex flex-wrap gap-1">
                {resume.tools && resume.tools.length > 0 ? (
                  resume.tools.map((t, i) => <span key={i} className="px-2 py-0.5 text-[10px] bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 rounded">{t}</span>)
                ) : <span className="text-[10px] text-slate-400 italic">None</span>}
              </div>
            </div>
          </div>
        </div>

        {/* Experience & Projects Sections */}
        <div className="space-y-4 pt-2">
          {resume.experience && resume.experience.length > 0 && (
            <div>
              <h3 className="flex items-center text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
                <Briefcase className="w-3.5 h-3.5 mr-1.5 text-indigo-500" /> Work Experience
              </h3>
              <ul className="space-y-1.5">
                {resume.experience.map((item, i) => (
                  <li key={i} className="text-xs text-slate-600 dark:text-slate-300 flex items-start leading-relaxed">
                    <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 mr-2 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {resume.projects && resume.projects.length > 0 && (
            <div>
              <h3 className="flex items-center text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
                <Layers className="w-3.5 h-3.5 mr-1.5 text-indigo-500" /> Key Projects
              </h3>
              <ul className="space-y-1.5">
                {resume.projects.map((item, i) => (
                  <li key={i} className="text-xs text-slate-600 dark:text-slate-300 flex items-start leading-relaxed">
                    <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-1.5 mr-2 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {resume.achievements && resume.achievements.length > 0 && (
            <div>
              <h3 className="flex items-center text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                <Award className="w-3.5 h-3.5 mr-1.5 text-amber-500" /> Achievements & Honors
              </h3>
              <ul className="space-y-1">
                {resume.achievements.map((item, i) => (
                  <li key={i} className="text-xs text-slate-600 dark:text-slate-300 flex items-center gap-1.5">
                    <span className="w-1 h-1 bg-amber-400 rounded-full" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

      </div>
    </motion.div>
  );
};

export default ProfileCard;
