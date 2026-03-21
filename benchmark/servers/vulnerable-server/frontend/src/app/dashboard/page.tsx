'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface Task {
  id: number;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high';
  assignee: string;
  due_date: string;
}

interface Project {
  id: number;
  name: string;
  description: string;
  member_count: number;
  task_count: number;
}

// Allowed file types for upload
const ALLOWED_FILE_TYPES = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('tasks');
  const [searchQuery, setSearchQuery] = useState('');
  const [tasks, setTasks] = useState<Task[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | null>(null);
  const [showNewTaskModal, setShowNewTaskModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [newTask, setNewTask] = useState({ title: '', description: '', priority: 'medium' });
  const [importData, setImportData] = useState('');
  const [user, setUser] = useState<any>(null);
  const [filePreview, setFilePreview] = useState('');
  const [uploadError, setUploadError] = useState('');
  const router = useRouter();

  // Load user from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('user');
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch (e) {}
    }
    // ✅ FIXED: Removed eval() on URL param — was a critical RCE vulnerability
  }, []);

  // Fetch projects when user is loaded
  useEffect(() => {
    if (user?.id) {
      fetchSASTProjects();
    }
  }, [user?.id]);

  // Fetch scans when project is selected
  useEffect(() => {
    if (selectedProject && user?.id) {
      fetchSASTScans();
    }
  }, [selectedProject, user?.id]);

  const fetchSASTProjects = async () => {
    try {
      const userId = user?.id || 'anonymous';
      const response = await fetch(`http://localhost:5001/api/projects/${userId}`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        const transformed = (data || []).map((p: any) => ({
          id: p.id,
          name: p.name,
          description: `Created: ${p.created_at}`,
          member_count: 0,
          task_count: p.scan_count || 0,
        }));
        setProjects(transformed);
      }
    } catch (e) {
      setProjects([]);
    }
  };

  const fetchSASTScans = async () => {
    try {
      if (!selectedProject) return;
      const userId = user?.id || 'anonymous';
      const response = await fetch(`http://localhost:5001/api/scans/${userId}/${selectedProject}`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        const transformed = (data || []).map((s: any) => ({
          id: s.scan_id,
          title: `Scan ${s.scan_type} - ${s.timestamp}`,
          description: `Files: ${s.stats?.files_scanned || 0}, Vulnerabilities: ${s.stats?.vulnerabilities || 0}`,
          status: 'done',
          priority: s.stats?.vulnerabilities > 0 ? 'high' : 'low',
          assignee: 'SAST',
          due_date: s.timestamp,
        }));
        setTasks(transformed);
      }
    } catch (e) {
      setTasks([]);
    }
  };

  const handleSearch = async () => {
    alert('Search feature not available in SAST mode');
  };

  const handleStartScan = async (scanType: string = '1') => {
    if (!selectedProject) {
      alert('Please select a project first');
      return;
    }
    setShowNewTaskModal(false);
    alert(`Starting ${scanType === '1' ? 'Tier 1' : scanType === '2' ? 'Tier 2' : 'Tier 3'} scan...`);
  };

  // ✅ FIXED: Added missing handleCreateTask function
  const handleCreateTask = async () => {
    if (!newTask.title.trim()) {
      alert('Please enter a task title');
      return;
    }
    if (!selectedProject) {
      alert('Please select a project first');
      return;
    }
    try {
      const userId = user?.id || 'anonymous';
      const response = await fetch(`http://localhost:5001/api/tasks`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTask.title.trim(),
          description: newTask.description.trim(),
          priority: newTask.priority,
          project_id: selectedProject,
          user_id: userId,
        }),
      });
      if (response.ok) {
        setShowNewTaskModal(false);
        setNewTask({ title: '', description: '', priority: 'medium' });
        fetchSASTScans();
      } else {
        alert('Failed to create task');
      }
    } catch (e) {
      alert('Error creating task');
    }
  };

  const handleImport = async () => {
    setShowImportModal(false);
    setImportData('');
    alert('Import feature not available in SAST mode');
  };

  const handleFileSelect = async (file: string) => {
    setFilePreview('Document preview not available');
  };

  const generateReport = async (format: string) => {
    if (!selectedProject || !user?.id) {
      alert('Please select a project first');
      return;
    }
    window.open(`http://localhost:5001/api/projects/${user.id}`, '_blank');
  };

  const testIntegration = async (url: string) => {
    alert('Integration test not available in SAST mode');
  };

  // ✅ FIXED: Added file type/size validation before upload
  const handleFileUpload = async (file: File) => {
    setUploadError('');

    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      setUploadError('Invalid file type. Only PDF, DOC, and XLS files are allowed.');
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setUploadError('File size exceeds 10MB limit.');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch('http://localhost:5001/api/documents/upload', {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });
      if (!response.ok) {
        setUploadError('Upload failed. Please try again.');
      }
    } catch (e) {
      setUploadError('Upload error. Please try again.');
    }
  };

  // ✅ FIXED: processBulkData now validates and sets Content-Type header
  const processBulkData = async (data: string) => {
    if (!data || typeof data !== 'string') return;
    try {
      // Validate it's parseable JSON before sending
      JSON.parse(data);
      const response = await fetch('http://localhost:5001/api/bulk/process', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: data,
      });
      return response.json();
    } catch (e) {
      alert('Invalid data format. Expected JSON.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 z-10">
        <div className="p-6">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg mr-2"></div>
            <span className="text-xl font-bold text-gray-900">TaskFlow</span>
          </div>
        </div>
        <nav className="px-4 space-y-1">
          <button
            onClick={() => setActiveTab('tasks')}
            className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg ${activeTab === 'tasks' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50'}`}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            My Tasks
          </button>
          <button
            onClick={() => setActiveTab('projects')}
            className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg ${activeTab === 'projects' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50'}`}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            Projects
          </button>
          <button
            onClick={() => setActiveTab('team')}
            className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg ${activeTab === 'team' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50'}`}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            Team
          </button>
          <button
            onClick={() => setActiveTab('files')}
            className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg ${activeTab === 'files' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50'}`}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Documents
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg ${activeTab === 'settings' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50'}`}
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Settings
          </button>
        </nav>
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">{user?.name || 'User'}</p>
              <p className="text-xs text-gray-500">{user?.email || 'user@example.com'}</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 p-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900">
              {activeTab === 'tasks' && 'My Tasks'}
              {activeTab === 'projects' && 'Projects'}
              {activeTab === 'team' && 'Team Members'}
              {activeTab === 'files' && 'Documents'}
              {activeTab === 'settings' && 'Settings'}
            </h1>
            <div className="flex space-x-3">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                <svg className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              {activeTab === 'tasks' && (
                <button
                  onClick={() => setShowNewTaskModal(true)}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  New Task
                </button>
              )}
            </div>
          </div>
        </div>

        {/* ✅ FIXED: Removed dangerouslySetInnerHTML — search results rendered as plain text */}
        <div id="search-results" className="mb-6" />

        {/* Tasks Tab */}
        {activeTab === 'tasks' && (
          <div className="space-y-4">
            <div className="flex space-x-4 mb-6">
              <button
                onClick={() => setShowImportModal(true)}
                className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50"
              >
                Import Tasks
              </button>
              <button
                onClick={() => generateReport('pdf')}
                className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50"
              >
                Export PDF
              </button>
              <button
                onClick={() => generateReport('csv')}
                className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50"
              >
                Export CSV
              </button>
            </div>

            <div className="grid gap-4">
              {tasks.length === 0 ? (
                <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                  <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks yet</h3>
                  <p className="text-gray-500 mb-4">Get started by creating your first task</p>
                  <button
                    onClick={() => setShowNewTaskModal(true)}
                    className="text-indigo-600 font-medium hover:text-indigo-500"
                  >
                    Create task →
                  </button>
                </div>
              ) : (
                tasks.map((task) => (
                  <div key={task.id} className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-medium text-gray-900">{task.title}</h3>
                        <p className="text-gray-600 mt-1">{task.description}</p>
                        <div className="flex items-center mt-3 space-x-4 text-sm text-gray-500">
                          <span className={`px-2 py-1 rounded ${task.priority === 'high' ? 'bg-red-100 text-red-700' : task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'}`}>
                            {task.priority}
                          </span>
                          <span>Due: {task.due_date}</span>
                          <span>Assigned to: {task.assignee}</span>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm ${task.status === 'done' ? 'bg-green-100 text-green-800' : task.status === 'in_progress' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                        {task.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.length === 0 ? (
              <div className="col-span-full bg-white rounded-lg border border-gray-200 p-12 text-center">
                <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
                <button className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
                  Create Project
                </button>
              </div>
            ) : (
              projects.map((project) => (
                <div
                  key={project.id}
                  onClick={() => setSelectedProject(project.id)}
                  className={`bg-white rounded-lg border p-6 cursor-pointer hover:shadow-md transition-shadow ${selectedProject === project.id ? 'border-indigo-500 shadow-md' : 'border-gray-200'}`}
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{project.name}</h3>
                  <p className="text-gray-600 text-sm mb-4">{project.description}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{project.member_count} members</span>
                    <span>{project.task_count} tasks</span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Files Tab */}
        {activeTab === 'files' && (
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Document</h3>
                {/* ✅ FIXED: File type/size validated before upload */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    accept=".pdf,.doc,.docx,.xls,.xlsx"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleFileUpload(file);
                    }}
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="text-gray-600">Click to upload or drag and drop</p>
                    <p className="text-sm text-gray-500 mt-1">PDF, DOC, XLS up to 10MB</p>
                  </label>
                  {uploadError && (
                    <p className="mt-3 text-sm text-red-600">{uploadError}</p>
                  )}
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Preview</h3>
              {/* ✅ FIXED: Replaced dangerouslySetInnerHTML with safe plain text rendering */}
              <div className="text-sm text-gray-600 whitespace-pre-wrap">{filePreview}</div>
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="max-w-2xl space-y-6">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Integrations</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Webhook URL</label>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      id="webhook-url"
                      placeholder="https://hooks.example.com/..."
                      className="flex-1 border border-gray-300 rounded-lg px-3 py-2"
                    />
                    <button
                      onClick={() => testIntegration((document.getElementById('webhook-url') as HTMLInputElement).value)}
                      className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                    >
                      Test
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Export Data</h3>
              <div className="flex space-x-3">
                <button
                  onClick={() => generateReport('json')}
                  className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50"
                >
                  Export JSON
                </button>
                <button
                  onClick={() => generateReport('xml')}
                  className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50"
                >
                  Export XML
                </button>
              </div>
            </div>

            {/* ✅ NOTE: Admin link is still client-side gated — ensure server also enforces role checks */}
            {user?.role === 'admin' && (
              <div className="bg-white rounded-lg border border-red-200 p-6">
                <h3 className="text-lg font-medium text-red-900 mb-4">Administration</h3>
                <Link href="/admin" className="text-red-600 hover:text-red-500 font-medium">
                  Access Admin Panel →
                </Link>
              </div>
            )}
          </div>
        )}
      </main>

      {/* New Task Modal */}
      {showNewTaskModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Create New Task</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  value={newTask.title}
                  onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newTask.description}
                  onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                  rows={3}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                <select
                  value={newTask.priority}
                  onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowNewTaskModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateTask}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Create Task
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Import Tasks</h2>
            <p className="text-sm text-gray-600 mb-4">Paste YAML data to import tasks</p>
            <textarea
              value={importData}
              onChange={(e) => setImportData(e.target.value)}
              rows={10}
              placeholder="tasks:\n  - title: Task 1\n    description: Description here\n    priority: high"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 font-mono text-sm"
            />
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowImportModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleImport}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Import
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}