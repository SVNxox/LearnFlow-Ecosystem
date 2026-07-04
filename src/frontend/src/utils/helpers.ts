export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
}

export function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;

  return formatDate(dateString);
}

export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

export function formatPercentage(value: number): string {
  return `${Math.round(value)}%`;
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${Math.round(bytes / Math.pow(k, i) * 100) / 100} ${sizes[i]}`;
}

export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
}

export function getInitials(firstName: string, lastName: string): string {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
}

export function getStatusColor(status: string): string {
  const statusColors: Record<string, string> = {
    // Enrollment
    active: 'bg-green-100 text-green-800',
    completed: 'bg-blue-100 text-blue-800',
    dropped: 'bg-gray-100 text-gray-800',

    // Progress
    locked: 'bg-gray-100 text-gray-800',
    unlocked: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    assessment_pending: 'bg-orange-100 text-orange-800',

    // Submission
    draft: 'bg-gray-100 text-gray-800',
    submitted: 'bg-blue-100 text-blue-800',
    under_review: 'bg-yellow-100 text-yellow-800',
    changes_requested: 'bg-orange-100 text-orange-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',

    // Assessment
    pending: 'bg-yellow-100 text-yellow-800',
    auto_graded: 'bg-blue-100 text-blue-800',
    mentor_review: 'bg-orange-100 text-orange-800',
    finalized: 'bg-green-100 text-green-800',

    // Certificate
    issued: 'bg-green-100 text-green-800',
    revoked: 'bg-red-100 text-red-800',

    // Admin: users
    blocked: 'bg-red-100 text-red-800',

    // Admin: enrollment (extended)
    suspended: 'bg-orange-100 text-orange-800',

    // Admin: payments
    failed: 'bg-red-100 text-red-800',
    refunded: 'bg-gray-100 text-gray-800',
    partially_refunded: 'bg-orange-100 text-orange-800',

    // Admin: course status
    published: 'bg-green-100 text-green-800',
    archived: 'bg-gray-100 text-gray-800',
  };

  return statusColors[status] || 'bg-gray-100 text-gray-800';
}

export function getContentTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    video: '🎥',
    pdf: '📄',
    slides: '📊',
    text: '📝',
    link: '🔗',
    recording: '🎙️',
    code: '💻',
  };

  return icons[type] || '📄';
}

export function isDeadlinePassed(deadline: string | null): boolean {
  if (!deadline) return false;
  return new Date(deadline) < new Date();
}

export function getDaysUntilDeadline(deadline: string | null): number | null {
  if (!deadline) return null;
  const diff = new Date(deadline).getTime() - new Date().getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}
