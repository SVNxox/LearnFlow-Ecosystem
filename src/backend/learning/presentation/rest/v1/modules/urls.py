"""
Module REST API URLs.

Routes:
- GET    /api/v1/learning/modules/                         - list modules
- POST   /api/v1/learning/modules/create/                  - create module
- GET    /api/v1/learning/modules/{module_id}/             - module detail
- PATCH  /api/v1/learning/modules/{module_id}/             - update module
- DELETE /api/v1/learning/modules/{module_id}/             - delete module (soft)
- POST   /api/v1/learning/modules/{module_id}/publish/     - publish module
- POST   /api/v1/learning/modules/{module_id}/unpublish/   - unpublish module
- POST   /api/v1/learning/modules/reorder/                 - reorder modules
"""

from django.urls import path

from .create import ModuleCreateView
from .detail import ModuleDetailView
from .list import ModuleListView
from .publish import ModulePublishView, ModuleUnpublishView
from .reorder import ModuleReorderView

urlpatterns = [
    
    path("", ModuleListView.as_view(), name="module-list"),

    
    path("create/", ModuleCreateView.as_view(), name="module-create"),

    
    path("<str:module_id>/", ModuleDetailView.as_view(), name="module-detail"),

    
    path("<str:module_id>/publish/", ModulePublishView.as_view(), name="module-publish"),
    path("<str:module_id>/unpublish/", ModuleUnpublishView.as_view(), name="module-unpublish"),

    
    path("reorder/", ModuleReorderView.as_view(), name="module-reorder"),
]