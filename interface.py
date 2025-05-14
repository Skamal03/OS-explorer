import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from main import Kernel

class OSControlPanel:
    def __init__(self, master):
        self.master = master
        self.master.title("MySimOS - Main Control Panel")
        self.kernel = Kernel()

        tk.Label(master, text="MySimOS Kernel Control Panel", font=("Arial", 16), fg="blue").pack(pady=10)

        buttons = [
            ("Process Management", self.process_management_menu),
            ("Process Scheduler", self.scheduler_menu),
            ("Memory Management", self.not_implemented),
            ("I/O Management", self.not_implemented),
            ("Other Operations", self.not_implemented)
        ]

        for text, cmd in buttons:
            tk.Button(master, text=text, width=40, command=cmd).pack(pady=5)

    def process_management_menu(self):
        win = tk.Toplevel(self.master)
        win.title("Process Management")

        tk.Label(win, text="Process Management Panel", font=("Arial", 14)).pack(pady=5)

        actions = [
            ("Create a Process", self.create_process),
            ("Destroy a Process", self.destroy_process),
            ("Suspend a Process", lambda: self.change_state("suspended")),
            ("Resume a Process", lambda: self.change_state("ready")),
            ("Block a Process", lambda: self.change_state("blocked")),
            ("Wakeup a Process", lambda: self.change_state("ready")),
            ("Dispatch a Process", lambda: self.change_state("running")),
            ("Change Process Priority", self.change_priority),
            ("Process Communication", self.process_communication),
            ("Show All Processes (Table)", self.show_all_processes_table),
            ("Show PCB by PID (Table)", self.show_pcb_table)
        ]

        for text, cmd in actions:
            tk.Button(win, text=text, width=40, command=cmd).pack(pady=2)

    def scheduler_menu(self):
        win = tk.Toplevel(self.master)
        win.title("Process Scheduler")

        tk.Label(win, text="Process Scheduler Panel", font=("Arial", 14)).pack(pady=5)

        buttons = [
            ("Dispatch (FCFS)", self.dispatch_fcfs),
            ("Dispatch (Priority)", self.dispatch_priority),
            ("Show All Queues", self.show_queues)
        ]

        for text, cmd in buttons:
            tk.Button(win, text=text, width=40, command=cmd).pack(pady=2)

    # Process Management Methods
    def create_process(self):
        name = simpledialog.askstring("Create Process", "Enter process name:")
        burst = simpledialog.askinteger("Burst Time", "Enter burst time for the process:", minvalue=1)
        priority = simpledialog.askinteger("Priority", "Enter priority (0-10):", minvalue=0, maxvalue=10)
        arrival = simpledialog.askinteger("Arrival Time", "Enter arrival time for the process:", minvalue=0)

        if name and burst is not None and priority is not None and arrival is not None:
            p = self.kernel.create_process(name, priority, burst, arrival)
            messagebox.showinfo("Process Created",
                                f"PID: {p.pid}\nName: {p.name}\nPriority: {p.priority}\nBurst Time: {p.burst}\nArrival Time: {p.arrival}")

    def destroy_process(self):
        pid = simpledialog.askstring("Destroy Process", "Enter PID:")
        if pid and self.kernel.destroy_process(pid):
            messagebox.showinfo("Success", f"Process {pid} destroyed.")
        else:
            messagebox.showerror("Error", "Process not found.")

    def change_state(self, state):
        pid = simpledialog.askstring("Change State", f"Enter PID to set to '{state}':")
        if pid and self.kernel.change_state(pid, state):
            messagebox.showinfo("Updated", f"Process {pid} state changed to {state}.")
        else:
            messagebox.showerror("Error", "Process not found.")

    def change_priority(self):
        pid = simpledialog.askstring("Change Priority", "Enter PID:")
        new_priority = simpledialog.askinteger("New Priority", "Enter priority (0-10):", minvalue=0, maxvalue=10)
        if pid and new_priority is not None and self.kernel.change_priority(pid, new_priority):
            messagebox.showinfo("Updated", f"Priority of {pid} changed to {new_priority}.")
        else:
            messagebox.showerror("Error", "Invalid input.")

    def process_communication(self):
        sender = simpledialog.askstring("Sender PID", "Enter sender PID:")
        receiver = simpledialog.askstring("Receiver PID", "Enter receiver PID:")
        message = simpledialog.askstring("Message", "Enter message:")
        if all([sender, receiver, message]):
            result = self.kernel.process_communicate(sender, receiver, message)
            if result:
                messagebox.showinfo("Message Sent", result)
            else:
                messagebox.showerror("Error", "Invalid PID(s)")
        else:
            messagebox.showerror("Error", "Incomplete input.")

    def show_all_processes_table(self):
        data = self.kernel.list_all_processes()
        if not data:
            messagebox.showinfo("No Data", "No processes available.")
            return
        win = tk.Toplevel(self.master)
        win.title("All Processes")

        cols = ("PID", "Name", "State", "Priority", "Burst Time")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
        for p in data:
            tree.insert("", "end", values=(p.pid, p.name, p.state, p.priority, p.burst))
        tree.pack(fill="both", expand=True)

    def show_pcb_table(self):
        pid = simpledialog.askstring("Enter PID", "Enter PID to view PCB:")
        pcb = self.kernel.get_pcb_info(pid)
        if not pcb:
            messagebox.showerror("Not Found", "Process not found.")
            return
        win = tk.Toplevel(self.master)
        win.title("PCB Information")

        tree = ttk.Treeview(win, columns=("Attribute", "Value"), show="headings")
        tree.heading("Attribute", text="Attribute")
        tree.heading("Value", text="Value")
        for key, val in pcb.items():
            tree.insert("", "end", values=(key, str(val)))
        tree.pack(fill="both", expand=True)

    def not_implemented(self):
        messagebox.showinfo("Coming Soon", "This module is not implemented yet.")

    # Process Scheduler Methods
    def dispatch_fcfs(self):
        processes = self.kernel.list_all_processes()
        if not processes:
            messagebox.showerror("Error", "No processes available for FCFS scheduling.")
            return

        processes.sort(key=lambda p: p.arrival)

        current_time = 0
        total_waiting_time = 0
        total_turnaround_time = 0

        # Create a new window for the scheduling result table
        win = tk.Toplevel(self.master)
        win.title("FCFS Scheduling Result")

        cols = ("PID", "Arrival", "Burst", "Start", "Finish", "Waiting", "Turnaround")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        for p in processes:
            start_time = max(current_time, p.arrival)
            finish_time = start_time + p.burst
            waiting_time = start_time - p.arrival
            turnaround_time = finish_time - p.arrival

            total_waiting_time += waiting_time
            total_turnaround_time += turnaround_time
            current_time = finish_time

            # Insert data into the table
            tree.insert("", "end",
                        values=(p.pid, p.arrival, p.burst, start_time, finish_time, waiting_time, turnaround_time))

        avg_waiting_time = total_waiting_time / len(processes)
        avg_turnaround_time = total_turnaround_time / len(processes)

        # Add average waiting and turnaround times at the bottom of the table
        tree.insert("", "end",
                    values=("Average", "", "", "", "", f"{avg_waiting_time:.2f}", f"{avg_turnaround_time:.2f}"))

    def dispatch_priority(self):
        processes = self.kernel.list_all_processes()
        if not processes:
            messagebox.showerror("Error", "No processes available for Priority scheduling.")
            return

        processes.sort(key=lambda p: (p.priority, p.arrival))

        current_time = 0
        total_waiting_time = 0
        total_turnaround_time = 0

        # Create a new window for the scheduling result table
        win = tk.Toplevel(self.master)
        win.title("Priority Scheduling Result")

        cols = ("PID", "Arrival", "Burst", "Priority", "Start", "Finish", "Waiting", "Turnaround")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        for p in processes:
            start_time = max(current_time, p.arrival)
            finish_time = start_time + p.burst
            waiting_time = start_time - p.arrival
            turnaround_time = finish_time - p.arrival

            total_waiting_time += waiting_time
            total_turnaround_time += turnaround_time
            current_time = finish_time

            # Insert data into the table
            tree.insert("", "end", values=(
            p.pid, p.arrival, p.burst, p.priority, start_time, finish_time, waiting_time, turnaround_time))

        avg_waiting_time = total_waiting_time / len(processes)
        avg_turnaround_time = total_turnaround_time / len(processes)

        # Add average waiting and turnaround times at the bottom of the table
        tree.insert("", "end",
                    values=("Average", "", "", "", "", f"{avg_waiting_time:.2f}", f"{avg_turnaround_time:.2f}"))

    def show_queues(self):
        queues = self.kernel.scheduler.get_queues()
        win = tk.Toplevel(self.master)
        win.title("Scheduler Queues")

        tree = ttk.Treeview(win, columns=("Queue", "Processes"), show="headings")
        tree.heading("Queue", text="Queue")
        tree.heading("Processes", text="Processes")
        for queue_name, procs in queues.items():
            tree.insert("", "end", values=(queue_name, ", ".join([p.pid for p in procs])))
        tree.pack(fill="both", expand=True)


