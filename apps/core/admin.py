from django.contrib import admin

from apps.core.models import Assignment, Scenario, Task, TaskRecord


class TaskAdmin(admin.ModelAdmin):
    list_filter = ("assigment__name", "user__username", "user__email")
    autocomplete_fields = ("user", )
    search_fields = ("user__username", )
    show_facets = admin.ShowFacets.ALWAYS


class TaskRecordAdmin(admin.ModelAdmin):
    list_filter = ("task__assigment__name", "task__user__username", "task__user__email", )
    autocomplete_fields = ("task", )
    show_facets = admin.ShowFacets.ALWAYS


class AssignmentAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS


class ScenarioAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS


admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskRecord, TaskRecordAdmin)
