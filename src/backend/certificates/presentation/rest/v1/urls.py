"""
Certificates REST API v1 URLs
"""

from django.urls import path

from src.backend.certificates.presentation.rest.v1.admin_templates import (
    AdminTemplateListCreateView,
    AdminTemplateDetailView,
    AdminTemplateDuplicateView,
    AdminTemplatePreviewView
)
from src.backend.certificates.presentation.rest.v1.admin_detail import AdminCertificateDetailView
from src.backend.certificates.presentation.rest.v1.admin_revoke import AdminRevokeCertificateView
from src.backend.certificates.presentation.rest.v1.admin_generate import AdminGenerateCertificateView
from src.backend.certificates.presentation.rest.v1.admin_list import AdminCertificatesListView
from src.backend.certificates.presentation.rest.v1.certificates.list import MyCertificatesListView
from src.backend.certificates.presentation.rest.v1.certificates.detail import CertificateDetailView
from src.backend.certificates.presentation.rest.v1.certificates.download import CertificateDownloadView
from src.backend.certificates.presentation.rest.v1.verification.verify import VerifyCertificateView

app_name = 'certificates'

urlpatterns = [
    path('admin/certificates/', AdminCertificatesListView.as_view(), name='admin-certificates-list'),
    path('admin/certificates/generate/', AdminGenerateCertificateView.as_view(), name='admin-certificates-generate'),
    path('admin/certificates/<str:certificate_id>/', AdminCertificateDetailView.as_view(), name='admin-certificate-detail'),
    path('admin/certificates/<str:certificate_id>/revoke/', AdminRevokeCertificateView.as_view(), name='admin-certificate-revoke'),

    
    path('certificates/', MyCertificatesListView.as_view(), name='certificate-list'),
    path('certificates/<str:certificate_id>/', CertificateDetailView.as_view(), name='certificate-detail'),
    path('certificates/<str:certificate_id>/download/', CertificateDownloadView.as_view(), name='certificate-download'),

    
    path('verify/<str:verification_code>/', VerifyCertificateView.as_view(), name='verify-certificate'),

    path('admin/templates/', AdminTemplateListCreateView.as_view(), name='admin-templates-list'),
    path('admin/templates/<str:template_id>/', AdminTemplateDetailView.as_view(), name='admin-template-detail'),
    path('admin/templates/<str:template_id>/duplicate/', AdminTemplateDuplicateView.as_view(), name='admin-template-duplicate'),
    path('admin/templates/<str:template_id>/preview/', AdminTemplatePreviewView.as_view(), name='admin-template-preview'),
]