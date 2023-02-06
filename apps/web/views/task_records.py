from uuid import UUID

from django.http import Http404
from django.shortcuts import render
from django.views import View

from apps.core.models import Task, TaskRecord


class TaskDetailDiff(View):
    def get(self, request, task_record_id: UUID):
        try:
            task_record = TaskRecord.objects.get(pk=task_record_id, diff_type=TaskRecord.DiffType.FILE)
        except Task.DoesNotExist:
            raise Http404()

        return render(request, 'web/diff.html', {
            'diff': task_record.diff
        })


__all__ = [
    'TaskDetailDiff',
]
