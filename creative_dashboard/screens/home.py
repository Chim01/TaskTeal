from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App

class HomeScreen(Screen):
    progress_summary = StringProperty("")
    font_size = NumericProperty(16)

    def on_pre_enter(self):
        try:
            app = App.get_running_app()
            projects = app.app_data.get("projects", [])
            total = len(projects)
            completed = len([p for p in projects if p.get("status") == "Completed"])
            self.progress_summary = f"{completed}/{total} projects completed 📈" if total > 0 else "No projects yet! 📋"
        except Exception as e:
            print(f"Error updating home: {e}")
            self.progress_summary = "Error loading summary 😢"