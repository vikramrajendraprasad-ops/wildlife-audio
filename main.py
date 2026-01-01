from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.audio import SoundLoader
import os

class WildlifeAudioApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        
        screen = MDScreen()
        
        # Main Layout
        layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            adaptive_height=True
        )
        
        # Title
        self.label = MDLabel(
            text="Wildlife Audio Player",
            halign="center",
            theme_text_color="Primary",
            font_style="H4"
        )
        
        # Play Button
        self.play_btn = MDFillRoundFlatIconButton(
            text="Play Tiger Sound",
            icon="play",
            pos_hint={"center_x": 0.5},
            on_release=self.play_audio
        )

        layout.add_widget(self.label)
        layout.add_widget(self.play_btn)
        screen.add_widget(layout)
        
        return screen

    def play_audio(self, instance):
        # This looks for a file named 'tiger.mp3' in your folder
        # Ensure you upload an mp3 file to GitHub with this name!
        sound = SoundLoader.load('tiger.mp3')
        if sound:
            sound.play()
            self.label.text = "Playing..."
        else:
            self.label.text = "Error: File not found"

if __name__ == '__main__':
    WildlifeAudioApp().run()
