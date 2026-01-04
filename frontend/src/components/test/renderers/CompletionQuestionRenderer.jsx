import { useMemo, createContext, useContext } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

// Context to pass data to the markdown components without breaking stability
const CompletionContext = createContext(null);

// Stable component for rendering blanks
const BlankLink = ({ node, href, ...props }) => {
  const { answer, blanks, handleInputChange } = useContext(CompletionContext);

  // Check if this is a blank marker
  if (href && href.startsWith('#blank-')) {
    const blankNum = href.split('-')[1];
    const blankId = `BLANK_${blankNum}`;
    const config = blanks?.find(b => b.blank_id === blankId);
    const currentValue = answer?.[blankId] || '';
    
    return (
      <span className="inline-block mx-1">
        <input
          type="text"
          value={currentValue}
          onChange={(e) => handleInputChange(blankId, e.target.value)}
          className="border-b-2 border-gray-400 bg-blue-50 focus:bg-white focus:border-primary-500 focus:outline-none px-2 py-0.5 text-center min-w-[120px] rounded-t transition-colors font-medium text-primary-900"
          placeholder={`(${config?.max_words || 3} words)`}
          aria-label={`Blank ${blankNum}`}
        />
      </span>
    );
  }
  
  // Normal link
  return <a href={href} target="_blank" rel="noopener noreferrer" {...props} />;
};

export default function CompletionQuestionRenderer({ question, answer, onAnswerChange }) {
  const { template_text, blanks } = question.type_specific_data || {};
  
  const handleInputChange = (blankId, value) => {
    // Update the answer object: { [blankId]: value }
    const newAnswer = { ...answer, [blankId]: value };
    onAnswerChange(newAnswer);
  };

  if (!template_text) return <div>Invalid question format</div>;

  // Replace [BLANK_X] with markdown links [BLANK_X](#blank-X)
  // This allows ReactMarkdown to handle the structure (paragraphs, lists) correctly
  // We use a hash URL (#blank-X) to avoid URL sanitization stripping custom protocols
  const processedTemplate = template_text.replace(/\[BLANK_(\d+)\]/g, '[BLANK_$1](#blank-$1)');

  // Memoize components to prevent re-mounting on every render (which causes focus loss)
  const components = useMemo(() => ({
    a: BlankLink,
    p: ({node, ...props}) => <p className="mb-4 last:mb-0" {...props} />
  }), []);

  return (
    <CompletionContext.Provider value={{ answer, blanks, handleInputChange }}>
      <div className="prose prose-blue max-w-none leading-loose text-lg">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm, remarkBreaks]}
          components={components}
        >
          {processedTemplate}
        </ReactMarkdown>
      </div>
    </CompletionContext.Provider>
  );
}
