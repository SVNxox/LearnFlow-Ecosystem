'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/admin/AdminLayout';
import { adminApi, handleApiError } from '@/lib/admin-api';
import { CertificateTemplate } from '@/types/api';
import { useTranslation } from '@/lib/i18n/useTranslation';

type Tab = 'design' | 'layout' | 'fonts' | 'preview';

export default function TemplateEditorPage() {
  const params = useParams();
  const router = useRouter();
  const { t } = useTranslation();

  const templateId = params?.id as string | undefined;

  if (!templateId || templateId === 'undefined') {
    return (
      <AdminLayout roles={['admin', 'staff']}>
        <div className="text-center py-12">
          <p className="text-destructive mb-4 font-body">Noto'g'ri shablon ID</p>
          <Link href="/dashboard/admin/certificates/templates" className="text-primary hover:underline font-body">
            ← {t.templates.backToTemplates}
          </Link>
        </div>
      </AdminLayout>
    );
  }

  const isNew = templateId === 'new';

  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState<Tab>('design');

  const [template, setTemplate] = useState<Partial<CertificateTemplate>>({
    name: '',
    description: '',
    background_image: '',
    pdf_template: '',
    font_config: {
      title: { family: 'Inter', size: 48, color: '
      subtitle: { family: 'Inter', size: 24, color: '
      body: { family: 'Inter', size: 16, color: '
      signature: { family: 'Dancing Script', size: 20, color: '
    },
    layout_config: {
      width: 1122,
      height: 793,
      orientation: 'landscape',
      elements: {
        title: { x: 561, y: 150, align: 'center' },
        student_name: { x: 561, y: 300, align: 'center' },
        course_name: { x: 561, y: 380, align: 'center' },
        date: { x: 561, y: 500, align: 'center' },
        signature: { x: 561, y: 650, align: 'center' },
      },
    },
    is_active: true,
  });

  const [previewHtml, setPreviewHtml] = useState('');
  const [previewSize, setPreviewSize] = useState({ width: 1122, height: 793 });

  // Загрузка шаблона
  useEffect(() => {
    if (isNew || !templateId) return;
    let active = true;
    setLoading(true);

    (async () => {
      try {
        const data = await adminApi.getTemplate(templateId);
        if (active) setTemplate(data);
      } catch (err) {
        if (active) setError(handleApiError(err));
      } finally {
        if (active) setLoading(false);
      }
    })();

    return () => { active = false; };
  }, [templateId, isNew]);

  // Загрузка preview
  const loadPreview = useCallback(async () => {
    if (!template.id) return;
    try {
      const data = await adminApi.previewTemplate(template.id, {
        student_name: 'John Doe',
        course_name: 'Python for Beginners',
        completion_date: 'June 30, 2026',
        certificate_number: 'LF-20260630-ABC123',
        final_score: '95',
      });
      setPreviewHtml(data.html);
      setPreviewSize({ width: data.width, height: data.height });
    } catch (err) {
      console.error('Preview error:', err);
    }
  }, [template.id]);

  useEffect(() => {
    if (isNew || !template.id) return;
    loadPreview();
  }, [template.id, isNew, loadPreview]);

  const handleSave = async () => {
    if (!template.name?.trim()) {
      setError(t.templates.templateNameRequired);
      return;
    }

    setSaving(true);
    setError('');
    setSuccess('');

    try {
      let saved;
      if (isNew) {
        saved = await adminApi.createTemplate(template);
        setSuccess(t.templates.templateCreated);
        setTimeout(() => router.push(`/dashboard/admin/certificates/templates/${saved.id}`), 1500);
      } else {
        saved = await adminApi.updateTemplate(templateId!, template);
        setTemplate(saved);
        setSuccess(t.templates.templateSaved);
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const updateFontConfig = (key: string, field: string, value: any) => {
    setTemplate(prev => ({
      ...prev,
      font_config: {
        ...prev.font_config,
        [key]: {
          ...(prev.font_config?.[key] || {}),
          [field]: value,
        },
      },
    }));
  };

  const updateLayoutConfig = (key: string, field: string, value: any) => {
    setTemplate(prev => ({
      ...prev,
      layout_config: {
        ...prev.layout_config,
        elements: {
          ...(prev.layout_config?.elements || {}),
          [key]: {
            ...(prev.layout_config?.elements?.[key] || {}),
            [field]: value,
          },
        },
      },
    }));
  };

  if (loading) {
    return (
      <AdminLayout roles={['admin', 'staff']}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout roles={['admin', 'staff']}>
      {/* Breadcrumbs */}
      <nav className="mb-4">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground font-body">
          <li>
            <Link href="/dashboard/admin/certificates/templates" className="hover:text-foreground transition-colors">
              {t.templates.title}
            </Link>
          </li>
          <li>/</li>
          <li className="text-foreground font-medium">
            {isNew ? t.templates.newTemplateTitle : template.name}
          </li>
        </ol>
      </nav>

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-foreground font-heading">
          {isNew ? t.templates.newTemplateTitle : `${t.templates.editTemplateTitle} ${template.name}`}
        </h1>
        <div className="flex gap-2">
          <Link
            href="/dashboard/admin/certificates/templates"
            className="btn-ghost text-sm"
          >
            {t.common.cancel}
          </Link>
          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary text-sm"
          >
            {saving ? t.templates.saving : t.templates.saveTemplate}
          </button>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-xl text-sm mb-4">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-xl text-sm mb-4">
          {success}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Editor */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4 font-heading">
              {t.templates.basicInfo}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1 font-body">
                  {t.templates.templateName} *
                </label>
                <input
                  type="text"
                  value={template.name || ''}
                  onChange={(e) => setTemplate(tmpl => ({ ...tmpl, name: e.target.value }))}
                  className="input"
                  placeholder={t.templates.templateNamePlaceholder}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1 font-body">
                  {t.templates.description}
                </label>
                <textarea
                  value={template.description || ''}
                  onChange={(e) => setTemplate(tmpl => ({ ...tmpl, description: e.target.value }))}
                  rows={2}
                  className="input resize-none"
                  placeholder={t.templates.descriptionPlaceholder}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1 font-body">
                  {t.templates.backgroundImage}
                </label>
                <input
                  type="text"
                  value={template.background_image || ''}
                  onChange={(e) => setTemplate(tmpl => ({ ...tmpl, background_image: e.target.value }))}
                  className="input"
                  placeholder={t.templates.backgroundImagePlaceholder}
                />
                <p className="text-xs text-muted-foreground mt-1 font-body">
                  {t.templates.backgroundImageHint}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={template.is_active || false}
                  onChange={(e) => setTemplate(tmpl => ({ ...tmpl, is_active: e.target.checked }))}
                  className="w-4 h-4"
                />
                <label htmlFor="is_active" className="text-sm text-foreground font-body">
                  {t.templates.activeLabel}
                </label>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="card overflow-hidden">
            <div className="flex border-b border-border">
              {(['design', 'layout', 'fonts', 'preview'] as Tab[]).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex-1 px-4 py-3 text-sm font-semibold capitalize transition-colors font-body ${
                    activeTab === tab
                      ? 'bg-primary/10 text-primary border-b-2 border-primary'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  }`}
                >
                  {tab === 'design' && '🎨 '}
                  {tab === 'layout' && '📐 '}
                  {tab === 'fonts' && '🔤 '}
                  {tab === 'preview' && '👁 '}
                  {t.templates[tab]}
                </button>
              ))}
            </div>

            <div className="p-6">
              {activeTab === 'design' && (
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground font-body">
                    {t.templates.pdfTemplateHint}{' '}
                    <code className="code-badge">{'{{ student_name }}'}</code>,{' '}
                    <code className="code-badge">{'{{ course_name }}'}</code>,{' '}
                    <code className="code-badge">{'{{ completion_date }}'}</code>,{' '}
                    <code className="code-badge">{'{{ certificate_number }}'}</code>,{' '}
                    <code className="code-badge">{'{{ final_score }}'}</code>
                  </p>
                  <textarea
                    value={template.pdf_template || ''}
                    onChange={(e) => setTemplate(tmpl => ({ ...tmpl, pdf_template: e.target.value }))}
                    rows={15}
                    className="input resize-none font-mono text-xs"
                    placeholder="<div class='certificate'>...</div>"
                  />
                </div>
              )}

              {activeTab === 'layout' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div>
                      <label className="block text-xs font-medium text-foreground mb-1 font-body">
                        {t.templates.width}
                      </label>
                      <input
                        type="number"
                        value={template.layout_config?.width || 1122}
                        onChange={(e) => setTemplate(tmpl => ({
                          ...tmpl,
                          layout_config: { ...tmpl.layout_config, width: parseInt(e.target.value) || 0 }
                        }))}
                        className="input text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-foreground mb-1 font-body">
                        {t.templates.height}
                      </label>
                      <input
                        type="number"
                        value={template.layout_config?.height || 793}
                        onChange={(e) => setTemplate(tmpl => ({
                          ...tmpl,
                          layout_config: { ...tmpl.layout_config, height: parseInt(e.target.value) || 0 }
                        }))}
                        className="input text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-foreground mb-1 font-body">
                        {t.templates.orientation}
                      </label>
                      <select
                        value={template.layout_config?.orientation || 'landscape'}
                        onChange={(e) => setTemplate(tmpl => ({
                          ...tmpl,
                          layout_config: { ...tmpl.layout_config, orientation: e.target.value }
                        }))}
                        className="input text-sm"
                      >
                        <option value="landscape">{t.templates.landscape}</option>
                        <option value="portrait">{t.templates.portrait}</option>
                      </select>
                    </div>
                  </div>

                  <h3 className="text-sm font-semibold text-foreground font-heading">
                    {t.templates.elementPositions}
                  </h3>
                  {Object.entries(template.layout_config?.elements || {}).map(([key, pos]) => (
                    <div key={key} className="p-3 bg-muted rounded-xl">
                      <p className="text-xs font-medium text-foreground mb-2 capitalize font-body">
                        {key.replace('_', ' ')}
                      </p>
                      <div className="grid grid-cols-3 gap-2">
                        <div>
                          <label className="text-xs text-muted-foreground font-mono">X</label>
                          <input
                            type="number"
                            value={pos.x || 0}
                            onChange={(e) => updateLayoutConfig(key, 'x', parseInt(e.target.value) || 0)}
                            className="input text-xs"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-muted-foreground font-mono">Y</label>
                          <input
                            type="number"
                            value={pos.y || 0}
                            onChange={(e) => updateLayoutConfig(key, 'y', parseInt(e.target.value) || 0)}
                            className="input text-xs"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-muted-foreground font-mono">Align</label>
                          <select
                            value={pos.align || 'center'}
                            onChange={(e) => updateLayoutConfig(key, 'align', e.target.value)}
                            className="input text-xs"
                          >
                            <option value="left">Left</option>
                            <option value="center">Center</option>
                            <option value="right">Right</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'fonts' && (
                <div className="space-y-4">
                  {Object.entries(template.font_config || {}).map(([key, config]) => (
                    <div key={key} className="p-4 bg-muted rounded-xl">
                      <p className="text-sm font-semibold text-foreground mb-3 capitalize font-heading">
                        {key}
                      </p>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="text-xs text-muted-foreground font-body">
                            {t.templates.fontFamily}
                          </label>
                          <input
                            type="text"
                            value={config.family || ''}
                            onChange={(e) => updateFontConfig(key, 'family', e.target.value)}
                            className="input text-sm"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-muted-foreground font-body">
                            {t.templates.fontSize}
                          </label>
                          <input
                            type="number"
                            value={config.size || 16}
                            onChange={(e) => updateFontConfig(key, 'size', parseInt(e.target.value) || 0)}
                            className="input text-sm"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-muted-foreground font-body">
                            {t.templates.fontColor}
                          </label>
                          <div className="flex gap-2">
                            <input
                              type="color"
                              value={config.color || '
                              onChange={(e) => updateFontConfig(key, 'color', e.target.value)}
                              className="w-10 h-9 border border-border rounded-xl cursor-pointer"
                            />
                            <input
                              type="text"
                              value={config.color || ''}
                              onChange={(e) => updateFontConfig(key, 'color', e.target.value)}
                              className="input text-sm font-mono flex-1"
                            />
                          </div>
                        </div>
                        <div>
                          <label className="text-xs text-muted-foreground font-body">
                            {t.templates.fontWeight}
                          </label>
                          <select
                            value={config.weight || 'normal'}
                            onChange={(e) => updateFontConfig(key, 'weight', e.target.value)}
                            className="input text-sm"
                          >
                            <option value="normal">{t.templates.normal}</option>
                            <option value="bold">{t.templates.bold}</option>
                            <option value="lighter">{t.templates.lighter}</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'preview' && (
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <p className="text-sm text-muted-foreground font-body">
                      {t.templates.livePreview}
                    </p>
                    <button
                      onClick={loadPreview}
                      className="text-xs text-primary hover:text-primary/80 font-semibold font-mono"
                    >
                      🔄 {t.templates.refresh}
                    </button>
                  </div>
                  <div
                    className="border border-border rounded-xl overflow-auto bg-muted"
                    style={{ maxHeight: '600px' }}
                  >
                    <div
                      style={{
                        transform: 'scale(0.5)',
                        transformOrigin: 'top left',
                        width: previewSize.width * 0.5,
                        height: previewSize.height * 0.5,
                      }}
                      dangerouslySetInnerHTML={{ __html: previewHtml }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right: Quick Preview */}
        <div className="space-y-4">
          <div className="card p-4 sticky top-4">
            <h3 className="text-sm font-semibold text-foreground mb-3 font-heading">
              {t.templates.quickPreview}
            </h3>
            <div
              className="border border-border rounded-xl overflow-hidden bg-muted"
              style={{ aspectRatio: `${previewSize.width} / ${previewSize.height}` }}
            >
              <div
                style={{
                  transform: 'scale(0.3)',
                  transformOrigin: 'top left',
                  width: previewSize.width * 0.3,
                  height: previewSize.height * 0.3,
                }}
                dangerouslySetInnerHTML={{ __html: previewHtml }}
              />
            </div>
            <button
              onClick={loadPreview}
              className="btn-ghost w-full text-xs mt-3"
            >
              🔄 {t.templates.refresh}
            </button>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}