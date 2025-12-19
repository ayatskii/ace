import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AdminLayout from '../../components/layout/AdminLayout';
import apiClient from '../../api/client';
import ListeningEditor from './editors/ListeningEditor';
import ReadingEditor from './editors/ReadingEditor';
import WritingEditor from './editors/WritingEditor';
import SpeakingEditor from './editors/SpeakingEditor';

export default function TestEditor() {
  const { testId } = useParams();
  const navigate = useNavigate();
  const [test, setTest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('sections');
  const [editingSection, setEditingSection] = useState(null);

  useEffect(() => {
    fetchTestDetails();
  }, [testId]);

  const fetchTestDetails = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/tests/templates/${testId}`);
      setTest(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch test details:', err);
      setError('Failed to load test details.');
    } finally {
      setLoading(false);
    }
  };

  const [showAddSection, setShowAddSection] = useState(false);
  const [newSection, setNewSection] = useState({
    section_type: 'listening',
    order: 1,
    total_questions: 10,
    duration_minutes: 30
  });

  const handleAddSection = async (e) => {
    e.preventDefault();
    try {
      await apiClient.post('/tests/sections', {
        ...newSection,
        test_template_id: parseInt(testId)
      });
      setShowAddSection(false);
      fetchTestDetails();
    } catch (err) {
      console.error('Failed to add section:', err);
      alert('Failed to add section');
    }
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-500">Loading test editor...</div>
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
          <button
            onClick={() => navigate('/admin/tests')}
            className="mt-4 text-primary-600 hover:text-primary-700 font-medium"
          >
            ← Back to Tests
          </button>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <div className="flex items-center text-sm text-gray-500 mb-1">
              <button 
                onClick={() => navigate('/admin/tests')}
                className="hover:text-gray-700"
              >
                Tests
              </button>
              <span className="mx-2">/</span>
              <span>Edit Test</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900">{test.title}</h1>
            <div className="flex items-center mt-2 space-x-4 text-sm text-gray-600">
              <span className="capitalize px-2 py-0.5 rounded bg-gray-100">
                {test.test_type.replace('_', ' ')}
              </span>
              <span>{test.duration_minutes} mins</span>
              <span className={`px-2 py-0.5 rounded ${
                test.is_published ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {test.is_published ? 'Published' : 'Draft'}
              </span>
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => window.open(`/student/tests/${testId}`, '_blank')}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Preview
            </button>
            <button
              onClick={() => navigate('/admin/tests')}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Done
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden min-h-[600px]">
          <div className="border-b border-gray-200">
            <nav className="flex">
              {['settings', 'sections', 'publish'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-6 py-4 text-sm font-medium capitalize ${
                    activeTab === tab
                      ? 'border-b-2 border-primary-600 text-primary-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'settings' && (
              <div className="max-w-2xl">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Test Settings</h3>
                <div className="bg-yellow-50 p-4 rounded-md text-yellow-800 text-sm">
                  Settings editing coming soon. Use "Create Test" to set initial values.
                </div>
              </div>
            )}

            {activeTab === 'sections' && (
              <div>
                {editingSection ? (
                  <div>
                    <button
                      onClick={() => setEditingSection(null)}
                      className="mb-4 text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center"
                    >
                      ← Back to Sections
                    </button>
                    
                    <div className="bg-gray-50 p-4 rounded-lg mb-6 border border-gray-200">
                      <h3 className="font-bold text-lg capitalize">{editingSection.section_type} Section Editor</h3>
                      <p className="text-sm text-gray-500">
                        {editingSection.total_questions} questions • {editingSection.duration_minutes} mins
                      </p>
                    </div>

                    {editingSection.section_type === 'listening' && (
                      <ListeningEditor sectionId={editingSection.id} testId={testId} />
                    )}

                    {editingSection.section_type === 'reading' && (
                      <ReadingEditor sectionId={editingSection.id} testId={testId} />
                    )}

                    {editingSection.section_type === 'writing' && (
                      <WritingEditor sectionId={editingSection.id} testId={testId} />
                    )}

                    {editingSection.section_type === 'speaking' && (
                      <SpeakingEditor sectionId={editingSection.id} testId={testId} />
                    )}
                  </div>
                ) : (
                  <div>
                    <div className="flex justify-between items-center mb-6">
                      <h3 className="text-lg font-medium text-gray-900">Test Sections</h3>
                      <button 
                        onClick={() => setShowAddSection(true)}
                        className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm"
                      >
                        + Add Section
                      </button>
                    </div>
                    
                    {test.sections && test.sections.length > 0 ? (
                      <div className="space-y-4">
                        {test.sections.map((section) => (
                          <div key={section.id} className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition">
                            <div className="flex justify-between items-center">
                              <div>
                                <h4 className="font-medium text-gray-900 capitalize">
                                  {section.section_type} Section
                                </h4>
                                <p className="text-sm text-gray-500">
                                  {section.total_questions} questions • {section.duration_minutes} mins
                                </p>
                              </div>
                              <button 
                                onClick={() => setEditingSection(section)}
                                className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                              >
                                Edit Content
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
                        <p className="text-gray-500 mb-2">No sections added yet</p>
                        <button 
                          onClick={() => setShowAddSection(true)}
                          className="text-primary-600 hover:text-primary-700 font-medium"
                        >
                          Add your first section
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'publish' && (
              <div className="max-w-2xl">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Publishing Status</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium text-gray-900">Current Status</h4>
                      <p className="text-sm text-gray-500">
                        {test.is_published ? 'Visible to students' : 'Hidden from students'}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      test.is_published ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {test.is_published ? 'Published' : 'Draft'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add Section Modal */}
      {showAddSection && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Add Test Section</h3>
            <form onSubmit={handleAddSection}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Section Type</label>
                  <select
                    value={newSection.section_type}
                    onChange={(e) => setNewSection({...newSection, section_type: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="listening">Listening</option>
                    <option value="reading">Reading</option>
                    <option value="writing">Writing</option>
                    <option value="speaking">Speaking</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Order</label>
                  <input
                    type="number"
                    min="1"
                    value={newSection.order}
                    onChange={(e) => setNewSection({...newSection, order: parseInt(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Total Questions</label>
                  <input
                    type="number"
                    min="0"
                    value={newSection.total_questions}
                    onChange={(e) => setNewSection({...newSection, total_questions: parseInt(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Duration (minutes)</label>
                  <input
                    type="number"
                    min="1"
                    value={newSection.duration_minutes}
                    onChange={(e) => setNewSection({...newSection, duration_minutes: parseInt(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowAddSection(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  Add Section
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AdminLayout>
  );
}
