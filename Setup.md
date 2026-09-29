# 🛠️ Step-by-Step Guide: Setting Up ADB & Fastboot Drivers

For your computer to talk to your phone in Fastboot or Sideload mode, your Windows system needs the proper Google USB drivers installed. Follow this quick guide to get connected in less than 5 minutes!

---

## 💾 Step 1: Download Google Platform-Tools & Drivers
1. **Download the Platform-Tools Zip:** 
   Go to the official Google Android Developer site and download the latest version of [SDK Platform-Tools for Windows](https://android.com).
2. **Download the USB Drivers:** 
   Download the official [Google USB Driver Zip](https://android.com).
3. **Extract the Files:** 
   Right-click both downloaded `.zip` folders and extract them somewhere safe on your computer (for example: `C:\platform-tools`).

---

## ⚙️ Step 2: Add Fastboot to your System PATH (Crucial Step)
Adding the folder to your system environment path lets Windows run fastboot commands from anywhere on your PC, ensuring the flasher tool works perfectly.

1. Press the **Windows Key**, type **"Environment Variables"**, and hit Enter.
2. Click the **"Environment Variables..."** button at the bottom right.
3. In the bottom box labeled *System variables*, scroll down, click on **`Path`**, and click **Edit...**.
4. Click the **New** button on the right side.
5. Paste the exact folder path where you extracted the tools (e.g., `C:\platform-tools`) and click **OK** on all windows to save the changes.

---

## 🔌 Step 3: Install the Device Drivers via Device Manager
If the flasher tool says "No device found", your computer is missing the hardware link. Let's fix it:

1. Boot your phone into **Fastboot Mode** (Hold *Volume Down + Power* while turning it on) and plug it into your PC.
2. Right-click the Windows Start Button and select **Device Manager**.
3. Look through the list:
   * If you see **"Android Device"** with a yellow warning triangle, or **"Other Devices -> Android"**, your drivers are missing.
4. Right-click on that item and select **Update driver**.
5. Choose **"Browse my computer for drivers"**, click **Browse...**, select the folder where you extracted the **Google USB Driver** zip in Step 1, and make sure *"Include subfolders"* is checked.
6. Click **Next** and accept any security popups to install the driver.

---

## ✅ Step 4: Verify the Connection
Open a standard **PowerShell** or **Command Prompt** window and test the connection:

* **For Fastboot Mode:** Type `fastboot devices` and press Enter.
* **For ADB Sideload Mode:** Type `adb devices` and press Enter.

If you see your phone's serial number appear in the terminal text layout, **SUCCESS!** Your environment setup is completely done, and you are ready to use the Universal Android Flasher tool to install your custom ROMs!
