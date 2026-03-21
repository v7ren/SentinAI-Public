import { useState, useEffect, useCallback } from 'react';
import * as projectsApi from '../api/projects';

export function useProjects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await projectsApi.list();
      setProjects(res.data.data || []);
    } catch (e) {
      setError(e.response?.data?.message || e.message);
      setProjects([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  const createProject = async (data) => {
    const res = await projectsApi.create(data);
    setProjects((prev) => [res.data.data, ...prev]);
    return res.data.data;
  };

  const updateProject = async (projectId, data) => {
    const res = await projectsApi.update(projectId, data);
    setProjects((prev) => prev.map((p) => (p.id === parseInt(projectId, 10) ? res.data.data : p)));
    return res.data.data;
  };

  const deleteProject = async (projectId) => {
    await projectsApi.remove(projectId);
    setProjects((prev) => prev.filter((p) => p.id !== parseInt(projectId, 10)));
  };

  return { projects, loading, error, refetch: fetch, createProject, updateProject, deleteProject };
}
