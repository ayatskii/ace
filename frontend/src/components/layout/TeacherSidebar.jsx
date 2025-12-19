import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export default function TeacherSidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuthStore();
  
  const isActive = (path) => location.pathname === path;
  
  const navItems = [
    { path: '/teacher/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/teacher/grading/writing', label: 'Grade Writing', icon: '✍️' },
    { path: '/teacher/grading/speaking', label: 'Grade Speaking', icon: '🎤' },
    { path: '/teacher/history', label: 'History', icon: '📋' },
  ];
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <div className="bg-primary-600 text-white font-bold text-xl px-3 py-2 rounded-lg text-center">
          IELTS
        </div>
        <p className="text-xs text-gray-600 text-center mt-2">Teacher Portal</p>
      </div>
      
      <nav className="flex-1 mt-5 px-3">
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
      
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={handleLogout}
          className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium transition"
        >
          Logout
        </button>
      </div>
    </aside>
  );
}
