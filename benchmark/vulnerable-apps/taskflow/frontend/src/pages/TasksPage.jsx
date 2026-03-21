import { useState } from 'react';
import PageWrapper from '../components/Layout/PageWrapper';
import { useTasks } from '../hooks/useTasks';
import { useProjects } from '../hooks/useProjects';
import TaskCard from '../components/Tasks/TaskCard';
import Modal from '../components/UI/Modal';
import TaskForm from '../components/Tasks/TaskForm';
import Button from '../components/UI/Button';
import Spinner from '../components/UI/Spinner';

export default function TasksPage() {
  const [projectId, setProjectId] = useState('');
  const [search, setSearch] = useState('');
  const { projects } = useProjects();
  const { tasks, loading, createTask } = useTasks(projectId || undefined, search);
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <PageWrapper title="Tasks">
      <div className="flex flex-wrap items-center gap-4 mb-6">
        <select
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2"
        >
          <option value="">All projects</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        <input
          type="search"
          placeholder="Search tasks…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 min-w-[200px]"
        />
        <Button onClick={() => setModalOpen(true)}>New task</Button>
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New task">
        <TaskForm
          projectId={projectId || (projects[0]?.id)}
          onSubmit={async (data) => {
            await createTask(data);
            setModalOpen(false);
          }}
          onCancel={() => setModalOpen(false)}
        />
      </Modal>

      {loading ? (
        <Spinner className="mx-auto my-8" />
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      )}
    </PageWrapper>
  );
}
