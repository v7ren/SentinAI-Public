import { Link } from 'react-router-dom';
import PageWrapper from '../components/Layout/PageWrapper';
import { useTasks } from '../hooks/useTasks';
import { useProjects } from '../hooks/useProjects';
import TaskCard from '../components/Tasks/TaskCard';
import Button from '../components/UI/Button';
import Spinner from '../components/UI/Spinner';

export default function DashboardPage() {
  const { tasks, loading: tasksLoading } = useTasks();
  const { projects, loading: projectsLoading } = useProjects();

  const openCount = tasks.filter((t) => t.status === 'open').length;
  const overdueCount = tasks.filter((t) => t.due_date && new Date(t.due_date) < new Date() && t.status !== 'done').length;
  const recentTasks = tasks.slice(0, 5);

  return (
    <PageWrapper title="Dashboard">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-sm font-medium text-gray-500">Open tasks</h3>
          <p className="text-3xl font-semibold text-gray-900 mt-1">{tasksLoading ? '—' : openCount}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-sm font-medium text-gray-500">Overdue</h3>
          <p className="text-3xl font-semibold text-gray-900 mt-1">{tasksLoading ? '—' : overdueCount}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-sm font-medium text-gray-500">Projects</h3>
          <p className="text-3xl font-semibold text-gray-900 mt-1">{projectsLoading ? '—' : projects.length}</p>
        </div>
      </div>

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Recent activity</h2>
        <Link to="/tasks">
          <Button size="sm">New task</Button>
        </Link>
      </div>

      {tasksLoading ? (
        <Spinner className="mx-auto my-8" />
      ) : recentTasks.length === 0 ? (
        <p className="text-gray-500">No tasks yet. Create a project and add tasks.</p>
      ) : (
        <div className="space-y-3">
          {recentTasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      )}
    </PageWrapper>
  );
}
