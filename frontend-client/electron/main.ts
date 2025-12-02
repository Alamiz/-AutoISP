import { app, Menu, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import { spawn, ChildProcess } from 'child_process';
import kill from 'tree-kill';
import log from 'electron-log';

let mainWindow: BrowserWindow | null;
let pythonProcess: ChildProcess | null = null;

const isDev = process.env.NODE_ENV === 'development';

import serve from 'electron-serve';

const serveURL = serve({ directory: path.join(__dirname, '../../out') });

function createWindow() {
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
        frame: false
    });

    if (isDev) {
        mainWindow.loadURL('http://localhost:3000');
    } else {
        serveURL(mainWindow);
    }

    if (isDev) {
        mainWindow.webContents.openDevTools();
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
        backendPath = path.join(__dirname, '../../../backend-engine');
        pythonExecutable = path.join(backendPath, 'venv', 'Scripts', 'python.exe');
        const scriptPath = path.join(backendPath, 'api.py');
        apiScript = [scriptPath];
        console.log(`Starting Development Backend: ${pythonExecutable} ${scriptPath}`);
    }

    pythonProcess = spawn(pythonExecutable, apiScript, {
        cwd: backendPath,
        stdio: 'inherit',
    });

    pythonProcess.on('error', (err) => {
        console.error('Failed to start Python backend:', err);
    });

    pythonProcess.on('exit', (code, signal) => {
        console.log(`Python backend exited with code ${code} and signal ${signal}`);
    });
}

function killPythonBackend() {
    if (pythonProcess) {
        console.log('Killing Python backend...');
        pythonProcess.kill();

        // Try to kill the process using tree-kill
        try {
            if (!pythonProcess.pid) return;
            kill(pythonProcess.pid, "SIGTERM", (err) => {
                if (err) log.error("Failed to kill Python backend process due to:", err)
                else log.info("Python backend process killed!")
            })
        } catch (error) {
            log.error("Failed to kill Python backend process:", error)
        }

        pythonProcess = null;
    }
}

app.on('ready', () => {
    startPythonBackend();
    createWindow();
});

app.on('window-all-closed', () => {
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

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('will-quit', () => {
    killPythonBackend();
});
