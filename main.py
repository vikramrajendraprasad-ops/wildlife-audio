import os
import shutil
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
from kivy.core.window import Window

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
            text="Initialize Engine",
            pos_hint={"center_x": 0.5},
            on_release=self.check_permissions
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
            from android import api_version
            
            # ANDROID 13+ FIX (API 33)
            # We must ask for READ_MEDIA_AUDIO, not READ_EXTERNAL_STORAGE
            if api_version >= 33:
                permissions = ['android.permission.READ_MEDIA_AUDIO']
            else:
                permissions = [Permission.READ_EXTERNAL_STORAGE]
                
            request_permissions(permissions, self.permission_callback)
        else:
            self.load_files()

    def permission_callback(self, permissions, results):
        if all(results):
            self.update_status("Locating Engine...")
            threading.Thread(target=self.install_engine).start()
        else:
            self.update_status("Permission Denied (Check Settings)")
            toast("Please enable Audio permissions in Android Settings")

    def update_status(self, text):
        def _update(dt):
            self.status_btn.text = text
        Clock.schedule_once(_update)

    def install_engine(self):
        # --- ROBUST ENGINE INSTALLER ---
        files_dir = self.user_data_dir
        dest = os.path.join(files_dir, 'ffmpeg_run') 

        # We used 'android.add_libs_arm64_v8a' in buildozer.spec
        # So the file IS at this specific system location:
        native_lib_path = f'/data/data/{self.get_application_config().split("org.wildlife")[0]}org.wildlife.wildlifeaudio/lib/libffmpeg_engine.so'
        
        # Fallback search
        possible_locations = [
            native_lib_path,
            os.path.join(os.path.dirname(__file__), 'libffmpeg_engine.so'),
            '/usr/lib/libffmpeg_engine.so' # For testing
        ]

        found_source = None
        for path in possible_locations:
            if os.path.exists(path):
                found_source = path
                break
        
        if found_source:
            try:
                # Copy to safe folder
                shutil.copy2(found_source, dest)
                # Make executable
                os.chmod(dest, 0o755) 
                self.ffmpeg_path = dest
                Clock.schedule_once(lambda x: self.engine_ready(True))
            except Exception as e:
                Clock.schedule_once(lambda x: self.engine_ready(False, str(e)))
        else:
            Clock.schedule_once(lambda x: self.engine_ready(False, "Engine file missing. Rebuild APK."))

    def engine_ready(self, success, message=""):
        if success:
            self.status_btn.text = "Engine Ready!"
            self.load_files()
        else:
            self.status_btn.text = "Engine Error"
            self.show_error(message)

    def get_storage_path(self):
        if platform == 'android':
            # Check if directory exists, if not create it
            path = "/storage/emulated/0/Download/Wildlife"
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except:
                    pass
            return path
        return "Wildlife_Test"

    def load_files(self):
        # CRASH FIX: Wrapped in Try/Except
        try:
            self.list_view.clear_widgets()
            path = self.get_storage_path()
            
            if not os.path.exists(path):
                self.status_btn.text = "Folder Not Found"
                return

            files = [f for f in os.listdir(path) if f.lower().endswith(('.mp3', '.wav', '.m4a'))]
            
            if not files:
                self.status_btn.text = "No Audio in Download/Wildlife"
                return

            for f in files:
                full_path = os.path.join(path, f)
                item = OneLineIconListItem(text=f, on_release=lambda x, p=full_path: self.open_menu(x, p))
                item.add_widget(IconLeftWidget(icon="music"))
                self.list_view.add_widget(item)
                
        except PermissionError:
            self.status_btn.text = "Storage Permission Error!"
            self.show_error("Android blocked file access.
1. Go to Settings > Apps > Wildlife Pro
2. Permissions > Music and Audio > Allow")
        except Exception as e:
            self.status_btn.text = "File Load Error"
            self.show_error(str(e))

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
        self.status_btn.text = "Processing..."
        threading.Thread(target=self.run_ffmpeg, args=(self.selected_file, preset)).start()

    def run_ffmpeg(self, input_path, preset):
        try:
            base = os.path.splitext(input_path)[0]
            
            # --- FORMULAS ---
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
            # ----------------

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                Clock.schedule_once(lambda x: self.success(os.path.basename(out)))
            else:
                err = stderr.decode('utf-8')
                Clock.schedule_once(lambda x: self.show_error(err[-300:]))

        except Exception as e:
            Clock.schedule_once(lambda x: self.show_error(str(e)))

    def success(self, filename):
        self.status_btn.text = f"Saved: {filename}"
        toast(f"Done! {filename}")
        # Refresh list safely
        Clock.schedule_once(lambda x: self.load_files(), 1)

    def show_error(self, error):
        self.status_btn.text = "Error!"
        if not self.dialog:
            self.dialog = MDDialog(title="Log", text=str(error))
        self.dialog.text = str(error)
        self.dialog.open()

if __name__ == '__main__':
    WildlifeStudio().run()
