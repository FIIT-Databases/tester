import pygal
from django.db.models import Count
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views import View

from apps.core.models import Task, TaskRecord


class Dashboard(View):
    def get(self, request):
        tasks = Task.objects.filter(
            executor=Task.Executor.FORM
        ).values("created_at__date").order_by('created_at__date').annotate(count=Count("id"))
        days = pygal.Line(show_legend=False, human_readable=True, x_label_rotation=40, height=300)
        days.x_labels = list(map(lambda item: str(item['created_at__date'].strftime("%d.%m")), tasks))
        days.add(_('Tasks'), list(map(lambda item: item['count'], tasks)))

        task_records = TaskRecord.objects.filter(
            task__executor=Task.Executor.FORM
        ).values("status").order_by().annotate(count=Count("id"))
        task_record_status = pygal.Pie()
        for task_record in task_records:
            task_record_status.add(task_record['status'], task_record['count'])

        return render(request, 'web/dashboard.html', {
            'total_tests': Task.objects.filter(executor=Task.Executor.FORM).count(),
            'tasks_by_day': days.render_data_uri(),
            'task_record_status': task_record_status.render_data_uri()
        })


__all__ = [
    'Dashboard',
]
