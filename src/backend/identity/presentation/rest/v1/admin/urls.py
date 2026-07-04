from django.urls import path
from .views import (
    UserListView,
    UserDetailView,
    UserChangeRoleView,
    UserBlockView,
    UserUnblockView,
    UserSessionsView,
)

urlpatterns = [
    path('users/', UserListView.as_view(), name='admin-user-list'),
    path('users/<uuid:user_id>/', UserDetailView.as_view(), name='admin-user-detail'),
    path('users/<uuid:user_id>/change-role/', UserChangeRoleView.as_view(), name='admin-user-change-role'),
    path('users/<uuid:user_id>/block/', UserBlockView.as_view(), name='admin-user-block'),
    path('users/<uuid:user_id>/unblock/', UserUnblockView.as_view(), name='admin-user-unblock'),
    path('users/<uuid:user_id>/sessions/', UserSessionsView.as_view(), name='admin-user-sessions'),
]