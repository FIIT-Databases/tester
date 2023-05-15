import csv
import io
from uuid import UUID

import django_rq
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView

from apps.core.jobs import basic_job
from apps.core.models import Task, Evaluation
from apps.web.forms import EvaluationForm


class CreateEvaluationView(LoginRequiredMixin, CreateView):
    model = Evaluation
    form_class = EvaluationForm
    template_name = 'web/evaluation.html'

    def __init__(self):
        self.object = None

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        with open(self.object.links.path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                task = Task.objects.create(
                    user=self.request.user,
                    assigment=self.object.assignment,
                    executor=Task.Executor.EVALUATION,
                    image=row['link'],
                    additional_information=row
                )
                self.object.tasks.add(task)
                django_rq.enqueue(basic_job, task.pk, False)
        return redirect('evaluation-overview')


class EvaluationOverview(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.is_superuser:
            raise Http404()

        try:
            evaluation = Evaluation.objects.all()
        except Evaluation.DoesNotExist:
            raise Http404()
        return render(request, 'web/evaluation_overview.html', {
            'evaluations': evaluation
        })


class EvaluationResult(LoginRequiredMixin, View):
    def get(self, request, evaluation_id: UUID):
        try:
            evaluation = Evaluation.objects.get(pk=evaluation_id)
        except Evaluation.DoesNotExist:
            raise Http404()

        if not evaluation.is_done():
            raise Http404()

        if not request.user.is_superuser:
            raise Http404()

        result = []
        keys = set()

        for task in evaluation.tasks.all():
            item = {
                'email': task.additional_information.get('email'),
                'name': task.additional_information.get('name'),
                'surname': task.additional_information.get('surname'),
                'seminar': task.additional_information.get('seminar'),
                'url': f"{settings.BASE_URL}{task.get_absolute_url()}",
                'status': task.status,
                'image': task.image
            }

            for record in task.records.all():
                item[f"{record.scenario.method} {record.scenario.url}"] = record.status

            keys.update(item.keys())
            result.append(item)

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(keys))
        writer.writeheader()
        writer.writerows(result)

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; {evaluation.pk}.csv'

        return response


__all__ = [
    'CreateEvaluationView',
    'EvaluationOverview',
    'EvaluationResult'
]
