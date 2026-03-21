'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface Account {
  account_number: string;
  balance: number;
  type: string;
}

interface Transaction {
  id: number;
  from_account: string;
  to_account: string;
  amount: number;
  description: string;
  status: string;
}

export default function DashboardPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [xmlInput, setXmlInput] = useState('');
  const [xmlResult, setXmlResult] = useState('');
  const [templateInput, setTemplateInput] = useState('');
  const router = useRouter();

  // VULNERABILITY: Clickjacking protection disabled via X-Frame-Options manipulation
  useEffect(() => {
    // This attempts to disable frame protection
    if (typeof document !== 'undefined') {
      const meta = document.createElement('meta');
      meta.httpEquiv = 'X-Frame-Options';
      meta.content = 'ALLOWALL';
      document.head.appendChild(meta);
    }
  }, []);

  // VULNERABILITY: Insecure token storage and transmission
  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (!token) {
      router.push('/login');
      return;
    }

    try {
      // VULNERABILITY: Client-side JWT decoding (exposes algorithm confusion)
      const payload = JSON.parse(atob(token.split('.')[1]));
      setUser({ ...JSON.parse(userData || '{}'), ...payload });

      // Auto-refresh token (no expiration check)
      refreshToken(token);
    } catch (e) {
      router.push('/login');
    }
  }, [router]);

  const refreshToken = async (oldToken: string) => {
    try {
      const response = await fetch('http://localhost:5007/api/token/refresh', {
        headers: { 'Authorization': `Bearer ${oldToken}` },
      });
      const data = await response.json();
      if (data.token) {
        localStorage.setItem('token', data.token);
      }
    } catch (e) {
      console.error('Token refresh failed');
    }
  };

  const fetchAccounts = async () => {
    // VULNERABILITY: Hardcoded account number (IDOR demo)
    const accountNumber = 'SB-1000001';

    try {
      const response = await fetch(`http://localhost:5007/api/account/balance?account=${accountNumber}`, {
        credentials: 'include',
      });
      const data = await response.json();
      if (response.ok) {
        setAccounts([data]);
      }
    } catch (e) {
      console.error('Failed to fetch accounts');
    }
  };

  const handleXmlSubmit = async () => {
    // VULNERABILITY: Sending unsanitized XML to server
    try {
      const response = await fetch('http://localhost:5007/api/payments/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/xml' },
        body: xmlInput,
      });
      const data = await response.json();
      setXmlResult(JSON.stringify(data, null, 2));
    } catch (e) {
      setXmlResult('Error processing XML');
    }
  };

  const handleTemplateRender = async () => {
    // VULNERABILITY: SSTI via user-provided template
    try {
      const response = await fetch('http://localhost:5007/api/account/statement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_number: 'SB-1000001',
          template: templateInput,
        }),
      });
      const data = await response.json();
      setXmlResult(data.statement || data.error);
    } catch (e) {
      setXmlResult('Error rendering template');
    }
  };

  const logout = () => {
    // VULNERABILITY: Session not invalidated on server
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/login');
  };

  if (!user) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation */}
      <nav className="bg-blue-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold">SecureBank</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm">Welcome, {user.username}</span>
              <span className="text-xs bg-blue-700 px-2 py-1 rounded">{user.role}</span>
              <button onClick={logout} className="text-sm hover:text-blue-200">
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Account Summary */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Account Summary</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {accounts.map((account) => (
                  <div key={account.account_number} className="bg-blue-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">{account.type} Account</p>
                    <p className="text-2xl font-bold text-blue-900">${account.balance?.toLocaleString()}</p>
                    <p className="text-xs text-gray-500">{account.account_number}</p>
                  </div>
                ))}
                {accounts.length === 0 && (
                  <div className="col-span-2 text-center py-8 text-gray-500">
                    <button
                      onClick={fetchAccounts}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Load Account
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="flex space-x-4">
                <Link
                  href="/transfer"
                  className="flex-1 bg-blue-600 text-white text-center py-3 rounded-lg hover:bg-blue-700"
                >
                  Transfer Money
                </Link>
                <button
                  onClick={() => {}}
                  className="flex-1 bg-gray-100 text-gray-700 text-center py-3 rounded-lg hover:bg-gray-200"
                >
                  Pay Bills
                </button>
                <button
                  onClick={() => {}}
                  className="flex-1 bg-gray-100 text-gray-700 text-center py-3 rounded-lg hover:bg-gray-200"
                >
                  Deposit Check
                </button>
              </div>
            </div>

            {/* XXE Testing Panel (Disguised as "Payment Processing") */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Processing (XML)</h3>
              <textarea
                value={xmlInput}
                onChange={(e) => setXmlInput(e.target.value)}
                placeholder="Paste XML payment data here..."
                rows={4}
                className="w-full border border-gray-300 rounded-md px-3 py-2 font-mono text-sm"
              />
              <button
                onClick={handleXmlSubmit}
                className="mt-3 w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700"
              >
                Process Payment
              </button>
              {xmlResult && (
                <pre className="mt-3 bg-gray-100 p-3 rounded text-xs overflow-auto">{xmlResult}</pre>
              )}
            </div>

            {/* SSTI Testing Panel (Disguised as "Statement Template") */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Statement Template</h3>
              <p className="text-sm text-gray-600 mb-2">Customize your statement format:</p>
              <textarea
                value={templateInput}
                onChange={(e) => setTemplateInput(e.target.value)}
                placeholder="e.g., Hello {{ account_number }}, your balance is ${{ balance }}"
                rows={3}
                className="w-full border border-gray-300 rounded-md px-3 py-2 font-mono text-sm"
              />
              <button
                onClick={handleTemplateRender}
                className="mt-3 w-full bg-purple-600 text-white py-2 rounded-md hover:bg-purple-700"
              >
                Preview Statement
              </button>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* User Info */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile</h3>
              <div className="space-y-2 text-sm">
                <p><span className="text-gray-500">Username:</span> {user.username}</p>
                <p><span className="text-gray-500">Email:</span> {user.email}</p>
                <p><span className="text-gray-500">Role:</span> {user.role}</p>
                {/* VULNERABILITY: Sensitive data displayed without masking */}
                {user.ssn && (
                  <p><span className="text-gray-500">SSN:</span> {user.ssn}</p>
                )}
                {user.credit_score && (
                  <p><span className="text-gray-500">Credit Score:</span> {user.credit_score}</p>
                )}
              </div>
            </div>

            {/* Admin Link - VULNERABILITY: Client-side only role check */}
            {user.role === 'admin' && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h4 className="text-red-800 font-semibold mb-2">Admin Panel</h4>
                <Link href="/admin" className="text-red-600 hover:text-red-800 text-sm">
                  Access Admin Controls →
                </Link>
              </div>
            )}

            {/* JWT Display - VULNERABILITY: Exposes token */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="text-yellow-800 font-semibold mb-2">Debug: Your Token</h4>
              <code className="text-xs break-all text-yellow-700">
                {localStorage.getItem('token')?.substring(0, 50)}...
              </code>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
