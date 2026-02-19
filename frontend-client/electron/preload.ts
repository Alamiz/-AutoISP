const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    minimize: () => ipcRenderer.send('window:minimize'),
    maximize: () => ipcRenderer.send('window:maximize'),
    close: () => ipcRenderer.send('window:close'),
    resize: (width: number, height: number) => ipcRenderer.send('window:resize', width, height),

    // Listen for maximize/unmaximize events
    onMaximize: (callback: () => void) => {
        ipcRenderer.on('window-maximized', callback);
    },
    onUnmaximize: (callback: () => void) => {
        ipcRenderer.on('window-unmaximized', callback);
    },

    // Cleanup listeners (optional but recommended)
    removeMaximizeListener: (callback: () => void) => {
        ipcRenderer.removeListener('window-maximized', callback);
    },
    removeUnmaximizeListener: (callback: () => void) => {
        ipcRenderer.removeListener('window-unmaximized', callback);
    },
    openDevTools: () => ipcRenderer.send('window:open-devtools'),

    // Log panel detachment
    detachLogPanel: () => ipcRenderer.send('log-panel:detach'),
    onLogPanelAttached: (callback: () => void) => {
        ipcRenderer.on('log-panel:attached', callback);
    },
    removeLogPanelAttachedListener: (callback: () => void) => {
        ipcRenderer.removeListener('log-panel:attached', callback);
    },
});

// Auto-updater API
contextBridge.exposeInMainWorld('updater', {
    checkForUpdates: () => ipcRenderer.invoke('update:check'),
    downloadUpdate: () => ipcRenderer.invoke('update:download'),
    installUpdate: () => ipcRenderer.invoke('update:install'),
    onUpdateEvent: (callback: (event: any) => void) => {
        const handler = (_ipcEvent: any, payload: any) => callback(payload);
        ipcRenderer.on('update:event', handler);
        // Return unsubscribe function
        return () => {
            ipcRenderer.removeListener('update:event', handler);
        };
    },
});