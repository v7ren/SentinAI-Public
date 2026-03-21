import { useState } from 'react';
import PageWrapper from '../components/Layout/PageWrapper';
import { useProjects } from '../hooks/useProjects';
import ProjectCard from '../components/Projects/ProjectCard';
import Modal from '../components/UI/Modal';
import Button from '../components/UI/Button';
import Spinner from '../components/UI/Spinner';

export default function ProjectsPage() {
  const { projects, loading, createProject } = useProjects();
  const [modalOpen, setModalOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createProject({ name, description });
      setName('');
      setDescription('');
      setModalOpen(false);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <PageWrapper title="Projects">
      <div className="flex justify-end mb-6">
        <Button onClick={() => setModalOpen(true)}>New project</Button>
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New project">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            />
          </div>
          <Button type="submit" disabled={submitting}>{submitting ? 'Creating…' : 'Create'}</Button>
        </form>
      </Modal>

      {loading ? (
        <Spinner className="mx-auto my-8" />
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((p) => (
            <ProjectCard key={p.id} project={p} />
          ))}
        </div>
      )}
    </PageWrapper>
  );
}
