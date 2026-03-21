export const formatDate = (d) => {
  if (!d) return '—';
  const date = new Date(d);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

export const formatRelative = (d) => {
  if (!d) return '';
  const diff = Date.now() - new Date(d);
  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return formatDate(d);
};

export const priorityLabel = (p) => (p || 'medium').charAt(0).toUpperCase() + (p || 'medium').slice(1);
export const statusLabel = (s) => (s || 'open').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
