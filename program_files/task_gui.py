import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw
import pystray
import threading

PH_TZ = timezone(timedelta(hours=8))  # UTC+8 for Philippines


# ====== FILE SETUP ======
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(BASE_DIR, "tasks.json")

# ====== TASK FUNCTIONS ======
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def get_new_id(tasks):
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


# ====== GUI CLASS ======
class TaskGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Tracker")
        self.geometry("900x600")
        self.configure(bg="#0f172a")

        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.icon = None  # tray icon instance

        self.create_widgets()
        self.load_task_list()

    def create_widgets(self):
        accent = "#38bdf8"
        text_light = "#e2e8f0"
        text_dim = "#94a3b8"

        header = tk.Label(
            self, text="⚡ Task Tracker", font=("Segoe UI", 22, "bold"),
            bg="#0f172a", fg=accent
        )
        header.pack(pady=(15, 5))

        instruction = tk.Label(
            self, text="Type your task below and click 'Add Task' or press Enter.",
            font=("Segoe UI", 10), bg="#0f172a", fg=text_dim
        )
        instruction.pack(pady=(0, 10))

        input_frame = tk.Frame(self, bg="#0f172a")
        input_frame.pack(pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.TEntry", fieldbackground="#1e293b",
            foreground=text_light, borderwidth=0, relief="flat", padding=8
        )
        style.configure(
            "Custom.TButton", background=accent, foreground="#0f172a",
            font=("Segoe UI", 10, "bold"), padding=6
        )
        style.map("Custom.TButton",
            background=[("active", "#0ea5e9"), ("!active", "#38bdf8")])

        style.configure(
            "Treeview", background="#1e293b", foreground=text_light,
            fieldbackground="#1e293b", rowheight=25, font=("Segoe UI", 10)
        )
        style.configure("Treeview.Heading", background=accent, foreground="#0f172a",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#0ea5e9")],
                  foreground=[("selected", "#0f172a")])

        self.desc_entry = ttk.Entry(input_frame, width=45, style="Custom.TEntry")
        self.desc_entry.pack(side=tk.LEFT, padx=5)
        self.desc_entry.focus()
        self.desc_entry.bind("<Return>", lambda e: self.add_task())

        add_btn = ttk.Button(input_frame, text="➕ Add/Update Task", command=self.add_task, style="Custom.TButton")
        add_btn.pack(side=tk.LEFT, padx=5)

        columns = ("id", "description", "status", "createdAt", "updatedAt")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        btn_frame = tk.Frame(self, bg="#0f172a")
        btn_frame.pack(pady=10)

        btns = [
            ("🚀 In Progress", lambda: self.update_status("in-progress")),
            ("✅ Mark Done", lambda: self.update_status("done")),
            ("✏️ Update Task", self.update_task),
            ("🗑 Delete Task", self.delete_task),
            ("🔄 Refresh", self.load_task_list)
        ]
        for i, (label, cmd) in enumerate(btns):
            btn = ttk.Button(btn_frame, text=label, command=cmd, style="Custom.TButton")
            btn.grid(row=0, column=i, padx=6)

        filter_frame = tk.Frame(self, bg="#0f172a")
        filter_frame.pack(pady=(10, 10))
        tk.Label(filter_frame, text="Filter by:", bg="#0f172a", fg=text_light,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.status_filter = ttk.Combobox(
            filter_frame, values=["All", "todo", "in-progress", "done"],
            state="readonly", width=15
        )
        self.status_filter.set("All")
        self.status_filter.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Apply", command=self.load_task_list, style="Custom.TButton").pack(side=tk.LEFT, padx=5)

    def load_task_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        tasks = load_tasks()
        status_filter = self.status_filter.get()
        for idx, t in enumerate(tasks):
            if status_filter != "All" and t["status"] != status_filter:
                continue
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=(t["id"], t["description"], t["status"],
                                                 t["createdAt"], t["updatedAt"]), tags=(tag,))
        self.tree.tag_configure('oddrow', background="#1e293b")
        self.tree.tag_configure('evenrow', background="#161e2a")

    def add_task(self):
        desc = self.desc_entry.get().strip()
        if not desc:
            messagebox.showwarning("Warning", "Task description cannot be empty.")
            return
        tasks = load_tasks()
        new_task = {
            "id": get_new_id(tasks),
            "description": desc,
            "status": "todo",
            "createdAt": datetime.now(PH_TZ).isoformat(timespec='seconds'),
            "updatedAt": datetime.now(PH_TZ).isoformat(timespec='seconds')
        }
        tasks.append(new_task)
        save_tasks(tasks)
        self.desc_entry.delete(0, tk.END)
        self.load_task_list()

    def get_selected_task(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "No task selected.")
            return None
        values = self.tree.item(selected, "values")
        tasks = load_tasks()
        for t in tasks:
            if t["id"] == int(values[0]):
                return t
        return None

    def update_status(self, status):
        task = self.get_selected_task()
        if not task:
            return
        task["status"] = status
        task["updatedAt"] = datetime.now().isoformat(timespec='seconds')
        tasks = load_tasks()
        for idx, t in enumerate(tasks):
            if t["id"] == task["id"]:
                tasks[idx] = task
        save_tasks(tasks)
        self.load_task_list()

    def update_task(self):
        task = self.get_selected_task()
        if not task:
            return
        new_desc = self.desc_entry.get().strip()
        if not new_desc:
            messagebox.showwarning("Warning", "Task description cannot be empty.")
            return
        task["description"] = new_desc
        task["updatedAt"] = datetime.now().isoformat(timespec='seconds')
        tasks = load_tasks()
        for idx, t in enumerate(tasks):
            if t["id"] == task["id"]:
                tasks[idx] = task
        save_tasks(tasks)
        self.desc_entry.delete(0, tk.END)
        self.load_task_list()

    def delete_task(self):
        task = self.get_selected_task()
        if not task:
            return
        tasks = load_tasks()
        tasks = [t for t in tasks if t["id"] != task["id"]]
        save_tasks(tasks)
        self.load_task_list()

    # ====== TRAY ICON ======
    def minimize_to_tray(self):
        """Hide the main window and show tray icon"""
        self.withdraw()
        image = self.create_icon_image()

        menu = (
            pystray.MenuItem("Show Task Tracker", self.restore_from_tray),
            pystray.MenuItem("Exit", self.exit_from_tray)
        )
        self.icon = pystray.Icon("TaskTracker", image, "Task Tracker", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def restore_from_tray(self, icon=None, item=None):
        """Restore the window from tray"""
        if self.icon:
            self.icon.stop()
        self.deiconify()

    def exit_from_tray(self, icon=None, item=None):
        """Completely exit the app"""
        if self.icon:
            self.icon.stop()
        self.destroy()

    def create_icon_image(self, color="#38bdf8", size=64):
        """Create a simple tray icon image"""
        image = Image.new("RGB", (size, size), color)
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, size, size), fill=color)
        draw.text((size//4, size//4), "⚡", fill="white")
        return image


# ====== RUN APP ======
if __name__ == "__main__":
    app = TaskGUI()
    app.mainloop()
