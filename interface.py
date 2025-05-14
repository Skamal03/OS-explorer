import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from main import Kernel

class OSControlPanel:
    def __init__(self, root):
        self.master = root
        self.master.title("OS-Explorer - Control Panel")
        style = ttk.Style(root)
        style.theme_use('clam')

        style.configure('TButton', padding=6, relief='raised', font=('Segoe UI', 10))
        style.map('TButton',
                  foreground=[('active', 'red')],
                  background=[('active', '#f0f0f0')])

        style.configure('Heading.TLabel', font=('Arial', 18, 'bold'), foreground='#333')

        style.configure('Group.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#555', padding=(0, 10))

        self.kernel = Kernel()

        ttk.Label(root, text="MySimOS Kernel Control Panel", style='Heading.TLabel').pack(pady=20)

        notebook = ttk.Notebook(root)

        process_tab = ttk.Frame(notebook)
        self.process_management_tab(process_tab)
        notebook.add(process_tab, text='Process Management')

        # Scheduler Tab
        scheduler_tab = ttk.Frame(notebook)
        self.scheduler_tab(scheduler_tab)
        notebook.add(scheduler_tab, text='Process Scheduler')

        process_tab = ttk.Frame(notebook)
        #self.create_process_management_tab(process_tab)
        notebook.add(process_tab, text='Memory Management')

        process_tab = ttk.Frame(notebook)
        #self.create_process_management_tab(process_tab)
        notebook.add(process_tab, text='I/O management')

        other_tab = ttk.Frame(notebook)
        self.other_tab(other_tab)
        notebook.add(other_tab, text='Other Operations')


        notebook.pack(expand=True, fill='both', padx=10, pady=10)

    def process_management_tab(self, parent):
        ttk.Label(parent, text="Manage Processes", style='Group.TLabel').pack(pady=(0, 10))

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
            ttk.Button(parent, text=text, width=35, command=cmd).pack(pady=3, padx=10, fill='x')

    def scheduler_tab(self, parent):
        ttk.Label(parent, text="Control Process Scheduling", style='Group.TLabel').pack(pady=(0, 10))

        buttons = [
            ("Scheduling (FCFS)", self.dispatch_fcfs),
            ("Scheduling (Priority)", self.dispatch_priority),
            ("Show All Queues", self.show_queues)
        ]

        for text, cmd in buttons:
            ttk.Button(parent, text=text, width=35, command=cmd).pack(pady=3, padx=10, fill='x')

    def Memory_tab(self, parent):
        ttk.Label(parent, text="Control Process Scheduling", style='Group.TLabel').pack(pady=(0, 10))

        buttons = [
            ("Paging"),
        ]

        for text, cmd in buttons:
            ttk.Button(parent, text=text, width=35, command=cmd).pack(pady=3, padx=10, fill='x')

    def other_tab(self, parent):
        ttk.Label(parent, text="Other System Operations", style='Group.TLabel').pack(pady=(0, 10))
        other_buttons = [
            ("More...", self.not_implemented)
        ]
        for text, cmd in other_buttons:
            ttk.Button(parent, text=text, width=35, command=cmd, state='disabled').pack(pady=3, padx=10, fill='x')

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
        tree.pack(fill="both", expand=True, padx=10, pady=10)

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
        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def not_implemented(self):
        messagebox.showinfo("Coming Soon", "This module is not implemented yet.")

    # Process Scheduler Methods (No functional changes)
    def dispatch_fcfs(self):
        processes = self.kernel.list_all_processes()
        if not processes:
            messagebox.showerror("Error", "No processes available for FCFS scheduling.")
            return

        processes.sort(key=lambda p: p.arrival)

        current_time = 0
        total_waiting_time = 0
        total_turnaround_time = 0

        win = tk.Toplevel(self.master)
        win.title("FCFS Scheduling Result")

        cols = ("PID", "Arrival", "Burst", "Start", "Finish", "Waiting", "Turnaround")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for p in processes:
            start_time = max(current_time, p.arrival)
            finish_time = start_time + p.burst
            waiting_time = start_time - p.arrival
            turnaround_time = finish_time - p.arrival

            total_waiting_time += waiting_time
            total_turnaround_time += turnaround_time
            current_time = finish_time

            tree.insert("", "end",
                        values=(p.pid, p.arrival, p.burst, start_time, finish_time, waiting_time, turnaround_time))

        avg_waiting_time = total_waiting_time / len(processes)
        avg_turnaround_time = total_turnaround_time / len(processes)

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

        win = tk.Toplevel(self.master)
        win.title("Priority Scheduling Result")

        cols = ("PID", "Arrival", "Burst", "Priority", "Start", "Finish", "Waiting", "Turnaround")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for p in processes:
            start_time = max(current_time, p.arrival)
            finish_time = start_time + p.burst
            waiting_time = start_time - p.arrival
            turnaround_time = finish_time - p.arrival

            total_waiting_time += waiting_time
            total_turnaround_time += turnaround_time
            current_time = finish_time

            tree.insert("", "end", values=(
            p.pid, p.arrival, p.burst, p.priority, start_time, finish_time, waiting_time, turnaround_time))

        avg_waiting_time = total_waiting_time / len(processes)
        avg_turnaround_time = total_turnaround_time / len(processes)

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
        tree.pack(fill="both", expand=True, padx=10, pady=10)

root = tk.Tk()
app = OSControlPanel(root)
root.mainloop()
