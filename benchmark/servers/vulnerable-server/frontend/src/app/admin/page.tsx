'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  company: string;
  created_at: string;
}

interface SystemStatus {
  db_status: string;
  storage_used: string;
  active_users: number;
  last_backup: string;
}

export default function AdminPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [logs, setLogs] = useState('');
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [selectedUser, setSelectedUser] = useState<number | null>(null);
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState('');
  const router = useRouter();

  useEffect(() => {
    fetchUsers();
    fetchSystemStatus();
    fetchLogs();
  }, []);

  const fetchUsers = async () => {
    const response = await fetch('http://localhost:5006/api/admin/users', {
      credentials: 'include',
    });
    if (response.ok) {
      const data = await response.json();
      setUsers(data.users);
    }
  };

  const fetchSystemStatus = async () => {
    const response = await fetch('http://localhost:5006/api/admin/status', {
      credentials: 'include',
    });
    if (response.ok) {
      const data = await response.json();
      setSystemStatus(data);
    }
  };

  const fetchLogs = async () => {
    const response = await fetch('http://localhost:5006/api/admin/logs?lines=100', {
      credentials: 'include',
    });
    if (response.ok) {
      const data = await response.json();
      setLogs(data.logs);
    }
  };

  const runDiagnostics = async (host: string) => {
    const response = await fetch(`http://localhost:5006/api/admin/diagnostics?host=${encodeURIComponent(host)}`, {
      credentials: 'include',
    });
    const data = await response.json();
    alert(JSON.stringify(data, null, 2));
  };

  const updateUser = async (userId: number, updates: any) => {
    await fetch(`http://localhost:5006/api/admin/users/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(updates),
    });
    fetchUsers();
  };

  const deleteUser = async (userId: number) => {
    if (confirm('Are you sure you want to delete this user?')) {
      await fetch(`http://localhost:5006/api/admin/users/${userId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      fetchUsers();
    }
  };

  const runCustomQuery = async () => {
    const response = await fetch('http://localhost:5006/api/admin/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ query }),
    });
    const data = await response.json();
    setQueryResult(JSON.stringify(data, null, 2));
  };

  const syncExternalData = async (source: string) => {
    await fetch(`http://localhost:5006/api/admin/sync?source=${encodeURIComponent(source)}`, {
      credentials: 'include',
    });
    alert('Sync initiated');
  };

  const processData = async (data: string) => {
    const response = await fetch('http://localhost:5006/api/admin/process', {
      method: 'POST',
      credentials: 'include',
      body: data,
    });
    return response.json();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-red-600 rounded-lg mr-2"></div>
              <span className="text-xl font-bold text-gray-900">Admin Panel</span>
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="text-gray-600 hover:text-gray-900"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* System Status */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Database Status</h3>
            <p className="text-2xl font-bold text-green-600">{systemStatus?.db_status || 'Connected'}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Storage Used</h3>
            <p className="text-2xl font-bold text-gray-900">{systemStatus?.storage_used || '2.4 GB'}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Active Users</h3>
            <p className="text-2xl font-bold text-gray-900">{systemStatus?.active_users || 142}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Last Backup</h3>
            <p className="text-lg font-bold text-gray-900">{systemStatus?.last_backup || '2 hours ago'}</p>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* User Management */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">User Management</h2>
            </div>
            <div className="p-6">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead>
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {users.length === 0 ? (
                      <tr>
                        <td colSpan={3} className="px-4 py-4 text-center text-gray-500">
                          Loading users...
                        </td>
                      </tr>
                    ) : (
                      users.map((user) => (
                        <tr key={user.id}>
                          <td className="px-4 py-3">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{user.name}</div>
                              <div className="text-sm text-gray-500">{user.email}</div>
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 text-xs rounded-full ${user.role === 'admin' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                              {user.role}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <button
                              onClick={() => setSelectedUser(user.id)}
                              className="text-indigo-600 hover:text-indigo-900 text-sm mr-3"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => deleteUser(user.id)}
                              className="text-red-600 hover:text-red-900 text-sm"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* System Logs */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">System Logs</h2>
            </div>
            <div className="p-6">
              <pre className="bg-gray-900 text-green-400 p-4 rounded-lg text-xs overflow-auto h-64 font-mono">
                {logs || 'Loading logs...'}
              </pre>
              <button
                onClick={fetchLogs}
                className="mt-4 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200"
              >
                Refresh Logs
              </button>
            </div>
          </div>
        </div>

        {/* Advanced Tools */}
        <div className="mt-8 grid lg:grid-cols-3 gap-6">
          {/* Database Query */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Database Query</h3>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="SELECT * FROM users WHERE..."
              rows={4}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 font-mono text-sm mb-3"
            />
            <button
              onClick={runCustomQuery}
              className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700"
            >
              Execute Query
            </button>
            {queryResult && (
              <pre className="mt-3 bg-gray-100 p-3 rounded text-xs overflow-auto max-h-40">
                {queryResult}
              </pre>
            )}
          </div>

          {/* Network Diagnostics */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Network Diagnostics</h3>
            <div className="space-y-3">
              <div>
                <input
                  type="text"
                  id="diag-host"
                  placeholder="Enter hostname or IP"
                  defaultValue="localhost"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
              <button
                onClick={() => runDiagnostics((document.getElementById('diag-host') as HTMLInputElement).value)}
                className="w-full bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200"
              >
                Run Ping Test
              </button>
            </div>
          </div>

          {/* External Sync */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">External Data Sync</h3>
            <div className="space-y-3">
              <input
                type="text"
                id="sync-source"
                placeholder="https://api.external-service.com/data"
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
              <button
                onClick={() => syncExternalData((document.getElementById('sync-source') as HTMLInputElement).value)}
                className="w-full bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200"
              >
                Sync Data
              </button>
            </div>
          </div>
        </div>

        {/* Maintenance Mode */}
        <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-yellow-900">Maintenance Mode</h3>
              <p className="text-yellow-700">Enable to put the site in maintenance mode</p>
            </div>
            <button
              onClick={() => setMaintenanceMode(!maintenanceMode)}
              className={`px-6 py-3 rounded-lg font-semibold ${maintenanceMode ? 'bg-yellow-600 text-white' : 'bg-white text-yellow-700 border border-yellow-300'}`}
            >
              {maintenanceMode ? 'Disable' : 'Enable'}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
