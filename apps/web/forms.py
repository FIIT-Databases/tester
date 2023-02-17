from django.forms import ModelForm

from apps.core.models import Task


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['assigment', 'image']

    def clean_image(self):
        return self.cleaned_data['image'].lower()
