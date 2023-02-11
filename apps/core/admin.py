from django.contrib import admin

from apps.core.models import Assignment, Scenario, Task, TaskRecord


class TaskAdmin(admin.ModelAdmin):
    list_filter = (
        'assigment__name',
    )


admin.site.register(Assignment)
admin.site.register(Scenario)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskRecord)
