import { useState, useEffect } from 'react';
import apiClient from '../../../api/client';

export default function SpeakingEditor({ sectionId, testId }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddTask, setShowAddTask] = useState(false);
  
  // Form State
  const [formData, setFormData] = useState({
    part_number: 1,
    task_type: 'speaking_part1',
    prompt_text: '',
    preparation_time_seconds: 0,
    speaking_time_seconds: 240,
    order: 1,
    cue_card_points: ['']
  });

  useEffect(() => {
    fetchTasks();
  }, [sectionId]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/speaking/tasks?section_id=${sectionId}`);
      setTasks(response.data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const payload = {
      ...formData,
      section_id: parseInt(sectionId),
      part_number: parseInt(formData.part_number),
      preparation_time_seconds: parseInt(formData.preparation_time_seconds),
      speaking_time_seconds: parseInt(formData.speaking_time_seconds),
      order: parseInt(formData.part_number), // Use part number as order for simplicity
      cue_card_points: formData.part_number === 2 ? formData.cue_card_points.filter(p => p.trim() !== '') : null
    };

    try {
      await apiClient.post('/speaking/tasks', payload);
      setShowAddTask(false);
      fetchTasks();
      
      // Reset form
      const nextPart = formData.part_number < 3 ? formData.part_number + 1 : 1;
      setFormData({
        part_number: nextPart,
        task_type: `speaking_part${nextPart}`,
        prompt_text: '',
        preparation_time_seconds: nextPart === 2 ? 60 : 0,
        speaking_time_seconds: nextPart === 2 ? 120 : 240,
        order: nextPart,
        cue_card_points: ['']
      });
    } catch (error) {
      console.error('Failed to save task:', error);
      alert('Failed to save task');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure?')) return;
    try {
      await apiClient.delete(`/speaking/tasks/${id}`);
      fetchTasks();
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  const handleCuePointChange = (idx, value) => {
    const newPoints = [...formData.cue_card_points];
    newPoints[idx] = value;
    setFormData({ ...formData, cue_card_points: newPoints });
  };

  const addCuePoint = () => {
    setFormData({ ...formData, cue_card_points: [...formData.cue_card_points, ''] });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Speaking Tasks</h3>
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
                    <span className="font-bold text-gray-900">Part {task.part_number}</span>
                    <span className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600">
                      {task.task_type.replace('speaking_', '').replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs text-gray-500">({task.speaking_time_seconds}s)</span>
                  </div>
                  <p className="text-gray-800 mb-2 whitespace-pre-wrap">{task.prompt_text}</p>
                  
                  {task.part_number === 2 && task.cue_card_points && (
                    <ul className="list-disc list-inside text-sm text-gray-600 mt-2 bg-gray-50 p-2 rounded">
                      {task.cue_card_points.map((point, idx) => (
                        <li key={idx}>{point}</li>
                      ))}
                    </ul>
                  )}
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
            <h3 className="text-xl font-bold text-gray-900 mb-4">Add Speaking Task</h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Part Number</label>
                  <select
                    value={formData.part_number}
                    onChange={(e) => {
                      const num = parseInt(e.target.value);
                      setFormData({
                        ...formData, 
                        part_number: num,
                        task_type: `speaking_part${num}`,
                        preparation_time_seconds: num === 2 ? 60 : 0,
                        speaking_time_seconds: num === 2 ? 120 : 240
                      });
                    }}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value={1}>Part 1 (Interview)</option>
                    <option value={2}>Part 2 (Cue Card)</option>
                    <option value={3}>Part 3 (Discussion)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Speaking Time (seconds)</label>
                  <input
                    type="number"
                    required
                    value={formData.speaking_time_seconds}
                    onChange={(e) => setFormData({...formData, speaking_time_seconds: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
              </div>

              {formData.part_number === 2 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Preparation Time (seconds)</label>
                  <input
                    type="number"
                    required
                    value={formData.preparation_time_seconds}
                    onChange={(e) => setFormData({...formData, preparation_time_seconds: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Prompt Text / Topic</label>
                <textarea
                  required
                  rows={3}
                  value={formData.prompt_text}
                  onChange={(e) => setFormData({...formData, prompt_text: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  placeholder={formData.part_number === 2 ? "Describe a..." : "Enter questions or topic..."}
                />
              </div>

              {formData.part_number === 2 && (
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">Cue Card Points</label>
                  {formData.cue_card_points.map((point, idx) => (
                    <input
                      key={idx}
                      type="text"
                      value={point}
                      onChange={(e) => handleCuePointChange(idx, e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 mb-2"
                      placeholder={`Point ${idx + 1}`}
                    />
                  ))}
                  <button
                    type="button"
                    onClick={addCuePoint}
                    className="text-sm text-primary-600 hover:text-primary-700"
                  >
                    + Add Point
                  </button>
                </div>
              )}

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
