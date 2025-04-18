from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.button import Button
import json
import os
import platform
import winreg

class SettingsScreen(Screen):
    theme = StringProperty("System Default")
    notifications = BooleanProperty(True)
    font_scale = StringProperty("Medium")
    font_size = NumericProperty(16)
    _theme_applied = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.theme = self.app.app_data.get("settings", {}).get("theme", "System Default")
        self.notifications = self.app.app_data.get("settings", {}).get("notifications", True)
        self.font_scale = self.app.app_data.get("settings", {}).get("font_scale", "Medium")

    def on_pre_enter(self):
        try:
            if not self._theme_applied:
                self.apply_theme()
                self._theme_applied = True
        except Exception as e:
            print(f"Error in on_pre_enter: {e}")

    def set_theme(self, value):
        self.theme = value
        self.save_settings()
        Clock.schedule_once(lambda dt: self.apply_theme(), 0.1)

    def set_font_scale(self, value):
        self.font_scale = value
        self.save_settings()
        Clock.schedule_once(lambda dt: self.app.on_window_resize(Window, Window.size[0], Window.size[1]), 0.1)

    def get_system_theme(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "Light" if value == 1 else "Dark"
        except Exception as e:
            print(f"Error accessing system theme: {e}")
            return "Light"

    def apply_theme(self):
        try:
            if not self.app.root:
                return
            theme = self.theme if self.theme != "System Default" else self.get_system_theme()
            bg_color = [1, 1, 1, 1] if theme == "Light" else [0.1, 0.3, 0.3, 1]
            text_color = [0.2, 0.6, 1, 1] if theme == "Light" else [0.9, 0.9, 0.9, 1]
            button_color = [0.5, 0.5, 0.5, 1]
            for screen in self.app.root.screens:
                screen.canvas.before.clear()
                with screen.canvas.before:
                    Color(*bg_color)
                    Rectangle(pos=screen.pos, size=screen.size)
                for widget in screen.walk():
                    if isinstance(widget, (Label, Button)) and not isinstance(widget, Factory.CenteredTextInput):
                        widget.color = text_color
                    if isinstance(widget, Factory.CustomButton):
                        widget.background_color = button_color
        except Exception as e:
            print(f"Error applying theme: {e}")

    def save_settings(self):
        self.app.app_data["settings"] = {
            "theme": self.theme,
            "notifications": self.notifications,
            "font_scale": self.font_scale
        }
        self.app.save_data()

    def show_export_chooser(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        file_chooser = FileChooserListView(path=os.path.expanduser("~"), filters=["*.json"])
        buttons = BoxLayout(size_hint_y=None, height=45, spacing=10)
        cancel_btn = Factory.CustomButton(text='Cancel', font_size=str(self.font_size) + 'sp', on_press=lambda x: popup.dismiss())
        save_btn = Factory.CustomButton(text='Save', font_size=str(self.font_size) + 'sp', on_press=lambda x: self.export_data(file_chooser.path, popup))
        buttons.add_widget(cancel_btn)
        buttons.add_widget(save_btn)
        content.add_widget(file_chooser)
        content.add_widget(buttons)
        popup = Popup(title='Export Data', content=content, size_hint=(0.8, 0.8))
        popup.open()

    def export_data(self, path, popup):
        try:
            file_path = os.path.join(path, "app_data.json")
            with open(file_path, "w") as f:
                json.dump(self.app_data, f)
            popup.dismiss()
        except Exception as e:
            print(f"Error exporting data: {e}")

    def show_import_chooser(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        file_chooser = FileChooserListView(path=os.path.expanduser("~"), filters=["*.json"])
        buttons = BoxLayout(size_hint_y=None, height=45, spacing=10)
        cancel_btn = Factory.CustomButton(text='Cancel', font_size=str(self.font_size) + 'sp', on_press=lambda x: popup.dismiss())
        load_btn = Factory.CustomButton(text='Load', font_size=str(self.font_size) + 'sp', on_press=lambda x: self.import_data(file_chooser.selection, popup))
        buttons.add_widget(cancel_btn)
        buttons.add_widget(load_btn)
        content.add_widget(file_chooser)
        content.add_widget(buttons)
        popup = Popup(title='Import Data', content=content, size_hint=(0.8, 0.8))
        popup.open()

    def import_data(self, selection, popup):
        try:
            if selection:
                with open(selection[0], "r") as f:
                    self.app.app_data = json.load(f)
                    self.app.save_data()
                    self.theme = self.app.app_data.get("settings", {}).get("theme", "System Default")
                    self.notifications = self.app.app_data.get("settings", {}).get("notifications", True)
                    self.font_scale = self.app.app_data.get("settings", {}).get("font_scale", "Medium")
                    self.apply_theme()
            popup.dismiss()
        except Exception as e:
            print(f"Error importing data: {e}")