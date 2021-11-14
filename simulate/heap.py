import heapq as h

class Heap:
    
    def __init__(self, items = []):
        items = [x for x in items]
        h.heapify(items)
        self.__heap = items
    
    @property
    def empty(self):
        return len(self.__heap) == 0
    
    @property
    def minim(self):
        return self.__heap[0]
    
    def clear(self):
        self.__heap.clear()
    
    def add(self, item):
        h.heappush(self.__heap, item)
    
    def pop(self):
        return h.heappop(self.__heap)
    
    def __len__(self):
        return len(self.__heap)