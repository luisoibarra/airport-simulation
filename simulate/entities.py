from typing import Callable, List, Optional, Union
from .heap import Heap
import simulate.visitor as visitor

class Event:
    def __init__(self, timestamp: float) -> None:
        self.timestamp = timestamp
        
    def __lt__(self, obj) -> bool:
        return _event_comparer(self, obj, lambda x,y: x < y)

    def __le__(self, obj) -> bool:
        return _event_comparer(self, obj, lambda x,y: x <= y)
    
    def __gt__(self, obj) -> bool:
        return _event_comparer(self, obj, lambda x,y: x > y)
    
    def __ge__(self, obj) -> bool:
        return _event_comparer(self, obj, lambda x,y: x >= y)
    
    def __eq__(self, obj) -> bool:
        return _event_comparer(self, obj, lambda x,y: x == y)
    
    def __ne__(self, obj) -> bool:
        return _event_comparer(self, obj, lambda x,y: x != y)
        
def _event_comparer(event1: Event, event2: Union[int, float, Event], comparer):
    if isinstance(event2, Event):
        return comparer(event1.timestamp, event2.timestamp)
    elif isinstance(event2, (int, float)):
        return comparer(event1.timestamp, event2)
    raise ValueError("Can't compare to non Event, int, float object with this instance")

class EventHandler:
    
    def __init__(self) -> None:
        self.process: Simulation = None
    
    def attach_to_process(self, process: 'Simulation'):
        self.process = process
    
    def update_current_time(self, time: float):
        self.process.current_time = time
        
    @visitor.on('event')
    def handle(self, event: Event):
        """
        Apply visitor pattern to this method on every subclass
        """
        pass
    
class Simulation:
    
    def __init__(self, name: str, first_event_function: Callable[[],Event], handler: EventHandler) -> None:
        self.name = name
        self.events = Heap()
        self.first_event_function = first_event_function
        self.handler = handler
        handler.attach_to_process(self)
        self.current_time = 0.0

    def reset_state(self):
        self.current_time = 0.0
        self.events.clear()
        self.add_event(self.first_event_function())

    def add_event(self, event: Event):
        self.events.add(event)
    
    def run_simulation(self):
        self.reset_state()
        for x in self:
            pass
        return x

    def __iter__(self):
        self.reset_state()
        return self
    
    def __next__(self):
        while len(self.events) > 0:
            current_event = self.events.pop()
            return self.handler.handle(current_event)
        raise StopIteration()
 