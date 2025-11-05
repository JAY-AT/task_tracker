import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from task_cli import load_tasks, save_tasks, get_new_id, find_task  # reuse CLI logic

TASKS_FILE = "tasks.json"

class TaskTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Tracker")
        self.geometry("700x500")
        self.configure(bg="#f5f5f5")

        self.create_widgets()
        self.load_task_list()

    def create_widgets(self):
        # Header
        header = tk.Label(self, text="📝 Task Tracker", font=("Segoe UI", 20, "bold"), bg="#f5f5f5", fg="#333")
        header.pack(pady=10)

        # Input frame
        input_frame = tk.Frame(self, bg="#f5f5f5")
        input_frame.pack(pady=5)

        self.desc_entry = ttk.Entry(input_frame, width=50)
        self.desc_entry.pack(side=tk.LEFT, padx=5)
        self.desc_entry.insert(0, "Enter new task description...")

        add_btn = ttk.Button(input_frame, text="Add Task", command=self.add_task)
        add_btn.pack(side=tk.LEFT, padx=5)

        # Task list
        columns = ("id", "description", "status", "createdAt", "updatedAt")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("description", text="Description")
        self.tree.heading("status", text="Status")
        self.tree.heading("createdAt", text="Created")
        self.tree.heading("updatedAt", text="Updated")

        for col in columns:
            self.tree.column(col, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Button frame
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Mark In Progress", command=lambda: self.update_status("in-progress")).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Mark Done", command=lambda: self.update_status("done")).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Update Task", command=self.update_task).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_task_list).grid(row=0, column=4, padx=5)

        # Filter dropdown
        filter_frame = tk.Frame(self, bg="#f5f5f5")
        filter_frame.pack(pady=5)
        tk.Label(filter_frame, text="Filter by:", bg="#f5f5f5").pack(side=tk.LEFT, padx=5)
        self.status_filter = ttk.Combobox(filter_frame, values=["All", "todo", "in-progress", "done"], state="readonly")
        self.status_filter.set("All")
        self.status_filter.pack(side=tk.LEFT)
        ttk.Button(filter_frame, text="Apply", command=self.load_task_list).pack(side=tk.LEFT, padx=5)

    def add_task(self):
        desc = self.desc_entry.get().strip()
        if not desc or desc == "Enter new task description...":
            messagebox.showwarning("Input Error", "Please enter a valid task description.")
            return
        tasks = load_tasks()
        new_task = {
            "id": get_new_id(tasks),
            "description": desc,
            "status": "todo",
            "createdAt": datetime.now().isoformat(timespec='seconds'),
            "updatedAt": datetime.now().isoformat(timespec='seconds')
        }
        tasks.append(new_task)
        save_tasks(tasks)
        self.desc_entry.delete(0, tk.END)
        self.load_task_list()
        messagebox.showinfo("Success", "Task added successfully!")

    def update_status(self, new_status):
        selected = self.get_selected_task()
        if not selected:
            return
        task_id = int(selected["id"])
        tasks = load_tasks()
        task = find_task(tasks, task_id)
        if not task:
            messagebox.showerror("Error", "Task not found.")
            return
        task["status"] = new_status
        task["updatedAt"] = datetime.now().isoformat(timespec='seconds')
        save_tasks(tasks)
        self.load_task_list()
        messagebox.showinfo("Updated", f"Task marked as {new_status}.")

    def update_task(self):
        selected = self.get_selected_task()
        if not selected:
            return
        new_desc = tk.simpledialog.askstring("Update Task", "Enter new description:", initialvalue=selected["description"])
        if not new_desc:
            return
        tasks = load_tasks()
        task = find_task(tasks, int(selected["id"]))
        if not task:
            messagebox.showerror("Error", "Task not found.")
            return
        task["description"] = new_desc
        task["updatedAt"] = datetime.now().isoformat(timespec='seconds')
        save_tasks(tasks)
        self.load_task_list()
        messagebox.showinfo("Updated", "Task updated successfully.")

    def delete_task(self):
        selected = self.get_selected_task()
        if not selected:
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Delete task #{selected['id']}?")
        if not confirm:
            return
        tasks = [t for t in load_tasks() if t["id"] != int(selected["id"])]
        save_tasks(tasks)
        self.load_task_list()
        messagebox.showinfo("Deleted", "Task deleted successfully.")

    def load_task_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        tasks = load_tasks()
        filter_val = self.status_filter.get()
        if filter_val != "All":
            tasks = [t for t in tasks if t["status"] == filter_val]
        for t in tasks:
            self.tree.insert("", tk.END, values=(t["id"], t["description"], t["status"], t["createdAt"], t["updatedAt"]))

    def get_selected_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a task first.")
            return None
        values = self.tree.item(selected[0], "values")
        return {
            "id": values[0],
            "description": values[1],
            "status": values[2],
            "createdAt": values[3],
            "updatedAt": values[4],
        }


if __name__ == "__main__":
    app = TaskTrackerApp()
    app.mainloop()
