
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
import os
import subprocess
import threading
import shutil

class WildlifeStudio(MDApp):
    dialog = None
    ffmpeg_path = "ffmpeg"
    
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
        self.status_btn = MDFillRoundFlatButton(
            text="Initialize Audio Engine",
            pos_hint={"center_x": 0.5},
            on_release=self.request_android_permissions
        )
        layout.add_widget(MDBoxLayout(self.status_btn, padding=20, adaptive_height=True))
        screen.add_widget(layout)
        return screen

    def on_start(self):
        if platform == 'android':
            self.request_android_permissions()
        else:
            self.load_files()

    def request_android_permissions(self, *args):
        from android.permissions import request_permissions, Permission
        request_permissions(
            [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE],
            self.permission_callback
        )

    def permission_callback(self, permissions, results):
        if all(results):
            self.status_btn.text = "Installing Engine..."
            threading.Thread(target=self.install_engine).start()
        else:
            self.status_btn.text = "Permission Denied"

    def install_engine(self):
        # 1. Find the file inside the APK assets
        app_folder = os.path.dirname(os.path.abspath(__file__))
        source = os.path.join(app_folder, 'libffmpeg_engine.so')
        
        # 2. Define where it needs to go (Private Storage)
        files_dir = os.environ.get('ANDROID_PRIVATE', app_folder)
        dest = os.path.join(files_dir, 'libffmpeg_engine.so')

        if os.path.exists(source):
            try:
                # 3. Copy it
                shutil.copy2(source, dest)
                # 4. Give it permission to run (chmod +x)
                os.chmod(dest, 0o755)
                self.ffmpeg_path = dest
                Clock.schedule_once(lambda x: self.engine_ready(True))
            except Exception as e:
                Clock.schedule_once(lambda x: self.engine_ready(False, str(e)))
        else:
            # If source is missing, the user forgot to add ',so' to buildozer.spec
            Clock.schedule_once(lambda x: self.engine_ready(False, "Engine file missing! Did you add ',so' to buildozer.spec?"))

    def engine_ready(self, success, error=""):
        if success:
            self.status_btn.text = "Engine Ready!"
            self.load_files()
        else:
            self.status_btn.text = "Engine Error"
            self.show_error(error)

    def get_storage_path(self):
        if platform == 'android':
            return "/storage/emulated/0/Download/Wildlife"
        return "Wildlife_Test"

    def load_files(self):
        self.list_view.clear_widgets()
        path = self.get_storage_path()
        if not os.path.exists(path):
            try: os.makedirs(path)
            except: pass
        files = [f for f in os.listdir(path) if f.lower().endswith(('.mp3', '.wav', '.flac', '.m4a'))]
        if not files:
            self.status_btn.text = "No Audio Files in Download/Wildlife"
            return
        for f in files:
            full_path = os.path.join(path, f)
            item = OneLineIconListItem(text=f, on_release=lambda x, p=full_path: self.open_dsp_menu(x, p))
            item.add_widget(IconLeftWidget(icon="waveform"))
            self.list_view.add_widget(item)

    def open_dsp_menu(self, item, filepath):
        self.selected_file = filepath
        menu_items = [
            {"viewclass": "OneLineListItem", "text": "Wide Cinema (Dolby)", "on_release": lambda: self.process_audio("wide_cinema")},
            {"viewclass": "OneLineListItem", "text": "Vocal Clarity (Sony)", "on_release": lambda: self.process_audio("vocal_clarity")},
            {"viewclass": "OneLineListItem", "text": "JBL Punch", "on_release": lambda: self.process_audio("jbl_punch")},
            {"viewclass": "OneLineListItem", "text": "Bose Deep", "on_release": lambda: self.process_audio("bose_deep")},
            {"viewclass": "OneLineListItem", "text": "5.1 Surround (AC3)", "on_release": lambda: self.process_audio("5.1_surround")},
            {"viewclass": "OneLineListItem", "text": "Binaural (Headphones)", "on_release": lambda: self.process_audio("binaural_magic")},
        ]
        self.menu = MDDropdownMenu(caller=item, items=menu_items, width_mult=6)
        self.menu.open()

    def process_audio(self, preset):
        self.menu.dismiss()
        self.status_btn.text = "Processing..."
        threading.Thread(target=self.run_dsp_engine, args=(self.selected_file, preset)).start()

    def run_dsp_engine(self, input_path, preset):
        try:
            base = os.path.splitext(input_path)[0]
            if preset == "wide_cinema":
                output_path = f"{base}_Dolby.mp3"
                fc = "stereotools=mlev=0.015625,aecho=0.8:0.9:1000:0.3,bass=g=3:f=100"
                cmd = [self.ffmpeg_path, '-y', '-i', input_path, '-af', fc, '-b:a', '320k', output_path]
            elif preset == "vocal_clarity":
                output_path = f"{base}_Sony.mp3"
                fc = "highpass=f=150,equalizer=f=3000:width_type=h:width=1000:g=5,equalizer=f=8000:width_type=h:width=2000:g=3"
                cmd = [self.ffmpeg_path, '-y', '-i', input_path, '-af', fc, '-b:a', '320k', output_path]
            elif preset == "jbl_punch":
                output_path = f"{base}_JBL.mp3"
                fc = "equalizer=f=60:width_type=h:width=50:g=5,equalizer=f=1000:width_type=h:width=200:g=-2,equalizer=f=12000:width_type=h:width=2000:g=4"
                cmd = [self.ffmpeg_path, '-y', '-i', input_path, '-af', fc, '-b:a', '320k', output_path]
            elif preset == "bose_deep":
                output_path = f"{base}_Bose.mp3"
                fc = "bass=g=8:f=110:width_type=h:width=80,lowpass=f=10000,compand=attacks=0:points=-80/-80|-12/-12|20/-12:gain=2"
                cmd = [self.ffmpeg_path, '-y', '-i', input_path, '-af', fc, '-b:a', '320k', output_path]
            elif preset == "5.1_surround":
                output_path = f"{base}_5.1.ac3"
                fc = "pan=5.1|FL=FL|FR=FR|FC=0.5*FL+0.5*FR|LFE=0.5*FL+0.5*FR|BL=FL|BR=FR"
                cmd = [self.ffmpeg_path, '-y', '-i', input_path, '-filter_complex', fc, '-c:a', 'ac3', '-b:a', '448k', output_path]
            elif preset == "binaural_magic":
                output_path = f"{base}_Binaural.wav"
                fc = "surround=delay=20,headphone=ir=builtin"
                cmd = [self.ffmpeg_path, '-y', '-i', input_path, '-af', fc, output_path]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                Clock.schedule_once(lambda x: self.success(os.path.basename(output_path)))
            else:
                error_msg = stderr.decode('utf-8')
                Clock.schedule_once(lambda x: self.show_error(error_msg[-300:]))
            
        except Exception as e:
            Clock.schedule_once(lambda x: self.show_error(str(e)))

    def success(self, filename):
        self.status_btn.text = f"Saved: {filename}"
        toast(f"Success! {filename}")
        self.load_files()

    def show_error(self, error):
        self.status_btn.text = "Error!"
        if not self.dialog:
            self.dialog = MDDialog(title="Error Log", text=str(error))
        self.dialog.text = str(error)
        self.dialog.open()

if __name__ == '__main__':
    WildlifeStudio().run()
