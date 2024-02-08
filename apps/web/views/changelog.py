import markdown
from django.conf import settings
from django.shortcuts import render
from django.views import View


class Changelog(View):
    def get(self, request):
        with open(f"{settings.BASE_DIR}/CHANGELOG.md") as fp:
            data = markdown.markdown(fp.read())
        return render(request, "web/changelog.html", {"data": data})


__all__ = ["Changelog"]
