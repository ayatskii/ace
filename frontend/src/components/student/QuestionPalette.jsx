import { useState } from 'react';

/**
 * QuestionPalette - Navigation palette for test questions
 * Shows all question numbers with status indicators (answered, flagged, etc.)
 */
export default function QuestionPalette({ 
  questions, 
  answers, 
  flagged, 
  currentIndex, 
  onSelect 
}) {
  const [isExpanded, setIsExpanded] = useState(true);

  const getStatus = (question, index) => {
    const qId = question.id;
    
    // Check if flagged
    if (flagged?.[qId]) return 'flagged';
    
    // Check if answered
    const answer = answers?.[qId];
    if (answer) {
      // Handle different answer structures
      if (typeof answer === 'string' && answer.trim()) return 'answered';
      if (typeof answer === 'object') {
        // Completion: check blanks
        if (answer.blanks && Object.values(answer.blanks).some(v => v?.trim())) return 'answered';
        // Matching: check mappings
        if (answer.mappings && Object.keys(answer.mappings).length > 0) return 'answered';
        // MCQ: check selected
        if (answer.selected && answer.selected.length > 0) return 'answered';
        // TFNG: check answers
        if (answer.answers && Object.keys(answer.answers).length > 0) return 'answered';
        // Diagram: check labels
        if (answer.labels && Object.values(answer.labels).some(v => v?.trim())) return 'answered';
      }
    }
    
    // Check if visited (past current)
    if (index < currentIndex) return 'visited';
    
    return 'not_visited';
  };

  const statusStyles = {
    flagged: 'bg-yellow-400 text-yellow-900 border-yellow-500',
    answered: 'bg-green-500 text-white border-green-600',
    visited: 'bg-red-400 text-white border-red-500',
    not_visited: 'bg-gray-200 text-gray-600 border-gray-300',
    current: 'ring-2 ring-primary-500 ring-offset-2'
  };

  const statusLabels = {
    flagged: 'Flagged for review',
    answered: 'Answered',
    visited: 'Visited but unanswered',
    not_visited: 'Not yet visited'
  };

  // Count statistics
  const stats = questions.reduce((acc, q, i) => {
    const status = getStatus(q, i);
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between hover:bg-gray-100 transition-colors"
      >
        <span className="font-medium text-gray-900">Question Navigator</span>
        <span className="text-gray-500">{isExpanded ? '▼' : '▶'}</span>
      </button>

      {isExpanded && (
        <>
          {/* Question Grid */}
          <div className="p-3">
            <div className="grid grid-cols-10 gap-1">
              {questions.map((q, index) => {
                const status = getStatus(q, index);
                const isCurrent = index === currentIndex;
                
                return (
                  <button
                    key={q.id}
                    onClick={() => onSelect(index)}
                    title={`Q${q.question_number || index + 1}: ${statusLabels[status]}`}
                    className={`
                      w-8 h-8 rounded text-sm font-medium border transition-all
                      ${statusStyles[status]}
                      ${isCurrent ? statusStyles.current : ''}
                      hover:opacity-80 hover:scale-105
                    `}
                  >
                    {q.question_number || index + 1}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Legend */}
          <div className="px-3 pb-3 pt-1 border-t border-gray-100">
            <div className="flex flex-wrap gap-3 text-xs">
              <div className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-green-500"></span>
                <span className="text-gray-600">Answered ({stats.answered || 0})</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-red-400"></span>
                <span className="text-gray-600">Unanswered ({stats.visited || 0})</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-yellow-400"></span>
                <span className="text-gray-600">Flagged ({stats.flagged || 0})</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="w-3 h-3 rounded bg-gray-200"></span>
                <span className="text-gray-600">Not visited ({stats.not_visited || 0})</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
