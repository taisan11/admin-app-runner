import TkEasyGUI as eg
import sys
import threading
import ctypes
import subprocess
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

true = True
false = False

def create_image(width, height, color1, color2):
    """
    シンプルなタスクトレイ用アイコン画像を作成します。
    """
    image = Image.new("RGB", (width, height), color1)
    draw = ImageDraw.Draw(image)
    draw.rectangle(
        [(width // 4, height // 4), (width * 3 // 4, height * 3 // 4)], fill=color2
    )
    return image

def minimize_to_tray(window):
    """
    タスクトレイアイコンを作成し、ウィンドウを非表示にします。
    """
    def on_click(icon, item):
        window.post_event("-RESTORE-", None)  # メインスレッドにイベントを送信
        icon.stop()

    menu = Menu(MenuItem("Open", on_click))
    icon = Icon("Test App", create_image(64, 64, "blue", "white"), menu=menu)
    icon.run()  # タスクトレイアイコンを表示

def run_with_admin(program_path, args=[]):
    """
    管理者権限で現在の権限を引き継いで別のプログラムを実行します。
    
    :param program_path: 実行するプログラムのパス
    :param args: 引数のリスト
    """
    try:
        subprocess.run([program_path] + args, check=True)
        print(f"{program_path} を管理者権限で実行しました。")
    except Exception as e:
        print(f"エラー: {e}")

def is_admin():
    """
    現在のスクリプトが管理者権限で実行されているかをチェックします。
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """
    現在のスクリプトを管理者権限で再実行します。
    """
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        except Exception as e:
            eg.popup_error(f"管理者権限で実行できませんでした。\nエラー: {e}")

# define layout
layout = [
    [eg.Text("File:"), eg.InputText("",size=(30,1),key="filepath"), eg.FileBrowse("Select",key="file")],
    [eg.Button("Upgrade Administrator"),eg.Button("Task Tray")],
    [eg.Button("run!!"),eg.Button("OpenSetting")],
]

settingLayout = [
    [eg.Text("Setting!!", font=("Arial", 20))],
    [eg.Text("Title:"),eg.InputText("Admin app runner",key="title")],
    [eg.Text("Icon:"),eg.InputText("icon.ico",key="icon"),eg.FileBrowse("Select")],
    [eg.Button("Save")],
]
# create a window
with eg.Window("Admin app runner", layout,resizable=True) as window:
    for event, values in window.event_iter():
        if event == "run!!":
            run_with_admin(values["filepath"])
        elif event == "Upgrade Administrator":
            run_as_admin()
        elif event == "Task Tray":
            window.hide()  # ウィンドウを非表示にする
            threading.Thread(target=minimize_to_tray, args=(window,), daemon=True).start()
        elif event == "OpenSetting":
            with eg.Window("Setting", settingLayout) as settingWindow:
                for Setevent, Setvalues in settingWindow.event_iter():
                    if Setevent == "Save":
                        window.set_title(Setvalues["title"])
                        if Setvalues["icon"] != "icon.ico":
                            window.set_icon(Setvalues["icon"])
                        settingWindow.close()
        elif event == "-RESTORE-":
            window.un_hide()  # ウィンドウを再表示する

