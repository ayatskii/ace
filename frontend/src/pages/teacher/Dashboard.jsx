import { useAuthStore } from '../../store/authStore';
import TeacherLayout from '../../components/layout/TeacherLayout';
import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import axios from 'axios';

export default function TeacherDashboard() {
  const { user, token } = useAuthStore();
  
  const [queueData, setQueueData] = useState(null);
  const [statsData, setStatsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch grading queue
        const queueResponse = await axios.get('/api/v1/grading/queue', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setQueueData(queueResponse.data);
        
        // Fetch stats
        const statsResponse = await axios.get('/api/v1/grading/stats', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStatsData(statsResponse.data);
        
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
      <TeacherLayout>
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="text-lg text-gray-600">Loading dashboard...</div>
          </div>
        </div>
      </TeacherLayout>
    );
  }
  
  if (error) {
    return (
      <TeacherLayout>
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </TeacherLayout>
    );
  }
  
  const pendingWriting = queueData?.pending_writing || 0;
  const pendingSpeaking = queueData?.pending_speaking || 0;
  const gradedToday = statsData?.graded_today || 0;
  const avgGradingTime = statsData?.avg_grading_time || '15 min';
  const recentSubmissions = queueData?.recent_submissions || [];
  
  return (
    <TeacherLayout>
      <div className="max-w-7xl mx-auto">
        {/* Welcome */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.full_name}! 👋
          </h1>
          <p className="text-gray-600 mt-2">Here's your grading overview for today</p>
        </div>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending Writing</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{pendingWriting}</p>
              </div>
              <div className="p-3 rounded-lg bg-yellow-50 text-yellow-600">
                <span className="text-2xl">✍️</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending Speaking</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{pendingSpeaking}</p>
              </div>
              <div className="p-3 rounded-lg bg-purple-50 text-purple-600">
                <span className="text-2xl">🎤</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Graded Today</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{gradedToday}</p>
              </div>
              <div className="p-3 rounded-lg bg-green-50 text-green-600">
                <span className="text-2xl">✅</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg. Time</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{avgGradingTime}</p>
              </div>
              <div className="p-3 rounded-lg bg-blue-50 text-blue-600">
                <span className="text-2xl">⏱️</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Link
            to="/teacher/grading/writing"
            className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl shadow-lg p-8 text-white hover:shadow-xl transition"
          >
            <h2 className="text-2xl font-bold mb-2">Grade Writing Submissions</h2>
            <p className="text-primary-100 mb-4">{pendingWriting} submissions waiting</p>
            <div className="flex items-center text-sm font-semibold">
              <span>Start Grading</span>
              <span className="ml-2">→</span>
            </div>
          </Link>
          
          <Link
            to="/teacher/grading/speaking"
            className="bg-gradient-to-r from-purple-600 to-purple-700 rounded-xl shadow-lg p-8 text-white hover:shadow-xl transition"
          >
            <h2 className="text-2xl font-bold mb-2">Grade Speaking Submissions</h2>
            <p className="text-purple-100 mb-4">{pendingSpeaking} submissions waiting</p>
            <div className="flex items-center text-sm font-semibold">
              <span>Start Grading</span>
              <span className="ml-2">→</span>
            </div>
          </Link>
        </div>
        
        {/* Recent Submissions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">Recent Submissions</h2>
            <Link to="/teacher/history" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View All →
            </Link>
          </div>
          
          <div className="space-y-3">
            {recentSubmissions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No pending submissions
              </div>
            ) : (
              recentSubmissions.map((submission) => (
                <div
                  key={submission.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                      submission.type === 'Writing' ? 'bg-yellow-100' : 'bg-purple-100'
                    }`}>
                      <span className="text-2xl">{submission.type === 'Writing' ? '✍️' : '🎤'}</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{submission.student}</h3>
                      <p className="text-sm text-gray-600">{submission.type} - {submission.task}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-500">{submission.submitted}</span>
                    <button className="text-primary-600 hover:text-primary-700 font-medium text-sm">
                      Grade Now
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </TeacherLayout>
  );
}
