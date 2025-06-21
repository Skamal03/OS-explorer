from collections import deque
import json

class Page:
    def __init__(self, pid, page_number):
        self.pid = pid
        self.page_number = page_number

    def __str__(self):
        return f"{self.pid}:{self.page_number}"

class MemoryManager:
    def __init__(self, total_memory_kb=1024, page_size_kb=64):
        self.page_size_kb = page_size_kb
        self.total_pages = total_memory_kb // page_size_kb
        self.memory = [None] * self.total_pages  # Each slot is a frame
        self.lru_queue = deque()  # Tracks frame indices for LRU
        self.page_table = {}  # Maps pid to list of frame indices

    def set_page_size(self, new_size_kb):
        if new_size_kb <= 0:
            raise ValueError("Page size must be positive")
        self.page_size_kb = new_size_kb
        self.total_pages = 1024 // self.page_size_kb
        self.memory = [None] * self.total_pages
        self.lru_queue.clear()
        self.page_table.clear()
        # Update configuration file
        with open("config.json", "r") as f:
            config = json.load(f)
        config["page_size_kb"] = new_size_kb
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

    def allocate_memory(self, process):
        pages_needed = -(-process.memory_required // self.page_size_kb)  # Ceiling division
        allocated_frames = []

        for page_num in range(pages_needed):
            frame_index = self._get_free_or_lru_frame()
            self.memory[frame_index] = Page(process.pid, page_num)
            allocated_frames.append(frame_index)
            self._update_lru(frame_index)

        self.page_table[process.pid] = allocated_frames
        process.page_table = allocated_frames
        process.memory_allocated = f"{len(allocated_frames)} pages in frames {allocated_frames}"
        return allocated_frames

    def deallocate_memory(self, process):
        if process.pid in self.page_table:
            for frame_index in self.page_table[process.pid]:
                self.memory[frame_index] = None
                if frame_index in self.lru_queue:
                    self.lru_queue.remove(frame_index)
            del self.page_table[process.pid]
            process.page_table = []
            process.memory_allocated = None

    def _get_free_or_lru_frame(self):
        # Check for free frame
        for i, frame in enumerate(self.memory):
            if frame is None:
                return i

        # Replace LRU frame if no free frame is available
        if self.lru_queue:
            lru_index = self.lru_queue.popleft()
            victim = self.memory[lru_index]
            if victim and victim.pid in self.page_table:
                self.page_table[victim.pid].remove(lru_index)
            self.memory[lru_index] = None
            return lru_index
        raise MemoryError("No available frames")

    def _update_lru(self, frame_index):
        if frame_index in self.lru_queue:
            self.lru_queue.remove(frame_index)
        self.lru_queue.append(frame_index)

    def view_memory_map(self):
        return [(i, str(page) if page else "Free") for i, page in enumerate(self.memory)]

    def simulate_lru(self, pages, capacity):
        memory = [None] * capacity
        page_faults = 0
        lru_queue = deque()
        history = []

        for page in pages:
            if page not in [p.page_number if p else None for p in memory]:
                page_faults += 1
                if len(lru_queue) == capacity:
                    lru_page = lru_queue.popleft()
                    for i in range(len(memory)):
                        if memory[i] and memory[i].page_number == lru_page:
                            memory[i] = None
                            break
                for i in range(len(memory)):
                    if memory[i] is None:
                        memory[i] = Page("simulated", page)
                        break
                lru_queue.append(page)
            else:
                lru_queue.remove(page)
                lru_queue.append(page)
            history.append((page, [p.page_number if p else None for p in memory], page_faults))

        return history, page_faults

    def get_page_table(self, pid):
        return self.page_table.get(pid, [])