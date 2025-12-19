import { useAuthStore } from '../../store/authStore';
import MainLayout from '../../components/layout/MainLayout';
import StatsCard from '../../components/student/StatsCard';
import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import axios from 'axios';

export default function StudentDashboard() {
  const { user, token } = useAuthStore();
  
  const [stats, setStats] = useState(null);
  const [recentTests, setRecentTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch student stats
        const statsResponse = await axios.get('/api/v1/users/me/stats', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStats(statsResponse.data);
        
        // Fetch recent test attempts (placeholder - endpoint may need to be created)
        setRecentTests([]);  // Will be populated when test attempts endpoint is available
        
        setError(null);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    if (token) {
      fetchDashboardData();
    }
  }, [token]);
  
  if (loading) {
    return (
      <MainLayout>
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="text-lg text-gray-600">Loading dashboard...</div>
          </div>
        </div>
      </MainLayout>
    );
  }
  
  if (error) {
    return (
      <MainLayout>
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </MainLayout>
    );
  }
  
  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.full_name}! 👋
          </h1>
          <p className="text-gray-600 mt-2">
            Track your progress and continue your IELTS preparation journey
          </p>
        </div>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Tests Completed"
            value={stats?.tests_completed || 0}
            icon="📝"
            color="primary"
          />
          <StatsCard
            title="Average Score"
            value={stats?.average_score || '-'}
            icon="⭐"
            color="green"
          />
          <StatsCard
            title="Hours Studied"
            value={stats?.hours_studied || 0}
            icon="⏱️"
            color="blue"
          />
          <StatsCard
            title="Current Streak"
            value={stats?.current_streak ? `${stats.current_streak} days` : '0 days'}
            icon="🔥"
            color="purple"
          />
        </div>
        
        {/* Quick Actions */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl shadow-lg p-8 mb-8 text-white">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold mb-2">Ready for your next test?</h2>
              <p className="text-primary-100">
                {stats?.next_test ? `Continue with: ${stats.next_test}` : 'Practice with full-length mock tests and improve your band score'}
              </p>
            </div>
            <Link
              to="/student/tests"
              className="bg-white text-primary-600 hover:bg-gray-50 px-6 py-3 rounded-lg font-semibold transition shadow-lg"
            >
              Browse Tests
            </Link>
          </div>
        </div>
        
        {/* Recent Tests */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">Recent Test Attempts</h2>
            <Link
              to="/student/results"
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              View All →
            </Link>
          </div>
          
          <div className="space-y-4">
            {recentTests.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No test attempts yet. Start your first test!
              </div>
            ) : (
              recentTests.map((test) => (
                <div
                  key={test.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                      <span className="text-primary-600 font-bold text-lg">
                        {test.score || '?'}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{test.name}</h3>
                      <p className="text-sm text-gray-600">{test.date}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <span className={`
                      px-3 py-1 rounded-full text-xs font-medium
                      ${test.status === 'Graded' 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-yellow-100 text-yellow-700'
                      }
                    `}>
                      {test.status}
                    </span>
                    <button className="text-primary-600 hover:text-primary-700 font-medium text-sm">
                      View Details
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
