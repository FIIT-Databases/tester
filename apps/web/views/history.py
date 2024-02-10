from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from apps.core.models import Task


class History(LoginRequiredMixin, View):
    def get(self, request):
        return render(
            request,
            "web/history.html",
            {"tasks": request.user.tasks.filter(executor=Task.Executor.FORM).order_by("-created_at")},
        )


__all__ = [
    "History",
]
