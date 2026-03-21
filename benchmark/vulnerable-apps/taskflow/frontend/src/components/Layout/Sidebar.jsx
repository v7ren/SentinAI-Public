import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export default function Sidebar() {
  const { user } = useAuth();

  const nav = [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/projects', label: 'Projects' },
    { to: '/tasks', label: 'Tasks' },
    { to: '/settings', label: 'Settings' },
  ];
  if (user?.role === 'admin') nav.push({ to: '/admin', label: 'Admin' });

  return (
    <aside className="w-56 bg-gray-900 text-white min-h-screen p-4">
      <Link to="/" className="text-xl font-bold text-indigo-300 block mb-8">TaskFlow</Link>
      <nav className="space-y-1">
        {nav.map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            className="block py-2 px-3 rounded-lg hover:bg-gray-800 text-gray-200"
          >
            {label}
          </Link>
        ))}
      </nav>
      <div className="mt-8 pt-8 border-t border-gray-700 text-sm text-gray-400">
        {user?.email}
      </div>
    </aside>
  );
}
