"""
Admin Certificate Templates API.

Endpoints:
- GET    /api/v1/certificates/admin/templates/
- POST   /api/v1/certificates/admin/templates/
- GET    /api/v1/certificates/admin/templates/{id}/
- PATCH  /api/v1/certificates/admin/templates/{id}/
- DELETE /api/v1/certificates/admin/templates/{id}/
- POST   /api/v1/certificates/admin/templates/{id}/duplicate/
- POST   /api/v1/certificates/admin/templates/{id}/preview/
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from src.backend.certificates.domain.models import CertificateTemplate
from src.backend.learning.utils.permissions import IsAdminOrStaff

logger = logging.getLogger(__name__)


def serialize_template(t: CertificateTemplate) -> dict:
    """Serialize template to dict."""
    return {
        "id": str(t.id),
        "name": t.name,
        "description": t.description,
        "background_image": t.background_image,
        "pdf_template": t.pdf_template,
        "font_config": t.font_config,
        "layout_config": t.layout_config,
        "is_active": t.is_active,
        "created_at": t.created_at.isoformat(),
        "updated_at": t.updated_at.isoformat(),
        "created_by_id": str(t.created_by_id) if t.created_by_id else None,
    }


class AdminTemplateListCreateView(APIView):
    """List and create certificate templates."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request) -> Response:
        """List all templates."""
        try:
            templates = CertificateTemplate.objects.all().order_by('-created_at')
            data = [serialize_template(t) for t in templates]
            return Response({"count": len(data), "results": data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error listing templates: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request: Request) -> Response:
        """Create a new template."""
        try:
            data = request.data

            
            if not data.get('name'):
                return Response({"detail": "name is required"}, status=status.HTTP_400_BAD_REQUEST)

            template = CertificateTemplate.objects.create(
                name=data.get('name'),
                description=data.get('description', ''),
                background_image=data.get('background_image', ''),
                pdf_template=data.get('pdf_template', ''),
                font_config=data.get('font_config', self._default_font_config()),
                layout_config=data.get('layout_config', self._default_layout_config()),
                is_active=data.get('is_active', True),
                created_by=request.user,
            )

            return Response(serialize_template(template), status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating template: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _default_font_config() -> dict:
        return {
            "title": {"family": "Inter", "size": 48, "color": "#1a1a1a"},
            "subtitle": {"family": "Inter", "size": 24, "color": "#4a4a4a"},
            "body": {"family": "Inter", "size": 16, "color": "#6a6a6a"},
            "signature": {"family": "Dancing Script", "size": 20, "color": "#1a1a1a"}
        }

    @staticmethod
    def _default_layout_config() -> dict:
        return {
            "width": 1122,  
            "height": 793,
            "orientation": "landscape",
            "elements": {
                "title": {"x": 561, "y": 150, "align": "center"},
                "student_name": {"x": 561, "y": 300, "align": "center"},
                "course_name": {"x": 561, "y": 380, "align": "center"},
                "date": {"x": 561, "y": 500, "align": "center"},
                "signature": {"x": 561, "y": 650, "align": "center"},
            }
        }


class AdminTemplateDetailView(APIView):
    """Get, update, delete a template."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request, template_id: str) -> Response:
        """Get template details."""
        try:
            template = get_object_or_404(CertificateTemplate, id=template_id)
            return Response(serialize_template(template), status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting template: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request: Request, template_id: str) -> Response:
        """Update template."""
        try:
            template = get_object_or_404(CertificateTemplate, id=template_id)
            data = request.data

            updatable_fields = [
                'name', 'description', 'background_image', 'pdf_template',
                'font_config', 'layout_config', 'is_active'
            ]

            updated_fields = []
            for field in updatable_fields:
                if field in data:
                    setattr(template, field, data[field])
                    updated_fields.append(field)

            if updated_fields:
                template.save(update_fields=updated_fields + ['updated_at'])

            return Response(serialize_template(template), status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error updating template: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, template_id: str) -> Response:
        """Delete template (only if not used)."""
        try:
            template = get_object_or_404(CertificateTemplate, id=template_id)

            
            from src.backend.certificates.domain.models import Certificate
            usage_count = Certificate.objects.filter(template=template).count()

            if usage_count > 0:
                return Response(
                    {"detail": f"Cannot delete template: it's used by {usage_count} certificate(s)"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            template.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            logger.error(f"Error deleting template: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminTemplateDuplicateView(APIView):
    """Duplicate a template."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, template_id: str) -> Response:
        """Create a copy of the template."""
        try:
            original = get_object_or_404(CertificateTemplate, id=template_id)

            
            new_template = CertificateTemplate.objects.create(
                name=f"{original.name} (Copy)",
                description=original.description,
                background_image=original.background_image,
                pdf_template=original.pdf_template,
                font_config=original.font_config,
                layout_config=original.layout_config,
                is_active=False,  
                created_by=request.user,
            )

            return Response(serialize_template(new_template), status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error duplicating template: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminTemplatePreviewView(APIView):
    """Generate preview HTML for a template."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, template_id: str) -> Response:
        """Generate preview HTML with sample data."""
        try:
            template = get_object_or_404(CertificateTemplate, id=template_id)
            data = request.data

            
            sample_data = {
                "student_name": data.get("student_name", "John Doe"),
                "course_name": data.get("course_name", "Python for Beginners"),
                "completion_date": data.get("completion_date", "June 30, 2026"),
                "certificate_number": data.get("certificate_number", "LF-20260630-ABC123"),
                "final_score": data.get("final_score", "95"),
            }

            
            html = self._generate_preview_html(template, sample_data)

            return Response({
                "html": html,
                "width": template.layout_config.get("width", 1122),
                "height": template.layout_config.get("height", 793),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error generating preview: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def _generate_preview_html(template: CertificateTemplate, data: dict) -> str:
        """Generate HTML preview of the certificate."""
        layout = template.layout_config
        fonts = template.font_config
        elements = layout.get("elements", {})

        
        html = f"""
        <div class="certificate-preview" style="
            width: {layout.get('width', 1122)}px;
            height: {layout.get('height', 793)}px;
            position: relative;
            background-image: url('{template.background_image}');
            background-size: cover;
            background-position: center;
            font-family: '{fonts.get('body', {}).get('family', 'Inter')}', sans-serif;
        ">
        """

        
        if 'title' in elements:
            pos = elements['title']
            style = fonts.get('title', {})
            html += f"""
            <div style="
                position: absolute;
                left: {pos.get('x', 0)}px;
                top: {pos.get('y', 0)}px;
                transform: translate(-50%, -50%);
                text-align: {pos.get('align', 'center')};
                font-family: '{style.get('family', 'Inter')}', sans-serif;
                font-size: {style.get('size', 48)}px;
                color: {style.get('color', '
                font-weight: {style.get('weight', 'bold')};
            ">CERTIFICATE OF COMPLETION</div>
            """

        
        if 'student_name' in elements:
            pos = elements['student_name']
            style = fonts.get('subtitle', {})
            html += f"""
            <div style="
                position: absolute;
                left: {pos.get('x', 0)}px;
                top: {pos.get('y', 0)}px;
                transform: translate(-50%, -50%);
                text-align: {pos.get('align', 'center')};
                font-family: '{style.get('family', 'Inter')}', sans-serif;
                font-size: {style.get('size', 24)}px;
                color: {style.get('color', '
                font-weight: {style.get('weight', 'normal')};
            ">{data['student_name']}</div>
            """

        
        if 'course_name' in elements:
            pos = elements['course_name']
            style = fonts.get('body', {})
            html += f"""
            <div style="
                position: absolute;
                left: {pos.get('x', 0)}px;
                top: {pos.get('y', 0)}px;
                transform: translate(-50%, -50%);
                text-align: {pos.get('align', 'center')};
                font-family: '{style.get('family', 'Inter')}', sans-serif;
                font-size: {style.get('size', 16)}px;
                color: {style.get('color', '
            ">for successfully completing<br/><strong>{data['course_name']}</strong></div>
            """

        
        if 'date' in elements:
            pos = elements['date']
            style = fonts.get('body', {})
            html += f"""
            <div style="
                position: absolute;
                left: {pos.get('x', 0)}px;
                top: {pos.get('y', 0)}px;
                transform: translate(-50%, -50%);
                text-align: {pos.get('align', 'center')};
                font-family: '{style.get('family', 'Inter')}', sans-serif;
                font-size: {style.get('size', 16)}px;
                color: {style.get('color', '
            ">Issued on {data['completion_date']}</div>
            """

        
        if 'signature' in elements:
            pos = elements['signature']
            style = fonts.get('signature', {})
            html += f"""
            <div style="
                position: absolute;
                left: {pos.get('x', 0)}px;
                top: {pos.get('y', 0)}px;
                transform: translate(-50%, -50%);
                text-align: {pos.get('align', 'center')};
                font-family: '{style.get('family', 'Dancing Script')}', cursive;
                font-size: {style.get('size', 20)}px;
                color: {style.get('color', '
            ">LearnFlow Academy<br/>
            <small style="font-family: Inter; font-size: 10px;">Certificate 
            </div>
            """

        html += "</div>"
        return html