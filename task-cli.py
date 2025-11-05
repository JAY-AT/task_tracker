import sys
import json
import os
from datetime import datetime

TASKS_FILE = "tasks.json"


def load_tasks():
    """Load tasks from JSON file or return an empty list."""
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_tasks(tasks):
    """Save tasks to JSON file."""
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def get_new_id(tasks):
    """Generate a new unique ID."""
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1

def find_task(tasks, task_id):
    """Find a task by ID."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None

def print_task(task):
    """Print a single task in a nice format."""
    print(f"[{task['id']}] {task['description']} - {task['status']} "
          f"(Created: {task['createdAt']}, Updated: {task['updatedAt']})")


def add_task(description):
    tasks = load_tasks()
    new_task = {
        "id": get_new_id(tasks),
        "description": description,
        "status": "todo",
        "createdAt": datetime.now().isoformat(timespec='seconds'),
        "updatedAt": datetime.now().isoformat(timespec='seconds')
    }
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"✅ Task added successfully (ID: {new_task['id']})")

def update_task(task_id, new_description):
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    if not task:
        print("❌ Task not found.")
        return
    task["description"] = new_description
    task["updatedAt"] = datetime.now().isoformat(timespec='seconds')
    save_tasks(tasks)
    print("✏️ Task updated successfully.")

def delete_task(task_id):
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    if not task:
        print("❌ Task not found.")
        return
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    print("🗑️ Task deleted successfully.")

def mark_task(task_id, status):
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    if not task:
        print("❌ Task not found.")
        return
    task["status"] = status
    task["updatedAt"] = datetime.now().isoformat(timespec='seconds')
    save_tasks(tasks)
    print(f"🔄 Task marked as '{status}'.")

def list_tasks(filter_status=None):
    tasks = load_tasks()
    if not tasks:
        print("📭 No tasks found.")
        return
    filtered = tasks
    if filter_status:
        filtered = [t for t in tasks if t["status"] == filter_status]
        if not filtered:
            print(f"📭 No tasks with status '{filter_status}'.")
            return
    for t in filtered:
        print_task(t)


def show_help():
    print("""
📘 Task Tracker CLI Usage:
---------------------------
Add a new task:
    python task-cli.py add "Task description"

Update a task:
    python task-cli.py update <id> "New description"

Delete a task:
    python task-cli.py delete <id>

Mark a task as in-progress or done:
    python task-cli.py mark-in-progress <id>
    python task-cli.py mark-done <id>

List all tasks:
    python task-cli.py list

List tasks by status:
    python task-cli.py list todo
    python task-cli.py list in-progress
    python task-cli.py list done
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1]

    if command == "add" and len(sys.argv) >= 3:
        description = " ".join(sys.argv[2:])
        add_task(description)
    elif command == "update" and len(sys.argv) >= 4:
        try:
            task_id = int(sys.argv[2])
            description = " ".join(sys.argv[3:])
            update_task(task_id, description)
        except ValueError:
            print("❌ Invalid task ID.")
    elif command == "delete" and len(sys.argv) == 3:
        try:
            delete_task(int(sys.argv[2]))
        except ValueError:
            print("❌ Invalid task ID.")
    elif command == "mark-in-progress" and len(sys.argv) == 3:
        try:
            mark_task(int(sys.argv[2]), "in-progress")
        except ValueError:
            print("❌ Invalid task ID.")
    elif command == "mark-done" and len(sys.argv) == 3:
        try:
            mark_task(int(sys.argv[2]), "done")
        except ValueError:
            print("❌ Invalid task ID.")
    elif command == "list":
        if len(sys.argv) == 3:
            status = sys.argv[2]
            if status not in ["todo", "in-progress", "done"]:
                print("❌ Invalid status. Use: todo, in-progress, done.")
                return
            list_tasks(status)
        else:
            list_tasks()
    else:
        show_help()

if __name__ == "__main__":
    main()
