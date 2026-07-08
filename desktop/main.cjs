const { app, BrowserWindow, dialog, shell } = require('electron')
const path = require('path')
const fs = require('fs')
const http = require('http')
const { spawn } = require('child_process')

const PORT = Number(process.env.KINETIX_PORT || 8765)
const APP_URL = `http://127.0.0.1:${PORT}`

let mainWindow = null
let serverProcess = null

function projectRoot() {
  return app.isPackaged
    ? path.join(process.resourcesPath)
    : path.join(__dirname, '..')
}

function staticDir() {
  const packaged = path.join(projectRoot(), 'frontend-dist')
  if (fs.existsSync(packaged)) return packaged
  return path.join(projectRoot(), 'frontend', 'dist')
}

function serverExePath() {
  return path.join(projectRoot(), 'kinetix-server', 'kinetix-server.exe')
}

function appDataDir() {
  return path.join(process.env.APPDATA || path.join(require('os').homedir(), 'AppData', 'Roaming'), 'Kinetix')
}

function findPython() {
  const candidates = ['py -3.12', 'py -3', 'python', 'python3']
  return candidates
}

function buildServerEnv() {
  const dbPath = path.join(appDataDir(), 'kinetix.db')
  fs.mkdirSync(appDataDir(), { recursive: true })
  return {
    ...process.env,
    KINETIX_PORT: String(PORT),
    KINETIX_STATIC_DIR: staticDir(),
    KINETIX_DB_PATH: dbPath,
  }
}

function startPackagedServer() {
  const exe = serverExePath()
  if (!fs.existsSync(exe)) {
    throw new Error(`Не найден сервер: ${exe}`)
  }
  serverProcess = spawn(exe, [], {
    cwd: path.dirname(exe),
    env: buildServerEnv(),
    windowsHide: true,
  })
  attachServerLogs(serverProcess)
}

function startDevServer() {
  const backendDir = path.join(projectRoot(), 'backend')
  const env = buildServerEnv()
  const tryStart = (commands, index = 0) => {
    if (index >= commands.length) {
      dialog.showErrorBox(
        'Kinetix',
        'Не найден Python 3.12.\n\nУстановите Python с https://www.python.org/downloads/ или соберите приложение через scripts/build-windows.ps1',
      )
      app.quit()
      return
    }
    const cmd = commands[index]
    const [bin, ...args] = cmd.split(' ')
    serverProcess = spawn(bin, [...args, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(PORT)], {
      cwd: backendDir,
      env,
      windowsHide: true,
      shell: bin === 'py',
    })
    serverProcess.once('error', () => {
      serverProcess = null
      tryStart(commands, index + 1)
    })
    attachServerLogs(serverProcess)
  }
  tryStart(findPython())
}

function attachServerLogs(proc) {
  proc.stdout?.on('data', (chunk) => console.log(`[server] ${chunk}`.trim()))
  proc.stderr?.on('data', (chunk) => console.error(`[server] ${chunk}`.trim()))
  proc.on('exit', (code) => {
    if (code && code !== 0) {
      console.error(`Server exited with code ${code}`)
    }
  })
}

function waitForHealth(timeoutMs = 90000) {
  const started = Date.now()
  return new Promise((resolve, reject) => {
    const check = () => {
      const req = http.get(`${APP_URL}/api/health`, (res) => {
        res.resume()
        if (res.statusCode === 200) resolve()
        else retry()
      })
      req.on('error', retry)
      req.setTimeout(4000, () => {
        req.destroy()
        retry()
      })
    }
    const retry = () => {
      if (Date.now() - started > timeoutMs) {
        reject(new Error('Сервер не запустился вовремя'))
        return
      }
      setTimeout(check, 600)
    }
    check()
  })
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1360,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: 'Kinetix CRM',
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  mainWindow.loadURL(APP_URL)
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })
}

function stopServer() {
  if (!serverProcess) return
  try {
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', String(serverProcess.pid), '/f', '/t'], { windowsHide: true })
    } else {
      serverProcess.kill('SIGTERM')
    }
  } catch {
    serverProcess.kill()
  }
  serverProcess = null
}

app.whenReady().then(async () => {
  try {
    if (app.isPackaged && fs.existsSync(serverExePath())) {
      startPackagedServer()
    } else {
      startDevServer()
    }
    await waitForHealth()
    createWindow()
  } catch (err) {
    dialog.showErrorBox('Kinetix', err.message || String(err))
    app.quit()
  }
})

app.on('window-all-closed', () => {
  stopServer()
  if (process.platform !== 'darwin') app.quit()
})

app.on('before-quit', () => stopServer())
