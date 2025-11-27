import { app, BrowserWindow } from 'electron';
import * as path from 'path';
import { spawn, ChildProcess } from 'child_process';

let mainWindow: BrowserWindow | null;
let pythonProcess: ChildProcess | null = null;

const isDev = process.env.NODE_ENV === 'development';

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
        },
    });

    const startUrl = isDev
        ? 'http://localhost:3000'
        : `file://${path.join(__dirname, '../../out/index.html')}`;

    mainWindow.loadURL(startUrl);

    if (isDev) {
        mainWindow.webContents.openDevTools();
    }

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

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('will-quit', () => {
    killPythonBackend();
});
