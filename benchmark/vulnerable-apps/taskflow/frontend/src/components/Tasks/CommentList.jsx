import { useState, useEffect } from 'react';
import client from '../../api/client';
import { formatRelative } from '../../utils/formatters';

export default function CommentList({ taskId }) {
  const [comments, setComments] = useState([]);
  const [body, setBody] = useState('');
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);

  const fetchComments = () => {
    client.get(`/api/v1/tasks/${taskId}/comments`).then((res) => {
      setComments(res.data.data || []);
    }).catch(() => setComments([])).finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchComments();
  }, [taskId]);

  const submit = async (e) => {
    e.preventDefault();
    if (!body.trim()) return;
    setPosting(true);
    try {
      await client.post(`/api/v1/tasks/${taskId}/comments`, { body: body.trim() });
      setBody('');
      fetchComments();
    } finally {
      setPosting(false);
    }
  };

  if (loading) return <p className="text-gray-500 text-sm">Loading comments…</p>;

  return (
    <div className="mt-8 pt-8 border-t border-gray-200">
      <h3 className="font-medium text-gray-900 mb-4">Comments</h3>
      <ul className="space-y-4 mb-6">
        {comments.length === 0 ? (
          <li className="text-gray-500 text-sm">No comments yet.</li>
        ) : (
          comments.map((c) => (
            <li key={c.id} className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                <span>{c.user_name || 'User'}</span>
                <span>{formatRelative(c.created_at)}</span>
              </div>
              <div
                className="text-gray-800"
                dangerouslySetInnerHTML={{ __html: c.body || '' }}
              />
            </li>
          ))
        )}
      </ul>
      <form onSubmit={submit}>
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Add a comment…"
          rows={3}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 mb-2"
        />
        <button
          type="submit"
          disabled={posting}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {posting ? 'Posting…' : 'Post'}
        </button>
      </form>
    </div>
  );
}
