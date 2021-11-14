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
break_probability = 0.1
loading_probability = 0.5
airplane_arrival = Exp(lambda_convertor(20))
airplane_loading = Exp(lambda_convertor(30))
airplane_landing = Normal(10, 5)
airplane_departing = Normal(10, 5)
airplane_loading_probability = lambda: U(0,1)() < loading_probability
airplane_break_probability = lambda: U(0,1)() < break_probability
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
    
    print(f"Running {n} simulations...")
    
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
    
    print(f"{n} simulations completed ")
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
    last_values = [[] for _ in range(length)]
    
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

        for free_time, last_value_list in zip(free_times, last_values):
            last_value_list.append(free_time[-1]) 
        
    for i,time in enumerate(times):
        mean_value = 0
        for free_time in free_times:
            mean_value += free_time[i]
        mean_value = mean_value/len(free_times)
        mean_time.append(mean_value)
 
    print("Media de tiempo libre final:", mean_time[-1])
    print()
    
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
    
    X = [i for i in range(length)]
    track_mean = []
    track_variance = []
    
    for i, values in enumerate(last_values):
        track_mean.append(sum(values)/len(values))
        track_variance.append(sum((x - track_mean[-1])**2 for x in values)/(len(values)-1))
        print(f"Media de tiempo libre pista {i}: {track_mean[-1]}")
        print(f"Varianza de tiempo libre pista {i}: {track_variance[-1]}")
        print(f"Desviación estándar de tiempo libre pista {i}: {track_variance[-1] ** (1/2)}")
        print(f"Calidad del estimador varianza/length pista {i}: {track_variance[-1]/len(values)}")
        print()
        
    plt.bar(X, track_mean, label="Media tiempo libre", width=0.33)
    plt.bar([x + 0.33 for x in X], [x ** (1/2) for x in track_variance], label="Desviación estándar tiempo libre", width=0.33)
    plt.legend()
    plt.xlabel("Pista")
    plt.title("Media y desviación estándar de pistas")
    plt.show()

r.seed(0) # Consistency in results

sim_info = simulate_concurrent(1000)

plot_info(sim_info, max_time)