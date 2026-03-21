import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import client from '../../api/client';
import Badge from '../UI/Badge';
import Button from '../UI/Button';
import Spinner from '../UI/Spinner';
import CommentList from './CommentList';
import { priorityLabel, statusLabel, formatDate } from '../../utils/formatters';

export default function TaskDetail() {
  const { taskId } = useParams();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    client.get(`/api/v1/tasks/${taskId}`)
      .then((res) => setTask(res.data.data))
      .catch((e) => setError(e.response?.data?.message || e.message))
      .finally(() => setLoading(false));
  }, [taskId]);

  if (loading) return <Spinner className="mx-auto mt-8" />;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!task) return <p className="text-gray-500">Task not found.</p>;

  return (
    <div className="max-w-3xl">
      <div className="mb-6 flex gap-2">
        <Badge>{statusLabel(task.status)}</Badge>
        <Badge variant="info">{priorityLabel(task.priority)}</Badge>
        {task.due_date && <span className="text-sm text-gray-500">Due {formatDate(task.due_date)}</span>}
      </div>
      <h1 className="text-2xl font-semibold text-gray-900 mb-4">{task.title}</h1>
      <div
        className="prose max-w-none text-gray-700"
        dangerouslySetInnerHTML={{ __html: task.description || '<p>No description.</p>' }}
      />
      <CommentList taskId={task.id} />
    </div>
  );
}
