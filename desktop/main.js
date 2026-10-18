// FastAPI 서버가 이미 떠 있어야 한다: 프로젝트 루트에서 `fastapi dev app/main.py`
const { app, BrowserWindow, dialog } = require("electron");

const UI_URL = "http://127.0.0.1:8000/ui/";

async function waitForServer(retries = 20) {
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch("http://127.0.0.1:8000/openapi.json");
      if (res.ok) return true;
    } catch (_) {}
    await new Promise((r) => setTimeout(r, 500));
  }
  return false;
}

app.whenReady().then(async () => {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    title: "가계부",
    autoHideMenuBar: true,
  });

  if (!(await waitForServer())) {
    dialog.showErrorBox("서버 없음", "FastAPI 서버(127.0.0.1:8000)가 켜져 있지 않습니다.\n프로젝트 루트에서 `fastapi dev app/main.py`를 먼저 실행하세요.");
  }
  // index.html을 고쳐도 예전 화면이 캐시에서 나오지 않도록 띄울 때마다 비운다.
  await win.webContents.session.clearCache();
  win.loadURL(UI_URL);
});

app.on("window-all-closed", () => app.quit());
