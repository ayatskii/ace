import { useState, useEffect } from 'react';
import TeacherLayout from '../../components/layout/TeacherLayout';
import BandScoreSlider from '../../components/teacher/BandScoreSlider';
import apiClient from '../../api/client';

export default function GradeSpeaking() {
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [pendingSubmissions, setPendingSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [scores, setScores] = useState({
    fluencyCoherence: 7.0,
    lexicalResource: 7.0,
    grammaticalRange: 6.5,
    pronunciation: 7.0,
  });
  
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    fetchPendingSubmissions();
  }, []);

  const fetchPendingSubmissions = async () => {
    try {
      const response = await apiClient.get('/grading/speaking/pending');
      setPendingSubmissions(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch submissions:', err);
      setError('Failed to load submissions.');
      setLoading(false);
    }
  };
  
  const calculateOverallScore = () => {
    const avg = (scores.fluencyCoherence + scores.lexicalResource + scores.grammaticalRange + scores.pronunciation) / 4;
    return (Math.round(avg * 2) / 2).toFixed(1);
  };
  
  const handleSubmitGrade = async () => {
    if (!selectedSubmission) return;

    try {
      const gradeData = {
        fluency_coherence_score: scores.fluencyCoherence,
        lexical_resource_score: scores.lexicalResource,
        grammatical_range_score: scores.grammaticalRange,
        pronunciation_score: scores.pronunciation,
        feedback_text: feedback
      };

      await apiClient.post(`/grading/speaking/${selectedSubmission.id}`, gradeData);
      
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
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Grade Speaking Submissions</h1>
          
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
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                        <span className="text-2xl">🎤</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {submission.student_name || 'Unknown Student'}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Part {submission.task_id} • {submission.duration_seconds}s • {new Date(submission.submitted_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
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
          <h1 className="text-3xl font-bold text-gray-900">Grade Speaking Submission</h1>
          <p className="text-gray-600 mt-2">
            Student: {selectedSubmission.student_name || 'Unknown'} | Part {selectedSubmission.task_id}
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Audio Player */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Audio Recording</h2>
            
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-8 mb-4">
              <div className="text-center mb-6">
                <div className="text-6xl mb-4">🎧</div>
                <p className="text-sm text-gray-600">Duration: {selectedSubmission.duration_seconds} seconds</p>
              </div>
              
              <audio
                controls
                className="w-full"
                src={selectedSubmission.audio_url.startsWith('http') ? selectedSubmission.audio_url : selectedSubmission.audio_url}
              >
                Your browser does not support the audio element.
              </audio>
            </div>
            
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800 font-medium mb-2">💡 Grading Tips:</p>
              <ul className="text-xs text-yellow-700 space-y-1">
                <li>• Listen to the entire recording</li>
                <li>• Note pauses, hesitations, and corrections</li>
                <li>• Assess vocabulary range and accuracy</li>
                <li>• Evaluate pronunciation clarity</li>
              </ul>
            </div>
          </div>
          
          {/* Grading Panel */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-6">IELTS Criteria</h2>
            
            <div className="space-y-6 mb-6">
              <BandScoreSlider
                label="Fluency & Coherence"
                value={scores.fluencyCoherence}
                onChange={(val) => setScores({ ...scores, fluencyCoherence: val })}
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
              
              <BandScoreSlider
                label="Pronunciation"
                value={scores.pronunciation}
                onChange={(val) => setScores({ ...scores, pronunciation: val })}
              />
            </div>
            
            {/* Overall Score */}
            <div className="bg-purple-50 rounded-lg p-4 mb-6">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-gray-700">Overall Band Score:</span>
                <span className="text-3xl font-bold text-purple-600">{calculateOverallScore()}</span>
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
                placeholder="Provide feedback on fluency, vocabulary, grammar, and pronunciation..."
                className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none text-sm"
              />
            </div>
            
            {/* Submit Button */}
            <button
              onClick={handleSubmitGrade}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-lg font-bold transition"
            >
              Submit Grade
            </button>
          </div>
        </div>
      </div>
    </TeacherLayout>
  );
}  
