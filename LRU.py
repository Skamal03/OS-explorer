def lru_page_replacement(pages, capacity):
    memory = []
    page_faults = 0

    for page in pages:
        if page not in memory:
            page_faults += 1
            if len(memory) == capacity:
                memory.pop(0)  # Remove LRU
            memory.append(page)  # Add new page as most recently used
        else:
            # Move the page to the end (most recently used)
            memory.remove(page)
            memory.append(page)
        print(f"Page: {page} -> Memory: {memory}")

    print(f"\nTotal Page Faults: {page_faults}")
    return page_faults

# Example usage:
pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3]
capacity = 4
lru_page_replacement(pages, capacity)
