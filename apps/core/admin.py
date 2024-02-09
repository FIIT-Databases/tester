from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext as _

from apps.core.models import Assignment, Scenario, Task, TaskRecord


def get_related_field(name, admin_order_field=None, short_description=None):
    related_names = name.split("__")

    def dynamic_attribute(obj):
        for related_name in related_names:
            obj = getattr(obj, related_name)
        return obj

    dynamic_attribute.admin_order_field = admin_order_field or name
    dynamic_attribute.short_description = short_description or related_names[-1].title().replace("_", " ")
    return dynamic_attribute


class RelatedFieldAdmin(admin.ModelAdmin):
    def __getattr__(self, attr):
        if "__" in attr:
            return get_related_field(attr)

        # not dynamic lookup, default behaviour
        return self.__getattribute__(attr)


class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "assigment", "user", "status", "url")
    list_filter = ("assigment__name", "status")
    autocomplete_fields = ("user",)
    search_fields = ("user__username",)
    show_facets = admin.ShowFacets.ALWAYS

    @admin.display(description=_("Viewer"))
    def url(self, obj):
        return format_html('<a href="{0}" target="_blank">Show</a>', obj.get_absolute_url())


class TaskRecordAdmin(RelatedFieldAdmin):
    list_display = ("id", "created_at", "task", "task__user")
    readonly_fields = ("created_at",)
    list_filter = ("task__assigment__name",)
    autocomplete_fields = ("task",)
    search_fields = ("task__user__username",)
    show_facets = admin.ShowFacets.ALWAYS


class AssignmentAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS


class ScenarioAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS
    list_filter = ("assigment__name",)


admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskRecord, TaskRecordAdmin)
