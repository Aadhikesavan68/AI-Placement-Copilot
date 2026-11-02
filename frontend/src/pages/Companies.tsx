import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Search, Building2, BookOpen } from 'lucide-react';

interface Company {
  id: string;
  company_name: string;
  company_logo: string;
  total_questions: number;
  topics: string[];
}

const Companies = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        const response = await api.get('/company/all');
        setCompanies(response.data);
      } catch (error) {
        console.error('Failed to fetch companies', error);
      } finally {
        setLoading(false);
      }
    };
    fetchCompanies();
  }, []);

  const handleSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearch(query);
    try {
      const response = await api.get(`/company/search?q=${query}`);
      setCompanies(response.data);
    } catch (error) {
      console.error('Failed to search companies', error);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Companies</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Explore interview questions from top tech companies</p>
        </div>
        
        <div className="relative w-full md:w-96">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white dark:bg-gray-800 dark:border-gray-700 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:text-sm transition-all"
            placeholder="Search companies..."
            value={search}
            onChange={handleSearch}
          />
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
            <div key={i} className="animate-pulse bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 h-48"></div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {companies.map((company) => (
            <div 
              key={company.id} 
              onClick={() => navigate(`/company/${company.company_name.toLowerCase()}`)}
              className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-lg hover:border-indigo-500 transition-all cursor-pointer group flex flex-col items-center text-center"
            >
              <div className="w-16 h-16 mb-4 rounded-xl bg-gray-50 dark:bg-gray-700 flex items-center justify-center overflow-hidden border border-gray-100 dark:border-gray-600 group-hover:scale-105 transition-transform">
                {company.company_logo ? (
                  <img src={company.company_logo} alt={company.company_name} className="w-10 h-10 object-contain" />
                ) : (
                  <Building2 className="w-8 h-8 text-gray-400" />
                )}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                {company.company_name}
              </h3>
              <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mt-2 bg-gray-50 dark:bg-gray-700/50 px-3 py-1 rounded-full">
                <BookOpen className="w-4 h-4 mr-2" />
                {company.total_questions} Questions
              </div>
            </div>
          ))}
        </div>
      )}
      
      {!loading && companies.length === 0 && (
        <div className="text-center py-20">
          <Building2 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">No companies found</h3>
          <p className="mt-1 text-gray-500 dark:text-gray-400">Try adjusting your search query.</p>
        </div>
      )}
    </div>
  );
};

export default Companies;
