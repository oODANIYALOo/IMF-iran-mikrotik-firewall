import subprocess
from django.shortcuts import render, redirect
from django.views import View

# address of dani script add
IMF_CONFIG = "imf-config"
IMF_INVENTORY = "imf-inventory"
ANSI_MIKROTICK_INVENTORY= "inventory.ini"
ANSI_MIKROTICK_CONFIG = "mikrotik-config"
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

        return redirect("configdev:add_dell")


class CheckMikrotick(View):
    def get(self, request):
        if request.method == 'POST':
            number = request.POST.get('number')

        result = subprocess.run("ansible allmikrotik -m community.routeros.command \
	       	-a \'{\"commands\": [\"/system resource print\"]}\' -i /app/inventory.ini \
            | grep -e version -e memory -e cpu -e platform | \
		       	tail -8 | cut -d \'\"\' -f 2", shell=True, capture_output=True, text=True)

        return render(request, 'devices/check.html', {"output": result.stdout})


class ConfigMikrotick(View):

    def execute(self):
        cmd = f"ansible-playbook -i {ANSI_MIKROTICK_INVENTORY} {ANSI_MIKROTICK_CONFIG}"
        return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

    def run_imf(self, command):
        cmd = f"{IMF_CONFIG} {command}".strip()
        return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

    def get(self, request):
        return render(request, "devices/config.html")

    def post(self, request):
        hostname = request.POST.get("hostname", "").strip()
        vlan = request.POST.get("vlan", "").strip()
        dhcp_server = request.POST.get("dhcp_server", "").strip()
        ntp = request.POST.get("ntp_server", "").strip()
        default_route = request.POST.get("default_route", "").strip()
        execute_flag = request.POST.get("execute")

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

        # Execute once
        if execute_flag and argument_string:
            self.run_imf(argument_string)
            self.execute()

        return render(request, "devices/config.html", {
            "msg": "Configuration applied successfully."
        })
