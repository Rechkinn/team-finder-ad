from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub репозиторий",
            "status": "Статус",
        }
        widgets = {
            "status": forms.Select(choices=Project.STATUS_CHOICES),
            "description": forms.Textarea(attrs={"placeholder": "Опишите ваш проект..."}),
            "github_url": forms.URLInput(attrs={"placeholder": "https://github.com/username/repository"}),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if url and "github.com" not in url:
            raise forms.ValidationError("Ссылка должна вести на GitHub")
        return url