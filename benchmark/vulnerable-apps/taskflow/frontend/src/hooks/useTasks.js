import { useState, useEffect, useCallback } from 'react';
import * as tasksApi from '../api/tasks';

export function useTasks(projectId, search) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = projectId ? { projectId, search: search || undefined } : {};
      const res = await tasksApi.list(params);
      setTasks(res.data.data || []);
    } catch (e) {
      setError(e.response?.data?.message || e.message);
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }, [projectId, search]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  const createTask = async (data) => {
    const res = await tasksApi.create(data);
    setTasks((prev) => [res.data.data, ...prev]);
    return res.data.data;
  };

  const updateTask = async (taskId, data) => {
    const res = await tasksApi.update(taskId, data);
    setTasks((prev) => prev.map((t) => (t.id === parseInt(taskId, 10) ? res.data.data : t)));
    return res.data.data;
  };

  const deleteTask = async (taskId) => {
    await tasksApi.remove(taskId);
    setTasks((prev) => prev.filter((t) => t.id !== parseInt(taskId, 10)));
  };

  return { tasks, loading, error, refetch: fetch, createTask, updateTask, deleteTask };
}
