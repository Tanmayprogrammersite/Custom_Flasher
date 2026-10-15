python
import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- CRITICAL FIX FOR WINDOWS EXECUTABLE LAUNCH CRASHES ---
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller/auto-py-to-exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

os.environ["PATH"] = resource_path(".") + os.path.pathsep + os.environ["PATH"]


class UniversalFlasherApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Universal Android Flasher & Sideload Suite")
        self.root.geometry("640x630")
        self.root.configure(bg="#1e1e24")  # Modern Dark Slate Background
        self.root.resizable(False, False)

        # Apply Modern Styling to Notebook Tabs and Dropdowns
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#1e1e24", foreground="#ffffff", fieldbackground="#2a2a35")
        self.style.configure("TCombobox", fieldbackground="#2a2a35", background="#3a3a4a", foreground="#ffffff", arrowcolor="#ffffff")
        self.style.configure("Odin.Horizontal.TProgressbar", thickness=25, troughcolor="#2a2a35", background="#007acc")

        # Variables for Flashing Engine Mode Selection
        self.flashing_mode = tk.StringVar(value="Fastboot")
        
        # Fastboot & Sideload Path Targets
        self.selected_file_path = tk.StringVar()
        self.selected_image_type = tk.StringVar()

        # Advanced Formatting & Security Checkboxes (Fastboot Only)
        self.disable_vbmeta = tk.BooleanVar(value=False)
        self.wipe_userdata = tk.BooleanVar(value=False)

        # Live Flashing Progress Trackers (Odin Style Progress Bar)
        self.flash_progress = tk.DoubleVar(value=0.0)
        self.status_label_text = tk.StringVar(value="SYSTEM READY")

        # --- SAMSUNG DOWNLOAD MODE MULTI-SLOT VARIABLES ---
        self.odin_slots = {
            "PIT": tk.StringVar(), "BL": tk.StringVar(), "AP": tk.StringVar(),
            "CP": tk.StringVar(), "CSC": tk.StringVar(), "USERDATA": tk.StringVar()
        }

        self.fastboot_partitions = ["boot", "dtbo", "vendor_boot", "init_boot", "vendor_dlkm", "recovery", "system", "vendor", "vbmeta", "product", "odm"]

        self.create_widgets()

    def create_widgets(self):
        # Header Application Brand Bar
        header_frame = tk.Frame(self.root, bg="#0e0e12", height=50)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        title_lbl = tk.Label(header_frame, text="UNIVERSAL HARDWARE FLASHING UTILITY", bg="#0e0e12", fg="#007acc", font=("Arial", 12, "bold"))
        title_lbl.pack(side="left", padx=20)
        
        self.device_status_lbl = tk.Label(header_frame, text="DISCONNECTED", bg="#d9534f", fg="white", font=("Arial", 9, "bold"), padx=10, pady=2)
        self.device_status_lbl.pack(side="right", padx=20)

        # Main Body Workspace Margin Container
        body = tk.Frame(self.root, bg="#1e1e24")
        body.pack(fill="both", expand=True, padx=20, pady=10)

        # ==========================================
        # 🛠️ FRAME A: ACTION MODE ROUTER
        # ==========================================
        mode_frame = tk.LabelFrame(body, text=" 1. Choose Flashing Mode / Protocol Engine ", bg="#1e1e24", fg="#a0a0ab", font=("Arial", 9, "bold"), bd=1, relief="solid")
        mode_frame.pack(fill="x", pady=5, ipady=5)

        tk.Label(mode_frame, text="Target Protocol:", bg="#1e1e24", fg="#ffffff").pack(side="left", padx=10)
        self.mode_combobox = ttk.Combobox(mode_frame, textvariable=self.flashing_mode, values=["Fastboot", "ADB Sideload", "Download Mode (Odin/Samsung)"], state="readonly", width=28)
        self.mode_combobox.pack(side="left", padx=10)
        self.mode_combobox.bind("<<ComboboxSelected>>", self.on_mode_change)

        # ==========================================
        # 📂 FRAME B: FILE INTERFACE (FASTBOOT/SIDELOAD)
        # ==========================================
        self.general_file_frame = tk.LabelFrame(body, text=" 2. Local File Image Resource Mapping ", bg="#1e1e24", fg="#a0a0ab", font=("Arial", 9, "bold"), bd=1, relief="solid")
        self.general_file_frame.pack(fill="x", pady=5, ipady=5)

        self.file_entry = tk.Entry(self.general_file_frame, textvariable=self.selected_file_path, bg="#2a2a35", fg="#ffffff", insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#3a3a4a")
        self.file_entry.pack(side="left", padx=10, expand=True, fill="x")

        browse_btn = tk.Button(self.general_file_frame, text="Browse Target", bg="#4a4a5a", fg="white", bd=0, padx=12, command=self.browse_general_file)
        browse_btn.pack(side="right", padx=10)

        # ==========================================
        # ⚙️ FRAME C: PARTITION CHOICE (FASTBOOT ONLY)
        # ==========================================
        self.general_type_frame = tk.Frame(body, bg="#1e1e24")
        self.general_type_frame.pack(fill="x", pady=2)
        
        self.part_lbl = tk.Label(self.general_type_frame, text="Target Partition Block:", bg="#1e1e24", fg="#ffffff")
        self.part_lbl.pack(side="left", padx=10)
        self.type_combobox = ttk.Combobox(self.general_type_frame, textvariable=self.selected_image_type, values=self.fastboot_partitions, state="readonly", width=20)
        self.type_combobox.pack(side="left", padx=5)
        self.type_combobox.set("boot")

        # ==========================================
        # 📱 FRAME D: SAMSUNG DOWNLOAD MODE CONFIGURATION PANEL
        # ==========================================
        self.samsung_odin_frame = tk.LabelFrame(body, text=" 2. Samsung Download Mode Flash Deck ", bg="#1e1e24", fg="#a0a0ab", font=("Arial", 9, "bold"), bd=1, relief="solid")
        
        for i, slot_name in enumerate(["PIT", "BL", "AP", "CP", "CSC", "USERDATA"]):
            lbl = tk.Label(self.samsung_odin_frame, text=f"[{slot_name}]", font=("Arial", 9, "bold"), bg="#1e1e24", fg="#007acc", width=12, anchor="e")
            lbl.grid(row=i, column=0, padx=5, pady=3, sticky="w")
            
            entry = tk.Entry(self.samsung_odin_frame, textvariable=self.odin_slots[slot_name], bg="#2a2a35", fg="#ffffff", insertbackground="white", bd=0, highlightthickness=1, highlightbackground="#3a3a4a")
            entry.grid(row=i, column=1, padx=5, pady=3, sticky="ew")
            
            btn = tk.Button(self.samsung_odin_frame, text="Load Binary", bg="#4a4a5a", fg="white", font=("Arial", 8), bd=0, padx=8, pady=1, command=lambda s=slot_name: self.browse_odin_slot(s))
            btn.grid(row=i, column=2, padx=10, pady=3)
            
        self.samsung_odin_frame.grid_columnconfigure(1, weight=1)

        # ==========================================
        # ⚠️ FRAME E: SAFETY FLAGS (FASTBOOT ONLY)
        # ==========================================
        self.options_frame = tk.Frame(body, bg="#1e1e24")
        self.options_frame.pack(fill="x", pady=5)

        self.vbmeta_check = tk.Checkbutton(self.options_frame, text="Disable AVB Verification (--disable-verity)", variable=self.disable_vbmeta, bg="#1e1e24", fg="#ffffff", selectcolor="#1e1e24", activebackground="#1e1e24", activeforeground="white")
        self.vbmeta_check.pack(anchor="w", padx=5)

        self.userdata_check = tk.Checkbutton(self.options_frame, text="Automate Wipe Data Allocation Sectors (fastboot -w / Factory Format)", variable=self.wipe_userdata, bg="#1e1e24", fg="#ffffff", selectcolor="#1e1e24", activebackground="#1e1e24", activeforeground="white")
        self.userdata_check.pack(anchor="w", padx=5)

        # ==========================================
        # 🟦 ODIN HIGH-CONTRAST METER
        # ==========================================
        progress_container = tk.Frame(body, bg="#2a2a35", bd=1, relief="solid")
        progress_container.pack(fill="x", pady=10)

        status_bar = tk.Frame(progress_container, bg="#252530", height=30)
        status_bar.pack(fill="x", side="top")
        status_bar.pack_propagate(False)

        status_lbl = tk.Label(status_bar, textvariable=self.status_label_text, bg="#252530", fg="#00ff00", font=("Consolas", 10, "bold"))
        status_lbl.pack(side="left", padx=10)

        self.odin_progress = ttk.Progressbar(progress_container, variable=self.flash_progress, maximum=100, style="Odin.Horizontal.TProgressbar")
        self.odin_progress.pack(fill="x", side="bottom")

        # ==========================================
        # 🖥️ FRAME F: TELEMETRY CONSOLE LOGS
        # ==========================================
        log_frame = tk.LabelFrame(body, text=" Hardware Transmission Telemetry ", bg="#1e1e24", fg="#a0a0ab", font=("Arial", 9, "bold"), bd=1, relief="solid")
        log_frame.pack(fill="both", expand=True, pady=5)

        self.log_text = tk.Text(log_frame, height=4, bg="#0e0e12", fg="#c0c0c0", font=("Consolas", 9), bd=0, insertbackground="white")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_text.insert("1.0", "System Pipeline Engine Standby...\n")
        self.log_text.config(state="disabled")

        # ==========================================
        # 🚀 ENGINE RUN CONTROL SUBMIT PIPELINES
        # ==========================================
        btn_frame = tk.Frame(body, bg="#1e1e24")
        btn_frame.pack(fill="x", side="bottom", pady=5)

Use code with caution.
check_btn = tk.Button(btn_frame, text="Verify Physical Link Status", bg="#3a3a4a", fg="white", font=("Arial", 10), bd=0, pady=6, cursor="hand2", activebackground="#2a2a35", activeforeground="white", command=self.check_device)
check_btn.pack(side="left", padx=5, expand=True, fill="x")
self.flash_btn = tk.Button(btn_frame, text="START SEQUENCE", bg="#007acc", fg="white", font=("Arial", 10, "bold"), bd=0, pady=6, cursor="hand2", activebackground="#0062a3", activeforeground="white", command=self.start_process)
self.flash_btn.pack(side="right", padx=5, expand=True, fill="x")
def log(self, message):
self.log_text.config(state="normal")
self.log_text.insert("end", message + "\n")
self.log_text.see("end")
self.log_text.config(state="disabled")
# ==========================================
# 🔄 UI ROUTER MECHANICS
# ==========================================
def on_mode_change(self, event):
mode = self.flashing_mode.get()
self.selected_file_path.set("")
self.flash_progress.set(0.0)
self.status_label_text.set("ENGINE MODE UPDATED")
if mode == "Download Mode (Odin/Samsung)":
self.general_file_frame.pack_forget()
self.general_type_frame.pack_forget()
self.options_frame.pack_forget()
self.part_lbl.pack_forget()
self.type_combobox.pack_forget()
self.samsung_odin_frame.pack(fill="x", pady=5, after=self.mode_combobox.master)
self.log("Switched to Samsung Download Mode Engine. Load target firmware binaries.")
else:
self.samsung_odin_frame.pack_forget()
self.general_file_frame.pack(fill="x", padx=20, pady=5, after=self.mode_combobox.master)
self.general_type_frame.pack(fill="x", pady=2, after=self.general_file_frame)
self.part_lbl.pack(side="left", padx=10)
self.type_combobox.pack(side="left", padx=5)
self.options_frame.pack(fill="x", pady=5, after=self.general_type_frame)
if mode == "ADB Sideload":
self.type_combobox.config(state="disabled")
self.vbmeta_check.config(state="disabled")
self.userdata_check.config(state="disabled")
self.log("Switched to ADB Sideload mode. Strict Filter: Only .zip files allowed.")
else:
self.type_combobox.config(state="readonly")
self.type_combobox.set("boot")
self.vbmeta_check.config(state="normal")
self.userdata_check.config(state="normal")
self.log("Switched to Fastboot Flash Engine. Strict Filter: Only .img file formats.")
def browse_general_file(self):
mode = self.flashing_mode.get()
ftypes = [("Zip Archive", ".zip")] if mode == "ADB Sideload" else [("Partition Image", ".img")]
title = "Select Sideload ROM Package (.zip)" if mode == "ADB Sideload" else "Select Fastboot Image Target (.img)"
file_path = filedialog.askopenfilename(title=title, filetypes=ftypes)
if file_path:
self.selected_file_path.set(file_path)
basename_lower = os.path.basename(file_path).lower()
self.log(f"Selected file asset: {os.path.basename(file_path)}")
if mode == "Fastboot" and "vbmeta" in basename_lower:
self.type_combobox.set("vbmeta")
self.disable_vbmeta.set(True)
self.log("💡 Visual Hint: Detected vbmeta image. AVB verification bypass auto-selected.")
def browse_odin_slot(self, slot_name):
ftypes = [("Samsung Binary Pack", "*.tar *.md5 *.bin *.pit")]
file_path = filedialog.askopenfilename(title=f"Select Binary for {slot_name} Slot", filetypes=ftypes)
if file_path:
self.odin_slots[slot_name].set(file_path)
basename_lower = os.path.basename(file_path).lower()
self.log(f"Download Mode: Loaded {os.path.basename(file_path)} directly into [{slot_name}].")
if slot_name == "USERDATA" and "userdata" in basename_lower:
self.log("💡 Visual Hint: Detected Samsung USERDATA/Disabled Vbmeta package asset.")
# ==========================================
# 🔍 DEVICE DETECTION LOGIC
# ==========================================
def is_device_connected(self):
mode = self.flashing_mode.get()
try:
adb_bin = resource_path("adb.exe")
fastboot_bin = resource_path("fastboot.exe")
heimdall_bin = resource_path("heimdall.exe")
if mode == "ADB Sideload":
out = subprocess.check_output([adb_bin, "devices"], text=True, creationflags=0x08000000)
connected = "sideload" in out.lower()
elif mode == "Download Mode (Odin/Samsung)":
out = subprocess.check_output([heimdall_bin, "detect"], text=True, creationflags=0x08000000)
connected = "detected" in out.lower()
else:
out = subprocess.check_output([fastboot_bin, "devices"], text=True, creationflags=0x08000000)
connected = bool(out.strip())
self.root.after(0, lambda: self.update_status_header(connected))
return connected
except Exception:
self.root.after(0, lambda: self.update_status_header(False))
return False
def update_status_header(self, connected):
if connected:
self.device_status_lbl.config(text="DEVICE CONNECTED", bg="#28a745")
else:
self.device_status_lbl.config(text="DISCONNECTED", bg="#d9534f")
def check_device(self):
mode = self.flashing_mode.get()
if self.is_device_connected():
self.log(f"Verification Check: Device active under '{mode}' engine pipelines.")
messagebox.showinfo("Success", f"Device handshake active under {mode} criteria!")
else:
self.log(f"Verification Check: Failed to verify status criteria for configuration mode: {mode}")
messagebox.showwarning("Warning", "No active smartphone hardware interface caught on USB nodes.")
# ==========================================
# ⚡ ENGINE FLASHING PIPELINES (THREADED)
# ==========================================
def start_process(self):
mode = self.flashing_mode.get()
if mode == "Download Mode (Odin/Samsung)":
active_slots = [s for s, var in self.odin_slots.items() if var.get().strip()]
if not active_slots:
messagebox.showerror("Error", "Download Mode Error: Please populate at least one target slot path.")
return
else:
file_path = self.selected_file_path.get()
if not file_path or not os.path.exists(file_path):
messagebox.showerror("Error", "Please locate a valid workspace target block asset first.")
return
if not self.is_device_connected():
messagebox.showerror("Error", "Execution Halted: Active device connection state validation failed.")
return
warning_msg = f"Execute {mode} write string lines for package setup?"
if mode == "Fastboot" and self.wipe_userdata.get():
warning_msg += "\n\n⚠️ WARNING: 'Wipe Userdata' is checked! This will completely format the phone's internal storage!"
if not messagebox.askyesno("Confirm Project Sequence", warning_msg):
return
self.flash_btn.config(state="disabled")
self.flash_progress.set(15.0)
self.status_label_text.set("TRANSMITTING HARDWARE BINARIES...")
threading.Thread(target=self.run_background_task, args=(mode,), daemon=True).start()
def run_background_task(self, mode):
adb_bin = resource_path("adb.exe")
fastboot_bin = resource_path("fastboot.exe")
heimdall_bin = resource_path("heimdall.exe")
try:
if mode == "ADB Sideload":
file_path = self.selected_file_path.get()
filename = os.path.basename(file_path)
self.log(f"🚀 Running command pipeline: adb sideload {filename}")
cmd = [adb_bin, "sideload", file_path]
res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x08000000, check=True)
if res.stdout: self.log(res.stdout.strip())
elif mode == "Download Mode (Odin/Samsung)":
self.log("⚡ Compiling Samsung multi-slot target profile command arguments...")
cmd = [heimdall_bin, "flash"]
partition_map = {"PIT": "--PIT", "BL": "--BOOTLOADER", "AP": "--SYSTEM", "CP": "--RADIO", "CSC": "--HIDDEN", "USERDATA": "--USERDATA"}
for slot_name, var in self.odin_slots.items():
slot_path = var.get().strip()
if slot_path and os.path.exists(slot_path):
cmd.append(partition_map[slot_name])
cmd.append(slot_path)
self.log(f"   -> Enqueued: [{slot_name}] linked to {os.path.basename(slot_path)}")
self.flash_progress.set(50.0)
self.log(f"🚀 Launching Heimdall Flash Core Sequence: {' '.join(cmd)}")
res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x08000000, check=True)
if res.stdout: self.log(res.stdout.strip())
else:
# FASTBOOT MODE COMMAND CHAINING
file_path = self.selected_file_path.get()
filename = os.path.basename(file_path)
img_type = self.selected_image_type.get()
if img_type == "vbmeta" and self.disable_vbmeta.get():
self.log(f"⚡ Running Command: fastboot flash --disable-verity --disable-verification vbmeta {filename}")
cmd = [fastboot_bin, "flash", "--disable-verity", "--disable-verification", "vbmeta", file_path]
else:
self.log(f"⚡ Running Command: fastboot flash {img_type} {filename}")
cmd = [fastboot_bin, "flash", img_type, file_path]
self.flash_progress.set(60.0)
res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x08000000, check=True)
if res.stdout: self.log(res.stdout.strip())
if self.wipe_userdata.get():
self.status_label_text.set("FORMATTING USERDATA STORAGE SECTORS...")
self.flash_progress.set(85.0)
self.log("🧹 Formatting storage sectors: fastboot -w...")
wipe_cmd = [fastboot_bin, "-w"]
wipe_res = subprocess.run(wipe_cmd, capture_output=True, text=True, creationflags=0x08000000, check=True)
if wipe_res.stdout: self.log(wipe_res.stdout.strip())
self.flash_progress.set(100.0)
self.status_label_text.set("FLASH COMPLETED SUCCESSFULLY")
self.log("🟢 Success: Flash block sequence operations executed cleanly!")
self.root.after(0, lambda: messagebox.showinfo("Success!", "Flashing sequence executed flawlessly!"))
except subprocess.CalledProcessError as e:
self.flash_progress.set(0.0)
self.status_label_text.set("CRITICAL HARDWARE FLASH ERROR")
self.log(f"🔴 Critical Operation Error Encountered!")
if e.stderr: self.log(f"Execution diagnostic logs:\n{e.stderr.strip()}")
self.root.after(0, lambda: messagebox.showerror("Execution Fault", f"Process failure reported errors:\n\n{e.stderr}"))
self.root.after(0, lambda: self.flash_btn.config(state="normal"))
if name == "main":
root = tk.Tk()
app = UniversalFlasherApp(root)
root.mainloop()