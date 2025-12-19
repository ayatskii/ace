import AdminLayout from '../../components/layout/AdminLayout';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuthStore } from '../../store/authStore';

export default function AdminDashboard() {
  const { token } = useAuthStore();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/v1/admin/stats', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStats(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch admin stats:', err);
        setError('Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    
    if (token) {
      fetchStats();
    }
  }, [token]);
  
  if (loading) {
    return (
      <AdminLayout>
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="text-lg text-gray-600">Loading dashboard...</div>
          </div>
        </div>
      </AdminLayout>
    );
  }
  
  if (error) {
    return (
      <AdminLayout>
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </AdminLayout>
    );
  }
  
  return (
    <AdminLayout>
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.total_users || 0}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {stats?.total_students || 0} students, {stats?.total_teachers || 0} teachers
                </p>
              </div>
              <div className="p-3 rounded-lg bg-primary-50 text-primary-600">
                <span className="text-2xl">👥</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Test Templates</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.total_tests || 0}</p>
                <p className="text-xs text-gray-500 mt-1">{stats?.active_tests || 0} active</p>
              </div>
              <div className="p-3 rounded-lg bg-green-50 text-green-600">
                <span className="text-2xl">📝</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Test Attempts</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.completed_attempts || 0}</p>
                <p className="text-xs text-gray-500 mt-1">All time</p>
              </div>
              <div className="p-3 rounded-lg bg-blue-50 text-blue-600">
                <span className="text-2xl">📊</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <a
            href="/admin/users"
            className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl shadow-lg p-8 text-white hover:shadow-xl transition block"
          >
            <h2 className="text-2xl font-bold mb-2">Manage Users</h2>
            <p className="text-primary-100 mb-4">View, edit, and manage all platform users</p>
            <div className="flex items-center text-sm font-semibold">
              <span>Go to Users</span>
              <span className="ml-2">→</span>
            </div>
          </a>
          
          <a
            href="/admin/tests"
            className="bg-gradient-to-r from-green-600 to-green-700 rounded-xl shadow-lg p-8 text-white hover:shadow-xl transition block"
          >
            <h2 className="text-2xl font-bold mb-2">Manage Tests</h2>
            <p className="text-green-100 mb-4">Create, edit, and publish test templates</p>
            <div className="flex items-center text-sm font-semibold">
              <span>Go to Tests</span>
              <span className="ml-2">→</span>
            </div>
          </a>
        </div>
        
        {/* Recent Activity - keeping static for now */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h2>
          <div className="text-center py-8 text-gray-500">
            Activity log coming soon
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
