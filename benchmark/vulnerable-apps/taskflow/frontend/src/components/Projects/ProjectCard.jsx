import { Link } from 'react-router-dom';

export default function ProjectCard({ project }) {
  return (
    <Link
      to={`/projects/${project.id}`}
      className="block p-5 bg-white rounded-xl border border-gray-200 hover:border-indigo-300 hover:shadow-md transition"
    >
      <h3 className="font-semibold text-gray-900">{project.name}</h3>
      {project.description && (
        <p className="text-sm text-gray-600 mt-1 line-clamp-2">{project.description}</p>
      )}
      {project.archived && (
        <span className="inline-block mt-2 text-xs text-amber-600 font-medium">Archived</span>
      )}
    </Link>
  );
}
