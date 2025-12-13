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
        args = []

        # ---------------------------------------------------------
        # HOSTNAME (only added if user enters a value)
        # ---------------------------------------------------------
        hostname = request.POST.get("hostname", "").strip()
        if hostname:
            args.append(f"--hostname {hostname}")

        # ---------------------------------------------------------
        # VLAN logic:
        # 1. If user typed a value → use "--vlan-id <value>"
        # 2. Else if checkbox is checked → use "--vlan"
        # 3. Otherwise → nothing
        # ---------------------------------------------------------
        vlan_chk = request.POST.get("vlan_chk")
        vlan_value = request.POST.get("vlan", "").strip()

        if vlan_value:
            args.append(f"--vlan-id {vlan_value}")
        elif vlan_chk:
            args.append("--vlan")

        # ---------------------------------------------------------
        # DHCP logic:
        # 1. If user typed a pool → "--dhcp-pool <value>"
        # 2. If only checkbox checked → "--dhcp-server"
        # ---------------------------------------------------------
        dhcp_chk = request.POST.get("dhcp_chk")
        dhcp_pool = request.POST.get("dhcp_pool", "").strip()

        if dhcp_pool:
            args.append(f"--dhcp-pool {dhcp_pool}")
        elif dhcp_chk:
            args.append("--dhcp-server")

        # ---------------------------------------------------------
        # NTP logic:
        # 1. Value → "--ntp-server <value>"
        # 2. Only checkbox → "--set-ntp"
        # ---------------------------------------------------------
        ntp_chk = request.POST.get("ntp_chk")
        ntp_server = request.POST.get("ntp_server", "").strip()

        if ntp_server:
            args.append(f"--ntp-server {ntp_server}")
        elif ntp_chk:
            args.append("--set-ntp")

        # ---------------------------------------------------------
        # STATIC ROUTE logic:
        # 1. Value → "--route-gateway <gw>"
        # 2. Only checkbox → "--add-route"
        # ---------------------------------------------------------
        route_chk = request.POST.get("route_chk")
        route_gw = request.POST.get("route_gw", "").strip()

        if route_gw:
            args.append(f"--route-gateway {route_gw}")
        elif route_chk:
            args.append("--add-route")

        # ---------------------------------------------------------
        # Build final command argument string
        # ---------------------------------------------------------
        argument_string = " ".join(args)

        # Send to IMF
        self.run_imf(request, argument_string)
        self.execute(request)

        messages.success(request, "Configuration applied successfully.")
        return render(request, "devices/config.html")
