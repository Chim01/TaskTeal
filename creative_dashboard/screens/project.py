from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.factory import Factory
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from datetime import datetime, timedelta
import re

class CenteredTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(text=self.on_text)

    def on_text(self, instance, value):
        if not value:
            self.canvas.after.clear()
            with self.canvas.after:
                Color(*self.hint_text_color)
                text_width = self._get_text_width(self.hint_text, self.tab_width, self._label_cached)
                pos_x = self.center_x - text_width / 2
                pos_y = self.center_y - self.font_size / 2
                Rectangle(pos=(pos_x, pos_y), size=(text_width, self.font_size))

class ProjectScreen(Screen):
    category = StringProperty("General")
    due_date = StringProperty("")
    recurrence = StringProperty("None")
    search_text = StringProperty("")
    sort_by = StringProperty("Name")
    filter_status = StringProperty("All")
    filter_recurrence = StringProperty("All")
    font_size = NumericProperty(16)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(search_text=self.update_project_list)
        self.bind(sort_by=self.update_project_list)
        self.bind(filter_status=self.update_project_list)
        self.bind(filter_recurrence=self.update_project_list)

    def set_category(self, value):
        self.category = value

    def set_due_date(self, value):
        if re.match(r"\d{4}-\d{2}-\d{2}", value):
            try:
                datetime.strptime(value, "%Y-%m-%d")
                self.due_date = value
            except ValueError:
                self.due_date = ""
                self.due_date_input.text = ""
                print("Invalid date format")
        else:
            self.due_date = ""
            self.due_date_input.text = ""

    def set_recurrence(self, value):
        self.recurrence = value

    def set_search_text(self, value):
        self.search_text = value.lower()
        Clock.schedule_once(lambda dt: self.update_project_list(), 0.1)

    def set_sort_by(self, value):
        self.sort_by = value
        self.update_project_list()

    def set_filter_status(self, value):
        self.filter_status = value
        self.update_project_list()

    def set_filter_recurrence(self, value):
        self.filter_recurrence = value
        self.update_project_list()

    def add_project(self):
        name = self.project_input.text.strip()
        if not name:
            print("Project name cannot be empty")
            return
        app = App.get_running_app()
        due_date = self.due_date  # No default to today
        project = {
            "name": name,
            "category": self.category,
            "status": "Not Started",
            "emoji": "📌",
            "due_date": due_date,
            "recurrence": self.recurrence,
            "history": []
        }
        app.app_data["projects"] = app.app_data.get("projects", []) + [project]
        app.save_data()
        self.project_input.text = ""
        self.due_date = ""
        self.due_date_input.text = ""
        self.recurrence = "None"
        self.recurrence_spinner.text = "None"
        self.update_project_list()

    def delete_project(self, project):
        app = App.get_running_app()
        projects = app.app_data.get("projects", [])
        if project in projects:
            projects.remove(project)
            app.app_data["projects"] = projects
            app.save_data()
            self.update_project_list()

    def reset_projects(self):
        app = App.get_running_app()
        app.app_data["projects"] = []
        app.save_data()
        self.update_project_list()

    def update_project_list(self, *args):
        try:
            self.project_list.clear_widgets()
            app = App.get_running_app()
            projects = app.app_data.get("projects", [])
            print(f"Updating project list with {len(projects)} projects")
            filtered = [
                p for p in projects
                if (self.filter_status == "All" or
                    (self.filter_status == "Active" and p.get("status") in ["Not Started", "In Progress"]) or
                    (self.filter_status == "Completed" and p.get("status") == "Completed"))
                and (self.filter_recurrence == "All" or p.get("recurrence") == self.filter_recurrence)
                and (not self.search_text or self.search_text in p.get("name", "").lower())
            ]
            if self.sort_by == "Name":
                filtered.sort(key=lambda x: x.get("name", "").lower())
            elif self.sort_by == "Date":
                filtered.sort(key=lambda x: x.get("due_date", "9999-12-31"))
            elif self.sort_by == "Status":
                filtered.sort(key=lambda x: ["Not Started", "In Progress", "Completed"].index(x.get("status", "Not Started")))

            for project in filtered:
                layout = BoxLayout(size_hint_y=None, height=48, spacing=10)
                due_date = project.get("due_date", "No Due Date")
                label = Label(
                    text=f"📌 {project.get('name')} - Due: {due_date} [{project.get('status')}] [{project.get('recurrence')}]",
                    font_name="assets/fonts/seguiemj.ttf",
                    font_size=str(self.font_size) + 'sp',
                    size_hint_x=0.6,
                    color=[1, 1, 1, 1]
                )
                edit_btn = Factory.CustomButton(
                    text="✏️ Edit",
                    font_name="assets/fonts/seguiemj.ttf",
                    font_size=str(self.font_size * 0.8) + 'sp',
                    size_hint_x=0.2,
                    size=(60, 45)
                )
                delete_btn = Factory.CustomButton(
                    text="✖️ Delete",
                    font_name="assets/fonts/seguiemj.ttf",
                    font_size=str(self.font_size * 0.8) + 'sp',
                    size_hint_x=0.2,
                    size=(60, 45)
                )
                edit_btn.bind(on_press=lambda instance, p=project: self.show_edit_popup(p))
                delete_btn.bind(on_press=lambda instance, p=project: self.delete_project(p))
                layout.add_widget(label)
                layout.add_widget(edit_btn)
                layout.add_widget(delete_btn)
                self.project_list.add_widget(layout)
        except Exception as e:
            print(f"Error updating project list: {e}")

    def show_edit_popup(self, project):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        name_input = CenteredTextInput(
            text=project.get("name", ""),
            hint_text="Project name",
            font_name="assets/fonts/seguiemj.ttf",
            font_size=str(self.font_size) + 'sp',
            multiline=False
        )
        category_spinner = Spinner(
            text=project.get("category", "General"),
            values=['General', 'Work', 'Personal', 'Hobby'],
            font_name="assets/fonts/seguiemj.ttf",
            font_size=str(self.font_size) + 'sp'
        )
        due_date_input = CenteredTextInput(
            text=project.get("due_date", ""),
            hint_text="YYYY-MM-DD",
            font_name="assets/fonts/seguiemj.ttf",
            font_size=str(self.font_size) + 'sp',
            multiline=False
        )
        recurrence_spinner = Spinner(
            text=project.get("recurrence", "None"),
            values=['None', 'Daily', 'Weekly', 'Monthly'],
            font_name="assets/fonts/seguiemj.ttf",
            font_size=str(self.font_size) + 'sp'
        )
        status_spinner = Spinner(
            text=project.get("status", "Not Started"),
            values=['Not Started', 'In Progress', 'Completed'],
            font_name="assets/fonts/seguiemj.ttf",
            font_size=str(self.font_size) + 'sp'
        )
        buttons = BoxLayout(size_hint_y=None, height=45, spacing=10)
        cancel_btn = Factory.CustomButton(
            text='Cancel',
            font_size=str(self.font_size) + 'sp'
        )
        save_btn = Factory.CustomButton(
            text='Save',
            font_size=str(self.font_size) + 'sp',
            on_press=lambda x: self.save_project(project, name_input.text, category_spinner.text, 
                                               due_date_input.text, recurrence_spinner.text, 
                                               status_spinner.text, popup)
        )
        buttons.add_widget(cancel_btn)
        buttons.add_widget(save_btn)
        content.add_widget(Label(text="Edit Project", font_name="assets/fonts/seguiemj.ttf", font_size=str(self.font_size) + 'sp'))
        content.add_widget(name_input)
        content.add_widget(category_spinner)
        content.add_widget(due_date_input)
        content.add_widget(recurrence_spinner)
        content.add_widget(status_spinner)
        content.add_widget(buttons)
        popup = Popup(title='Edit Project', content=content, size_hint=(0.6, 0.7))
        popup.open()

    def save_project(self, project, name, category, due_date, recurrence, status, popup):
        try:
            if not name.strip():
                print("Project name cannot be empty")
                return
            app = App.get_running_app()
            old_data = project.copy()
            project["name"] = name.strip()
            project["category"] = category
            project["recurrence"] = recurrence
            project["status"] = status
            project["due_date"] = due_date if re.match(r"\d{4}-\d{2}-\d{2}", due_date) else ""
            if project["due_date"]:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    project["due_date"] = ""
                    print("Invalid date format")
            project["history"].append({
                "timestamp": datetime.now().isoformat(),
                "old": old_data,
                "new": project.copy()
            })
            app.save_data()
            self.update_project_list()
            popup.dismiss()
        except Exception as e:
            print(f"Error saving project: {e}")