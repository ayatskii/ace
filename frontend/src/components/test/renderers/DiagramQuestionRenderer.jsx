import { useState, useRef, useEffect } from 'react';

export default function DiagramQuestionRenderer({ question, answer, onAnswerChange }) {
  const { image_url, labels, max_words_per_label } = question.type_specific_data || {};
  const containerRef = useRef(null);

  // answer is expected to be: { [labelId]: textValue }

  const handleInputChange = (labelId, value) => {
    const newAnswer = { ...answer, [labelId]: value };
    onAnswerChange(newAnswer);
  };

  if (!image_url) return <div>Image not available</div>;

  return (
    <div className="relative inline-block w-full max-w-4xl mx-auto" ref={containerRef}>
      <img
        src={image_url}
        alt="Diagram to label"
        className="w-full h-auto rounded-lg shadow-sm border border-gray-200"
      />
      
      {labels?.map((label) => (
        <div
          key={label.label_id}
          className="absolute transform -translate-x-1/2 -translate-y-1/2"
          style={{ left: `${label.x}%`, top: `${label.y}%` }}
        >
          <div className="relative group">
            {/* Marker */}
            <div className="w-6 h-6 bg-primary-600 rounded-full border-2 border-white shadow-md flex items-center justify-center text-white text-xs font-bold mb-1 mx-auto z-10 relative">
              {label.label_id}
            </div>
            
            {/* Input Field */}
            <div className="bg-white p-1.5 rounded shadow-lg border border-gray-200 min-w-[120px]">
              <input
                type="text"
                value={answer?.[label.label_id] || ''}
                onChange={(e) => handleInputChange(label.label_id, e.target.value)}
                className="w-full border border-gray-300 rounded px-2 py-1 text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder={`Label ${label.label_id}`}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
