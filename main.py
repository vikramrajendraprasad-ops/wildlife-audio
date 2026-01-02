
# RESCUE MODE MAIN.PY
# This script is designed to NOT CRASH.
import os
import shutil
import sys

# We use standard Kivy first because it is safer than KivyMD for debugging
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import platform
from kivy.clock import Clock

class RescueApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Status Label
        self.status = Label(text="Starting Rescue Mode...", font_size='20sp', halign='center')
        self.layout.add_widget(self.status)
        
        # Check Button
        btn = Button(text="Check for Engine File", size_hint=(1, 0.2))
        btn.bind(on_release=self.check_engine)
        self.layout.add_widget(btn)
        
        return self.layout

    def on_start(self):
        # Allow the UI to draw before doing work
        self.status.text = "App Loaded.\nPress button to check engine."

    def check_engine(self, *args):
        self.status.text = "Searching for 'libffmpeg_engine.so'..."
        
        # 1. GET FOLDER PATHS
        app_folder = os.path.dirname(os.path.abspath(__file__))
        
        # 2. LOOK FOR FILE
        source = os.path.join(app_folder, 'libffmpeg_engine.so')
        
        if os.path.exists(source):
            file_size = os.path.getsize(source)
            self.status.text = f"SUCCESS!\nFound engine file.\nSize: {file_size} bytes\n\nReady to switch back to Pro Mode."
        else:
            self.status.text = f"FAILED.\nCould not find 'libffmpeg_engine.so'\n\nChecked in:\n{app_folder}\n\nDid you upload it to GitHub?\nDid you add ',so' to buildozer.spec?"

if __name__ == '__main__':
    try:
        RescueApp().run()
    except Exception as e:
        print(f"CRASH: {e}")
