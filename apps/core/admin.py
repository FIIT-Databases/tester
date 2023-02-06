from django.contrib import admin

from apps.core.models import Assignment, Scenario, Task, TaskRecord

admin.site.register(Assignment)
admin.site.register(Scenario)
admin.site.register(Task)
admin.site.register(TaskRecord)
