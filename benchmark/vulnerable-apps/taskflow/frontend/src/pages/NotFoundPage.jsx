import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900">404</h1>
        <p className="text-gray-600 mt-2">Page not found.</p>
        <Link to="/" className="mt-4 inline-block text-indigo-600 hover:underline">Back to home</Link>
      </div>
    </div>
  );
}
