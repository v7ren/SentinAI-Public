import { useParams, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import client from '../api/client';
import PageWrapper from '../components/Layout/PageWrapper';
import ProjectSettings from '../components/Projects/ProjectSettings';
import Button from '../components/UI/Button';
import Spinner from '../components/UI/Spinner';

export default function ProjectDetailPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    client.get(`/api/v1/projects/${projectId}`)
      .then((res) => setProject(res.data.data))
      .catch(() => setProject(null))
      .finally(() => setLoading(false));
  }, [projectId]);

  if (loading) return <PageWrapper><Spinner className="mx-auto my-8" /></PageWrapper>;
  if (!project) return <PageWrapper><p className="text-gray-500">Project not found.</p></PageWrapper>;

  return (
    <PageWrapper title={project.name}>
      <p className="text-gray-600 mb-6">{project.description || 'No description.'}</p>
      <div className="flex gap-4 mb-6">
        <Link to={`/tasks?projectId=${project.id}`}>
          <Button>View tasks</Button>
        </Link>
        <Button variant="outline" onClick={() => setShowSettings(!showSettings)}>
          {showSettings ? 'Hide settings' : 'Settings'}
        </Button>
      </div>
      {showSettings && (
        <ProjectSettings project={project} onUpdated={() => setLoading(true)} />
      )}
    </PageWrapper>
  );
}
