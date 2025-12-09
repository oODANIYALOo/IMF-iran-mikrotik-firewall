from django.http import HttpResponse
from django.views import View


class Index(View):
    def get(self, request, *args, **kwargs):
        # display list of devices
        return HttpResponse("Hello, this is index view!")

    def post(self, request, *args, **kwargs):
        # adding device
        # deleting device
        pass
