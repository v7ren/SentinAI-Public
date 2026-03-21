'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function TransferPage() {
  const [fromAccount, setFromAccount] = useState('SB-1000001');
  const [toAccount, setToAccount] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [confirming, setConfirming] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!confirming) {
      setConfirming(true);
      return;
    }

    setLoading(true);
    setResult('');

    try {
      // VULNERABILITY: CSRF - no CSRF token in request
      const response = await fetch('http://localhost:5007/api/transfer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // VULNERABILITY: Token sent in header but no CSRF protection for state-changing action
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
        credentials: 'include',
        body: JSON.stringify({
          from_account: fromAccount,
          to_account: toAccount,
          amount: parseFloat(amount),
          description,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setResult(`Success: ${data.message}`);
        setTimeout(() => {
          router.push('/dashboard');
        }, 2000);
      } else {
        setResult(`Error: ${data.message || 'Transfer failed'}`);
      }
    } catch (err) {
      setResult('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <nav className="bg-blue-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold">SecureBank</span>
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="text-sm hover:text-blue-200"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </nav>

      {/* VULNERABILITY: No X-Frame-Options header allows clickjacking */}
      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white shadow rounded-lg p-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Transfer Money</h1>

          {result && (
            <div className={`mb-4 p-4 rounded-md ${result.includes('Success') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {result}
            </div>
          )}

          {/* VULNERABILITY: Clickjacking - this form can be framed by attacker */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                From Account
              </label>
              <input
                type="text"
                value={fromAccount}
                onChange={(e) => setFromAccount(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                To Account Number
              </label>
              <input
                type="text"
                value={toAccount}
                onChange={(e) => setToAccount(e.target.value)}
                placeholder="SB-XXXXXXXX"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Amount ($)
              </label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Description (Optional)
              </label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g., Rent payment"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {confirming && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <p className="text-sm text-yellow-800">
                  Please confirm: Transfer <strong>${amount}</strong> to account <strong>{toAccount}</strong>
                </p>
              </div>
            )}

            {/* VULNERABILITY: Clickjacking target - opaque overlay could hide malicious UI */}
            <div className="relative">
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Processing...' : confirming ? 'Confirm Transfer' : 'Review Transfer'}
              </button>
            </div>

            {confirming && (
              <button
                type="button"
                onClick={() => setConfirming(false)}
                className="w-full py-3 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancel
              </button>
            )}
          </form>

          {/* VULNERABILITY: Invisible iframe could overlay this for clickjacking */}
          <div className="mt-8 p-4 bg-gray-50 rounded-md">
            <p className="text-xs text-gray-500">
              Need help? Call our 24/7 support line at 1-800-SECURE or email support@securebank.com
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
