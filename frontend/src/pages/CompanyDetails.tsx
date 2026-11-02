import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { ArrowLeft, Building2, BookOpen } from 'lucide-react';
import QuestionViewer from '../components/QuestionViewer';

interface CompanyStats {
  total_questions: number;
  easy: number;
  medium: number;
  hard: number;
}

interface Company {
  id: string;
  company_name: string;
  company_logo: string;
  description: string;
  topics: string[];
}

const CompanyDetails = () => {
  const { companyName } = useParams();
  const navigate = useNavigate();
  const [company, setCompany] = useState<Company | null>(null);
  const [stats, setStats] = useState<CompanyStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCompanyData = async () => {
      try {
        const [compRes, statsRes] = await Promise.all([
          api.get(`/company/${companyName}`),
          api.get(`/company/${companyName}/stats`)
        ]);
        setCompany(compRes.data);
        setStats(statsRes.data);
      } catch (error) {
        console.error('Failed to fetch company details', error);
      } finally {
        setLoading(false);
      }
    };
    if (companyName) {
      fetchCompanyData();
    }
  }, [companyName]);

  if (loading) {
    return <div className="p-8 flex justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div></div>;
  }

  if (!company) {
    return (
      <div className="p-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Company Not Found</h2>
        <button onClick={() => navigate('/companies')} className="text-indigo-600 hover:underline">Return to Companies</button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in">
      <button 
        onClick={() => navigate('/companies')}
        className="flex items-center text-gray-500 hover:text-indigo-600 transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-2" /> Back to Companies
      </button>

      {/* Header Profile */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-sm border border-gray-100 dark:border-gray-700 flex flex-col md:flex-row items-start md:items-center gap-8 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>
        
        <div className="w-32 h-32 rounded-2xl bg-gray-50 dark:bg-gray-700 flex flex-shrink-0 items-center justify-center p-4 border border-gray-100 dark:border-gray-600">
          {company.company_logo ? (
            <img src={company.company_logo} alt={company.company_name} className="w-full h-full object-contain" />
          ) : (
            <Building2 className="w-16 h-16 text-gray-400" />
          )}
        </div>

        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{company.company_name}</h1>
          <p className="text-gray-500 dark:text-gray-400 mb-6">{company.description}</p>
          
          {/* Stats Row */}
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 px-4 py-2 rounded-lg font-medium">
              <BookOpen className="w-5 h-5 mr-2" /> {stats?.total_questions} Questions
            </div>
            {(stats?.easy ?? 0) > 0 && (
              <div className="flex items-center bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-4 py-2 rounded-lg font-medium">
                 Easy: {stats?.easy}
              </div>
            )}
            {(stats?.medium ?? 0) > 0 && (
              <div className="flex items-center bg-yellow-50 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 px-4 py-2 rounded-lg font-medium">
                 Medium: {stats?.medium}
              </div>
            )}
            {(stats?.hard ?? 0) > 0 && (
              <div className="flex items-center bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300 px-4 py-2 rounded-lg font-medium">
                 Hard: {stats?.hard}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Question Viewer */}
      <QuestionViewer companyName={company.company_name} />
      
    </div>
  );
};

export default CompanyDetails;
