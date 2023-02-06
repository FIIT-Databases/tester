from uuid import UUID

import django_rq
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView

from apps.core import jobs
from apps.core.models import Task
from apps.web.forms import TaskForm


class TaskManagement(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'web/task.html'

    def __init__(self):
        self.object = None

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        django_rq.enqueue(jobs.basic, self.object.pk, self.request.user.is_anonymous)
        return HttpResponseRedirect(self.get_success_url())


class TaskDetail(View):
    def get(self, request, task_id: UUID):
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise Http404()
        return render(request, 'web/task_detail.html', {
            'task': task
        })


__all__ = [
    'TaskManagement',
    'TaskDetail'
]
