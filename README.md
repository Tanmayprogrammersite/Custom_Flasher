# Universal Android Flasher & Sideloader

A lightweight, standalone desktop utility to easily flash partition images (.img) and sideload custom ROM packages (.zip) via ADB and Fastboot without touching the command line. Perfect for flashing PixelOS, LineageOS, EvolutionX, or any other custom firmware!

## ⚠️ Disclaimer & Warning
> **YOUR WARRANTY IS NOW VOID.**
> 
> I am not responsible for bricked devices, dead SD cards, thermonuclear war, or you getting fired because the alarm app failed. Please do some research if you have any concerns about features included in this tool before flashing it! 
> 
> You choose to make these modifications yourself. If you select the **wrong partition image type** or flash a corrupt file and brick your device, **I am not responsible**. Proceed entirely at your own risk.

## ⚡ Key Features
- **Fastboot Mode**: Manually assign and flash `.img` files (`boot`, `dtbo`, `vendor_boot`, `vendor_dlkm`, `recovery`, `system`, etc.).
- **ADB Sideload Mode**: Safely sideload `.zip` ROM packages or OTA updates directly through Recovery.
- **Embedded Dependencies**: Includes built-in Google platform-tools (`adb` and `fastboot`). Runs perfectly out-of-the-box on any Windows PC with no manual driver environment setup required.
- **Asynchronous Safe Threading**: Prevents application crashes and GUI window freezes if a device gets accidentally disconnected mid-flash.

## 🚀 How to Download & Run
1. Head over to the **[Releases](https://github.com)** section.
2. Download the latest **`universal_flasher.exe`** file.
3. Move the tool anywhere on your PC (e.g., Desktop).
4. Double-click to run!

## 📲 Usage Guide

### 1. Fastboot Mode (Flashing Images)
- Boot your phone into **Bootloader/Fastboot Mode**.
- Set the app dropdown mode selection to **Fastboot**.
- Click **Browse...**, pick your target `.img` file.
- Select the matching target partition from the menu drop list.
- Click **Check Connection Status** to ensure your drivers are active, then click **Execute Process**.

### 2. ADB Sideload Mode (Flashing ROM Zips)
- Boot your phone into your custom **Recovery Mode**.
- Go to **Advanced** / **Apply Update** and select **Apply update from ADB (Sideload)**.
- Set the app dropdown mode selection to **ADB Sideload**.
- Click **Browse...** (the explorer filter will filter strictly for `.zip` files). Pick your ROM zip.
- Click **Execute Process** and monitor your phone's screen status.
