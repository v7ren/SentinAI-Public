import { useState, useEffect } from 'react';
import { getAllUsers, deleteUser } from '../../api/admin';
import Button from '../UI/Button';
import Spinner from '../UI/Spinner';

export default function UserTable() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = () => {
    setLoading(true);
    getAllUsers()
      .then((res) => setUsers(res.data.data || []))
      .catch((e) => setError(e.response?.data?.message || e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => load(), []);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this user?')) return;
    try {
      await deleteUser(id);
      setUsers((prev) => prev.filter((u) => u.id !== id));
    } catch (e) {
      setError(e.response?.data?.message || e.message);
    }
  };

  if (loading) return <Spinner className="mx-auto mt-8" />;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Org</th>
            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {users.map((u) => (
            <tr key={u.id}>
              <td className="px-4 py-3 text-sm text-gray-900">{u.id}</td>
              <td className="px-4 py-3 text-sm text-gray-900">{u.email}</td>
              <td className="px-4 py-3 text-sm text-gray-900">{u.full_name}</td>
              <td className="px-4 py-3 text-sm text-gray-900">{u.role}</td>
              <td className="px-4 py-3 text-sm text-gray-900">{u.org_id}</td>
              <td className="px-4 py-3 text-right">
                <Button variant="danger" size="sm" onClick={() => handleDelete(u.id)}>Delete</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
