import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

/**
 * MarkdownEditor - A reusable component for rich text editing using Markdown.
 * 
 * Features:
 * - Write/Preview tabs
 * - Basic toolbar (Bold, Italic, List, etc.)
 * - Renders markdown with tailwind typography plugin (prose)
 * - Handles newlines and paragraphs intuitively
 */
export default function MarkdownEditor({ value, onChange, placeholder, rows = 6, label, className = '' }) {
  const [activeTab, setActiveTab] = useState('write'); // 'write' | 'preview'

  const insertText = (before, after = '') => {
    const textarea = document.getElementById(`markdown-editor-${label || 'default'}`);
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    const selectedText = text.substring(start, end);
    
    const newText = text.substring(0, start) + before + selectedText + after + text.substring(end);
    
    onChange({ target: { value: newText } });
    
    // Restore focus and selection (approximate)
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + before.length, end + before.length);
    }, 0);
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {label && <label className="block text-sm font-medium text-gray-700">{label}</label>}
      
      <div className="border border-gray-300 rounded-lg overflow-hidden bg-white">
        {/* Toolbar / Tabs */}
        <div className="flex items-center justify-between bg-gray-50 border-b border-gray-200 px-2 py-1">
          <div className="flex space-x-1">
            <button
              type="button"
              onClick={() => setActiveTab('write')}
              className={`px-3 py-1.5 text-sm font-medium rounded-t-md ${
                activeTab === 'write' 
                  ? 'bg-white text-primary-600 border-t border-l border-r border-gray-200 -mb-1.5 pb-2 z-10' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              }`}
            >
              Write
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('preview')}
              className={`px-3 py-1.5 text-sm font-medium rounded-t-md ${
                activeTab === 'preview' 
                  ? 'bg-white text-primary-600 border-t border-l border-r border-gray-200 -mb-1.5 pb-2 z-10' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              }`}
            >
              Preview
            </button>
          </div>

          {activeTab === 'write' && (
            <div className="flex items-center space-x-1 text-gray-600">
              <button
                type="button"
                onClick={() => insertText('**', '**')}
                className="p-1 hover:bg-gray-200 rounded"
                title="Bold"
              >
                <b>B</b>
              </button>
              <button
                type="button"
                onClick={() => insertText('*', '*')}
                className="p-1 hover:bg-gray-200 rounded italic"
                title="Italic"
              >
                I
              </button>
              <div className="w-px h-4 bg-gray-300 mx-1"></div>
              <button
                type="button"
                onClick={() => insertText('- ')}
                className="p-1 hover:bg-gray-200 rounded"
                title="Bullet List"
              >
                • List
              </button>
              <button
                type="button"
                onClick={() => insertText('1. ')}
                className="p-1 hover:bg-gray-200 rounded"
                title="Numbered List"
              >
                1. List
              </button>
              <div className="w-px h-4 bg-gray-300 mx-1"></div>
              <button
                type="button"
                onClick={() => insertText('### ')}
                className="p-1 hover:bg-gray-200 rounded font-bold text-xs"
                title="Heading 3"
              >
                H3
              </button>
            </div>
          )}
        </div>

        {/* Content Area */}
        <div className="p-0">
          {activeTab === 'write' ? (
            <textarea
              id={`markdown-editor-${label || 'default'}`}
              value={value}
              onChange={onChange}
              rows={rows}
              className="w-full p-4 border-none focus:ring-0 font-mono text-sm resize-y min-h-[150px]"
              placeholder={placeholder || "Type markdown here... (Use **bold**, *italic*, - list)"}
            />
          ) : (
            <div 
              className="prose prose-sm max-w-none p-4 min-h-[150px] overflow-y-auto bg-gray-50"
              style={{ maxHeight: `${rows * 1.5 + 4}rem` }}
            >
              {value ? (
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm, remarkBreaks]}
                  components={{
                    // Ensure links open in new tab
                    a: ({node, ...props}) => <a target="_blank" rel="noopener noreferrer" {...props} />
                  }}
                >
                  {value}
                </ReactMarkdown>
              ) : (
                <p className="text-gray-400 italic">Nothing to preview</p>
              )}
            </div>
          )}
        </div>
        
        {/* Footer help text */}
        <div className="bg-gray-50 px-3 py-1 border-t border-gray-200 text-xs text-gray-500 flex justify-between">
          <span>Markdown supported</span>
          <a 
            href="https://www.markdownguide.org/basic-syntax/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-primary-600 hover:underline"
          >
            Formatting Help
          </a>
        </div>
      </div>
    </div>
  );
}
