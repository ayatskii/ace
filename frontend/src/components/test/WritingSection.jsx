import { useState, useEffect } from 'react';

export default function WritingSection({ taskNumber, minWords }) {
  const [content, setContent] = useState('');
  const [wordCount, setWordCount] = useState(0);
  
  useEffect(() => {
    const words = content.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
  }, [content]);
  
  const isMinimumMet = wordCount >= minWords;
  
  return (
    <div className="space-y-4">
      {/* Task Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-bold text-gray-900 mb-2">
          {taskNumber === 1 ? 'Task 1' : 'Task 2'}
        </h3>
        <p className="text-gray-700 text-sm">
          {taskNumber === 1 
            ? 'Summarize the information by selecting and reporting the main features, and make comparisons where relevant.'
            : 'Present a written argument or case to an educated reader with no specialist knowledge.'}
        </p>
        <p className="text-gray-600 text-xs mt-2">
          Write at least {minWords} words
        </p>
      </div>
      
      {/* Word Counter */}
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700">Your Response:</span>
        <div className={`text-sm font-bold px-3 py-1 rounded-lg ${
          isMinimumMet 
            ? 'bg-green-100 text-green-700' 
            : 'bg-yellow-100 text-yellow-700'
        }`}>
          {wordCount} / {minWords} words
          {isMinimumMet && ' ✓'}
        </div>
      </div>
      
      {/* Text Editor */}
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Start writing your response here..."
        className="w-full h-96 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none font-mono text-sm"
      />
      
      {/* Tips */}
      <div className="text-xs text-gray-500">
        <span className="font-semibold">Tips:</span> Organize your ideas, use paragraphs, check grammar and spelling
      </div>
    </div>
  );
}
