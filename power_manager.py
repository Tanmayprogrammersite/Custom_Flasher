import os
import sys
import subprocess
import logging

class HardwarePowerManager:
    def __init__(self, binary_resolver_func):
        """ Expects the resource_path utility method to dynamically locate adb/fastboot/heimdall """
        self.get_bin = binary_resolver_func
        
    def execute_power_state(self, engine_mode: str, action_payload: str):
        """
        Processes low-level hardware command strings based on interface variables.
        action_payload handles: 'shutdown', 'system', 'recovery', 'bootloader', 'fastbootd'
        """
        try:
            adb_bin = self.get_bin("adb.exe")
            fastboot_bin = self.get_bin("fastboot.exe")
            heimdall_bin = self.get_bin("heimdall.exe")
            
            cmd = []

            # ==========================================
            # 🤖 CONTEXT A: ADB RUNTIME MODE
            # ==========================================
            if engine_mode == "ADB Sideload":
                if action_payload == "shutdown":
                    cmd = [adb_bin, "reboot", "poweroff"]
                elif action_payload == "system":
                    cmd = [adb_bin, "reboot"]
                elif action_payload == "recovery":
                    cmd = [adb_bin, "reboot", "recovery"]
                elif action_payload == "bootloader":
                    cmd = [adb_bin, "reboot", "bootloader"]
                elif action_payload == "fastbootd":
                    cmd = [adb_bin, "reboot", "fastboot"]

            # ==========================================
            # ⚡ CONTEXT B: FASTBOOT RUNTIME MODE
            # ==========================================
            elif engine_mode == "Fastboot":
                if action_payload == "shutdown":
                    # Note: Certain older bootloaders require 'fastboot powerdown'
                    cmd = [fastboot_bin, "reboot", "poweroff"]
                elif action_payload == "system":
                    cmd = [fastboot_bin, "reboot"]
                elif action_payload == "recovery":
                    # Chained reboot string targets to boot image boundaries directly
                    cmd = [fastboot_bin, "reboot-recovery"]
                elif action_payload == "bootloader":
                    cmd = [fastboot_bin, "reboot", "bootloader"]
                elif action_payload == "fastbootd":
                    cmd = [fastboot_bin, "reboot", "fastboot"]

            # ==========================================
            # 🌀 CONTEXT C: SAMSUNG DOWNLOAD MODE (ODIN)
            # ==========================================
            elif "Odin" in engine_mode or "Download" in engine_mode:
                # Heimdall safely resets the USB kernel handles to force loop exit states
                if action_payload in ["shutdown", "system", "reboot_system"]:
                    cmd = [heimdall_bin, "close"]

            if cmd:
                # Fire command silently into hidden OS subprocess layer blocks
                subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    creationflags=0x08000000, 
                    check=True
                )
                return {"status": "success", "msg": f"Command executed successfully: {' '.join(cmd)}"}
                
        except subprocess.CalledProcessError as e:
            return {"status": "error", "msg": f"Hardware rejection stream traces:\n{e.stderr}"}
        except Exception as e:
            return {"status": "error", "msg": str(e)}
