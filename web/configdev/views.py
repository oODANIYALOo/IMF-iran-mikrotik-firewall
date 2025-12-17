import os
from django.conf import settings
import subprocess
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

# address of dani script add
IMF_CONFIG = "imf-config"
IMF_INVENTORY = "imf-inventory"
ANSI_MIKROTICK_INVENTORY= "inventory.ini"
ANSI_MIKROTICK_CONFIG = "mikrotik-config.yml"
CUSTOM_CONFIG_DIR = os.path.join(settings.BASE_DIR, "../web_custom_configs")
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



class MikrotickCustomconfigView(View):

    def get(self, request):
        files = []
        if os.path.exists(CUSTOM_CONFIG_DIR):
            files = os.listdir(CUSTOM_CONFIG_DIR)

        return render(
            request,
            "devices/custom_config.html",
            {
                "files": files,
            }
        )
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

    def run_imf(self, request, FIlE):
        try:
            result = subprocess.run(
                f"imf-config --header --file-config {CUSTOM_CONFIG_DIR}/{FIlE}", shell=True, capture_output=True, text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            messages.error(request, e.stderr or str(e))
            return ""

    def post(self, request):
        action = request.POST.get("action")

        os.makedirs(CUSTOM_CONFIG_DIR, exist_ok=True)

        files = os.listdir(CUSTOM_CONFIG_DIR)

        # -----------------------------
        # LOAD FILE CONTENT
        # -----------------------------
        if action == "load":
            selected_file = request.POST.get("selected_file")

            if not selected_file:
                messages.error(request, "Please select a file.")
                return redirect("configdev:mikrotick_custom_config")

            file_path = os.path.join(CUSTOM_CONFIG_DIR, selected_file)

            if not os.path.exists(file_path):
                messages.error(request, "File not found.")
                return redirect("configdev:mikrotick_custom_config")

            with open(file_path, "r") as f:
                content = f.read()

            return render(
                request,
                "devices/custom_config.html",
                {
                    "files": files,
                    "selected_file": selected_file,
                    "file_content": content,
                }
            )

        # -----------------------------
        # CREATE NEW FILE
        # -----------------------------
        if action == "add":
            new_filename = request.POST.get("new_filename", "").strip()
            content = request.POST.get("content", "")

            if not new_filename:
                messages.error(request, "Filename is required.")
                return redirect("configdev:mikrotick_custom_config")

            if "/" in new_filename or ".." in new_filename:
                messages.error(request, "Invalid filename.")
                return redirect("configdev:mikrotick_custom_config")

            file_path = os.path.join(CUSTOM_CONFIG_DIR, new_filename)

            if os.path.exists(file_path):
                messages.error(request, "File already exists.")
            else:
                with open(file_path, "w") as f:
                    f.write(content)
                messages.success(request, "File created successfully.")

            return redirect("configdev:mikrotick_custom_config")

        # -----------------------------
        # ACTIONS ON EXISTING FILE
        # -----------------------------
        selected_file = request.POST.get("selected_file")

        if not selected_file:
            messages.error(request, "Please select a file.")
            return redirect("configdev:mikrotick_custom_config")

        file_path = os.path.join(CUSTOM_CONFIG_DIR, selected_file)

        if not os.path.exists(file_path):
            messages.error(request, "File not found.")
            return redirect("configdev:mikrotick_custom_config")

        # UPDATE
        if action == "edit":
            updated_content = request.POST.get("updated_content", "")
            with open(file_path, "w") as f:
                f.write(updated_content)
            messages.success(request, "File updated successfully.")

        # DELETE
        elif action == "delete":
            os.remove(file_path)
            messages.success(request, "File deleted successfully.")

        # EXECUTE
        elif action == "execute":
            # Placeholder for execution logic (SSH / API / subprocess)
            messages.success(request, f"{selected_file} executed successfully.")

        else:
            messages.error(request, "Invalid action.")

        return redirect("configdev:mikrotick_custom_config")