import sys
import os
import ctypes
from ctypes import wintypes
os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QTimer
import vlc
from PyQt5.QtGui import QWindow, QScreen


class VideoWallpaper(QMainWindow):
    def __init__(self, video_path):
        super().__init__()

        # Config de la fenêtre
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        # Plein écran sur l'écran principal
        screen: QScreen = QApplication.primaryScreen()
        geometry = screen.geometry()
        self.setGeometry(geometry)

        # Création du player VLC
        self.instance = vlc.Instance('--video-on-top', '--no-video-title-show', '--fullscreen')
        self.mediaplayer = self.instance.media_player_new()
        self.mediaplayer.audio_set_mute(True)

        # Mettre la fenêtre PyQt5 derrière les icônes du bureau
        self.set_wallpaper_window()

        # Lier la vidéo au player
        if sys.platform.startswith("win"):
            self.mediaplayer.set_hwnd(int(self.winId()))
        else:
            self.mediaplayer.set_xwindow(self.winId())

        media = self.instance.media_new(video_path)
        self.mediaplayer.set_media(media)

        # Lancer la lecture
        self.mediaplayer.play()

        # Boucler la vidéo
        self.mediaplayer.get_media().add_option("input-repeat=-1")

    def set_wallpaper_window(self):
        # Utilise les APIs Windows pour coller la fenêtre au fond d'écran

        progman = ctypes.windll.user32.FindWindowW("Progman", None)
        result = ctypes.c_ulong()
        ctypes.windll.user32.SendMessageTimeoutW(progman, 0x052C, 0, 0,
                                                  0, 1000, ctypes.byref(result))

        def enum_handler(hwnd, lParam):
            shell = ctypes.create_unicode_buffer(255)
            ctypes.windll.user32.GetClassNameW(hwnd, shell, 255)
            if shell.value == "WorkerW":
                ctypes.windll.user32.ShowWindow(hwnd, 0)

        # Cache les autres fenêtres
        ctypes.windll.user32.EnumWindows(
            ctypes.WINFUNCTYPE(None, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)(enum_handler), 0
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)

    video_path = os.path.abspath("videos/ta_video.mp4")  # ← change le nom ici si besoin
    if not os.path.exists(video_path):
        print(f"Fichier vidéo introuvable : {video_path}")
        sys.exit(1)

    player = VideoWallpaper(video_path)
    player.show()

    sys.exit(app.exec_())
