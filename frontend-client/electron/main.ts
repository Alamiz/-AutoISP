import { app, Menu, BrowserWindow, ipcMain, dialog } from 'electron';
import * as path from 'path';
import { spawn, ChildProcess } from 'child_process';
import kill from 'tree-kill';
import log from 'electron-log';
import net from 'net';
import { autoUpdater } from 'electron-updater';

let mainWindow: BrowserWindow | null;
let loadingWindow: BrowserWindow | null;
let logWindow: BrowserWindow | null = null;
let pythonProcess: ChildProcess | null = null;

const isDev = process.env.NODE_ENV === 'development';

import serve from 'electron-serve';

const serveURL = serve({ directory: path.join(__dirname, '../../out') });

function createWindow() {
    if (loadingWindow)
        loadingWindow.close();

    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
        },
        frame: false,
        icon: path.join(__dirname, '../../public/logo.png')
    });

    if (isDev) {
        mainWindow.loadURL('http://localhost:3000');
        mainWindow.webContents.openDevTools();
    } else {
        serveURL(mainWindow);
    }

    Menu.setApplicationMenu(null);

    mainWindow.on('maximize', () => {
        mainWindow?.webContents.send('window-maximized');
    });

    mainWindow.on('unmaximize', () => {
        mainWindow?.webContents.send('window-unmaximized');
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    mainWindow.webContents.on('before-input-event', (event, input) => {
        if (input.type === 'keyDown') {
            if (input.key === 'F12') {
                mainWindow?.webContents.toggleDevTools();
                event.preventDefault();
            } else if (input.control && input.shift && input.key.toLowerCase() === 'i') {
                mainWindow?.webContents.toggleDevTools();
                event.preventDefault();
            }
        }
    });
}

function createLoadingWindow() {
    loadingWindow = new BrowserWindow({
        width: 500,
        height: 450,
        frame: false
    });

    Menu.setApplicationMenu(null);
    loadingWindow.loadFile(path.join(__dirname, "../loading.html"));
}

function createLogWindow() {
    if (logWindow) {
        logWindow.focus();
        return;
    }

    logWindow = new BrowserWindow({
        width: 600,
        height: 900,
        minWidth: 600,
        minHeight: 500,
        // No parent - independent window for separate taskbar entry
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
        },
        frame: false,
        title: 'Live Activity Log',
        skipTaskbar: false, // Ensure it shows in taskbar
    });

    if (isDev) {
        logWindow.loadURL('http://localhost:3000/logs');
    } else {
        logWindow.loadFile(path.join(__dirname, '../../out/logs.html'));
    }

    logWindow.on('closed', () => {
        logWindow = null;
        // Notify main window that log panel should be shown again
        if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.webContents.send('log-panel:attached');
        }
    });
}

function startPythonBackend() {
    let pythonExecutable: string;
    let apiScript: string[];
    let backendPath: string;

    if (app.isPackaged) {
        // In production, the backend is an executable in resources/backend/api.exe
        const executablePath = path.join(process.resourcesPath, 'backend', 'api.exe');
        pythonExecutable = executablePath;
        apiScript = []; // No script argument needed for compiled exe
        backendPath = path.dirname(executablePath);
        console.log(`Starting Production Backend: ${executablePath}`);
    } else {
        // In development
        backendPath = path.join(__dirname, '../../../light-engine');
        pythonExecutable = path.join(backendPath, 'venv', 'Scripts', 'python.exe');
        const scriptPath = path.join(backendPath, 'api.py');
        apiScript = [scriptPath];
        console.log(`Starting Development Backend: ${pythonExecutable} ${scriptPath}`);
    }

    pythonProcess = spawn(pythonExecutable, apiScript, {
        cwd: backendPath,
        stdio: 'pipe', // Change to pipe to capture logs
        env: {
            ...process.env,
            PYTHONIOENCODING: 'utf-8',
            PYTHONLEGACYWINDOWSSTDIO: 'utf-8',
        }
    });

    if (pythonProcess.stdout) {
        pythonProcess.stdout.on('data', (data) => {
            log.info(`[Backend STDOUT]: ${data.toString()}`);
        });
    }

    if (pythonProcess.stderr) {
        pythonProcess.stderr.on('data', (data) => {
            log.error(`[Backend STDERR]: ${data.toString()}`);
        });
    }

    pythonProcess.on('error', (err) => {
        log.error('Failed to start Python backend:', err);
    });

    pythonProcess.on('exit', (code, signal) => {
        log.warn(`Python backend exited with code ${code} and signal ${signal}`);
        if (code !== 0 && code !== null) {
            log.error(`Backend crashed with exit code ${code}. Check logs at: ${log.transports.file.getFile().path}`);
        }
    });
}

function killPythonBackend() {
    if (pythonProcess && pythonProcess.pid) {
        const pid = pythonProcess.pid;
        console.log(`Killing Python backend (PID: ${pid})...`);

        try {
            // On Windows, use taskkill with /F (force) and /T (terminate child processes)
            if (process.platform === 'win32') {
                const { execSync } = require('child_process');
                execSync(`taskkill /F /T /PID ${pid}`, { stdio: 'ignore' });
                log.info(`Python backend process (PID: ${pid}) killed via taskkill`);
            } else {
                // On Unix, use tree-kill
                kill(pid, 'SIGKILL', (err) => {
                    if (err) log.error("Failed to kill Python backend process:", err);
                    else log.info("Python backend process killed!");
                });
            }
        } catch (error) {
            // taskkill might fail if process already dead, which is fine
            log.warn(`taskkill error (process may already be dead):`, error);
        }

        pythonProcess = null;
    }
}

