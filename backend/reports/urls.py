from django.urls import path
from .views import AdminDashboardReportAPIView

urlpatterns = [
    path('dashboard/', AdminDashboardReportAPIView.as_view(), name='admin-dashboard-report'),
]
