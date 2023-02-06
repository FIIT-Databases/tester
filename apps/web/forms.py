from django.forms import ModelForm

from apps.core.models import Task


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['assigment', 'image']
