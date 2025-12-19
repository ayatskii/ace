import { Link } from 'react-router-dom';

export default function TestCard({ test }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{test.title}</h3>
          <p className="text-sm text-gray-600 mt-1">{test.description}</p>
        </div>
        <span className={`
          px-3 py-1 rounded-full text-xs font-medium
          ${test.test_type === 'academic' 
            ? 'bg-primary-100 text-primary-700' 
            : 'bg-purple-100 text-purple-700'
          }
        `}>
          {test.test_type === 'academic' ? 'Academic' : 'General Training'}
        </span>
      </div>
      
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
        <div className="text-sm text-gray-600">
          <span className="font-medium">4 Sections</span> • Listening, Reading, Writing, Speaking
        </div>
        <Link
          to={`/student/tests/${test.id}`}
          className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition"
        >
          View Test
        </Link>
      </div>
    </div>
  );
}
