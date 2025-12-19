import os
import subprocess

from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages


# =========================
# CONSTANTS
# =========================

IMF_CONFIG = "imf-config"
IMF_INVENTORY = "imf-inventory"

ANSI_MIKROTICK_INVENTORY = "inventory.ini"
ANSI_MIKROTICK_CONFIG = "mikrotik-config.yml"

CUSTOM_CONFIG_DIR = os.path.join(settings.BASE_DIR, "../web_custom_configs")


# =========================
# BASE UTIL
# =========================

def run_command(request, cmd):
    """
    Run shell command safely and return stdout on success.
    On failure, show error message and return None.
    """
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        messages.error(request, result.stderr or "Command execution failed")
        return None

    return result.stdout


# =========================
# INDEX
# =========================

class IndexView(View):
    def get(self, request):
        return render(request, "index.html")


# =========================
# ADD / DELETE MIKROTIK
# =========================

class AddAndDeleteMikrotickViewe(View):

    def get(self, request):
        output = run_command(request, f"{IMF_INVENTORY} show | grep mikrotik")
        devices = output.splitlines() if output else []
        return render(request, "devices/devices.html", {"devices": devices})

    def post(self, request):
        action = request.POST.get("action")

        if action == "add":
            ip = request.POST.get("ip")
            user = request.POST.get("user")
            password = request.POST.get("password")

            result = run_command(
                request,
                f"{IMF_INVENTORY} add {ip} {user} {password}"
            )

            if result is not None:
                messages.success(request, "Device added successfully.")

        elif action == "delete":
            target = request.POST.get("target")

            result = run_command(
                request,
                f"{IMF_INVENTORY} del {target}"
            )

            if result is not None:
                messages.success(request, "Device deleted successfully.")

        return redirect("configdev:add_dell")


# =========================
# CHECK MIKROTIK STATUS
# =========================

class CheckMikrotick(View):

    def get(self, request):
        cmd = (
            "ansible allmikrotik -m community.routeros.command "
            "-a '{\"commands\": [\"/system resource print\"]}' "
            f"-i {ANSI_MIKROTICK_INVENTORY} "
            "| grep -e version -e memory -e cpu -e platform | "
            "tail -8 | cut -d '\"' -f 2"
        )

        output = run_command(request, cmd)
        return render(request, "devices/check.html", {"output": output or ""})


# =========================
# CONFIG MIKROTIK (FORM)
# =========================

class ConfigMikrotick(View):

    def get(self, request):
        return render(request, "devices/config.html")

    def post(self, request):
        args = []

        # HOSTNAME
        hostname = request.POST.get("hostname", "").strip()
        if hostname:
            args.append(f"--hostname {hostname}")

        # VLAN
        vlan_chk = request.POST.get("vlan_chk")
        vlan_value = request.POST.get("vlan", "").strip()
        if vlan_value:
            args.append(f"--vlan-id {vlan_value}")
        elif vlan_chk:
            args.append("--vlan")

        # DHCP
        dhcp_chk = request.POST.get("dhcp_chk")
        dhcp_pool = request.POST.get("dhcp_pool", "").strip()
        if dhcp_pool:
            args.append(f"--dhcp-pool {dhcp_pool}")
        elif dhcp_chk:
            args.append("--dhcp-server")

        # NTP
        ntp_chk = request.POST.get("ntp_chk")
        ntp_server = request.POST.get("ntp_server", "").strip()
        if ntp_server:
            args.append(f"--ntp-server {ntp_server}")
        elif ntp_chk:
            args.append("--set-ntp")

        # STATIC ROUTE
        route_chk = request.POST.get("route_chk")
        route_gw = request.POST.get("route_gw", "").strip()
        if route_gw:
            args.append(f"--route-gateway {route_gw}")
        elif route_chk:
            args.append("--add-route")

        argument_string = " ".join(args)

        # Run IMF
        imf_result = run_command(
            request,
            f"{IMF_CONFIG} {argument_string}"
        )

        if imf_result is None:
            return render(request, "devices/config.html")

        # Run Ansible
        ansible_result = run_command(
            request,
            f"ansible-playbook -i {ANSI_MIKROTICK_INVENTORY} {ANSI_MIKROTICK_CONFIG}"
        )

        if ansible_result is None:
            return render(request, "devices/config.html")

        messages.success(request, "Configuration applied successfully.")
        return render(request, "devices/config.html")


# =========================
# CUSTOM CONFIG FILES
# =========================

class MikrotickCustomconfigView(View):

    def get(self, request):
        os.makedirs(CUSTOM_CONFIG_DIR, exist_ok=True)
        files = os.listdir(CUSTOM_CONFIG_DIR)
        return render(request, "devices/custom_config.html", {"files": files})

    def post(self, request):
        action = request.POST.get("action")
        os.makedirs(CUSTOM_CONFIG_DIR, exist_ok=True)
        files = os.listdir(CUSTOM_CONFIG_DIR)

        # LOAD FILE
        if action == "load":
            selected_file = request.POST.get("selected_file")
            if not selected_file:
                messages.error(request, "Please select a file.")
                return redirect("configdev:mikrotick_custom_config")

            file_path = os.path.join(CUSTOM_CONFIG_DIR, selected_file)
            if not os.path.exists(file_path):
                messages.error(request, "File not found.")
                return redirect("configdev:mikrotick_custom_config")

            with open(file_path) as f:
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

        # CREATE FILE
        if action == "add":
            filename = request.POST.get("new_filename", "").strip()
            content = request.POST.get("content", "")

            if (
                    not filename
                    or "/" in filename
                    or ".." in filename
                    or " " in filename
                    or not filename.isalnum()
            ):
                # invalid filename
                messages.error(request, "Invalid filename.")
                return redirect("configdev:mikrotick_custom_config")

            file_path = os.path.join(CUSTOM_CONFIG_DIR, filename)

            if os.path.exists(file_path):
                messages.error(request, "File already exists.")
            else:
                with open(file_path, "w") as f:
                    f.write(content)
                messages.success(request, "File created successfully.")

            return redirect("configdev:mikrotick_custom_config")

        # FILE ACTIONS
        selected_file = request.POST.get("selected_file")
        if not selected_file:
            messages.error(request, "Please select a file.")
            return redirect("configdev:mikrotick_custom_config")

        file_path = os.path.join(CUSTOM_CONFIG_DIR, selected_file)
        if not os.path.exists(file_path):
            messages.error(request, "File not found.")
            return redirect("configdev:mikrotick_custom_config")

        # EDIT
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
            imf_result = run_command(
                request,
                f"{IMF_CONFIG} --header --file-config {file_path}"
            )

            if imf_result is None:
                return redirect("configdev:mikrotick_custom_config")

            ansible_result = run_command(
                request,
                f"ansible-playbook -i {ANSI_MIKROTICK_INVENTORY} {ANSI_MIKROTICK_CONFIG}"
            )

            if ansible_result is None:
                return redirect("configdev:mikrotick_custom_config")

            messages.success(request, f"{selected_file} executed successfully.")

        else:
            messages.error(request, "Invalid action.")

        return redirect("configdev:mikrotick_custom_config")
