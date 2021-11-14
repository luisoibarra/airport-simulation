
from simulate.entities import Event
from airport_sim.entities import Airplane

class BaseAirplaneEvent(Event):
    def __init__(self, timestamp: float, airplane: Airplane) -> None:
        super().__init__(timestamp)
        self.airplane = airplane

    def __str__(self) -> str:
        return f"{type(self).__name__} at {self.timestamp} with {self.airplane}"
    
class AirplaneArrival(BaseAirplaneEvent):
    """
    Event that represents the arrival of an airplane to the airport
    """
    pass
        
class AirplaneLanded(BaseAirplaneEvent):
    """
    Event that represents the end of the landing procedure of an airplane in the airport
    """
    pass

class AirplaneDeparture(BaseAirplaneEvent):
    """
    Event that represents the begining of the departure procedure of an airplane from the airport
    """
    pass

class AirplaneDepartured(BaseAirplaneEvent):
    """
    Event that represents the end of the departuring procedure of an airplane from the airport
    """
    pass

class AirplaneLoadedUnloaded(BaseAirplaneEvent):
    """
    Event that represents the end of the loading/unloading procedure of an airplane in the airport
    """
    pass

class AirplaneFueled(BaseAirplaneEvent):
    """
    Event that represents the end of the fueling procedure of an airplane in the airport
    """
    pass

class AirplaneRepaired(BaseAirplaneEvent):
    """
    Event that represents the end of the repairing procedure of an airplane in the airport
    """
    pass
