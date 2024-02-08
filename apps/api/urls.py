from django.urls import path

from apps.api.views import status

urlpatterns = [
    # Status
    path("status", status.StatusManagement.as_view(), name="status"),
]
