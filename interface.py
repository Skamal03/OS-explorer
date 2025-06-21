import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from main import Kernel
import socket
import json

class OSControlPanel:
    def __init__(self, root):
        self.master = root
        self.master.title("SimOS - Control Panel")
        self.master.geometry("600x600")
        self.kernel = Kernel()

        # Configure styles
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=8, font=("Arial", 10))
        style.configure("Heading.TLabel", font=("Arial", 16, "bold"))
        style.configure("Group.TLabel", font=("Arial", 12, "bold"))

        # Header
        ttk.Label(self.master, text="SimOS Control Panel", style="Heading.TLabel").pack(pady=20)

        # Notebook for tabs
        notebook = ttk.Notebook(self.master)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Process Management Tab
        process_tab = ttk.Frame(notebook)
        self.process_management_tab(process_tab)
        notebook.add(process_tab, text="Process Management")

        # Scheduler Tab
        scheduler_tab = ttk.Frame(notebook)
        self.scheduler_tab(scheduler_tab)
        notebook.add(scheduler_tab, text="Scheduler")

        # Memory Management Tab
        memory_tab = ttk.Frame(notebook)
        self.memory_management_tab(memory_tab)
        notebook.add(memory_tab, text="Memory Management")

        # Synchronization Tab
        sync_tab = ttk.Frame(notebook)
        self.synchronization_tab(sync_tab)
        notebook.add(sync_tab, text="Synchronization")

        # Distributed OS Tab
        dist_tab = ttk.Frame(notebook)
        self.distributed_os_tab(dist_tab)
        notebook.add(dist_tab, text="Distributed OS")

    def process_management_tab(self, parent):
        ttk.Label(parent, text="Process Management", style="Group.TLabel").pack(pady=10)
        actions = [
            ("Create Process", self.create_process),
            ("Destroy Process", self.destroy_process),
            ("Suspend Process", lambda: self.change_state("suspended")),
            ("Resume Process", lambda: self.change_state("ready")),
            ("Block Process", lambda: self.change_state("blocked")),
            ("Wakeup Process", lambda: self.change_state("ready")),
            ("Dispatch Process", self.dispatch_process),
            ("Change Priority", self.change_priority),
            ("Process Communication", self.process_communicate),
            ("List All Processes", self.show_all_processes),
            ("View PCB Info", self.show_pcb_info)
        ]
        for text, cmd in actions:
            ttk.Button(parent, text=text, command=cmd, width=30).pack(pady=5, padx=10)

    def scheduler_tab(self, parent):
        ttk.Label(parent, text="Scheduler", style="Group.TLabel").pack(pady=10)
        actions = [
            ("Run FCFS", self.run_fcfs),
            ("Run Priority", self.run_priority),
            ("View Queues", self.view_queues)
        ]
        for text, cmd in actions:
            ttk.Button(parent, text=text, command=cmd, width=30).pack(pady=5, padx=10)

    def memory_management_tab(self, parent):
        ttk.Label(parent, text="Memory Management", style="Group.TLabel").pack(pady=10)
        actions = [
            ("Set Page Size", self.set_page_size),
            ("Simulate Paging", self.simulate_paging),
            ("Simulate LRU", self.simulate_lru),
            ("View Memory Map", self.view_memory_map)
        ]
        for text, cmd in actions:
            ttk.Button(parent, text=text, command=cmd, width=30).pack(pady=5, padx=10)

    def synchronization_tab(self, parent):
        ttk.Label(parent, text="Synchronization", style="Group.TLabel").pack(pady=10)
        actions = [
            ("Acquire Resource", self.acquire_resource),
            ("Release Resource", self.release_resource),
            ("View Resource Status", self.view_resource_status)
        ]
        for text, cmd in actions:
            ttk.Button(parent, text=text, command=cmd, width=30).pack(pady=5, padx=10)

    def distributed_os_tab(self, parent):
        ttk.Label(parent, text="Distributed OS", style="Group.TLabel").pack(pady=10)
        actions = [
            ("Create Remote Process", self.create_remote_process),
            ("View Remote Processes", self.view_remote_processes)
        ]
        for text, cmd in actions:
            ttk.Button(parent, text=text, command=cmd, width=30).pack(pady=5, padx=10)

    def create_process(self):
        try:
            name = simpledialog.askstring("Input", "Process Name:")
            priority = simpledialog.askinteger("Input", "Priority (0-10):", minvalue=0, maxvalue=10)
            burst = simpledialog.askinteger("Input", "Burst Time:", minvalue=1)
            arrival = simpledialog.askinteger("Input", "Arrival Time:", minvalue=0)
            if all([name, priority is not None, burst, arrival]):
                proc = self.kernel.create_process(name, priority, burst, arrival)
                messagebox.showinfo("Success", f"Created {proc}")
            else:
                raise ValueError("Incomplete input")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def destroy_process(self):
        try:
            pid = simpledialog.askstring("Input", "Enter PID:")
            if pid and self.kernel.destroy_process(pid):
                messagebox.showinfo("Success", f"Process {pid} destroyed")
            else:
                messagebox.showerror("Error", "Process not found")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def change_state(self, state):
        try:
            pid = simpledialog.askstring("Input", f"Enter PID to {state}:")
            if pid and self.kernel.change_state(pid, state):
                messagebox.showinfo("Success", f"Process {pid} set to {state}")
            else:
                messagebox.showerror("Error", "Process not found")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def change_priority(self):
        try:
            pid = simpledialog.askstring("Input", "Enter PID:")
            priority = simpledialog.askinteger("Input", "New Priority (0-10):", minvalue=0, maxvalue=10)
            if pid and priority is not None and self.kernel.change_priority(pid, priority):
                messagebox.showinfo("Success", f"Priority of {pid} set to {priority}")
            else:
                messagebox.showerror("Error", "Invalid input")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def process_communicate(self):
        try:
            mode = simpledialog.askstring("Input", "Mode (message, shared_memory_write, shared_memory_read):")
            if mode not in ["message", "shared_memory_write", "shared_memory_read"]:
                raise ValueError("Invalid mode")
            pid = simpledialog.askstring("Input", "Enter PID:")
            if mode == "message":
                receiver = simpledialog.askstring("Input", "Receiver PID:")
                message = simpledialog.askstring("Input", "Message:")
                if all([pid, receiver, message]):
                    result = self.kernel.process_communicate(pid, receiver, message, mode)
                    messagebox.showinfo("Success", result)
                else:
                    raise ValueError("Incomplete input")
            elif mode == "shared_memory_write":
                data = simpledialog.askstring("Input", "Data to write:")
                if pid and data:
                    result = self.kernel.process_communicate(pid, None, data, mode)
                    messagebox.showinfo("Success", result)
                else:
                    raise ValueError("Incomplete input")
            else:  # shared_memory_read
                if pid:
                    result = self.kernel.process_communicate(pid, None, None, mode)
                    messagebox.showinfo("Success", result)
                else:
                    raise ValueError("Incomplete input")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def dispatch_process(self):
        try:
            pid = simpledialog.askstring("Input", "Enter PID to dispatch:")
            if pid and self.kernel.change_state(pid, "running"):
                messagebox.showinfo("Success", f"Process {pid} dispatched")
            else:
                messagebox.showerror("Error", "Process not found")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_all_processes(self):
        try:
            procs = self.kernel.list_all_processes()
            if not procs:
                messagebox.showinfo("Info", "No processes")
                return
            win = tk.Toplevel(self.master)
            win.title("All Processes")
            tree = ttk.Treeview(win, columns=("PID", "Name", "State", "Priority", "Burst"), show="headings")
            for col in tree["columns"]:
                tree.heading(col, text=col)
            for p in procs:
                tree.insert("", "end", values=(p.pid, p.name, p.state, p.priority, p.burst))
            tree.pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_pcb_info(self):
        try:
            pid = simpledialog.askstring("Input", "Enter PID:")
            pcb = self.kernel.get_pcb_info(pid)
            if not pcb:
                messagebox.showerror("Error", "Process not found")
                return
            win = tk.Toplevel(self.master)
            win.title(f"PCB Info: {pid}")
            tree = ttk.Treeview(win, columns=("Attribute", "Value"), show="headings")
            tree.heading("Attribute", text="Attribute")
            tree.heading("Value", text="Value")
            for k, v in pcb.items():
                tree.insert("", "end", values=(k, str(v)))
            tree.pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_fcfs(self):
        try:
            procs = self.kernel.list_all_processes()
            if not procs:
                messagebox.showerror("Error", "No processes")
                return
            procs.sort(key=lambda p: p.arrival)
            current_time = 0
            results = []
            for p in procs:
                start = max(current_time, p.arrival)
                finish = start + p.burst
                wait = start - p.arrival
                turnaround = finish - p.arrival
                results.append((p.pid, p.arrival, p.burst, start, finish, wait, turnaround))
                current_time = finish
            self._show_schedule("FCFS", results)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_priority(self):
        try:
            procs = self.kernel.list_all_processes()
            if not procs:
                messagebox.showerror("Error", "No processes")
                return
            procs.sort(key=lambda p: (p.priority, p.arrival))
            current_time = 0
            results = []
            for p in procs:
                start = max(current_time, p.arrival)
                finish = start + p.burst
                wait = start - p.arrival
                turnaround = finish - p.arrival
                results.append((p.pid, p.arrival, p.burst, p.priority, start, finish, wait, turnaround))
                current_time = finish
            self._show_schedule("Priority", results, priority=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _show_schedule(self, title, results, priority=False):
        win = tk.Toplevel(self.master)
        win.title(f"{title} Schedule")
        cols = ["PID", "Arrival", "Burst"]
        if priority:
            cols.append("Priority")
        cols.extend(["Start", "Finish", "Wait", "Turnaround"])
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        for row in results:
            tree.insert("", "end", values=row)
        avg_wait = sum(r[-2] for r in results) / len(results)
        avg_turn = sum(r[-1] for r in results) / len(results)
        tree.insert("", "end", values=("Avg", "", "", "", "", "", f"{avg_wait:.2f}", f"{avg_turn:.2f}")[:len(cols)])
        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def view_queues(self):
        try:
            queues = self.kernel.scheduler.view_queues()
            win = tk.Toplevel(self.master)
            win.title("Queues")
            tree = ttk.Treeview(win, columns=("Queue", "Processes"), show="headings")
            tree.heading("Queue", text="Queue")
            tree.heading("Processes", text="Processes")
            tree.column("Queue", width=100)
            tree.column("Processes", width=400)
            for q, procs in queues.items():
                tree.insert("", "end", values=(q, ", ".join(p.pid for p in procs)))
            tree.pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def set_page_size(self):
        try:
            size = simpledialog.askinteger("Input", "Page Size (KB):", minvalue=1)
            if size:
                self.kernel.memory_manager.set_page_size(size)
                messagebox.showinfo("Success", f"Page size set to {size} KB")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def simulate_paging(self):
        try:
            pid = simpledialog.askstring("Input", "Enter PID to allocate pages:")
            proc = self.kernel.find_process(pid)
            if not proc:
                messagebox.showerror("Error", "Process not found")
                return
            frames = self.kernel.memory_manager.get_page_table(pid)
            if not frames:
                frames = self.kernel.memory_manager.allocate_memory(proc)
            win = tk.Toplevel(self.master)
            win.title(f"Page Table for {pid}")
            tree = ttk.Treeview(win, columns=("Page", "Frame"), show="headings")
            tree.heading("Page", text="Page")
            tree.heading("Frame", text="Frame")
            tree.column("Page", width=100)
            tree.column("Frame", width=100)
            for i, frame in enumerate(frames):
                tree.insert("", "end", values=(i, frame))
            tree.pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def simulate_lru(self):
        try:
            pages = simpledialog.askstring("Input", "Enter page references (comma-separated):")
            capacity = simpledialog.askinteger("Input", "Memory capacity (pages):", minvalue=1)
            if pages and capacity:
                pages = [int(p.strip()) for p in pages.split(",")]
                history, faults = self.kernel.memory_manager.simulate_lru(pages, capacity)
                win = tk.Toplevel(self.master)
                win.title("LRU Simulation")
                tree = ttk.Treeview(win, columns=("Page", "Memory", "Faults"), show="headings")
                tree.heading("Page", text="Page")
                tree.heading("Memory", text="Memory")
                tree.heading("Faults", text="Faults")
                tree.column("Page", width=100)
                tree.column("Memory", width=200)
                tree.column("Faults", width=100)
                for page, mem, fault in history:
                    tree.insert("", "end", values=(page, str(mem), fault))
                tree.pack(fill="both", expand=True, padx=10, pady=10)
                messagebox.showinfo("Result", f"Total Page Faults: {faults}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_memory_map(self):
        try:
            mem = self.kernel.memory_manager.view_memory_map()
            win = tk.Toplevel(self.master)
            win.title("Memory Map")
            tree = ttk.Treeview(win, columns=("Frame", "Content"), show="headings")
            tree.heading("Frame", text="Frame")
            tree.heading("Content", text="Content")
            tree.column("Frame", width=100)
            tree.column("Content", width=400)
            for frame, content in mem:
                tree.insert("", "end", values=(frame, content))
            tree.pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def acquire_resource(self):
        try:
            pid = simpledialog.askstring("Input", "Enter PID to acquire resource:")
            if pid:
                result = self.kernel.acquire_resource(pid)
                messagebox.showinfo("Success", result)
            else:
                raise ValueError("Invalid PID")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def release_resource(self):
        try:
            pid = simpledialog.askstring("Input", "Enter PID to release resource:")
            if pid:
                result = self.kernel.release_resource(pid)
                messagebox.showinfo("Success", result)
            else:
                raise ValueError("Invalid PID")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_resource_status(self):
        try:
            status = self.kernel.get_resource_status()
            messagebox.showinfo("Resource Status", status)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_remote_process(self):
        try:
            name = simpledialog.askstring("Input", "Process Name:")
            priority = simpledialog.askinteger("Input", "Priority (0-10):", minvalue=0, maxvalue=10)
            burst = simpledialog.askinteger("Input", "Burst Time:", minvalue=1)
            arrival = simpledialog.askinteger("Input", "Arrival Time:", minvalue=0)
            if all([name, priority is not None, burst, arrival]):
                # Connect to server
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(("localhost", 9999))  # Replace with server's actual IP
                    request = {
                        "action": "create_process",
                        "name": name,
                        "priority": priority,
                        "burst": burst,
                        "arrival": arrival
                    }
                    s.send(json.dumps(request).encode())
                    response = json.loads(s.recv(1024).decode())
                    if response["status"] == "success":
                        messagebox.showinfo("Success", f"Remote process created with PID: {response['pid']}")
                    else:
                        messagebox.showerror("Error", response["message"])
            else:
                raise ValueError("Incomplete input")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create remote process: {str(e)}")

    def view_remote_processes(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", 9999))  # Replace with server's actual IP
                request = {"action": "list_processes"}
                s.send(json.dumps(request).encode())
                response = json.loads(s.recv(1024).decode())
                if response["status"] == "success":
                    win = tk.Toplevel(self.master)
                    win.title("Remote Processes")
                    tree = ttk.Treeview(win, columns=("PID", "Name", "State"), show="headings")
                    tree.heading("PID", text="PID")
                    tree.heading("Name", text="Name")
                    tree.heading("State", text="State")
                    tree.column("PID", width=100)
                    tree.column("Name", width=200)
                    tree.column("State", width=100)
                    for proc in response["processes"]:
                        tree.insert("", "end", values=(proc["pid"], proc["name"], proc["state"]))
                    tree.pack(fill="both", expand=True, padx=10, pady=10)
                else:
                    messagebox.showerror("Error", response["message"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch remote processes: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OSControlPanel(root)
    root.mainloop()