import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminLayout from '../../components/layout/AdminLayout';
import apiClient from '../../api/client';
import { useAuthStore } from '../../store/authStore';

export default function TestManagement() {
  const navigate = useNavigate();
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetchTests();
  }, []);
  
  const fetchTests = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/admin/tests');
      
      // Ensure response.data is an array
      const testsData = Array.isArray(response.data) ? response.data : [];
      setTests(testsData);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch tests:', err);
      setError('Failed to load tests. Please try again later.');
      setTests([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };
  
  const toggleStatus = async (testId, currentStatus) => {
    try {
      const endpoint = currentStatus ? 'unpublish' : 'publish';
      await apiClient.post(`/tests/templates/${testId}/${endpoint}`);
      
      // Update local state
      setTests(tests.map(test => 
        test.id === testId ? { ...test, is_published: !currentStatus } : test
      ));
    } catch (err) {
      console.error('Failed to toggle test status:', err);
      alert(err.response?.data?.detail || 'Failed to update test status');
    }
  };
  
  const handleDeleteTest = async (testId) => {
    if (!confirm('Are you sure you want to delete this test? This action cannot be undone.')) return;
    
    try {
      await apiClient.delete(`/tests/templates/${testId}`);
      
      setTests(tests.filter(t => t.id !== testId));
    } catch (err) {
      console.error('Failed to delete test:', err);
      alert(err.response?.data?.detail || 'Failed to delete test');
    }
  };
  
  if (loading) {
    return (
      <AdminLayout>
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Test Management</h1>
          <div className="text-center py-12">
            <div className="text-lg text-gray-600">Loading tests...</div>
          </div>
        </div>
      </AdminLayout>
    );
  }
  
  if (error) {
    return (
      <AdminLayout>
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Test Management</h1>
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
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Test Management</h1>
            <div className="text-sm text-gray-600 mt-1">
              {tests.length} total tests
            </div>
          </div>
          <button 
            onClick={() => navigate('/admin/tests/create')}
            className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg font-medium transition flex items-center"
          >
            <span className="mr-2">+</span> Create Test
          </button>
        </div>
        
        {/* Tests Grid */}
        {tests.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <div className="text-gray-500">
              <p className="text-lg mb-2">No tests created yet</p>
              <p className="text-sm">Create your first test to get started</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            {tests.map((test) => (
              <div key={test.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{test.title}</h3>
                    {test.description && (
                      <p className="text-sm text-gray-600 mt-1">{test.description}</p>
                    )}
                    <div className="flex items-center space-x-3 mt-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        test.test_type === 'academic'
                          ? 'bg-primary-100 text-primary-700'
                          : 'bg-purple-100 text-purple-700'
                      }`}>
                        {test.test_type === 'academic' ? 'Academic' : 'General Training'}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        test.is_published
                          ? 'bg-green-100 text-green-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {test.is_published ? 'Published' : 'Draft'}
                      </span>
                      {test.difficulty_level && (
                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 capitalize">
                          {test.difficulty_level}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => navigate(`/admin/tests/${test.id}/edit`)}
                      className="px-4 py-2 rounded-lg font-medium text-sm transition bg-gray-100 text-gray-700 hover:bg-gray-200"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => toggleStatus(test.id, test.is_published)}
                      className={`px-4 py-2 rounded-lg font-medium text-sm transition ${
                        test.is_published
                          ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}
                    >
                      {test.is_published ? 'Unpublish' : 'Publish'}
                    </button>
                    <button 
                      onClick={() => handleDeleteTest(test.id)}
                      className="text-red-600 hover:text-red-700 px-4 py-2 font-medium text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-200">
                  <div>
                    <p className="text-xs text-gray-500">Duration</p>
                    <p className="text-lg font-bold text-gray-900">{test.duration_minutes} min</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Created</p>
                    <p className="text-sm font-medium text-gray-700">
                      {new Date(test.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Test ID</p>
                    <p className="text-sm font-medium text-gray-700">#{test.id}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
