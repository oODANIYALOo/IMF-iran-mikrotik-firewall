import subprocess
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

# address of dani script add
IMF_CONFIG = "imf-config"
IMF_INVENTORY = "imf-inventory"
ANSI_MIKROTICK_INVENTORY= "inventory.ini"
ANSI_MIKROTICK_CONFIG = "mikrotik-config.yml"
class IndexView(View):
    def get(self, request):
        return render(request, "index.html")

class AddAndDeleteMikrotickViewe(View):

    # Run IMF command
    def run_imf(self, request, command):
        try:
            cmd = f"{IMF_INVENTORY} {command}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            messages.error(request, e.stderr or str(e))
            return ""

    # Show device list
    def get(self, request):
        output = self.run_imf(request, "show | grep mikrotik")
        devices = output.splitlines()
        return render(request, "devices/devices.html", {"devices": devices})

    # Handle add/delete dev
    def post(self, request):
        action = request.POST.get("action")

        if action == "add":
            ip = request.POST.get("ip")
            user = request.POST.get("user")
            password = request.POST.get("password")

            self.run_imf(request, f"add {ip} {user} {password}")
            messages.success(request, "Device added successfully.")

        elif action == "delete":
            target = request.POST.get("target")

            self.run_imf(request, f"del {target}")
            messages.success(request, "Device deleted successfully.")

        return redirect("configdev:add_dell")
class CheckMikrotick(View):
    def get(self, request):
        try:
            result = subprocess.run(
                "ansible allmikrotik -m community.routeros.command "
                "-a '{\"commands\": [\"/system resource print\"]}' -i /app/inventory.ini "
                "| grep -e version -e memory -e cpu -e platform | "
                "tail -8 | cut -d '\"' -f 2",
                shell=True,
                capture_output=True,
                text=True
            )
            return render(request, 'devices/check.html', {"output": result.stdout})

        except subprocess.CalledProcessError as e:
            messages.error(request, e.stderr or str(e))
            return render(request, 'devices/check.html', {"output": ""})
class ConfigMikrotick(View):

    def execute(self, request):
        try:
            cmd = f"ansible-playbook -i {ANSI_MIKROTICK_INVENTORY} {ANSI_MIKROTICK_CONFIG}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            messages.error(request, e.stderr or str(e))
            return ""

    def run_imf(self, request, command):
        try:
            cmd = f"{IMF_CONFIG} {command}".strip()
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            messages.error(request, e.stderr or str(e))
            return ""

    def get(self, request):
        return render(request, "devices/config.html")

    def post(self, request):
        hostname = request.POST.get("hostname", "").strip()
        vlan = request.POST.get("vlan", "").strip()
        dhcp_server = request.POST.get("dhcp_server", "").strip()
        ntp = request.POST.get("ntp_server", "").strip()
        default_route = request.POST.get("default_route", "").strip()

        args = []

        if hostname:
            args.append(f"--hostname {hostname}")
        if vlan:
            args.append(f"--vlan {vlan}")
        if dhcp_server:
            args.append(f"--dhcp-server {dhcp_server}")
        if ntp:
            args.append(f"--ntp {ntp}")
        if default_route:
            args.append(f"--route {default_route}")

        argument_string = " ".join(args)

        if not argument_string:
            messages.error(request, "Please enter at least one field.")
            return render(request, "devices/config.html")

        # Run IMF commands
        self.run_imf(request, argument_string)
        # execute anis
        self.execute(request)

        messages.success(request, "Configuration applied successfully.")

        return render(request, "devices/config.html")
