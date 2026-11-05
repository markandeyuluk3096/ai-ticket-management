from rest_framework.permissions import BasePermission, SAFE_METHODS


class TicketAccessPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'admin':
            return True
        if request.method in SAFE_METHODS:
            return obj.customer_id == user.id or obj.assigned_agent_id == user.id
        return user.role == 'agent' and obj.assigned_agent_id == user.id
