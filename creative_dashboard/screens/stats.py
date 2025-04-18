from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App
from datetime import datetime, timedelta

class StatsScreen(Screen):
    stats_summary = StringProperty("")
    font_size = NumericProperty(16)

    def on_enter(self):
        try:
            app = App.get_running_app()
            projects = app.app_data.get("projects", [])
            total_projects = len(projects)
            completed = len([p for p in projects if p.get("status") == "Completed"])
            last_week = datetime.now().date() - timedelta(days=7)
            recent_projects = len([
                p for p in projects 
                if p.get("due_date") and datetime.strptime(p["due_date"], "%Y-%m-%d").date() >= last_week
            ])
            streaks = {}
            for p in projects:
                if p.get("recurrence", "None") != "None" and p.get("status") == "Completed":
                    key = (p["name"], p["recurrence"])
                    streaks[key] = streaks.get(key, 0) + 1
            streak_text = "\n".join([f"{name} 📈 {count} {rec} streak" for (name, rec), count in streaks.items()]) or "No streaks yet 📉"
            summary = (
                f"Total Projects: {total_projects} 📋\n"
                f"Completed: {completed} ✅\n"
                f"Projects Due Last Week: {recent_projects} 📅\n"
                f"Streaks:\n{streak_text}"
            )
            self.stats_summary = summary
        except Exception as e:
            print(f"Error loading stats: {e}")
            self.stats_summary = "Error loading stats 😢"