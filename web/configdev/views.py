import subprocess
from django.shortcuts import render, redirect
from django.views import View

# address of dani script add
SCRIPT_PATH_ADD = "../script/ADDv2.sh"


class DeviceView(View):
# this line is our script runer
    def run_script_add(self, command):
        cmd = f"{SCRIPT_PATH_ADD} {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout

    def get(self, request):
        # Show device list
        output = self.run_script_add("show")
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
            self.run_script_add(f"add {ip} {user} {password}")
# and this delete dev

        elif action == "delete":
            target = request.POST.get("target")
            self.run_script_add(f"del {target}")

        return redirect("device-page")
