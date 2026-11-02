import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, AlertCircle, Loader2, CheckCircle2, FileText, ClipboardPaste, Sparkles, X, RotateCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import toast from 'react-hot-toast';

interface JobDescriptionUploadProps {
  onUploadSuccess: (data: any) => void;
}

const JobDescriptionUpload: React.FC<JobDescriptionUploadProps> = ({ onUploadSuccess }) => {
  const [activeTab, setActiveTab] = useState<'file' | 'text'>('file');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [pastedText, setPastedText] = useState('');
  const [jobTitle, setJobTitle] = useState('');

  // File Drop Handler
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      const err = 'File size exceeds 10MB limit.';
      setUploadError(err);
      toast.error(err);
      return;
    }

    setUploadError(null);
    setIsUploading(true);
    setUploadProgress(20);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/job/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(Math.max(25, percent));
          }
        },
      });

      setUploadProgress(100);
      toast.success('Job Description uploaded and parsed successfully!');
      onUploadSuccess(response.data);
    } catch (error: any) {
      console.error('JD Upload error:', error);
      const errMsg = error.response?.data?.detail?.message || error.response?.data?.detail || 'Failed to upload job description.';
      setUploadError(errMsg);
      toast.error(errMsg);
    } finally {
      setIsUploading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive, isDragReject, open } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: isUploading,
  });

  // Handle Pasted Text Submit
  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pastedText.trim()) {
      toast.error('Please paste a job description first.');
      return;
    }

    setUploadError(null);
    setIsUploading(true);
    try {
      const response = await api.post('/job/upload', {
        title: jobTitle.trim() || undefined,
        text: pastedText.trim(),
      });

      toast.success('Job Description parsed and saved successfully!');
      onUploadSuccess(response.data);
      setPastedText('');
      setJobTitle('');
    } catch (error: any) {
      console.error('JD Paste error:', error);
      const errMsg = error.response?.data?.detail?.message || error.response?.data?.detail || 'Failed to parse job description.';
      setUploadError(errMsg);
      toast.error(errMsg);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full bg-white dark:bg-slate-800 rounded-2xl shadow-xs border border-slate-200 dark:border-slate-700 p-5 md:p-6"
    >
      {/* Header & Tabs */}
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-700 pb-4 mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-500" />
            Job Description (JD)
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Upload file or paste JD text to match requirements
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex bg-slate-100 dark:bg-slate-900/80 p-1 rounded-xl">
          <button
            type="button"
            onClick={() => { setActiveTab('file'); setUploadError(null); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'file'
                ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            Upload File
          </button>
          <button
            type="button"
            onClick={() => { setActiveTab('text'); setUploadError(null); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'text'
                ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <ClipboardPaste className="w-3.5 h-3.5" />
            Paste Text
          </button>
        </div>
      </div>

      {/* Tab 1: File Dropzone */}
      {activeTab === 'file' ? (
        <div
          {...getRootProps()}
          className={`relative p-6 md:p-8 w-full rounded-xl border-2 border-dashed transition-all duration-300 ease-in-out cursor-pointer overflow-hidden text-center
            ${
              isDragActive
                ? 'border-purple-500 bg-purple-50/80 dark:bg-purple-950/40 scale-[1.01]'
                : 'border-slate-300 dark:border-slate-700 hover:border-purple-400 hover:bg-slate-50/80 dark:hover:bg-slate-800/60'
            }
            ${isDragReject ? 'border-red-500 bg-red-50 dark:bg-red-950/30' : ''}
            ${uploadError ? 'border-red-300 dark:border-red-800 bg-red-50/40 dark:bg-red-950/20' : ''}
            ${isUploading ? 'pointer-events-none opacity-90' : ''}
          `}
        >
          <input {...getInputProps()} />

          <div className="flex flex-col items-center justify-center space-y-3 z-10 relative">
            <div className={`p-3.5 rounded-2xl transition-colors ${
              isUploading 
                ? 'bg-purple-100 text-purple-600 dark:bg-purple-900/60 dark:text-purple-400' 
                : uploadError
                ? 'bg-red-100 text-red-600 dark:bg-red-900/50'
                : isDragActive 
                ? 'bg-purple-100 text-purple-600 dark:bg-purple-900/50' 
                : 'bg-purple-50 text-purple-600 dark:bg-slate-800 dark:text-purple-400'
            }`}>
              {isUploading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : uploadError ? (
                <AlertCircle className="w-6 h-6 text-red-500" />
              ) : isDragActive ? (
                <CheckCircle2 className="w-6 h-6 text-purple-500" />
              ) : (
                <UploadCloud className="w-6 h-6" />
              )}
            </div>

            <div>
              <h4 className="text-base font-semibold text-slate-900 dark:text-white">
                {isUploading
                  ? 'Parsing Job Description...'
                  : isDragActive
                  ? 'Drop JD file here!'
                  : uploadError
                  ? 'Failed to Parse JD'
                  : 'Upload Job Description File'}
              </h4>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
                {isUploading
                  ? 'Extracting required skills, technologies, experience & responsibilities...'
                  : uploadError
                  ? uploadError
                  : 'Drag & drop PDF, DOCX, or TXT file here, or click to browse.'}
              </p>

              <div className="mt-2 flex items-center justify-center gap-1.5">
                <span className="px-2 py-0.5 text-[10px] font-bold bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-300 rounded border border-purple-100 dark:border-purple-900">
                  PDF
                </span>
                <span className="px-2 py-0.5 text-[10px] font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 rounded border border-indigo-100 dark:border-indigo-900">
                  DOCX
                </span>
                <span className="px-2 py-0.5 text-[10px] font-bold bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded">
                  TXT
                </span>
                <span className="text-[10px] text-slate-400 ml-1">
                  Max 10MB
                </span>
              </div>
            </div>

            {uploadError && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setUploadError(null);
                  open();
                }}
                className="mt-1 inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors cursor-pointer"
              >
                <RotateCw className="w-3.5 h-3.5" />
                Try Again
              </button>
            )}
          </div>

          {/* Progress Bar */}
          <AnimatePresence>
            {isUploading && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="absolute bottom-0 left-0 w-full h-1.5 bg-slate-200 dark:bg-slate-700"
              >
                <motion.div
                  className="h-full bg-gradient-to-r from-purple-500 to-indigo-600"
                  initial={{ width: '0%' }}
                  animate={{ width: `${uploadProgress}%` }}
                  transition={{ ease: 'easeInOut', duration: 0.3 }}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ) : (
        /* Tab 2: Paste Text Form */
        <form onSubmit={handleTextSubmit} className="space-y-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Target Role / Position Title (Optional)
            </label>
            <input
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="e.g. Senior Full Stack Engineer"
              disabled={isUploading}
              className="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-slate-900 dark:text-white placeholder-slate-400"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">
                Paste Full Job Description Text *
              </label>
              {pastedText && (
                <button
                  type="button"
                  onClick={() => setPastedText('')}
                  className="text-[11px] text-slate-400 hover:text-red-500 flex items-center gap-0.5 cursor-pointer"
                >
                  <X className="w-3 h-3" /> Clear
                </button>
              )}
            </div>
            <textarea
              rows={4}
              value={pastedText}
              onChange={(e) => setPastedText(e.target.value)}
              placeholder="Paste the full job posting here (responsibilities, required skills, tools, qualification)..."
              disabled={isUploading}
              required
              className="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-slate-900 dark:text-white placeholder-slate-400 font-mono resize-none leading-relaxed"
            />
          </div>

          <div className="flex items-center justify-between pt-1">
            <span className="text-[11px] text-slate-400 dark:text-slate-500">
              {pastedText.length} characters
            </span>
            <button
              type="submit"
              disabled={isUploading || !pastedText.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 text-white rounded-xl text-xs font-semibold shadow-sm transition-all cursor-pointer disabled:cursor-not-allowed"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  Parsing JD...
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  Parse & Save JD
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </motion.div>
  );
};

export default JobDescriptionUpload;
