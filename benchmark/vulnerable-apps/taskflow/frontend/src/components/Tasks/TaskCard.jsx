import { Link } from 'react-router-dom';
import Badge from '../UI/Badge';
import { priorityLabel, statusLabel, formatDate } from '../../utils/formatters';

export default function TaskCard({ task }) {
  const statusVariant = { open: 'default', in_progress: 'info', done: 'success' }[task.status] || 'default';
  const priorityVariant = { high: 'danger', medium: 'warning', low: 'default' }[task.priority] || 'default';

  return (
    <Link
      to={`/tasks/${task.id}`}
      className="block p-4 bg-white rounded-lg border border-gray-200 hover:border-indigo-300 hover:shadow-sm transition"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-medium text-gray-900 truncate flex-1">{task.title}</h3>
        <div className="flex gap-1 shrink-0">
          <Badge variant={statusVariant}>{statusLabel(task.status)}</Badge>
          <Badge variant={priorityVariant}>{priorityLabel(task.priority)}</Badge>
        </div>
      </div>
      {task.due_date && (
        <p className="text-sm text-gray-500 mt-1">Due {formatDate(task.due_date)}</p>
      )}
      {task.assignee_name && (
        <p className="text-sm text-gray-500 mt-0.5">Assignee: {task.assignee_name}</p>
      )}
    </Link>
  );
}
