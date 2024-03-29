from uuid import UUID

import django_rq
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView

from apps.core.jobs import basic_job
from apps.core.models import Task, Assignment
from apps.web.forms import TaskForm


class CrateTaskView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "web/task.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def get_initial(self):
        task_form = self.request.session.pop("task_form", {})

        try:
            assignment = Assignment.objects.get(pk=task_form.get("assignment"))
        except Assignment.DoesNotExist:
            assignment = None

        return {
            "image": task_form.get("image", ""),
            "assignment": assignment,
        }

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        self.request.session["task_form"] = self.request.POST.dict()
        django_rq.enqueue(basic_job, self.object.pk, not self.request.user.is_staff)
        return HttpResponseRedirect(self.get_success_url())


class TaskArchiveView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "web/archive.html")


class TaskDetail(View):
    def get(self, request, task_id: UUID):
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise Http404()
        return render(request, "web/task_detail.html", {"task": task})


__all__ = ["CrateTaskView", "TaskDetail"]
