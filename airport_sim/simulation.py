from simulate.heap import Heap
from typing import Callable, List, Optional
from simulate.entities import Event, EventHandler, Simulation, visitor
from airport_sim.events import AirplaneArrival, AirplaneDeparture, AirplaneDepartured,\
    AirplaneFueled, AirplaneLanded, AirplaneLoadedUnloaded, AirplaneRepaired
from airport_sim.entities import Airplane, Track


class AirportSimulation(Simulation):
    """
    Airport simulation instance
    """
    
    def __init__(self, landing_tracks: int,
                max_time: float,
                first_event_function: Callable[[], AirplaneArrival], 
                airplane_arrival_function: Callable[[], float],
                airplane_landing_function: Callable[[], float],
                airplane_departure_function: Callable[[], float], 
                airplane_loading_function: Callable[[], float],
                airplane_loading_probability_function: Callable[[], bool],
                airplane_break_probability_function: Callable[[], bool], 
                airplane_break_delay_function: Callable[[], float],
                airplane_fueling_function: Callable[[], float]) -> None:
        
        self.airplane_arrival_function = airplane_arrival_function
        self.airplane_landing_function = airplane_landing_function
        self.airplane_departure_function = airplane_departure_function
        self.airplane_loading_function = airplane_loading_function
        self.airplane_loading_probability_function = airplane_loading_probability_function
        self.airplane_break_probability_function = airplane_break_probability_function
        self.airplane_break_delay_function = airplane_break_delay_function
        self.airplane_fueling_function = airplane_fueling_function
        super().__init__("Aeropuerto de Barajas", first_event_function, AirportEventHandler())
        self.airplane_queue: List[Airplane] = []
        self.tracks: List[Track] = []
        self.track_amount = landing_tracks
        self.max_time = max_time

    def reset_state(self):
        self.airplane_queue: List[Airplane] = []
        self.tracks = [Track(i) for i in range(self.track_amount)]
        return super().reset_state()

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        name = self.name + "\n"
        
        queue = "No airplanes waiting for landing"
        if len(self.airplane_queue) > 0:
            queue = f"Airplanes waiting: {len(self.airplane_queue)}"
        
        next_action = "No events"
        if len(self.events) > 0:
            next_action = "Next Event: " + str(self.events.minim)
        
        tracks = "Tracks:\n\n" + "\n".join(str(x) for x in self.tracks)
        
        return "\n".join([name, queue, next_action, tracks])

class AirportEventHandler(EventHandler):
    """
    Airport event handler
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.airport: AirportSimulation = None
    
    def attach_to_process(self, process: 'Simulation'):
        super().attach_to_process(process)
        self.airport: AirportSimulation = self.process
    
    def add_landed_event(self, airplane, event_time, track: Track):
        track.set_airplane(airplane, event_time)
        event_time = self.airport.current_time + self.airport.airplane_landing_function()
        landed = AirplaneLanded(event_time, airplane)
        self.airport.add_event(landed)
    
    @visitor.on('event')
    def handle(self, event):
        pass
    
    @visitor.when(AirplaneArrival)
    def handle(self, event: AirplaneArrival):
        self.update_current_time(event.timestamp)
        
        if self.airport.current_time < self.airport.max_time: # Add new arrival to timeline
            arrival_time = self.airport.current_time + self.airport.airplane_arrival_function()
            arrival = AirplaneArrival(arrival_time, Airplane(arrival_time))
            self.airport.add_event(arrival)
        
        not_busy = [x for x in self.airport.tracks if not x.busy]
        if not_busy: # Track available
            track = not_busy[0]
            self.add_landed_event(event.airplane, event.timestamp, track)
        else: # All tracks busy
            self.airport.airplane_queue.append(event.airplane)
            
        return self.airport
    
    @visitor.when(AirplaneLanded)
    def handle(self, event: AirplaneLanded):
        self.update_current_time(event.timestamp)
        
        # Loading and Fueling are happening at the same time 
        
        if self.airport.airplane_loading_probability_function(): # If airplane must load or unload
            time = self.airport.current_time + self.airport.airplane_loading_function()
            loaded = AirplaneLoadedUnloaded(time, event.airplane)
            event.airplane.pending_tasks += 1
            self.airport.add_event(loaded)
        
        # Fueling the airplane
        time = self.airport.current_time + self.airport.airplane_fueling_function()
        fueled = AirplaneFueled(time, event.airplane)
        event.airplane.pending_tasks += 1
        self.airport.add_event(fueled)
        
        return self.airport
        
    @visitor.when(AirplaneLoadedUnloaded)
    def handle(self, event: AirplaneLoadedUnloaded):
        self.update_current_time(event.timestamp)

        event.airplane.pending_tasks -= 1    
        
        if event.airplane.pending_tasks == 0: # No task pending then leave
            self.airport.add_event(AirplaneDeparture(event.timestamp, event.airplane))
    
        return self.airport
    
    @visitor.when(AirplaneFueled)
    def handle(self, event: AirplaneFueled):
        self.update_current_time(event.timestamp)

        event.airplane.pending_tasks -= 1
        
        if event.airplane.pending_tasks == 0: # No task pending then leave
            self.airport.add_event(AirplaneDeparture(event.timestamp, event.airplane))
        
        return self.airport
            
    @visitor.when(AirplaneDeparture)
    def handle(self, event: AirplaneDeparture):
        self.update_current_time(event.timestamp)
        
        if self.airport.airplane_break_probability_function(): # The airplane broke
            time = self.airport.current_time + self.airport.airplane_break_delay_function()
            event.airplane.pending_tasks += 1
            repaired = AirplaneRepaired(time, event.airplane)
            self.airport.add_event(repaired)
        else: # The ariplane is ready to departure
            
            if event.airplane.pending_tasks:
                raise Exception("Airplane trying to departure with pending tasks")
            
            time = self.airport.current_time + self.airport.airplane_departure_function()
            departured = AirplaneDepartured(time, event.airplane)
            self.airport.add_event(departured)
            
        return self.airport
    
    @visitor.when(AirplaneRepaired)
    def handle(self, event: AirplaneDeparture):
        self.update_current_time(event.timestamp)
        
        event.airplane.pending_tasks -= 1
        
        if event.airplane.pending_tasks == 0: # No task pending then leave
            self.airport.add_event(AirplaneDeparture(event.timestamp, event.airplane))

        return self.airport
    
    @visitor.when(AirplaneDepartured)
    def handle(self, event: AirplaneDepartured):
        self.update_current_time(event.timestamp)
        
        event.airplane.track.set_airplane(None, event.timestamp) # Clear the track
        
        if self.airport.airplane_queue: # First airplane in queue to land on this free track
            airplane = self.airport.airplane_queue.pop(0)
            self.add_landed_event(airplane, event.timestamp, event.airplane.track)
        
        return self.airport

  