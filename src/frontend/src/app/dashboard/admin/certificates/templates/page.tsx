'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { CertificateTemplate } from '@/types/api';
import { formatDate } from '@/utils/helpers';
import { useTranslation } from '@/lib/i18n/useTranslation';

export default function AdminTemplatesPage() {
  const { t } = useTranslation();
  const [templates, setTemplates] = useState<CertificateTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [duplicatingId, setDuplicatingId] = useState<string | null>(null);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const data = await adminApi.getTemplates();
      setTemplates(data.results || []);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDuplicate = async (id: string) => {
    setDuplicatingId(id);
    try {
      await adminApi.duplicateTemplate(id);
      await loadTemplates();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setDuplicatingId(null);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`${t.templates.deleteConfirm}\n\n"${name}"\n\n${t.templates.deleteWarning}`)) return;
    try {
      await adminApi.deleteTemplate(id);
      setTemplates(prev => prev.filter(tmpl => tmpl.id !== id));
    } catch (err) {
      setError(handleApiError(err));
    }
  };

  const handleToggleActive = async (template: CertificateTemplate) => {
    try {
      const updated = await adminApi.updateTemplate(template.id, {
        is_active: !template.is_active,
      });
      setTemplates(prev => prev.map(tmpl => tmpl.id === template.id ? updated : tmpl));
    } catch (err) {
      setError(handleApiError(err));
    }
  };

  const activeCount = templates.filter(tmpl => tmpl.is_active).length;

  return (
    <AdminLayout roles={['admin', 'staff']}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-foreground font-heading">
            {t.templates.title} ({templates.length})
          </h1>
          <p className="text-sm text-muted-foreground mt-1 font-body">
            {t.templates.subtitle}
          </p>
        </div>
        <Link
          href="/dashboard/admin/certificates/templates/new"
          className="btn-primary text-sm inline-flex items-center gap-2"
        >
          <span>+</span>
          {t.templates.newTemplate}
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.templates.totalTemplates}</p>
          <p className="stat-value mt-2">{templates.length}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label uppercase tracking-wider">{t.templates.activeTemplates}</p>
          <p className="stat-value mt-2" style={{ color: 'var(--color-success)' }}>{activeCount}</p>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4">
          {error}
        </div>
      )}

      {/* Templates Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="card overflow-hidden">
              <div className="h-48 bg-muted animate-pulse" />
              <div className="p-4 space-y-2">
                <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
                <div className="h-3 bg-muted rounded animate-pulse w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : templates.length === 0 ? (
        <div className="card p-12 text-center">
          <div className="text-5xl mb-4">🎨</div>
          <h3 className="text-lg font-semibold text-foreground mb-2 font-heading">
            {t.templates.noTemplates}
          </h3>
          <p className="text-sm text-muted-foreground mb-4 font-body">
            {t.templates.noTemplatesDesc}
          </p>
          <Link
            href="/dashboard/admin/certificates/templates/new"
            className="btn-primary inline-flex items-center gap-2"
          >
            <span>+</span>
            {t.templates.createFirst}
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <div
              key={template.id}
              className="card overflow-hidden hover:border-primary/30 hover:-translate-y-0.5 transition-all duration-200 group"
            >
              {/* Preview */}
              <div
                className="h-48 bg-muted relative overflow-hidden"
                style={{
                  backgroundImage: template.background_image ? `url(${template.background_image})` : undefined,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                }}
              >
                {!template.background_image && (
                  <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
                    <span className="text-4xl">📜</span>
                  </div>
                )}
                {!template.is_active && (
                  <div className="absolute top-2 right-2 bg-background/80 backdrop-blur-sm text-muted-foreground text-xs px-2 py-1 rounded-lg border border-border font-mono">
                    {t.templates.inactive}
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="p-4">
                <h3 className="font-semibold text-foreground mb-1 truncate font-heading">
                  {template.name}
                </h3>
                {template.description && (
                  <p className="text-sm text-muted-foreground mb-2 line-clamp-2 font-body">
                    {template.description}
                  </p>
                )}
                <p className="text-xs text-muted-foreground mb-3 font-mono">
                  {t.templates.created} {formatDate(template.created_at)}
                </p>

                {/* Actions */}
                <div className="flex gap-2 flex-wrap">
                  <Link
                    href={`/dashboard/admin/certificates/templates/${template.id}`}
                    className="flex-1 text-center btn-primary text-xs py-2"
                  >
                    {t.templates.edit}
                  </Link>
                  <button
                    onClick={() => handleToggleActive(template)}
                    className={`px-3 py-2 text-xs rounded-xl font-semibold transition-colors ${
                      template.is_active
                        ? 'bg-warning/10 border border-warning/30 text-warning hover:bg-warning/20'
                        : 'bg-success/10 border border-success/30 text-success hover:bg-success/20'
                    }`}
                  >
                    {template.is_active ? t.templates.deactivate : t.templates.activate}
                  </button>
                  <button
                    onClick={() => handleDuplicate(template.id)}
                    disabled={duplicatingId === template.id}
                    className="btn-ghost text-xs py-2 px-3 disabled:opacity-50"
                  >
                    {duplicatingId === template.id ? '...' : t.templates.copy}
                  </button>
                  <button
                    onClick={() => handleDelete(template.id, template.name)}
                    className="btn-danger text-xs py-2 px-3"
                  >
                    {t.templates.delete}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </AdminLayout>
  );
}