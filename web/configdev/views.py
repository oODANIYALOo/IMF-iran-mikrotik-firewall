from django.http import HttpResponse
from django.views import View


class Index(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello, this is index view!")