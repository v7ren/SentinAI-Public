import { useState } from 'react';
import PageWrapper from '../components/Layout/PageWrapper';
import { useAuth } from '../hooks/useAuth';
import client from '../api/client';
import Button from '../components/UI/Button';

export default function SettingsPage() {
  const { user } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      await client.patch('/api/v1/users/profile', { full_name: fullName });
      setMessage('Profile updated.');
    } catch (err) {
      setMessage(err.response?.data?.message || 'Update failed');
    } finally {
      setSaving(false);
    }
  };

  return (
    <PageWrapper title="Settings">
      <form onSubmit={handleSubmit} className="max-w-md space-y-4">
        {message && <p className="text-sm text-gray-600">{message}</p>}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input type="text" value={user?.email || ''} readOnly className="w-full border border-gray-200 rounded-lg px-3 py-2 bg-gray-50" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Full name</label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2"
          />
        </div>
        <Button type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save'}</Button>
      </form>
    </PageWrapper>
  );
}
