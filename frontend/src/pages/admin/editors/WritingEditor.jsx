import { useState, useEffect } from 'react';
import apiClient from '../../../api/client';

export default function WritingEditor({ sectionId, testId }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddTask, setShowAddTask] = useState(false);
  
  // Form State
  const [formData, setFormData] = useState({
    task_number: 1,
    task_type: 'writing_task1_academic',
    prompt_text: '',
    image_url: '',
    word_limit_min: 150,
    word_limit_max: 0,
    time_limit_minutes: 20,
    instructions: ''
  });

  useEffect(() => {
    fetchTasks();
  }, [sectionId]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/writing/tasks?section_id=${sectionId}`);
      setTasks(response.data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiClient.post('/upload/image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setFormData(prev => ({ ...prev, image_url: response.data.url }));
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload image');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const payload = {
      ...formData,
      section_id: parseInt(sectionId),
      task_number: parseInt(formData.task_number),
      word_limit_min: parseInt(formData.word_limit_min),
      word_limit_max: formData.word_limit_max ? parseInt(formData.word_limit_max) : null,
      time_limit_minutes: parseInt(formData.time_limit_minutes)
    };

    try {
      await apiClient.post('/writing/tasks', payload);
      setShowAddTask(false);
      fetchTasks();
      
      // Reset form or set defaults for next task
      const nextTaskNum = formData.task_number === 1 ? 2 : 1;
      setFormData({
        task_number: nextTaskNum,
        task_type: nextTaskNum === 2 ? 'writing_task2_essay' : 'writing_task1_academic',
        prompt_text: '',
        image_url: '',
        word_limit_min: nextTaskNum === 2 ? 250 : 150,
        word_limit_max: 0,
        time_limit_minutes: nextTaskNum === 2 ? 40 : 20,
        instructions: ''
      });
    } catch (error) {
      console.error('Failed to save task:', error);
      alert('Failed to save task');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure?')) return;
    try {
      await apiClient.delete(`/writing/tasks/${id}`);
      fetchTasks();
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Writing Tasks</h3>
        <button
          onClick={() => setShowAddTask(true)}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm"
        >
          + Add Task
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading tasks...</div>
      ) : tasks.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
          <p className="text-gray-500">No tasks added yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <div key={task.id} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="font-bold text-gray-900">Task {task.task_number}</span>
                    <span className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600">
                      {task.task_type.replace('writing_', '').replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs text-gray-500">({task.time_limit_minutes} mins)</span>
                  </div>
                  <p className="text-gray-800 mb-2 whitespace-pre-wrap">{task.prompt_text}</p>
                  {task.image_url && (
                    <div className="mt-2">
                      <img src={task.image_url} alt="Task Prompt" className="h-32 object-contain border border-gray-200 rounded" />
                    </div>
                  )}
                  <div className="mt-2 text-xs text-gray-500">
                    Min words: {task.word_limit_min} {task.word_limit_max ? `| Max words: ${task.word_limit_max}` : ''}
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button 
                    onClick={() => handleDelete(task.id)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Task Modal */}
      {showAddTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full p-6 m-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Add Writing Task</h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Task Number</label>
                  <select
                    value={formData.task_number}
                    onChange={(e) => {
                      const num = parseInt(e.target.value);
                      setFormData({
                        ...formData, 
                        task_number: num,
                        task_type: num === 1 ? 'writing_task1_academic' : 'writing_task2_essay',
                        word_limit_min: num === 1 ? 150 : 250,
                        time_limit_minutes: num === 1 ? 20 : 40
                      });
                    }}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value={1}>Task 1</option>
                    <option value={2}>Task 2</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Task Type</label>
                  <select
                    value={formData.task_type}
                    onChange={(e) => setFormData({...formData, task_type: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="writing_task1_academic">Task 1 Academic (Graph/Chart)</option>
                    <option value="writing_task1_general">Task 1 General (Letter)</option>
                    <option value="writing_task2_essay">Task 2 Essay</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Prompt Text</label>
                <textarea
                  required
                  rows={5}
                  value={formData.prompt_text}
                  onChange={(e) => setFormData({...formData, prompt_text: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  placeholder="Enter the question prompt here..."
                />
              </div>

              {formData.task_number === 1 && formData.task_type === 'writing_task1_academic' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Chart/Graph Image</label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                  {formData.image_url && (
                    <div className="mt-2">
                      <img src={formData.image_url} alt="Preview" className="h-20 object-contain border border-gray-200 rounded" />
                    </div>
                  )}
                </div>
              )}

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Min Words</label>
                  <input
                    type="number"
                    required
                    value={formData.word_limit_min}
                    onChange={(e) => setFormData({...formData, word_limit_min: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Words (0=No limit)</label>
                  <input
                    type="number"
                    value={formData.word_limit_max}
                    onChange={(e) => setFormData({...formData, word_limit_max: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Time Limit (mins)</label>
                  <input
                    type="number"
                    required
                    value={formData.time_limit_minutes}
                    onChange={(e) => setFormData({...formData, time_limit_minutes: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddTask(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  Save Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
