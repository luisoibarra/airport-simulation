
from typing import Optional


class Airplane:
    """
    Airplane
    """
    def __init__(self, number) -> None:
        self.number = int(number)
        self.pending_tasks = 0
        self.track: Track = None
    
    def __repr__(self) -> str:
        return str(self)
    
    def __str__(self) -> str:
        return f"Airplane {self.number}. Pending tasks: {self.pending_tasks}"

class Track:
    """
    Landing airport track
    
    Stores the airplane if any and also computes the track's free time. 
    """
    
    def __init__(self, number) -> None:
        self.track_number = number
        self.__airplane: Optional[Airplane] = None
        self.__last_available = 0.0
        self.free_time = 0.0
    
    @property
    def airplane(self):
        """
        Current airplane on track if no airplane then None
        """
        return self.__airplane
    
    def set_airplane(self, airplane: Optional[Airplane], current_time):
        """
        Set the airplane and update the free time.
        """
        if self.airplane and not airplane: # Setting track clear
            self.__airplane = airplane
            self.__last_available = current_time
        elif not self.airplane and airplane: # Setting track full
            self.__airplane = airplane
            self.free_time += current_time - self.__last_available
            self.airplane.track = self
        else:
            raise ValueError("Invalid airplane set. self.airplane and airplane must be None and not None or viceversa")
    
    @property
    def busy(self):
        """
        Returns if the track has an airplane
        """
        return self.airplane is not None
    
    def __repr__(self) -> str:
        return str(self)
    
    def __str__(self) -> str:
        return f"Track {self.track_number}: {'Empty' if not self.busy else str(self.airplane)}"
  