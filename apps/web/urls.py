from django.urls import path

from apps.web.views import tasks, dashboard, changelog, task_records, evaluation, history

urlpatterns = [
    path("task_records/<uuid:task_record_id>/diff", task_records.TaskDetailDiff.as_view(), name="task-record-diff"),
    path("tasks/<uuid:task_id>", tasks.TaskDetail.as_view(), name="task-detail"),
    path("tasks/new", tasks.CrateTaskView.as_view(), name="task-new"),
    path("tasks/archive", tasks.TaskArchiveView.as_view(), name="task-archive"),
    path("evaluations/<uuid:evaluation_id>", evaluation.EvaluationResult.as_view(), name="evaluation-result"),
    path("history", history.History.as_view(), name="history"),
    path("changelog", changelog.Changelog.as_view(), name="changelog"),
    path("", dashboard.Dashboard.as_view(), name="dashboard"),
]
