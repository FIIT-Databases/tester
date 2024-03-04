import django_rq
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _
from rq import Queue

from apps.core.jobs import basic_job
from apps.core.models import Assignment, Scenario, Task, TaskRecord, Evaluation


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


class EvaluationAdmin(ExtraButtonsMixin, RelatedFieldAdmin):
    list_display = ("id", "created_at", "assignment", "status", "protocol")
    readonly_fields = ("created_at", "tasks", "id")
    exclude = ("creator",)
    list_filter = ("assignment__name",)
    show_facets = admin.ShowFacets.ALWAYS

    def save_form(self, request, form, change):
        obj = super().save_form(request, form, change)
        if not change:
            obj.creator = request.user
        return obj

    @admin.display(description=_("Status"))
    def status(self, obj):
        done = obj.tasks.filter(status=Task.Status.DONE).count()
        pending = obj.tasks.filter(status=Task.Status.PENDING).count()
        failed = obj.tasks.filter(status=Task.Status.FAILED).count()
        return format_html(
            '<strong style="color: green;">{0}</strong> - '
            '<strong style="color: red;">{1}</strong> - '
            '<strong style="color: blue;">{2}</strong>',
            done,
            failed,
            pending,
        )

    @admin.display(description=_("Protocol"))
    def protocol(self, obj):
        if obj.is_done():
            return format_html(
                '<a href="{0}" target="_blank">Download</a>',
                reverse("evaluation-result", kwargs={"evaluation_id": obj.pk}),
            )
        else:
            return ""

    @button(html_attrs={"style": "background-color:#88FF88;color:black"})
    def recreate_queue(self, request):
        django_rq.get_queue("default").empty()
        jobs = []

        for task in Task.objects.filter(status=Task.Status.PENDING):
            jobs.append(
                Queue.prepare_data(
                    basic_job,
                    (
                        task.pk,
                        False,
                    ),
                )
            )

        django_rq.get_queue("default").enqueue_many(jobs)

        self.message_user(request, "Pending tasks were added back to queue")
        return HttpResponseRedirectToReferrer(request)


class AssignmentAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS


class ScenarioAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS
    list_filter = ("assigment__name",)


admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskRecord, TaskRecordAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
