import Sidebar from './Sidebar';
import Navbar from './Navbar';

export default function PageWrapper({ children, title }) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="flex-1 p-6">
          {title && (
            <h1 className="text-2xl font-semibold text-gray-900 mb-6">{title}</h1>
          )}
          {children}
        </main>
      </div>
    </div>
  );
}
