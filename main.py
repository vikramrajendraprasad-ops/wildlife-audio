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

class WildlifeStudio(MDApp):
    dialog = None
    
    def build(self):
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.theme_style = "Dark"
        
        screen = MDScreen()
        layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(title="Wildlife Audio Master")
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
            self.status_btn.text = "Select Audio File"
            self.load_files()
        else:
            self.status_btn.text = "Permission Denied"

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
            self.status_btn.text = "No Audio Files Found"
            return

        for f in files:
            full_path = os.path.join(path, f)
            item = OneLineIconListItem(text=f, on_release=lambda x, p=full_path: self.open_dsp_menu(x, p))
            item.add_widget(IconLeftWidget(icon="waveform"))
            self.list_view.add_widget(item)

    def open_dsp_menu(self, item, filepath):
        self.selected_file = filepath
        menu_items = [
            # 1. Wide Cinema (Dolby Style)
            {"viewclass": "OneLineListItem", "text": "Wide Cinema (Dolby Style)", 
             "on_release": lambda: self.process_audio("wide_cinema")},
            
            # 2. Vocal Clarity (Sony Style)
            {"viewclass": "OneLineListItem", "text": "Vocal Clarity (Sony Style)", 
             "on_release": lambda: self.process_audio("vocal_clarity")},
            
            # 3. JBL Punch (Harman V-Shape)
            {"viewclass": "OneLineListItem", "text": "JBL Punch (Party Style)", 
             "on_release": lambda: self.process_audio("jbl_punch")},

            # 4. Bose Deep (Active EQ)
            {"viewclass": "OneLineListItem", "text": "Bose Deep (Active EQ)", 
             "on_release": lambda: self.process_audio("bose_deep")},

            # 5. Wildlife 5.1 Formula
            {"viewclass": "OneLineListItem", "text": "Make 5.1 Surround (AC3)", 
             "on_release": lambda: self.process_audio("5.1_surround")},
            
            # 6. Binaural Magic (Headphone)
            {"viewclass": "OneLineListItem", "text": "Binaural Magic (Headphones)", 
             "on_release": lambda: self.process_audio("binaural_magic")},
        ]
        self.menu = MDDropdownMenu(caller=item, items=menu_items, width_mult=6)
        self.menu.open()

    def process_audio(self, preset):
        self.menu.dismiss()
        self.status_btn.text = "Processing... (Using your Custom Formula)"
        threading.Thread(target=self.run_dsp_engine, args=(self.selected_file, preset)).start()

    def run_dsp_engine(self, input_path, preset):
        try:
            base = os.path.splitext(input_path)[0]
            
            # --- YOUR CUSTOM ENGINEERING RECIPES ---
            
            if preset == "wide_cinema":
                # 1. WIDE CINEMA (Dolby Style)
                # stereotools for width + aecho for space + bass for immersion
                output_path = f"{base}_Dolby_Cinema.mp3"
                fc = "stereotools=mlev=0.015625,aecho=0.8:0.9:1000:0.3,bass=g=3:f=100"
                cmd = f'ffmpeg -y -i "{input_path}" -af "{fc}" -b:a 320k "{output_path}"'

            elif preset == "vocal_clarity":
                # 2. VOCAL CLARITY (Sony Style)
                # highpass 150Hz + 3kHz Boost + 8kHz Air
                output_path = f"{base}_Sony_Clarity.mp3"
                fc = "highpass=f=150," \
                     "equalizer=f=3000:width_type=h:width=1000:g=5," \
                     "equalizer=f=8000:width_type=h:width=2000:g=3"
                cmd = f'ffmpeg -y -i "{input_path}" -af "{fc}" -b:a 320k "{output_path}"'

            elif preset == "jbl_punch":
                # 3. JBL PUNCH (Harman Style)
                # Boost 60Hz Kick + Cut Mids + Boost 12kHz Sparkle
                output_path = f"{base}_JBL_Punch.mp3"
                fc = "equalizer=f=60:width_type=h:width=50:g=5," \
                     "equalizer=f=1000:width_type=h:width=200:g=-2," \
                     "equalizer=f=12000:width_type=h:width=2000:g=4"
                cmd = f'ffmpeg -y -i "{input_path}" -af "{fc}" -b:a 320k "{output_path}"'

            elif preset == "bose_deep":
                # 4. BOSE DEEP (Active EQ Style)
                # Thick 110Hz Bass + Lowpass 10k + Heavy Compression (Compand)
                output_path = f"{base}_Bose_Deep.mp3"
                fc = "bass=g=8:f=110:width_type=h:width=80," \
                     "lowpass=f=10000," \
                     "compand=attacks=0:points=-80/-80|-12/-12|20/-12:gain=2"
                cmd = f'ffmpeg -y -i "{input_path}" -af "{fc}" -b:a 320k "{output_path}"'

            elif preset == "5.1_surround":
                # 5. WILDLIFE 5.1 SURROUND
                # Simplified Mapping: FL, FR, Center mix, LFE mix, Rear mix
                output_path = f"{base}_5.1_Surround.ac3"
                # Using the simplified formula you provided
                fc = "pan=5.1|FL=FL|FR=FR|FC=0.5*FL+0.5*FR|LFE=0.5*FL+0.5*FR|BL=FL|BR=FR"
                cmd = f'ffmpeg -y -i "{input_path}" -filter_complex "{fc}" -map 0:a -c:a ac3 -b:a 448k "{output_path}"'

            elif preset == "binaural_magic":
                # 6. BINAURAL MAGIC (Headphone)
                # Option A: Built-in HRTF (No external files needed)
                output_path = f"{base}_Binaural_Headphone.wav"
                fc = "surround=delay=20,headphone=ir=builtin"
                cmd = f'ffmpeg -y -i "{input_path}" -af "{fc}" "{output_path}"'

            # ---------------------------

            subprocess.call(cmd, shell=True)
            Clock.schedule_once(lambda x: self.success(os.path.basename(output_path)))
            
        except Exception as e:
            Clock.schedule_once(lambda x: self.error(str(e)))

    def success(self, filename):
        self.status_btn.text = f"Export Complete: {filename}"
        toast(f"Saved {filename}")
        self.load_files()

    def error(self, error):
        self.status_btn.text = "Processing Error"
        if not self.dialog:
            self.dialog = MDDialog(title="Error", text=str(error))
        self.dialog.text = str(error)
        self.dialog.open()

if __name__ == '__main__':
    WildlifeStudio().run()
