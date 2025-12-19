import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import TeacherLayout from '../../components/layout/TeacherLayout';
import BandScoreSlider from '../../components/teacher/BandScoreSlider';

export default function GradeWriting() {
  const navigate = useNavigate();
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  
  // Mock pending submissions
  const pendingSubmissions = [
    { id: 1, student: 'John Doe', task: 'Task 1', wordCount: 287, submitted: '2 hours ago' },
    { id: 2, student: 'Jane Smith', task: 'Task 2', wordCount: 315, submitted: '3 hours ago' },
    { id: 3, student: 'Mike Johnson', task: 'Task 1', wordCount: 165, submitted: '4 hours ago' },
  ];
  
  const [scores, setScores] = useState({
    taskAchievement: 7.0,
    coherenceCohesion: 7.0,
    lexicalResource: 6.5,
    grammaticalRange: 7.0,
  });
  
  const [feedback, setFeedback] = useState('');
  
  const calculateOverallScore = () => {
    const avg = (scores.taskAchievement + scores.coherenceCohesion + scores.lexicalResource + scores.grammaticalRange) / 4;
    return avg.toFixed(1);
  };
  
  const handleSubmitGrade = () => {
    // TODO: API call to submit grade
    alert(`Grade submitted: ${calculateOverallScore()}`);
    setSelectedSubmission(null);
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
            
            <div className="space-y-3">
              {pendingSubmissions.map((submission) => (
                <div
                  key={submission.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition cursor-pointer"
                  onClick={() => setSelectedSubmission(submission)}
                >
                  <div>
                    <h3 className="font-semibold text-gray-900">{submission.student}</h3>
                    <p className="text-sm text-gray-600">
                      {submission.task} • {submission.wordCount} words • {submission.submitted}
                    </p>
                  </div>
                  <button className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                    Grade Now
                  </button>
                </div>
              ))}
            </div>
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
            Student: {selectedSubmission.student} | {selectedSubmission.task}
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Student Response */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Student Response</h2>
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <p className="text-sm text-gray-600 mb-2">Word Count: {selectedSubmission.wordCount}</p>
              <div className="prose max-w-none text-gray-800 text-sm leading-relaxed">
                <p>The graph illustrates the percentage of population aged 65 and over in three countries from 1940 to 2040. Overall, all three countries show an upward trend in their elderly population throughout the period.</p>
                <p>In 1940, the USA had the highest proportion at approximately 9%, while Sweden and Japan both started at around 7%. Over the next few decades, the USA and Sweden experienced steady growth, reaching about 15% and 14% respectively by 1980.</p>
                <p>However, Japan's elderly population remained relatively stable until 1980, after which it began to increase rapidly. By 2020, Japan had overtaken both the USA and Sweden, with approximately 23% of its population aged 65 and over.</p>
                <p>The projections for 2040 show that all three countries will continue this upward trend, with Japan leading at around 27%, followed closely by Sweden at 25%, and the USA at approximately 23%.</p>
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
