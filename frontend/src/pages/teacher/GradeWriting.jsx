import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import TeacherLayout from '../../components/layout/TeacherLayout';
import BandScoreSlider from '../../components/teacher/BandScoreSlider';
import apiClient from '../../api/client';

export default function GradeWriting() {
  const navigate = useNavigate();
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [pendingSubmissions, setPendingSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [scores, setScores] = useState({
    taskAchievement: 7.0,
    coherenceCohesion: 7.0,
    lexicalResource: 6.5,
    grammaticalRange: 7.0,
  });
  
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    fetchPendingSubmissions();
  }, []);

  const fetchPendingSubmissions = async () => {
    try {
      const response = await apiClient.get('/grading/writing/pending');
      setPendingSubmissions(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch submissions:', err);
      setError('Failed to load submissions.');
      setLoading(false);
    }
  };
  
  const calculateOverallScore = () => {
    const avg = (scores.taskAchievement + scores.coherenceCohesion + scores.lexicalResource + scores.grammaticalRange) / 4;
    // Round to nearest 0.5
    return (Math.round(avg * 2) / 2).toFixed(1);
  };
  
  const handleSubmitGrade = async () => {
    if (!selectedSubmission) return;

    try {
      const gradeData = {
        task_achievement_score: scores.taskAchievement,
        coherence_cohesion_score: scores.coherenceCohesion,
        lexical_resource_score: scores.lexicalResource,
        grammatical_range_score: scores.grammaticalRange,
        feedback_text: feedback
      };

      await apiClient.post(`/grading/writing/${selectedSubmission.id}`, gradeData);
      
      alert(`Grade submitted successfully! Overall Score: ${calculateOverallScore()}`);
      setSelectedSubmission(null);
      fetchPendingSubmissions(); // Refresh list
    } catch (err) {
      console.error('Failed to submit grade:', err);
      alert('Failed to submit grade. Please try again.');
    }
  };
  
  if (!selectedSubmission) {
    return (
      <TeacherLayout>
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Grade Writing Submissions</h1>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">
              Pending Submissions ({pendingSubmissions.length})
            </h2>
            
            {loading ? (
              <div className="text-center py-8">Loading submissions...</div>
            ) : error ? (
              <div className="text-center py-8 text-red-600">{error}</div>
            ) : pendingSubmissions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">No pending submissions found.</div>
            ) : (
              <div className="space-y-3">
                {pendingSubmissions.map((submission) => (
                  <div
                    key={submission.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition cursor-pointer"
                    onClick={() => setSelectedSubmission(submission)}
                  >
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {submission.student_name || 'Unknown Student'}
                      </h3>
                      <p className="text-sm text-gray-600">
                        Task {submission.task_id} • {submission.word_count || 0} words • {new Date(submission.submitted_at).toLocaleString()}
                      </p>
                    </div>
                    <button className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                      Grade Now
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </TeacherLayout>
    );
  }
  
  return (
    <TeacherLayout>
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => setSelectedSubmission(null)}
            className="text-primary-600 hover:text-primary-700 font-medium text-sm mb-2"
          >
            ← Back to Submissions
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Grade Writing Submission</h1>
          <p className="text-gray-600 mt-2">
            Student: {selectedSubmission.student_name || 'Unknown'} | Task {selectedSubmission.task_id}
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Student Response */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Student Response</h2>
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <p className="text-sm text-gray-600 mb-2">Word Count: {selectedSubmission.word_count}</p>
              <div className="prose max-w-none text-gray-800 text-sm leading-relaxed whitespace-pre-wrap break-words overflow-y-auto max-h-[600px]">
                {selectedSubmission.response_text}
              </div>
            </div>
          </div>
          
          {/* Grading Panel */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-6">IELTS Criteria</h2>
            
            <div className="space-y-6 mb-6">
              <BandScoreSlider
                label="Task Achievement"
                value={scores.taskAchievement}
                onChange={(val) => setScores({ ...scores, taskAchievement: val })}
              />
              
              <BandScoreSlider
                label="Coherence & Cohesion"
                value={scores.coherenceCohesion}
                onChange={(val) => setScores({ ...scores, coherenceCohesion: val })}
              />
              
              <BandScoreSlider
                label="Lexical Resource"
                value={scores.lexicalResource}
                onChange={(val) => setScores({ ...scores, lexicalResource: val })}
              />
              
              <BandScoreSlider
                label="Grammatical Range & Accuracy"
                value={scores.grammaticalRange}
                onChange={(val) => setScores({ ...scores, grammaticalRange: val })}
              />
            </div>
            
            {/* Overall Score */}
            <div className="bg-primary-50 rounded-lg p-4 mb-6">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-gray-700">Overall Band Score:</span>
                <span className="text-3xl font-bold text-primary-600">{calculateOverallScore()}</span>
              </div>
            </div>
            
            {/* Feedback */}
            <div className="mb-6">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Feedback (Optional)
              </label>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Provide detailed feedback to help the student improve..."
                className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none text-sm"
              />
            </div>
            
            {/* Submit Button */}
            <button
              onClick={handleSubmitGrade}
              className="w-full bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-lg font-bold transition"
            >
              Submit Grade
            </button>
          </div>
        </div>
      </div>
    </TeacherLayout>
  );
}
