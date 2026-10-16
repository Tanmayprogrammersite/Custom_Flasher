import os, sys, subprocess, threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- CRITICAL FIX FOR WINDOWS EXECUTABLE LAUNCH CRASHES ---
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

os.environ["PATH"] = resource_path(".") + os.path.pathsep + os.environ["PATH"]

class UniversalFlasherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Android Flasher & Sideload Suite")
        self.root.geometry("640x670") # Made the window height shorter too!
        self.root.configure(bg="#1e1e24")
        self.root.resizable(False, False)

        # Style System Configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#1e1e24", foreground="#ffffff", fieldbackground="#2a2a35")
        self.style.configure("TCombobox", fieldbackground="#2a2a35", background="#3a3a4a", foreground="#ffffff", arrowcolor="#ffffff")
        self.style.configure("Odin.Horizontal.TProgressbar", thickness=25, troughcolor="#2a2a35", background="#007acc")

        # Variables Array
        self.flashing_mode = tk.StringVar(value="Fastboot")
        self.selected_file_path, self.selected_image_type = tk.StringVar(), tk.StringVar()
        self.disable_vbmeta, self.wipe_userdata = tk.BooleanVar(value=False), tk.BooleanVar(value=False)
        self.flash_progress, self.status_label_text = tk.DoubleVar(value=0.0), tk.StringVar(value="SYSTEM READY")

        # Dynamic Maps Configuration
        self.fastboot_partitions = ["boot", "dtbo", "vendor_boot", "init_boot", "vendor_dlkm", "recovery", "system", "vendor", "vbmeta", "product", "odm"]
        self.odin_slots = {s: tk.StringVar() for s in ["PIT", "BL", "AP", "CP", "CSC", "USERDATA"]}

        self.create_widgets()

    def create_widgets(self):
        # Header Brand Banner
        header = tk.Frame(self.root, bg="#0e0e12", height=45)
        header.pack(fill="x", side="top"); header.pack_propagate(False)
        tk.Label(header, text="UNIVERSAL HARDWARE FLASHING UTILITY", bg="#0e0e12", fg="#007acc", font=("Arial", 11, "bold")).pack(side="left", padx=20)
        self.device_status_lbl = tk.Label(header, text="DISCONNECTED", bg="#d9534f", fg="white", font=("Arial", 8, "bold"), padx=10, pady=2)
        self.device_status_lbl.pack(side="right", padx=20)

        body = tk.Frame(self.root, bg="#1e1e24"); body.pack(fill="both", expand=True, padx=20, pady=5)

        # 1. Action Mode Router
        mode_frame = tk.LabelFrame(body, text=" 1. Choose Flashing Mode / Protocol Engine ", bg="#1e1e24", fg="#a0a0ab", font=("Arial", 9, "bold"), bd=1, relief="solid")
        mode_frame.pack(fill="x", pady=4, ipady=4)
        tk.Label(mode_frame, text="Target Protocol:", bg="#1e1e24", fg="#ffffff").pack(side="left", padx=10)
        self.mode_combobox = ttk.Combobox(mode_frame, textvariable=self.flashing_mode, values=["Fastboot", "ADB Sideload", "Download Mode (Odin/Samsung)"], state="readonly", width=28)
        self.mode_combobox.pack(side="left", padx=10); self.mode_combobox.bind("<<ComboboxSelected>>", self.on_mode_change)

        # 2. File Interface (Fastboot/Sideload)
        self.general_file_frame = tk.LabelFrame(body, text=" 2. Local File Image Resource Mapping ", bg="#1e1e24", fg="#a0a0ab", font=("Arial", 9, "bold"), bd=1, relief="solid")
        self.general_file_frame.pack(fill="x", pady=4, ipady=4)
        tk.Entry(self.general_file_frame, textvariable=self.selected_file_path, bg="#2a2a35", fg="#ffffff", insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#3a3a4a").pack(side="left", padx=10, expand=True, fill="x")
        tk.Button(self.general_file_frame, text="Browse Target", bg="#4a4a5a", fg="white", bd=0, padx=12, command=self.browse_general_file).pack(side="right", padx=10)

        # 3. Partition Choice (Fastboot Only)
        self.general_type_frame = tk.Frame(body, bg="#1e1e24"); self.general_type_frame.pack(fill="x", pady=2)
        self.part_lbl = tk.Label(self.general_type_frame, text="Target Partition Block:", bg="#1e1e24", fg="#ffffff")
        self.part_lbl.pack(side="left", padx=10)
        self.type_combobox = ttk.Combobox(self.general_type_frame, textvariable=self.selected_image_type, values=self.fastboot_partitions, state="readonly", width=20)
        self.type_combobox.pack(side="left", padx=5); self.type_combobox.set("boot")

        # 4. LOOP ENGINE COMPRESSION: Auto-builds the entire Samsung Odin Multi-Slot Grid Layout in 6 lines of code!
        self.samsung_odin_frame = tk.LabelFrame(body, text=" 2. Samsung Download Mode Flash Deck ", bg="#1e1e24", fg="#a0a0ab", font=("Arial", 9, "bold"), bd=1, relief="solid")
        for i, slot in enumerate(self.odin_slots.keys()):
            tk.Label(self.samsung_odin_frame, text=f"[{slot}]", font=("Arial", 9, "bold"), bg="#1e1e24", fg="#007acc", width=12, anchor="e").grid(row=i, column=0, padx=5, pady=2, sticky="w")
            tk.Entry(self.samsung_odin_frame, textvariable=self.odin_slots[slot], bg="#2a2a35", fg="#ffffff", insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#3a3a4a").grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            tk.Button(self.samsung_odin_frame, text="Load Binary", bg="#4a4a5a", fg="white", font=("Arial", 8), bd=0, padx=8, command=lambda s=slot: self.browse_odin_slot(s)).grid(row=i, column=2, padx=10, pady=2)
        self.samsung_odin_frame.grid_columnconfigure(1, weight=1)

        # 5. Safety Flags
        self.options_frame = tk.Frame(body, bg="#1e1e24"); self.options_frame.pack(fill="x", pady=4)
        tk.Checkbutton(self.options_frame, text="Disable AVB Verification (--disable-verity)", variable=self.disable_vbmeta, bg="#1e1e24", fg="#ffffff", selectcolor="#1e1e24", activebackground="#1e1e24").pack(anchor="w", padx=5)
        tk.Checkbutton(self.options_frame, text="Automate Wipe Data Allocation Sectors (fastboot -w)", variable=self.wipe_userdata, bg="#1e1e24", fg="#ffffff", selectcolor="#1e1e24", activebackground="#1e1e24").pack(anchor="w", padx=5)

        # 6. Progress Meter Indicator
        progress_container = tk.Frame(body, bg="#2a2a35", bd=1, relief="solid"); progress_container.pack(fill="x", pady=6)
        status_bar = tk.Frame(progress_container, bg="#252530", height=26); status_bar.pack(fill="x", side="top"); status_bar.pack_propagate(False)
        tk.Label(status_bar, textvariable=self.status_label_text, bg="#252530", fg="#00ff00", font=("Consolas", 9, "bold")).pack(side="left", padx=10)
        ttk.Progressbar(progress_container, variable=self.flash_progress, maximum=100, style="Odin.Horizontal.TProgressbar").pack(fill="x", side="bottom")

        # 7. Telemetry Logger Output Window
        log_frame = tk.LabelFrame(body, text=" Hardware Transmission Telemetry ", bg="#1e1e24", fg="#a0a0ab", font=("Arial", 9, "bold"), bd=1, relief="solid"); log_frame.pack(fill="both", expand=True, pady=4)
        self.log_text = tk.Text(log_frame, height=3, bg="#0e0e12", fg="#c0c0c0", font=("Consolas", 9), bd=0, insertbackground="white")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=4); self.log_text.insert("1.0", "System Pipeline Engine Standby...\n"); self.log_text.config(state="disabled")

        # 8. Execution Controls Run Buttons Layout
        btn_frame = tk.Frame(body, bg="#1e1e24"); btn_frame.pack(fill="x", side="bottom", pady=2)
        tk.Button(btn_frame, text="Link Diagnostic", bg="#3a3a4a", fg="white", font=("Arial", 10), bd=0, pady=5, command=self.check_device).pack(side="left", padx=4, expand=True, fill="x")
        tk.Button(btn_frame, text="Power Controls...", bg="#4a4a5a", fg="white", font=("Arial", 10), bd=0, pady=5, command=self.open_power_menu).pack(side="left", padx=4, expand=True, fill="x")
        self.flash_btn = tk.Button(btn_frame, text="START SEQUENCE", bg="#007acc", fg="white", font=("Arial", 10, "bold"), bd=0, pady=5, command=self.start_process)
        self.flash_btn.pack(side="right", padx=4, expand=True, fill="x")

    def log(self, message):
        self.log_text.config(state="normal"); self.log_text.insert("end", message + "\n"); self.log_text.see("end"); self.log_text.config(state="disabled")

    def on_mode_change(self, event):
        mode = self.flashing_mode.get(); self.selected_file_path.set(""); self.flash_progress.set(0.0); self.status_label_text.set("ENGINE MODE UPDATED")
        if mode == "Download Mode (Odin/Samsung)":
            self.general_file_frame.pack_forget(); self.general_type_frame.pack_forget(); self.options_frame.pack_forget(); self.part_lbl.pack_forget(); self.type_combobox.pack_forget()
            self.samsung_odin_frame.pack(fill="x", pady=5, after=self.mode_combobox.master)
            self.log("Switched to Samsung Download Mode Engine.")
        else:
            self.samsung_odin_frame.pack_forget(); self.general_file_frame.pack(fill="x", padx=20, pady=5, after=self.mode_combobox.master); self.general_type_frame.pack(fill="x", pady=2, after=self.general_file_frame)
            self.part_lbl.pack(side="left", padx=10); self.type_combobox.pack(side="left", padx=5); self.options_frame.pack(fill="x", pady=5, after=self.general_type_frame)
            self.type_combobox.config(state="disabled" if mode == "ADB Sideload" else "readonly")
            if mode == "Fastboot": self.type_combobox.set("boot")
            self.log(f"Switched to {mode} Engine.")

    def browse_general_file(self):
        mode = self.flashing_mode.get()
        ftypes = [("Zip Archive", "*.zip")] if mode == "ADB Sideload" else [("Partition Image", "*.img")]
        fp = filedialog.askopenfilename(title="Select File Target", filetypes=ftypes)
        if fp:
            self.selected_file_path.set(fp)
            self.log(f"Loaded target file: {os.path.basename(fp)}")

    def  browse_odin_slot(self, slot_name):
        fp = filedialog.askopenfilename(title=f"Select Binary for {slot_name} Slot", filetypes=[("Samsung Packs", "*.tar *.md5 *.bin *.pit")])
        if fp:
            self.odin_slots[slot_name].set(fp)
            self.log(f"Download Mode: Loaded {os.path.basename(fp)} into [{slot_name}].")

    def is_device_connected(self):
        mode = self.flashing_mode.get()
        try:
            if mode == "ADB Sideload":
                out = subprocess.check_output([resource_path("adb.exe"), "devices"], text=True, creationflags=0x08000000)
                conn = "sideload" in out.lower()
            elif "Download" in mode:
                out = subprocess.check_output([resource_path("heimdall.exe"), "detect"], text=True, creationflags=0x08000000)
                conn = "detected" in out.lower()
            else:
                out = subprocess.check_output([resource_path("fastboot.exe"), "devices"], text=True, creationflags=0x08000000)
                conn = bool(out.strip())
            self.root.after(0, lambda: self.device_status_lbl.config(text="DEVICE CONNECTED" if conn else "DISCONNECTED", bg="#28a745" if conn else "#d9534f"))
            return conn
        except Exception:
            self.root.after(0, lambda: self.device_status_lbl.config(text="DISCONNECTED", bg="#d9534f"))
            return False

    def check_device(self):
        if self.is_device_connected():
            messagebox.showinfo("Success", "Device link handshake verified!")
        else:
            messagebox.showwarning("Warning", "No responsive device interface registered on USB nodes.")

    def open_power_menu(self):
        mode = self.flashing_mode.get()
        popup = tk.Toplevel(self.root)
        popup.title("Power")
        popup.geometry("380x260")
        popup.configure(bg="#2a2a35")
        popup.transient(self.root)
        popup.grab_set()
        
        tk.Label(popup, text="🔌 Hardware State Controls", bg="#2a2a35", fg="#007acc", font=("Arial", 11, "bold")).pack(pady=10)
        
        if "Download" in mode:
            tk.Button(popup, text="🛑 Shutdown / Exit Download Mode", bg="#d9534f", fg="white", font=("Arial", 9, "bold"), bd=0, width=32, pady=8, command=lambda: self.run_power_cmd(mode, "shutdown", popup)).pack(pady=15)
            tk.Button(popup, text="🔄 Reboot Normal to System OS", bg="#3a3a4a", fg="white", font=("Arial", 9), bd=0, width=32, pady=8, command=lambda: self.run_power_cmd(mode, "system", popup)).pack(pady=5)
        else:
            for act, label in [("system", "📱 Reboot to System OS"), ("recovery", "🛠️ Reboot to Recovery Environment"), ("bootloader", "⚡ Reboot to Bootloader (Fastboot)"), ("fastbootd", "⚙️ Reboot to User-Space (Fastbootd)")]:
                tk.Button(popup, text=label, bg="#3a3a4a", fg="white", font=("Arial", 9), bd=0, width=32, pady=5, command=lambda a=act: self.run_power_cmd(mode, a, popup)).pack(pady=3)
            tk.Button(popup, text="🛑 Safe Hardware Shutdown", bg="#d9534f", fg="white", font=("Arial", 9, "bold"), bd=0, width=32, pady=5, command=lambda: self.run_power_cmd(mode, "shutdown", popup)).pack(pady=6)

    def run_power_cmd(self, mode, action, window):
        window.destroy()
        self.status_label_text.set("SENDING POWER COMMAND...")
        adb, fb, heim = resource_path("adb.exe"), resource_path("fastboot.exe"), resource_path("heimdall.exe")
        cmd = []
        
        if mode == "ADB Sideload":
            cmd = [adb, "reboot", "poweroff" if action=="shutdown" else "fastboot" if action=="fastbootd" else action] if action != "system" else [adb, "reboot"]
        elif mode == "Fastboot":
            cmd = [fb, "reboot", "poweroff" if action=="shutdown" else "fastboot" if action=="fastbootd" else action] if action not in ["system", "recovery"] else [fb, "reboot-recovery"] if action=="recovery" else [fb, "reboot"]
        elif "Download" in mode:
            cmd = [heim, "close"]
            
        if cmd:
            try:
                subprocess.run(cmd, capture_output=True, text=True, creationflags=0x08000000, check=True)
                self.status_label_text.set("POWER OPERATION SUCCESSFUL")
            except Exception:
                self.status_label_text.set("POWER COMMAND FAILURE")

    def start_process(self):
        mode = self.flashing_mode.get()
        if mode == "Download Mode (Odin/Samsung)" and not any(v.get().strip() for v in self.odin_slots.values()):
            messagebox.showerror("Error", "Please populate at least one target slot.")
            return
        elif mode != "Download Mode (Odin/Samsung)" and (not self.selected_file_path.get() or not os.path.exists(self.selected_file_path.get())):
            messagebox.showerror("Error", "Please locate a valid workspace target block file.")
            return
            
        if not self.is_device_connected():
            messagebox.showerror("Error", "Handshake validation check failed.")
            return
        if not messagebox.askyesno("Confirm", f"Initiate block flash routine sequence for {mode}?"):
            return
            
        self.flash_btn.config(state="disabled")
        self.flash_progress.set(15.0)
        self.status_label_text.set("TRANSMITTING BINARIES...")
        threading.Thread(target=self.run_background_task, args=(mode,), daemon=True).start()

    def run_background_task(self, mode):
        adb, fb, heim = resource_path("adb.exe"), resource_path("fastboot.exe"), resource_path("heimdall.exe")
        try:
            if mode == "ADB Sideload":
                res = subprocess.run([adb, "sideload", self.selected_file_path.get()], capture_output=True, text=True, creationflags=0x08000000, check=True)
                if res.stdout:
                    self.log(res.stdout.strip())
            elif "Download" in mode:
                cmd = [heim, "flash"]
                p_map = {"PIT": "--PIT", "BL": "--BOOTLOADER", "AP": "--SYSTEM", "CP": "--RADIO", "CSC": "--HIDDEN", "USERDATA": "--USERDATA"}
                for k, v in self.odin_slots.items():
                    if v.get().strip():
                        cmd.extend([p_map[k], v.get().strip()])
                        self.log(f" Enqueued: [{k}] -> {os.path.basename(v.get().strip())}")
                self.flash_progress.set(50.0)
                res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x08000000, check=True)
                if res.stdout:
                    self.log(res.stdout.strip())
            else:
                fp, it = self.selected_file_path.get(), self.selected_image_type.get()
                cmd = [fb, "flash", "--disable-verity", "--disable-verification", "vbmeta", fp] if (it == "vbmeta" and self.disable_vbmeta.get()) else [fb, "flash", it, fp]
                self.flash_progress.set(60.0)
                res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x08000000, check=True)
                if res.stdout:
                    self.log(res.stdout.strip())
                if self.wipe_userdata.get():
                    self.status_label_text.set("FORMATTING DATA SECTORS Gold...")
                    self.flash_progress.set(85.0)
                    subprocess.run([fb, "-w"], creationflags=0x08000000, check=True)
                    
            self.flash_progress.set(100.0)
            self.status_label_text.set("FLASH COMPLETED")
            messagebox.showinfo("Success!", "Flashing sequence executed flawlessly!")
        except Exception:
            self.flash_progress.set(0.0)
            self.status_label_text.set("FLASH ERROR")
            messagebox.showerror("Execution Fault", "Process failure reported errors.")
        self.root.after(0, lambda: self.flash_btn.config(state="normal"))


if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalFlasherApp(root)
    root.mainloop()
