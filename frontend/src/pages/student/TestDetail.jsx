import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import MainLayout from '../../components/layout/MainLayout';
import { testsApi } from '../../api/tests';

export default function TestDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [showStartModal, setShowStartModal] = useState(false);
  
  // Fetch test details
  const { data: test, isLoading: isTestLoading } = useQuery({
    queryKey: ['test', id],
    queryFn: () => testsApi.getById(id),
  });
  
  // Fetch user's attempts to check status
  const { data: attempts, isLoading: isAttemptsLoading } = useQuery({
    queryKey: ['my-attempts'],
    queryFn: () => testsApi.getMyAttempts(),
  });

  const existingAttempt = attempts?.data?.find(
    (attempt) => attempt.test_template_id === parseInt(id)
  );

  const isCompleted = existingAttempt && ['submitted', 'graded'].includes(existingAttempt.status);
  const isInProgress = existingAttempt && existingAttempt.status === 'in_progress';
  
  // Start test mutation
  const startTestMutation = useMutation({
    mutationFn: (templateId) => testsApi.startAttempt(templateId),
    onSuccess: (data) => {
      navigate(`/student/test/${data.data.id}`);
    },
    onError: (error) => {
        // If backend says we already have an attempt (which shouldn't happen with UI checks, but just in case)
        if (error.response?.status === 400 && error.response?.data?.detail === "You have already completed this test") {
            alert("You have already completed this test.");
        }
    }
  });
  
  const handleStartTest = () => {
    if (isCompleted) {
        navigate(`/student/results/${existingAttempt.id}`); // Assuming there's a results page
        return;
    }
    if (isInProgress) {
        navigate(`/student/test/${existingAttempt.id}`);
        return;
    }
    startTestMutation.mutate(parseInt(id));
  };
  
  if (isTestLoading || isAttemptsLoading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </MainLayout>
    );
  }
  
  const testData = test?.data;
  
  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mb-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{testData?.title}</h1>
              <p className="text-gray-600 mt-2">{testData?.description}</p>
            </div>
            <span className={`px-4 py-2 rounded-lg text-sm font-semibold ${
              testData?.test_type === 'academic' 
                ? 'bg-primary-100 text-primary-700' 
                : 'bg-purple-100 text-purple-700'
            }`}>
              {testData?.test_type === 'academic' ? 'Academic' : 'General Training'}
            </span>
          </div>
          
          {/* Test Structure */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-2xl mb-2">🎧</div>
              <div className="text-sm font-semibold text-gray-700">Listening</div>
              <div className="text-xs text-gray-500">40 minutes</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-2xl mb-2">📖</div>
              <div className="text-sm font-semibold text-gray-700">Reading</div>
              <div className="text-xs text-gray-500">60 minutes</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-2xl mb-2">✍️</div>
              <div className="text-sm font-semibold text-gray-700">Writing</div>
              <div className="text-xs text-gray-500">60 minutes</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-2xl mb-2">🎤</div>
              <div className="text-sm font-semibold text-gray-700">Speaking</div>
              <div className="text-xs text-gray-500">11-14 minutes</div>
            </div>
          </div>
          
          {isCompleted ? (
              <button
                onClick={() => navigate(`/student/results`)} 
                className="w-full bg-green-600 hover:bg-green-700 text-white py-4 rounded-lg font-bold text-lg transition shadow-lg"
              >
                View Results
              </button>
          ) : isInProgress ? (
              <button
                onClick={() => navigate(`/student/test/${existingAttempt.id}`)}
                className="w-full bg-yellow-500 hover:bg-yellow-600 text-white py-4 rounded-lg font-bold text-lg transition shadow-lg"
              >
                Resume Test
              </button>
          ) : (
              <button
                onClick={() => setShowStartModal(true)}
                className="w-full bg-primary-600 hover:bg-primary-700 text-white py-4 rounded-lg font-bold text-lg transition shadow-lg"
              >
                Start Test
              </button>
          )}
        </div>
        
        {/* Instructions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Test Instructions</h2>
          <div className="space-y-3 text-gray-700">
            <p>• You will complete 4 sections: Listening, Reading, Writing, and Speaking</p>
            <p>• Each section has a time limit - manage your time carefully</p>
            <p>• Listening and Reading will be auto-graded immediately</p>
            <p>• Writing and Speaking will be graded by a teacher within 24-48 hours</p>
            <p>• You can navigate between questions within each section</p>
            <p>• Your progress is saved automatically</p>
            <p>• Make sure you have a stable internet connection</p>
            <p>• For Speaking, you'll need microphone access to record your responses</p>
          </div>
        </div>
      </div>
      
      {/* Start Test Modal */}
      {showStartModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Ready to Start?</h3>
            <p className="text-gray-600 mb-6">
              Once you start, the timer will begin. Make sure you have enough time to complete all sections.
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowStartModal(false)}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-3 rounded-lg font-semibold transition"
              >
                Cancel
              </button>
              <button
                onClick={handleStartTest}
                disabled={startTestMutation.isPending}
                className="flex-1 bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-lg font-semibold transition disabled:opacity-50"
              >
                {startTestMutation.isPending ? 'Starting...' : 'Start Now'}
              </button>
            </div>
          </div>
        </div>
      )}
    </MainLayout>
  );
}