function waitForBackend(port: number, host = "127.0.0.1", retries = 60, delay = 1000) {
    return new Promise<void>((resolve, reject) => {
        let attempts = 0;

        const check = () => {
            const socket = net.connect(port, host, () => {
                socket.end();
                log.info(`Backend is ready after ${attempts + 1} attempt(s)`);
                resolve();
            });

            socket.on("error", () => {
                attempts++;
                if (attempts % 10 === 0) {
                    log.info(`Waiting for backend... attempt ${attempts}/${retries}`);
                }
                if (attempts < retries) {
                    setTimeout(check, delay);
                } else {
                    reject(new Error(`Backend did not start after ${retries} attempts (${retries * delay / 1000}s)`));
                }
            });
        };

        check();
    });
}

// ─── Auto-Updater Configuration ────────────────────────────────────────────
autoUpdater.autoDownload = false;
autoUpdater.autoInstallOnAppQuit = true;
autoUpdater.logger = log;

let isCheckingForUpdate = false;

function sendUpdateEvent(payload: Record<string, unknown>) {
    if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('update:event', payload);
    }
}

// Forward updater events to renderer
autoUpdater.on('checking-for-update', () => {
    sendUpdateEvent({ type: 'checking' });
});

autoUpdater.on('update-available', (info) => {
    isCheckingForUpdate = false;
    sendUpdateEvent({ type: 'available', version: info.version });
});

autoUpdater.on('update-not-available', (_info) => {
    isCheckingForUpdate = false;
    sendUpdateEvent({ type: 'not-available' });
});

autoUpdater.on('download-progress', (progress) => {
    sendUpdateEvent({
        type: 'progress',
        percent: progress.percent,
        bytesPerSecond: progress.bytesPerSecond,
        transferred: progress.transferred,
        total: progress.total,
    });
});

autoUpdater.on('update-downloaded', (info) => {
    isCheckingForUpdate = false;
    sendUpdateEvent({ type: 'downloaded', version: info.version });
});

autoUpdater.on('error', (err) => {
    isCheckingForUpdate = false;
    log.error('Auto-updater error:', err);
    sendUpdateEvent({ type: 'error', message: err?.message || 'Unknown update error' });
});

// IPC handlers for renderer
ipcMain.handle('update:check', async () => {
    if (isCheckingForUpdate) return;
    isCheckingForUpdate = true;
    try {
        await autoUpdater.checkForUpdates();
    } catch (err) {
        isCheckingForUpdate = false;
        throw err;
    }
});

ipcMain.handle('update:download', async () => {
    await autoUpdater.downloadUpdate();
});

ipcMain.handle('update:install', async () => {
    // Show native confirmation dialog
    const result = dialog.showMessageBoxSync(mainWindow!, {
        type: 'warning',
        title: 'Install Update',
        message: 'Install update and restart?',
        detail: 'The app will close and any running automations will be terminated.',
        buttons: ['Install & Restart', 'Cancel'],
        defaultId: 0,
        cancelId: 1,
    });

    if (result === 1) return; // User cancelled

    // Gracefully terminate backend before installing
    killPythonBackend();

    // Give the backend a moment to shut down, then install
    await new Promise((resolve) => setTimeout(resolve, 1000));
    autoUpdater.quitAndInstall(false, true);
});

// ─── App Lifecycle ─────────────────────────────────────────────────────────
app.whenReady().then(
    async () => {
        startPythonBackend();
        createLoadingWindow();

        try {
            await waitForBackend(8000);
            createWindow();

            // Initial update check (delayed to let the window settle)
            setTimeout(() => {
                autoUpdater.checkForUpdates().catch((err) => {
                    log.warn('Initial update check failed:', err);
                });
            }, 5000);

            // Periodic update check every 6 hours
            setInterval(() => {
                if (!isCheckingForUpdate) {
                    isCheckingForUpdate = true;
                    autoUpdater.checkForUpdates().catch((err) => {
                        isCheckingForUpdate = false;
                        log.warn('Periodic update check failed:', err);
                    });
                }
            }, 6 * 60 * 60 * 1000);
        } catch (error) {
            log.error("Backend failed to start:", error);
            const logPath = log.transports.file.getFile().path;
            dialog.showErrorBox(
                'AutoISP - Backend Failed to Start',
                `The backend server failed to start. This can happen if:\n\n` +
                `• Visual C++ Redistributable is not installed\n` +
                `• Antivirus is blocking the application\n` +
                `• The app is still loading (try again)\n\n` +
                `Log file: ${logPath}`
            );
            app.quit();
        }
    }
)

app.on('window-all-closed', () => {
    killPythonBackend(); // Kill backend when all windows close
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

ipcMain.on('window:minimize', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender);
    win?.minimize();
});

ipcMain.on('window:maximize', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender);
    if (win?.isMaximized()) {
        win.unmaximize();
    } else {
        win?.maximize();
    }
});

ipcMain.on('window:close', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender);
    win?.close();
});

ipcMain.on('window:resize', (event, width: number, height: number) => {
    const win = BrowserWindow.fromWebContents(event.sender);
    win?.setSize(width, height, true);
    win?.center();
});

ipcMain.on('window:open-devtools', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender);
    win?.webContents.openDevTools();
});

// Log panel detachment
ipcMain.on('log-panel:detach', () => {
    createLogWindow();
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('will-quit', () => {
    killPythonBackend();
});
