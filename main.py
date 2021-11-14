from typing import List
from airport_sim.entities import Airplane
from airport_sim.events import AirplaneArrival
from airport_sim.simulation import AirportSimulation
from simulate.rand_var import *
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future, wait


def lambda_convertor(minutes):
    """
    Converts minutes into frecuency
    """
    return 1/minutes

track_amount = 5
max_time = 10080
airplane_arrival = Exp(lambda_convertor(20))
airplane_loading = Exp(lambda_convertor(30))
airplane_landing = Normal(10, 5)
airplane_departing = Normal(10, 5)
airplane_loading_probability = lambda: U(0,1)() < 0.5
airplane_break_probability = lambda: U(0,1)() < 0.1
airplane_repair = Exp(lambda_convertor(15))
airplane_fueling = Exp(lambda_convertor(30))

def simulate_concurrent(n, threads=10):
    # pool = ThreadPoolExecutor(threads)
    pool = ProcessPoolExecutor(threads)
    with pool:
        futures: List[Future] = []
        for _ in range(threads):
            fut = pool.submit(simulate, n//threads)
            futures.append(fut)
        
        wait(futures, return_when='ALL_COMPLETED')
        
        output = []
        for f in futures:
            output.extend(f.result())
        
        return output

def simulate(n: int, verbose=False):
    process = AirportSimulation(track_amount,
                            max_time, # One week in minutes
                            lambda: AirplaneArrival(airplane_arrival(), Airplane(0)),
                            airplane_arrival, 
                            airplane_landing, 
                            airplane_departing, 
                            airplane_loading,
                            airplane_loading_probability,
                            airplane_break_probability,
                            airplane_repair,
                            airplane_fueling)
    
    simulation_info = []
    for i in range(n):
        track_info = {}
        for x in process:
            if verbose:
                print(x)
            track_info[x.current_time] = [(x.free_time, x.busy) for x in x.tracks]

        for track in process.tracks:
            if verbose:
                print(f"Track {track.track_number} free time: {track.free_time}")
        
        simulation_info.append(track_info)
    return simulation_info

def plot_info(simulation_info, max_time):
    import matplotlib.pyplot as plt
    
    length = 0
    s = simulation_info[0]
    for v in s.values():
        length = len(v)
        break
    
    fig, axes = plt.subplots(3,2)
    mean_ax = axes[2,1]
    axes = [
        axes[0,0],
        axes[0,1],
        axes[1,0],
        axes[1,1],
        axes[2,0],
    ]
    
    max_value = 0
    mean_time = []
    
    for track_info in simulation_info:
        times = [x for x in track_info.keys()]
        times.sort()
        free_times = [[] for _ in track_info[times[0]]]
        
        for time in times:
            for (free_time,_),free_time_list in zip(track_info[time], free_times):
                free_time_list.append(free_time)
                max_value = max(max_value, free_time)
        
        for ax, free_time in zip(axes, free_times):
            ax.plot(times, free_time)
    
    for i,time in enumerate(times):
        mean_value = 0
        for free_time in free_times:
            mean_value += free_time[i]
        mean_time.append(mean_value/len(free_times))
    
    mean_ax.plot(times, mean_time)
    mean_ax.set_ylim([-1, max_value + max_value/10])
    mean_ax.set_title("Media del tiempo libre")
    mean_ax.set_ylabel("Tiempo libre")
    mean_ax.plot([max_time, max_time], [0, max_value], c='k', ls="--")
    # mean_ax.set_xlabel("Tiempo")
    
    for i,ax in enumerate(axes):
        ax.set_ylim([-1, max_value + max_value/10])
        ax.set_title(f"Pista de aterrizaje {i}")
        # ax.set_xlabel("Tiempo")
        ax.set_ylabel("Tiempo libre")
        ax.plot([max_time, max_time], [0, max_value], c='k', ls="--")

    plt.show()
    
    print("Media de tiempo libre final:", mean_time[-1])
    
# sim_info = simulate(1)

sim_info = simulate_concurrent(1000)

plot_info(sim_info, max_time)