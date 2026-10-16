// Options.js - Power & State Command Router Component

const FlasherHardwareBridge = {
    // Sockets to route actions to the Python backend process core
    sendTargetState: function(engineMode, targetAction) {
        console.log(`📡 Sending Action payload: Mode [${engineMode}] -> Command [${targetAction}]`);
        // Native framework handle invocation hook (e.g., QWebChannel or PyWebView)
        if (window.pyWebView && window.pyWebView.api) {
            window.pyWebView.api.executePowerState(engineMode, targetAction);
        }
    }
};

const DevicePowerSuite = {
    activeEngineMode: "Fastboot", // Context shifts dynamically per device state

    // 1. Initial layer button click logic
    handleRebootMenuClick: function() {
        this.renderContextualModalDeck();
    },

    // 2. Build and display the dynamic nested UI options panel
    renderContextualModalDeck: function() {
        console.log("🎨 Opening UI layout panel for Engine Mode: " + this.activeEngineMode);
        
        // Context UI mapping dependent on current connected socket type
        if (this.activeEngineMode === "Odin Mode (Samsung)") {
            this.showOdinSpecificDeck();
        } else {
            this.showStandardAndroidDeck();
        }
    },

    showStandardAndroidDeck: function() {
        // UI Mockup definition for viewers' action cards
        const choices = {
            title: "🔌 Choose Device Power Action",
            options: [
                { label: "🛑 Safe Shutdown", action: "shutdown" },
                { 
                    label: "🔄 System Reboot...", 
                    action: "reboot_menu",
                    subModes: [
                        { label: "📱 Reboot to System OS", target: "system" },
                        { label: "🛠️ Reboot to Recovery Mode", target: "recovery" },
                        { label: "⚡ Reboot to Bootloader (Fastboot)", target: "bootloader" },
                        { label: "⚙️ Reboot to Fastbootd (User Space)", target: "fastbootd" }
                    ]
                }
            ]
        };
        this.paintInterfaceToCanvas(choices);
    },

    showOdinSpecificDeck: function() {
        const choices = {
            title: "🔌 Samsung Odin Mode Power Options",
            options: [
                { label: "🛑 Safe Shutdown (Exit Download Mode)", action: "shutdown" },
                { label: "🔄 Normal Reboot to System", action: "reboot_system" }
            ]
        };
        this.paintInterfaceToCanvas(choices);
    },

    paintInterfaceToCanvas: function(data) {
        // Renders visual HTML template containers over the active frame
        // Triggered selection calls: FlasherHardwareBridge.sendTargetState(this.activeEngineMode, choice)
    }
};
