from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.clock import Clock
from screens.home import HomeScreen
from screens.project import ProjectScreen
from screens.settings import SettingsScreen
from screens.stats import StatsScreen
from datetime import datetime, timedelta
from plyer import notification
import json
import os

# Register CustomButton for Python access
Builder.load_string("""
<CustomButton@Button>:
    font_name: 'assets/fonts/seguiemj.ttf'
    font_size: str(root.font_size * 1.0) + 'sp'
    size_hint: None, None
    size: 60, 45
    border: 15, 15, 15, 15
    background_normal: ''
    background_down: ''
    background_color: [0.5, 0.5, 0.5, 1]
    color: [1, 1, 1, 1]
    canvas.before:
        Color:
            rgba: [0, 0, 0, 0.2]
        RoundedRectangle:
            pos: self.pos[0], self.pos[1] - 2
            size: self.size[0], self.size[1]
            radius: [10]
        Color:
            rgba: self.background_color if self.state == 'normal' else [self.background_color[0] * 0.9, self.background_color[1] * 0.9, self.background_color[2] * 0.9, 1]
        RoundedRectangle:
            pos: self.pos[0] + 2, self.pos[1] + 2
            size: self.size[0] - 4, self.size[1] - 4
            radius: [10]
    canvas.after:
        PushMatrix:
        Scale:
            origin: self.center
            x: 0.95 if self.state == 'down' else 1
            y: 0.95 if self.state == 'down' else 1
        PopMatrix:
""")

Builder.load_file("kv/home.kv")
Builder.load_file("kv/project.kv")
Builder.load_file("kv/settings.kv")
Builder.load_file("kv/stats.kv")

class MainApp(App):
    def build(self):
        self.app_data = self.load_data()
        sm = ScreenManager(transition=SlideTransition(duration=0.3))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ProjectScreen(name="project"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(StatsScreen(name="stats"))
        Window.bind(on_resize=self.on_window_resize)
        return sm

    def on_start(self):
        Clock.schedule_once(lambda dt: self.on_window_resize(Window, Window.size[0], Window.size[1]), 0)
        Clock.schedule_interval(self.schedule_notifications, 86400)  # Check daily

    def schedule_notifications(self, dt):
        if not self.app_data.get("settings", {}).get("notifications", True):
            return
        today = datetime.now().date()
        for project in self.app_data.get("projects", []):
            due_date_str = project.get("due_date", "")
            if not due_date_str:
                continue
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                days_left = (due_date - today).days
                if days_left == 7:
                    notification.notify(
                        title="Creative Dashboard",
                        message=f"'{project['name']}' is due in 1 week ({due_date_str})",
                        app_name="Creative Dashboard",
                        timeout=10
                    )
                elif days_left == 2:
                    notification.notify(
                        title="Creative Dashboard",
                        message=f"'{project['name']}' is due in 2 days ({due_date_str})",
                        app_name="Creative Dashboard",
                        timeout=10
                    )
                elif days_left == 0:
                    notification.notify(
                        title="Creative Dashboard",
                        message=f"'{project['name']}' is due today ({due_date_str})",
                        app_name="Creative Dashboard",
                        timeout=10
                    )
            except ValueError:
                print(f"Invalid due date for '{project['name']}': {due_date_str}")

    def load_data(self):
        data_file = "app_data.json"
        try:
            if os.path.exists(data_file):
                with open(data_file, "r") as f:
                    data = json.load(f)
                    if "projects" in data and data["projects"]:
                        validated_projects = []
                        for p in data["projects"]:
                            if isinstance(p, dict) and "name" in p:
                                p.setdefault("status", "Not Started")
                                p.setdefault("emoji", "📌")
                                p.setdefault("recurrence", "None")
                                p.setdefault("history", [])
                                p.setdefault("due_date", "")
                                validated_projects.append(p)
                            elif isinstance(p, str):
                                print(f"Converting string project '{p}' to dictionary")
                                validated_projects.append({
                                    "name": p,
                                    "category": "General",
                                    "status": "Not Started",
                                    "emoji": "📌",
                                    "recurrence": "None",
                                    "due_date": "",
                                    "history": []
                                })
                            else:
                                print(f"Skipping invalid project entry: {p}")
                        data["projects"] = validated_projects
                    if "settings" not in data:
                        data["settings"] = {"theme": "System Default", "notifications": True, "font_scale": "Medium"}
                    return data
            return {
                "projects": [], 
                "settings": {"theme": "System Default", "notifications": True, "font_scale": "Medium"}
            }
        except Exception as e:
            print(f"Error loading data: {e}")
            return {
                "projects": [], 
                "settings": {"theme": "System Default", "notifications": True, "font_scale": "Medium"}
            }

    def save_data(self):
        try:
            with open("app_data.json", "w") as f:
                json.dump(self.app_data, f)
        except Exception as e:
            print(f"Error saving data: {e}")

    def on_window_resize(self, window, width, height):
        scale = min(width / 1920, height / 1080) * 1.1
        font_scale = {"Small": 14/16, "Medium": 16/16, "Large": 18/16, "ExtraLarge": 20/16}.get(
            self.app_data.get("settings", {}).get("font_scale", "Medium"), 16/16
        )
        base_font_size = 24  # 1.5x from 16
        base_header_size = 54  # 1.5x from 36
        base_button_size = 30  # 1.5x from 20
        if self.root:
            for screen in self.root.screens:
                screen.font_size = base_font_size * scale * font_scale
                for widget in screen.walk():
                    if hasattr(widget, 'font_size'):
                        if isinstance(widget, Label) and 'header' in widget.text.lower():
                            widget.font_size = f'{base_header_size * scale * font_scale}sp'
                        elif isinstance(widget, Factory.CustomButton):
                            widget.font_size = f'{base_button_size * scale * font_scale}sp'
                        else:
                            widget.font_size = f'{base_font_size * scale * font_scale}sp'
                    if hasattr(widget, 'padding') and isinstance(widget, Screen):
                        widget.padding = 20 if width < 1400 else 30
                    if hasattr(widget, 'spacing') and isinstance(widget, Screen):
                        widget.spacing = 15 if width < 1400 else 20

    def on_stop(self):
        self.save_data()

if __name__ == "__main__":
    MainApp().run()