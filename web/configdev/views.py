import subprocess
from django.shortcuts import render, redirect
from django.views import View

# address of dani script add
IMF_INVENTORY = "imf-inventory"


class IndexView(View):
    def get(self, request):
        return render(request, "index.html")

class AddAndDeleteMikrotickViewe(View):
# this line is our script runer
    def run_imf(self, command):
        cmd = f"{IMF_INVENTORY} {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout

    def get(self, request):
        # Show device list
        output = self.run_imf("show | grep mikrotik")
        devices = output.splitlines()
        return render(request, "devices/devices.html", {"devices": devices})
# and this is control sender
    def post(self, request):
        action = request.POST.get("action")
# and this add dev
        if action == "add":
            ip = request.POST.get("ip")
            user = request.POST.get("user")
            password = request.POST.get("password")
            self.run_imf(f"add {ip} {user} {password}")
# and this delete dev

        elif action == "delete":
            target = request.POST.get("target")
            self.run_imf(f"del {target}")

        return redirect("device-page")


class CheckMikrotick(View):
    def get(self, request):
        pass


class ConfigMikrotick(View):
    def get(self, request):
        pass
