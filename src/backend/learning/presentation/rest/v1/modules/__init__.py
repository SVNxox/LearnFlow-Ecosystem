"""
Modules REST API - exports for convenience.

Views:
- ModuleCreateView - POST /api/learning/{course_id}/modules/
- ModuleDetailView - GET /api/learning/{course_id}/modules/{module_id}/
- ModuleUpdateView - PATCH /api/learning/{course_id}/modules/{module_id}/
- ModuleDeleteView - DELETE /api/learning/{course_id}/modules/{module_id}/
- ModulePublishView - POST /api/learning/{course_id}/modules/{module_id}/publish/
- ModuleUnpublishView - POST /api/learning/{course_id}/modules/{module_id}/unpublish/
- ModuleReorderView - POST /api/learning/{course_id}/modules/reorder/
"""

from .create import ModuleCreateView
from .detail import ModuleDetailView
from .list import ModuleListView
from .publish import ModulePublishView, ModuleUnpublishView
from .reorder import ModuleReorderView
from .update import ModuleUpdateView, ModuleDeleteView

__all__ = [
    "ModuleCreateView",
    "ModuleDetailView",
    "ModuleListView",
    "ModulePublishView",
    "ModuleUnpublishView",
    "ModuleUpdateView",
    "ModuleDeleteView",
    "ModuleReorderView",
]
