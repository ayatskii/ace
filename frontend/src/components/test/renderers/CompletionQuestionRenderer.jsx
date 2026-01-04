import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

export default function CompletionQuestionRenderer({ question, answer, onAnswerChange }) {
  const { template_text, blanks } = question.type_specific_data || {};
  
  // Parse template to separate text and blanks
  const parts = useMemo(() => {
    if (!template_text) return [];
    return template_text.split(/(\[BLANK_\d+\])/g);
  }, [template_text]);

  const handleInputChange = (blankId, value) => {
    // Update the answer object: { [blankId]: value }
    const newAnswer = { ...answer, [blankId]: value };
    onAnswerChange(newAnswer);
  };

  if (!template_text) return <div>Invalid question format</div>;

  return (
    <div className="leading-loose text-lg">
      {parts.map((part, idx) => {
        const match = part.match(/\[BLANK_(\d+)\]/);
        if (match) {
          const blankId = `BLANK_${match[1]}`;
          const config = blanks?.find(b => b.blank_id === blankId);
          const currentValue = answer?.[blankId] || '';

          return (
            <span key={idx} className="inline-block mx-1">
              <input
                type="text"
                value={currentValue}
                onChange={(e) => handleInputChange(blankId, e.target.value)}
                className="border-b-2 border-gray-400 bg-blue-50 focus:bg-white focus:border-primary-500 focus:outline-none px-2 py-0.5 text-center min-w-[120px] rounded-t transition-colors font-medium text-primary-900"
                placeholder={`(${config?.max_words || 3} words)`}
                aria-label={`Blank ${match[1]}`}
              />
            </span>
          );
        }
        return (
          <span key={idx} className="inline">
            <ReactMarkdown 
              remarkPlugins={[remarkGfm, remarkBreaks]} 
              components={{
                p: ({node, ...props}) => <span {...props} />
              }}
            >
              {part}
            </ReactMarkdown>
          </span>
        );
      })}
    </div>
  );
}
