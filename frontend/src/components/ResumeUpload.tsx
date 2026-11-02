import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, AlertCircle, Loader2, CheckCircle2, RotateCw, FileCheck } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import toast from 'react-hot-toast';

interface ResumeUploadProps {
  onUploadSuccess: (data: any) => void;
}

const ResumeUpload: React.FC<ResumeUploadProps> = ({ onUploadSuccess }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [lastUploadedFile, setLastUploadedFile] = useState<string | null>(null);

  const processFile = async (file: File) => {
    if (file.size > 10 * 1024 * 1024) {
      const err = 'File size exceeds the 10MB limit. Please upload a smaller file.';
      setUploadError(err);
      toast.error(err);
      return;
    }

    setUploadError(null);
    setIsUploading(true);
    setUploadProgress(15);
    setLastUploadedFile(file.name);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/resume/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(Math.max(20, percentCompleted));
          }
        },
      });

      setUploadProgress(100);
      toast.success('Resume parsed successfully!');
      onUploadSuccess(response.data);
    } catch (error: any) {
      console.error('Upload error', error);
      const errMsg = error.response?.data?.detail?.message || error.response?.data?.detail || 'Failed to parse resume. Please ensure the file is not password protected.';
      setUploadError(errMsg);
      toast.error(errMsg);
    } finally {
      setIsUploading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;
    await processFile(file);
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive, isDragReject, open } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    disabled: isUploading,
    noClick: false,
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full"
    >
      <div
        {...getRootProps()}
        className={`relative p-6 md:p-8 w-full rounded-2xl border-2 border-dashed transition-all duration-300 ease-in-out cursor-pointer overflow-hidden
          ${isDragActive ? 'border-indigo-500 bg-indigo-50/80 dark:bg-indigo-950/40 scale-[1.01]' : 'border-slate-300 dark:border-slate-700 hover:border-indigo-400 hover:bg-slate-50/80 dark:hover:bg-slate-800/60'}
          ${isDragReject ? 'border-red-500 bg-red-50 dark:bg-red-950/30' : ''}
          ${uploadError ? 'border-red-300 dark:border-red-800 bg-red-50/40 dark:bg-red-950/20' : ''}
          ${isUploading ? 'pointer-events-none opacity-90' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center justify-center space-y-3.5 text-center z-10 relative">
          <div className={`p-3.5 rounded-2xl transition-colors ${
            isUploading 
              ? 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/60 dark:text-indigo-400' 
              : uploadError 
              ? 'bg-red-100 text-red-600 dark:bg-red-900/50 dark:text-red-400' 
              : isDragActive 
              ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/50' 
              : lastUploadedFile 
              ? 'bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400'
              : 'bg-indigo-50 text-indigo-600 dark:bg-slate-800 dark:text-indigo-400'
          }`}>
            {isUploading ? (
              <Loader2 className="w-7 h-7 animate-spin" />
            ) : uploadError ? (
              <AlertCircle className="w-7 h-7 text-red-500" />
            ) : isDragActive ? (
              <CheckCircle2 className="w-7 h-7 text-emerald-500" />
            ) : lastUploadedFile ? (
              <FileCheck className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
            ) : (
              <UploadCloud className="w-7 h-7" />
            )}
          </div>
          
          <div>
            <h3 className="text-base font-semibold text-slate-900 dark:text-white">
              {isUploading
                ? 'Parsing Resume & Extracting Skills...'
                : isDragActive
                ? 'Drop your Resume here!'
                : uploadError
                ? 'Extraction Failed'
                : 'Upload Candidate Resume'}
            </h3>
            
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
              {isUploading
                ? 'Analyzing education, experience, achievements, and technical stack...'
                : uploadError
                ? uploadError
                : 'Drag and drop your PDF or DOCX resume here, or click to browse files.'}
            </p>

            <div className="mt-2.5 flex items-center justify-center gap-1.5">
              <span className="px-2 py-0.5 text-[10px] font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 rounded border border-indigo-100 dark:border-indigo-900">
                PDF
              </span>
              <span className="px-2 py-0.5 text-[10px] font-bold bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-300 rounded border border-purple-100 dark:border-purple-900">
                DOCX
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
              className="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors cursor-pointer"
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
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-600"
                initial={{ width: '0%' }}
                animate={{ width: `${uploadProgress}%` }}
                transition={{ ease: "easeInOut", duration: 0.3 }}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default ResumeUpload;
