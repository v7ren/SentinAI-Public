'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function AdminPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [logs, setLogs] = useState('');
  const [pingTarget, setPingTarget] = useState('localhost');
  const [pingResult, setPingResult] = useState('');
  const [userRole, setUserRole] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    // VULNERABILITY: Client-side auth check only
    const user = localStorage.getItem('user');
    if (user) {
      const parsed = JSON.parse(user);
      setUserRole(parsed.role);
      if (parsed.role !== 'admin') {
        setError('Unauthorized - Admin access required');
      }
    } else {
      router.push('/login');
    }
  }, [router]);

  const fetchUsers = async () => {
    try {
      // VULNERABILITY: Host header manipulation attempt
      const response = await fetch('http://localhost:5007/api/admin/users', {
        headers: {
          'X-Forwarded-Host': 'evil.com',
        },
        credentials: 'include',
      });
      const data = await response.json();
      setUsers(data.users || []);
    } catch (e) {
      setError('Failed to fetch users');
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await fetch('http://localhost:5007/api/admin/logs?date=2024-01-01;cat /etc/passwd', {
        credentials: 'include',
      });
      const data = await response.json();
      setLogs(data.logs || 'No logs available');
    } catch (e) {
      setLogs('Error fetching logs');
    }
  };

  const runPing = async () => {
    try {
      const response = await fetch(`http://localhost:5007/api/admin/ping?target=${encodeURIComponent(pingTarget)}`, {
        credentials: 'include',
      });
      const data = await response.json();
      setPingResult(data.output || data.error || JSON.stringify(data));
    } catch (e) {
      setPingResult('Error running ping');
    }
  };

  const handleDeserialize = async () => {
    // VULNERABILITY: Send malicious pickled data
    const maliciousPayload = btoa('mock_pickle_payload');

    try {
      const response = await fetch('http://localhost:5007/api/admin/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/octet-stream' },
        body: Uint8Array.from(atob(maliciousPayload), c => c.charCodeAt(0)),
        credentials: 'include',
      });
      const data = await response.json();
      alert(JSON.stringify(data));
    } catch (e) {
      alert('Deserialization failed');
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h1>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-red-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold">SecureBank Admin</span>
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="text-sm hover:text-red-200"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* User Management */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">User Management</h2>
            <button
              onClick={fetchUsers}
              className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Load Users
            </button>
            <div className="space-y-2 max-h-64 overflow-auto">
              {users.map((user: any) => (
                <div key={user._id || user.id} className="p-2 bg-gray-50 rounded text-sm">
                  <p><strong>{user.username}</strong> ({user.role})</p>
                  <p className="text-gray-500">{user.email}</p>
                  {/* VULNERABILITY: Exposing sensitive data */}
                  {user.ssn && <p className="text-red-500">SSN: {user.ssn}</p>}
                </div>
              ))}
            </div>
          </div>

          {/* System Logs */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">System Logs</h2>
            <button
              onClick={fetchLogs}
              className="mb-4 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Fetch Logs
            </button>
            <pre className="bg-gray-900 text-green-400 p-3 rounded text-xs overflow-auto max-h-64">
              {logs || 'Click Fetch Logs to view'}
            </pre>
          </div>

          {/* Network Diagnostics */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Network Diagnostics</h2>
            <div className="space-y-3">
              <input
                type="text"
                value={pingTarget}
                onChange={(e) => setPingTarget(e.target.value)}
                placeholder="Target host (e.g., localhost, google.com)"
                className="w-full px-3 py-2 border border-gray-300 rounded"
              />
              <button
                onClick={runPing}
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
              >
                Ping Target
              </button>
              {pingResult && (
                <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto">{pingResult}</pre>
              )}
            </div>
          </div>

          {/* Insecure Operations */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4 text-red-600">Advanced Operations</h2>
            <div className="space-y-3">
              <button
                onClick={handleDeserialize}
                className="w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Update Config (Deserialize)
              </button>
              <p className="text-xs text-gray-500">
                ⚠️ These operations require admin privileges. Use with caution.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
