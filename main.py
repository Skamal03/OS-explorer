import uuid
import json
import queue
import threading
from collections import deque
from memory import MemoryManager

# Load configuration
try:
    with open("config.json", "r") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    CONFIG = {"page_size_kb": 64, "total_memory_kb": 1024}
    with open("config.json", "w") as f:
        json.dump(CONFIG, f, indent=4)

# Process Control Block (PCB)
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
        self.memory_required = 128  # Default memory in KB
        self.memory_allocated = None
        self.page_table = []  # List of frame indices
        self.registers = {"PC": 0, "ACC": 0, "SP": 0}
        self.processor = "CPU-1"
        self.io_state = "idle"
        self.owner = "admin"

    def __str__(self):
        return f"{self.pid} - {self.name} ({self.state})"

# Resource Manager for Synchronization
class ResourceManager:
    def __init__(self, resource_name="Printer", max_available=1):
        self.resource_name = resource_name
        self.semaphore = threading.Semaphore(max_available)
        self.current_holder = None

    def acquire_resource(self, pid):
        self.semaphore.acquire()
        self.current_holder = pid
        return f"Resource '{self.resource_name}' acquired by {pid}"

    def release_resource(self, pid):
        if self.current_holder == pid:
            self.current_holder = None
            self.semaphore.release()
            return f"Resource '{self.resource_name}' released by {pid}"
        return f"Error: {pid} does not hold '{self.resource_name}'"

    def get_status(self):
        return f"Resource '{self.resource_name}' held by {self.current_holder or 'None'}"

# Kernel
class Kernel:
    def __init__(self):
        self.processes = []
        self.scheduler = Scheduler()
        self.memory_manager = MemoryManager(
            total_memory_kb=CONFIG["total_memory_kb"],
            page_size_kb=CONFIG["page_size_kb"]
        )
        self.resource_manager = ResourceManager()
        self.message_queue = queue.Queue()  # For message passing
        self.shared_memory = {"data": None, "lock": threading.Lock()}  # For shared memory

    def create_process(self, name, priority, burst, arrival):
        if not name or priority < 0 or burst <= 0 or arrival < 0:
            raise ValueError("Invalid process parameters")
        p = Process(name, priority, burst, arrival)
        self.memory_manager.allocate_memory(p)
        self.processes.append(p)
        self.scheduler.admit(p)
        return p

    def destroy_process(self, pid):
        proc = self.find_process(pid)
        if proc:
            self.memory_manager.deallocate_memory(proc)
            self.processes.remove(proc)
            self.scheduler.remove_process(proc)
            if self.resource_manager.current_holder == pid:
                self.resource_manager.release_resource(pid)
            return True
        return False

    def find_process(self, pid):
        return next((p for p in self.processes if p.pid == pid), None)

    def change_state(self, pid, new_state):
        valid_states = ["new", "ready", "running", "blocked", "suspended", "terminated"]
        if new_state not in valid_states:
            raise ValueError(f"Invalid state: {new_state}")
        proc = self.find_process(pid)
        if proc:
            proc.state = new_state
            self.scheduler.update_queues(proc, new_state)
            return True
        return False

    def change_priority(self, pid, new_priority):
        if new_priority < 0 or new_priority > 10:
            raise ValueError("Priority must be between 0 and 10")
        proc = self.find_process(pid)
        if proc:
            proc.priority = new_priority
            return True
        return False

    def acquire_resource(self, pid):
        return self.resource_manager.acquire_resource(pid)

    def release_resource(self, pid):
        return self.resource_manager.release_resource(pid)

    def get_resource_status(self):
        return self.resource_manager.get_status()

    def send_message(self, sender_pid, receiver_pid, message):
        proc = self.find_process(receiver_pid)
        if proc:
            self.message_queue.put((sender_pid, receiver_pid, message))
            return f"Message from {sender_pid} to {receiver_pid} queued"
        return f"Receiver {receiver_pid} not found"

    def receive_message(self, pid):
        try:
            while not self.message_queue.empty():
                sender, receiver, msg = self.message_queue.get_nowait()
                if receiver == pid:
                    return f"Message from {sender}: {msg}"
            return "No messages for {pid}"
        except queue.Empty:
            return "No messages for {pid}"

    def write_shared_memory(self, pid, data):
        with self.shared_memory["lock"]:
            self.shared_memory["data"] = (pid, data)
            return f"Shared memory written by {pid}: {data}"

    def read_shared_memory(self, pid):
        with self.shared_memory["lock"]:
            if self.shared_memory["data"]:
                writer_pid, data = self.shared_memory["data"]
                return f"Shared memory read by {pid}: {data} (written by {writer_pid})"
            return "Shared memory is empty"

    def process_communicate(self, sender_pid, receiver_pid, message, mode="message"):
        if mode == "message":
            return self.send_message(sender_pid, receiver_pid, message)
        elif mode == "shared_memory_write":
            return self.write_shared_memory(sender_pid, message)
        elif mode == "shared_memory_read":
            return self.read_shared_memory(sender_pid)
        else:
            return "Invalid communication mode"

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
            "Owner": proc.owner,
            "Priority": proc.priority,
            "Parent": proc.parent.pid if proc.parent else "None",
            "Children": [child.pid for child in proc.children],
            "Memory Required": f"{proc.memory_required} KB",
            "Memory Allocated": proc.memory_allocated or "None",
            "Page Table": proc.page_table,
            "CPU Registers": proc.registers,
            "Processor": proc.processor,
            "I/O State": proc.io_state
        }

# Scheduler
class Scheduler:
    def __init__(self):
        self.ready_queue = deque()
        self.blocked_queue = deque()
        self.suspended_queue = deque()
        self.running_process = None

    def admit(self, process):
        process.state = "ready"
        self.ready_queue.append(process)

    def remove_process(self, process):
        if process in self.ready_queue:
            self.ready_queue.remove(process)
        elif process in self.blocked_queue:
            self.blocked_queue.remove(process)
        elif process in self.suspended_queue:
            self.suspended_queue.remove(process)
        elif self.running_process == process:
            self.running_process = None

    def update_queues(self, process, new_state):
        self.remove_process(process)
        if new_state == "ready":
            self.ready_queue.append(process)
        elif new_state == "blocked":
            self.blocked_queue.append(process)
        elif new_state == "suspended":
            self.suspended_queue.append(process)
        elif new_state == "running":
            self.running_process = process

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

    def view_queues(self):
        return {
            "Ready": list(self.ready_queue),
            "Blocked": list(self.blocked_queue),
            "Suspended": list(self.suspended_queue),
            "Running": [self.running_process] if self.running_process else []
        }