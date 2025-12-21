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
def mikrotik_devices_exist(request):
    """
    Check if at least one mikrotik device exists.
    """
    result = run_command(
        request,
        f"{IMF_INVENTORY} show | grep mikrotik"
    )
    return bool(result)

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
        output = run_command(request, f"{IMF_INVENTORY} show | grep mikrotik")
        devices = output.splitlines() if output else []

        return render(
            request,
            "devices/show_device.html",
            {
                "devices": devices,
            }
        )

    def post(self, request):
        # 👇 فقط دریافت انتخاب‌ها (هیچ ذخیره‌ای)
        selected_devices = request.POST.getlist("devices")

        # (فعلاً فقط برای اینکه ببینی گرفته شده)
        print("Selected devices:", selected_devices)

        cmd = (
            "ansible allmikrotik -m community.routeros.command "
            "-a '{\"commands\": [\"/system resource print\"]}' "
            f"-i {ANSI_MIKROTICK_INVENTORY} "
            "| grep -e version -e memory -e cpu -e platform | "
            "tail -8 | cut -d '\"' -f 2"
        )

        output = run_command(request, cmd)

        return render(
            request,
            "devices/check.html",
            {
                "output": output or "",
                "selected_devices": selected_devices,  # فقط برای نمایش
            }
        )

# =========================
# CONFIG MIKROTIK (FORM)
# =========================

class ConfigMikrotick(View):

    def get(self, request):
        output = run_command(request, f"{IMF_INVENTORY} show | grep mikrotik")
        devices = output.splitlines() if output else []

        return render(
            request,
            "devices/config.html",
            {
                "devices": devices,
            }
        )

    def post(self, request):
        if not mikrotik_devices_exist(request):
            messages.error(request, "No mikrotik devices found.")
            return redirect("configdev:config_mikrotick")

        # ✅ دستگاه‌های انتخاب‌شده (بدون session)
        selected_devices = request.POST.getlist("devices")

        if not selected_devices:
            messages.error(request, "Please select at least one device.")
            return redirect("configdev:config_mikrotick")

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

        if request.POST.get("harden_chk"):
            args.append("--harden")

        if request.POST.get("firewall_chk"):
            args.append("--firewall")

        argument_string = " ".join(args)

        # فقط برای اینکه بعداً استفاده کنی
        #print("Selected devices:", selected_devices)

        # Run IMF
        imf_result = run_command(
            request,
            f"{IMF_CONFIG} {argument_string}"
        )
        if imf_result is None:
            return render(request, "devices/config.html")

        # 🔥 فعلاً روی همه اجرا می‌شود (بعداً limit می‌کنی)
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

class MikrotikCustomConfigView(View):

    template_name = "devices/custom_config.html"

    def get(self, request):
        os.makedirs(CUSTOM_CONFIG_DIR, exist_ok=True)

        files = os.listdir(CUSTOM_CONFIG_DIR)

        output = run_command(request, f"{IMF_INVENTORY} show | grep mikrotik")
        devices = output.splitlines() if output else []

        return render(
            request,
            self.template_name,
            {
                "files": files,
                "devices": devices,
            }
        )

    def post(self, request):
        os.makedirs(CUSTOM_CONFIG_DIR, exist_ok=True)

        action = request.POST.get("action")

        files = os.listdir(CUSTOM_CONFIG_DIR)

        output = run_command(request, f"{IMF_INVENTORY} show | grep mikrotik")
        devices = output.splitlines() if output else []

        selected_file = None
        file_content = None

        # ----------------------------
        # Create new file
        # ----------------------------
        if action == "add":
            filename = request.POST.get("new_filename")
            content = request.POST.get("content", "")

            if filename:
                path = os.path.join(CUSTOM_CONFIG_DIR, filename)
                with open(path, "w") as f:
                    f.write(content)

                messages.success(request, "File created successfully.")
                return redirect(request.path)

        # ----------------------------
        # Load file content
        # ----------------------------
        if action == "load":
            selected_file = request.POST.get("selected_file")

            if selected_file:
                path = os.path.join(CUSTOM_CONFIG_DIR, selected_file)
                if os.path.exists(path):
                    with open(path) as f:
                        file_content = f.read()

        # ----------------------------
        # Edit file
        # ----------------------------
        if action == "edit":
            selected_file = request.POST.get("selected_file")
            updated_content = request.POST.get("updated_content", "")

            if selected_file:
                path = os.path.join(CUSTOM_CONFIG_DIR, selected_file)
                with open(path, "w") as f:
                    f.write(updated_content)

                messages.success(request, "File updated successfully.")

                file_content = updated_content

        # ----------------------------
        # Execute file (fake execution for now)
        # ----------------------------
        if action == "execute":
            selected_file = request.POST.get("selected_file")

            # توهم اجرا – فعلاً هیچ کاری نمی‌کنیم
            messages.success(
                request,
                f"Configuration '{selected_file}' executed on selected MikroTik devices."
            )

        # ----------------------------
        # Delete file
        # ----------------------------
        if action == "delete":
            selected_file = request.POST.get("selected_file")

            if selected_file:
                path = os.path.join(CUSTOM_CONFIG_DIR, selected_file)
                if os.path.exists(path):
                    os.remove(path)

                messages.success(request, "File deleted successfully.")
                return redirect(request.path)

        # ----------------------------
        # Receive MikroTik selection (no session)
        # ----------------------------
        if action == "select_mikrotik":
            raw = request.POST.get("selected_indexes", "")
            selected_indexes = [
                int(i) for i in raw.split(",") if i.strip() != ""
            ]

            # فعلاً فقط در حافظه است
            print("Selected MikroTik indexes:", selected_indexes)

            messages.success(request, "MikroTik selection received.")
            return redirect(request.path)

        return render(
            request,
            self.template_name,
            {
                "files": files,
                "devices": devices,
                "selected_file": selected_file,
                "file_content": file_content,
            }
        )