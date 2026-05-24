# launcher.py — يوضع جوا LapApp/
import sys
import os
import threading
import time
import urllib.request
import ctypes
import socket

# ============================================================
# Redirect streams في بيئة الـ EXE (يمنع كسر المكتبات)
# ============================================================
if getattr(sys, 'frozen', False):
    import pathlib
    log_path = pathlib.Path(os.path.dirname(sys.executable)) / "R_log.txt"
    sys.stdout = open(log_path, 'w', encoding='utf-8')
    sys.stderr = sys.stdout

# تأكد إن الـ working directory صح
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

# ============================================================
# إخفاء نافذة الـ Console
# ============================================================
def hide_console():
    time.sleep(0.1)
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)

threading.Thread(target=hide_console, daemon=True).start()

# ============================================================
# اختيار port متاح تلقائياً
# ============================================================
def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

PORT = get_free_port()

# ============================================================
# تشغيل Flask في thread منفصل
# ============================================================
def run_flask():
    from app import app, initialize
    initialize()
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# ============================================================
# انتظر حتى Flask يكون جاهز (max 20 ثانية)
# ============================================================
for _ in range(40):
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PORT}", timeout=1)
        break
    except:
        time.sleep(0.5)

# ============================================================
# افتح WebView
# ============================================================
import webview

window = webview.create_window(
    title="Nebras Medical Laboratory",
    url=f"http://127.0.0.1:{PORT}/new-report",
    width=1280,
    height=800,
    resizable=True,
)

webview.start()