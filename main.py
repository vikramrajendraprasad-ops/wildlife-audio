
import os
import glob
import threading
import subprocess
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast
from kivy.utils import platform
from kivy.clock import Clock
from jnius import autoclass

class WildlifeStudio(MDApp):
    ffmpeg_path = "" 
    dialog = None
    
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        
        screen = MDScreen()
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(title="Wildlife Pro Studio")
        toolbar.right_action_items = [["refresh", lambda x: self.load_files()]]
        layout.add_widget(toolbar)

        scroll = MDScrollView()
        self.list_view = MDList()
        scroll.add_widget(self.list_view)
        layout.add_widget(scroll)
        
        # Hidden status button (only appears if there is a critical error)
        self.status_btn = MDFillRoundFlatButton(
            text="Loading...",
            pos_hint={"center_x": 0.5},
            opacity=0 
        )
        layout.add_widget(MDBoxLayout(self.status_btn, padding=20, adaptive_height=True))

        screen.add_widget(layout)
        return screen

    def on_start(self):
        if platform == 'android':
            self.check_permissions()
        else:
            self.load_files()

    def check_permissions(self, *args):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions(
                [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE],
                self.permission_callback
            )
        else:
            self.load_files()

    def permission_callback(self, permissions, results):
        if all(results):
            # SILENTLY FIND THE ENGINE
            self.find_engine_silent()
        else:
            self.show_error("Permission Denied")

    def find_engine_silent(self):
        # 1. Try Java (Best)
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity.getApplicationContext()
            path = context.getApplicationInfo().nativeLibraryDir + "/libffmpeg_engine.so"
            if os.path.exists(path):
                self.ffmpeg_path = path
                self.load_files()
                return
        except: pass

        # 2. Try Wildcard (Fix for random letters)
        try:
            matches = glob.glob("/data/app/org.wildlife.wildlifeaudio*/lib/*/libffmpeg_engine.so")
            if matches and os.path.exists(matches[0]):
                self.ffmpeg_path = matches[0]
                self.load_files()
                return
        except: pass

        # 3. Try System Path (Fallback)
        try:
            path = os.path.join(os.environ.get("LD_LIBRARY_PATH", ""), "libffmpeg_engine.so")
            if os.path.exists(path):
                self.ffmpeg_path = path
                self.load_files()
                return
        except: pass

        # If we get here, it's missing
        self.status_btn.opacity = 1
        self.status_btn.text = "Error: Engine Missing"
        self.show_error("Could not find libffmpeg_engine.so. Did you upload it?")

    def load_files(self):
        self.list_view.clear_widgets()
        path = "/storage/emulated/0/Download/Wildlife"
        if not os.path.exists(path):
            try: os.makedirs(path)
            except: pass
            
        try:
            files = [f for f in os.listdir(path) if f.lower().endswith(('.mp3', '.wav', '.m4a'))]
        except: files = []

        if not files:
            self.status_btn.opacity = 1
            self.status_btn.text = "No Files in Download/Wildlife"
            return

        # Restore UI
        self.status_btn.opacity = 0
        for f in files:
            full_path = os.path.join(path, f)
            item = OneLineIconListItem(text=f, on_release=lambda x, p=full_path: self.open_menu(x, p))
            item.add_widget(IconLeftWidget(icon="music"))
            self.list_view.add_widget(item)

    def open_menu(self, item, filepath):
        self.selected_file = filepath
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Wide Cinema (Dolby)", "on_release": lambda: self.process("wide_cinema")},
            {"viewclass": "OneLineListItem", "text": "Vocal Clarity (Sony)", "on_release": lambda: self.process("vocal_clarity")},
            {"viewclass": "OneLineListItem", "text": "JBL Punch", "on_release": lambda: self.process("jbl_punch")},
            {"viewclass": "OneLineListItem", "text": "Bose Deep", "on_release": lambda: self.process("bose_deep")},
            {"viewclass": "OneLineListItem", "text": "5.1 Surround (AC3)", "on_release": lambda: self.process("5.1_surround")},
            {"viewclass": "OneLineListItem", "text": "Binaural 3D", "on_release": lambda: self.process("binaural_magic")},
        ]
        self.menu = MDDropdownMenu(caller=item, items=menu_items, width_mult=6)
        self.menu.open()

    def process(self, preset):
        self.menu.dismiss()
        toast("Processing... Please wait.")
        threading.Thread(target=self.run_ffmpeg, args=(self.selected_file, preset)).start()

    def run_ffmpeg(self, input_path, preset):
        try:
            base = os.path.splitext(input_path)[0]
            
            # --- PROFESSIONAL AUDIO FORMULAS ---
            if preset == "wide_cinema":
                out = f"{base}_Dolby.mp3"
                fc = "stereotools=mlev=0.015625,aecho=0.8:0.9:1000:0.3,bass=g=3:f=100"
                cmd = [self.ffmpeg_path, '-y', '-i', input_path, '-af', fc, '-b:a', '320k', out]
            elif preset == "vocal_clarity":
                out = f"{base}_Sony.mp3"
                fc = "highpass=f=150,equalizer=f=3000:width_type=h:width=1000:g=5,equalizer=f=8000:width_type=h:width=2000:g=3"
                cmd = [self.ffmpeg_path, '-y', '-i', input_path, '-af', fc, '-b:a', '320k', out]
            elif preset == "jbl_punch":
                out = f"{base}_JBL.mp3"
                fc = "equalizer=f=60:width_type=h:width=50:g=5,equalizer=f=1000:width_type=h:width=200:g=-2,equalizer=f=12000:width_type=h:width=2000:g=4"
                cmd = [self.ffmpeg_path, '-y', '-i', input_path, '-af', fc, '-b:a', '320k', out]
            elif preset == "bose_deep":
                out = f"{base}_Bose.mp3"
                fc = "bass=g=8:f=110:width_type=h:width=80,lowpass=f=10000,compand=attacks=0:points=-80/-80|-12/-12|20/-12:gain=2"
                cmd = [self.ffmpeg_path, '-y', '-i', input_path, '-af', fc, '-b:a', '320k', out]
            elif preset == "5.1_surround":
                out = f"{base}_5.1.ac3"
                fc = "pan=5.1|FL=FL|FR=FR|FC=0.5*FL+0.5*FR|LFE=0.5*FL+0.5*FR|BL=FL|BR=FR"
                cmd = [self.ffmpeg_path, '-y', '-i', input_path, '-filter_complex', fc, '-c:a', 'ac3', '-b:a', '448k', out]
            elif preset == "binaural_magic":
                out = f"{base}_Binaural.wav"
                fc = "surround=delay=20,headphone=ir=builtin"
                cmd = [self.ffmpeg_path, '-y', '-i', input_path, '-af', fc, out]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                Clock.schedule_once(lambda x: self.success(os.path.basename(out)))
            else:
                err = stderr.decode('utf-8')
                Clock.schedule_once(lambda x: self.show_error(err))

        except Exception as e:
            Clock.schedule_once(lambda x: self.show_error(str(e)))

    def success(self, filename):
        toast(f"Success! Saved {filename}")
        self.load_files()

    def show_error(self, error):
        if not self.dialog:
            self.dialog = MDDialog(title="Error", text=str(error))
        self.dialog.text = str(error)
        self.dialog.open()

if __name__ == '__main__':
    WildlifeStudio().run()
