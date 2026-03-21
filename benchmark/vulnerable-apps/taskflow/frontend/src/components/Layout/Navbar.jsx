import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Button from '../UI/Button';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <Link to="/dashboard" className="font-semibold text-gray-800">TaskFlow</Link>
        <span className="text-sm text-gray-500">{user?.full_name}</span>
      </div>
      <nav className="flex items-center gap-4">
        <Link to="/settings" className="text-sm text-gray-600 hover:text-gray-900">Settings</Link>
        <Button variant="outline" size="sm" onClick={logout}>Log out</Button>
      </nav>
    </header>
  );
}
