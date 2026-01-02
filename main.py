
import os
import threading
import subprocess
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.toast import toast
from kivy.utils import platform
from kivy.clock import Clock

class WildlifeStudio(MDApp):
    # We don't need a path anymore. 'ffmpeg' is now a system command.
    ffmpeg_command = "ffmpeg"
    
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
        
        # This button is just for status now
        self.status_btn = MDFillRoundFlatButton(
            text="Ready",
            pos_hint={"center_x": 0.5},
            disabled=True
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
            self.load_files()
        else:
            self.status_btn.text = "Permission Denied"

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
            self.status_btn.text = "No Audio Files Found"
            return

        self.status_btn.text = f"Found {len(files)} files"
        for f in files:
            full_path = os.path.join(path, f)
            # Tapping a file immediately starts the standard 'JBL Punch' conversion
            item = OneLineIconListItem(text=f, on_release=lambda x, p=full_path: self.process_audio(p))
            item.add_widget(IconLeftWidget(icon="music"))
            self.list_view.add_widget(item)

    def process_audio(self, filepath):
        self.status_btn.text = "Processing..."
        toast("Starting Conversion...")
        threading.Thread(target=self.run_ffmpeg, args=(filepath,)).start()

    def run_ffmpeg(self, input_path):
        try:
            base = os.path.splitext(input_path)[0]
            out = f"{base}_JBL.mp3"
            
            # The 'ffmpeg' command is now available system-wide in the app
            cmd = [
                'ffmpeg', '-y', '-i', input_path, 
                '-af', 'equalizer=f=60:width_type=h:width=50:g=5', 
                '-b:a', '320k', out
            ]
            
            # We catch the output to see if it actually runs
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                Clock.schedule_once(lambda x: self.success(os.path.basename(out)))
            else:
                # If it fails, we show the REAL error from the engine
                err = stderr.decode('utf-8')
                if not err: err = "Unknown Engine Error (Permissions?)"
                Clock.schedule_once(lambda x: self.show_error(err))

        except Exception as e:
            Clock.schedule_once(lambda x: self.show_error(f"Crash: {str(e)}"))

    def success(self, filename):
        self.status_btn.text = "Success!"
        toast(f"Saved: {filename}")
        self.load_files()

    def show_error(self, error):
        self.status_btn.text = "Error"
        # Print error to toast so you can see it quickly
        toast(f"Error: {str(error)[:100]}") 
        print(error)

if __name__ == '__main__':
    WildlifeStudio().run()
