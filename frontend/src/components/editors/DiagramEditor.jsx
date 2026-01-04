import { useState, useEffect, useRef } from 'react';
import apiClient from '../../api/client';
import DiagramQuestionRenderer from '../test/renderers/DiagramQuestionRenderer';

/**
 * DiagramEditor - Editor for diagram/map labeling questions
 * 
 * Features:
 * - Image upload
 * - Click-to-add label points on image
 * - Drag to reposition labels
 * - Answer configuration per label
 */
export default function DiagramEditor({ value, onChange }) {
  const [imageUrl, setImageUrl] = useState(value?.image_url || '');
  const [labels, setLabels] = useState(value?.labels || []);
  // answers comes as either {labels: {...}} or directly as {...}
  const [answers, setAnswers] = useState(value?.answers?.labels || value?.answers || {});
  const [maxWords, setMaxWords] = useState(value?.max_words_per_label || 2);
  const [uploading, setUploading] = useState(false);
  const imageRef = useRef(null);

  // Track if we're doing a local update to prevent re-initialization loop
  const isLocalUpdate = useRef(false);

  // Re-initialize state when value changes from EXTERNAL source (editing existing question)
  // Skip if this is just a reflection of our own updates
  useEffect(() => {
    // Skip re-initialization if this change came from our own onChange call
    if (isLocalUpdate.current) {
      isLocalUpdate.current = false;
      return;
    }
    
    if (value?.image_url) setImageUrl(value.image_url);
    if (value?.labels) setLabels(value.labels);
    if (value?.answers?.labels) setAnswers(value.answers.labels);
    else if (value?.answers && typeof value.answers === 'object') setAnswers(value.answers);
    if (value?.max_words_per_label) setMaxWords(value.max_words_per_label);
  }, [value?.image_url, JSON.stringify(value?.labels), JSON.stringify(value?.answers), value?.max_words_per_label]);

  // Notify parent of changes
  useEffect(() => {
    // Mark that we're doing a local update so we don't re-initialize from our own change
    isLocalUpdate.current = true;
    onChange?.({
      type_specific_data: {
        image_url: imageUrl,
        labels: labels,
        max_words_per_label: maxWords
      },
      answer_data: {
        labels: answers
      }
    });
  }, [imageUrl, labels, answers, maxWords]);

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      const response = await apiClient.post('/upload/image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setImageUrl(response.data.url);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload image');
    } finally {
      setUploading(false);
    }
  };

  const handleImageClick = (e) => {
    if (!imageRef.current) return;
    
    const rect = imageRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    
    const newLabelId = String(labels.length + 1);
    const newLabel = {
      label_id: newLabelId,
      x: Math.round(x * 10) / 10,
      y: Math.round(y * 10) / 10
    };
    
    setLabels([...labels, newLabel]);
    setAnswers({ ...answers, [newLabelId]: [] });
  };

  const removeLabel = (labelId) => {
    setLabels(labels.filter(l => l.label_id !== labelId));
    const newAnswers = { ...answers };
    delete newAnswers[labelId];
    setAnswers(newAnswers);
  };

  const updateLabelAnswer = (labelId, answerList) => {
    setAnswers({ ...answers, [labelId]: answerList });
  };

  return (
    <div className="space-y-6">
      {/* Image Upload */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Diagram/Map Image
        </label>
        <div className="flex items-center gap-4">
          <input
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="border border-gray-300 rounded-lg px-3 py-2"
          />
          {uploading && <span className="text-gray-500">Uploading...</span>}
          {imageUrl && <span className="text-green-600 text-sm">✓ Image uploaded</span>}
        </div>
      </div>

      {/* Max Words Setting */}
      <div className="flex items-center gap-4">
        <label className="text-sm text-gray-700">
          Max words per label:
          <select
            value={maxWords}
            onChange={(e) => setMaxWords(parseInt(e.target.value))}
            className="ml-2 border rounded px-2 py-1"
          >
            {[1, 2, 3, 4, 5].map(n => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </label>
      </div>

      {/* Interactive Image */}
      {imageUrl && (
        <div className="border rounded-lg overflow-hidden">
          <div className="bg-gray-100 px-4 py-2 border-b text-sm text-gray-600">
            Click on the image to add label points. {labels.length} labels added.
          </div>
          <div className="relative inline-block">
            <img
              ref={imageRef}
              src={imageUrl}
              alt="Diagram"
              onClick={handleImageClick}
              className="max-w-full cursor-crosshair"
              style={{ maxHeight: '400px' }}
            />
            {labels.map((label) => (
              <div
                key={label.label_id}
                className="absolute w-7 h-7 bg-red-500 rounded-full text-white text-sm font-bold flex items-center justify-center transform -translate-x-1/2 -translate-y-1/2 cursor-pointer shadow-lg hover:bg-red-600 transition-colors"
                style={{ left: `${label.x}%`, top: `${label.y}%` }}
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm(`Remove label ${label.label_id}?`)) {
                    removeLabel(label.label_id);
                  }
                }}
                title={`Label ${label.label_id} - Click to remove`}
              >
                {label.label_id}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Label Answers */}
      {labels.length > 0 && (
        <div className="border rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-2 border-b">
            <h4 className="font-medium text-gray-900">Label Answers</h4>
          </div>
          <div className="divide-y">
            {labels.map((label) => (
              <div key={label.label_id} className="p-4 flex items-start gap-4">
                <div className="w-8 h-8 bg-red-500 rounded-full text-white font-bold flex items-center justify-center flex-shrink-0">
                  {label.label_id}
                </div>
                <div className="flex-1">
                  <LabelAnswerInput
                    answers={answers[label.label_id] || []}
                    onChange={(ans) => updateLabelAnswer(label.label_id, ans)}
                  />
                </div>
                <button
                  type="button"
                  onClick={() => removeLabel(label.label_id)}
                  className="text-gray-400 hover:text-red-500"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {!imageUrl && (
        <div className="p-8 border-2 border-dashed border-gray-300 rounded-lg text-center text-gray-500">
          Upload an image to start adding label points
        </div>
      )}

      {/* Student Preview */}
      <div className="border rounded-lg overflow-hidden mt-8">
        <div className="bg-blue-50 px-4 py-2 border-b border-blue-100">
          <h4 className="font-medium text-blue-900">Student Preview</h4>
        </div>
        <div className="p-4 bg-white">
          <DiagramQuestionRenderer 
            question={{
              type_specific_data: {
                image_url: imageUrl,
                labels: labels,
                max_words_per_label: maxWords
              }
            }}
            answer={answers}
            onAnswerChange={(newAnswers) => setAnswers(newAnswers)}
          />
        </div>
      </div>
    </div>
  );
}

// Answer input for a single label
function LabelAnswerInput({ answers, onChange }) {
  const [inputValue, setInputValue] = useState('');

  const handleAdd = () => {
    if (inputValue.trim()) {
      onChange([...answers, inputValue.trim()]);
      setInputValue('');
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {answers.map((answer, idx) => (
          <span
            key={idx}
            className={`inline-flex items-center gap-1 px-2 py-1 rounded text-sm ${
              idx === 0 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-700'
            }`}
          >
            {answer}
            <button
              type="button"
              onClick={() => onChange(answers.filter((_, i) => i !== idx))}
              className="text-gray-400 hover:text-red-500"
            >
              ×
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAdd())}
          placeholder={answers.length === 0 ? "Correct answer..." : "Alternative..."}
          className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm"
        />
        <button
          type="button"
          onClick={handleAdd}
          disabled={!inputValue.trim()}
          className="px-3 py-1 bg-primary-600 text-white rounded text-sm hover:bg-primary-700 disabled:opacity-50"
        >
          Add
        </button>
      </div>
    </div>
  );
}
