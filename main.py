import uuid
from collections import deque

# Process Class
class Process:
    def __init__(self, name, priority, burst, arrival):
        self.pid = str(uuid.uuid4())[:4]
        self.name = name
        self.state = "new"
        self.priority = priority
        self.burst = burst
        self.arrival = arrival
        self.parent = None
        self.children = []
        self.memory_required = 128
        self.memory_allocated = None
        self.registers = {"PC": 0, "ACC": 0}
        self.processor = "CPU-1"
        self.io_state = "idle"

    def __str__(self):
        return f"{self.pid} - {self.name} ({self.state})"

# Kernel Class
class Kernel:
    def __init__(self):
        self.processes = []
        self.scheduler = Scheduler()

    def create_process(self, name, priority, burst, arrival):
        p = Process(name, priority, burst, arrival)
        self.processes.append(p)
        self.scheduler.admit(p)  # Admit the process to the scheduler
        return p

    def destroy_process(self, pid):
        proc = self.find_process(pid)
        if proc:
            self.processes.remove(proc)
            return True
        return False

    def find_process(self, pid):
        for p in self.processes:
            if p.pid == pid:
                return p
        return None

    def change_state(self, pid, new_state):
        proc = self.find_process(pid)
        if proc:
            proc.state = new_state
            return True
        return False

    def change_priority(self, pid, new_priority):
        proc = self.find_process(pid)
        if proc:
            proc.priority = new_priority
            return True
        return False

    def process_communicate(self, sender_pid, receiver_pid, message):
        s = self.find_process(sender_pid)
        r = self.find_process(receiver_pid)
        if s and r:
            return f"{s.pid} ➝ {r.pid}: \"{message}\""
        return None

    def list_all_processes(self):
        return self.processes

    def get_pcb_info(self, pid):
        proc = self.find_process(pid)
        if not proc:
            return None
        return {
            "PID": proc.pid,
            "Name": proc.name,
            "State": proc.state,
            "Owner": "admin",
            "Priority": proc.priority,
            "Parent": proc.parent.pid if proc.parent else "None",
            "Children": [child.pid for child in proc.children],
            "Memory Required": f"{proc.memory_required} KB",
            "Memory Allocated": proc.memory_allocated or "None",
            "CPU Registers": proc.registers,
            "Processor": proc.processor,
            "I/O State": proc.io_state
        }

# Scheduler Class
class Scheduler:
    def __init__(self):
        self.ready_queue = deque()
        self.blocked_queue = deque()
        self.suspended_queue = deque()
        self.running_process = None

    def admit(self, process):  # High-level scheduling
        process.state = "ready"
        self.ready_queue.append(process)

    def suspend(self, pid):
        for q in [self.ready_queue, self.blocked_queue]:
            for proc in list(q):
                if proc.pid == pid:
                    q.remove(proc)
                    proc.state = "suspended"
                    self.suspended_queue.append(proc)
                    return True
        return False

    def resume(self, pid):
        for proc in list(self.suspended_queue):
            if proc.pid == pid:
                self.suspended_queue.remove(proc)
                proc.state = "ready"
                self.ready_queue.append(proc)
                return True
        return False

    def block_running(self):
        if self.running_process:
            self.running_process.state = "blocked"
            self.blocked_queue.append(self.running_process)
            self.running_process = None

    def wakeup_blocked(self, pid):
        for proc in list(self.blocked_queue):
            if proc.pid == pid:
                self.blocked_queue.remove(proc)
                proc.state = "ready"
                self.ready_queue.append(proc)
                return True
        return False

    def dispatch_fcfs(self):
        if self.running_process:
            self.running_process.state = "ready"
            self.ready_queue.append(self.running_process)
        if self.ready_queue:
            self.running_process = self.ready_queue.popleft()
            self.running_process.state = "running"
            return self.running_process
        self.running_process = None
        return None

    def dispatch_priority(self):
        if self.running_process:
            self.running_process.state = "ready"
            self.ready_queue.append(self.running_process)
        if self.ready_queue:
            self.running_process = min(self.ready_queue, key=lambda p: p.priority)
            self.ready_queue.remove(self.running_process)
            self.running_process.state = "running"
            return self.running_process
        self.running_process = None
        return None

    def get_queues(self):
        return {
            "Ready": list(self.ready_queue),
            "Blocked": list(self.blocked_queue),
            "Suspended": list(self.suspended_queue),
            "Running": [self.running_process] if self.running_process else []
        }