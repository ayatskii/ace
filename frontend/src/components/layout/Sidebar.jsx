import { Link, useLocation } from 'react-router-dom';

export default function Sidebar() {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;
  
  const navItems = [
    { path: '/student/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/student/tests', label: 'Browse Tests', icon: '📝' },
    { path: '/student/results', label: 'My Results', icon: '🏆' },
    { path: '/student/profile', label: 'Profile', icon: '👤' },
  ];
  
  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen">
      <nav className="mt-5 px-3">
        <div className="space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center px-4 py-3 text-sm font-medium rounded-lg transition
                ${isActive(item.path)
                  ? 'bg-primary-50 text-primary-700 border-l-4 border-primary-600'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-primary-600'
                }
              `}
            >
              <span className="text-xl mr-3">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </div>
      </nav>
    </aside>
  );
}
