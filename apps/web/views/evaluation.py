import csv
import io
from uuid import UUID

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.views import View

from apps.core.models import Evaluation


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
                "timestamp": task.additional_information.get("Časová pečiatka"),
                "email": task.additional_information.get("E-mailová adresa"),
                "name": task.additional_information.get("Meno"),
                "surname": task.additional_information.get("Priezvisko"),
                "seminar": task.additional_information.get("Cvicenie"),
                "url": f"{settings.BASE_URL}{task.get_absolute_url()}",
                "status": task.status,
                "image": task.image,
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
        response = HttpResponse(buffer, content_type="text/csv")
        response["Content-Disposition"] = f"attachment; {evaluation.pk}.csv"

        return response


__all__ = ["EvaluationResult"]
