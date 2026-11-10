from collections import deque

processes = [
    {"name": "P1", "arrival": 0,"burst_time": 8},
    {"name": "P2", "arrival": 1, "burst_time": 4},
    {"name": "P3", "arrival": 2, "burst_time": 9},
    {"name": "P4", "arrival": 3, "burst_time": 5},
    {"name": "P5", "arrival": 4, "burst_time": 2}
]

QUANTUM = 3

def prepare_processes(processes):
    data = []

    for process in processes:
        data.append({
            "name": process["name"],
            "arrival": process["arrival"],
            "burst_time": process["burst_time"],
            "remaining_time": process["burst_time"],
            "first_response_time": None,
            "completion_time": None,
        })

    return data

def add_gantt_chart_entry(gantt_chart, process_name, start_time, end_time):

    if start_time == end_time:
        return

    if (
        gantt_chart
        and gantt_chart[-1]["process_name"] == process_name
        and gantt_chart[-1]["end_time"] == start_time
    ):
        gantt_chart[-1]["end_time"] = end_time

    else:
        gantt_chart.append({
            "process_name": process_name,
            "start_time": start_time,
            "end_time": end_time,
        })

def calculate_average_times(processes):

    results = []

    for p in processes:

        completion_time = p["completion_time"]

        turnaround_time = completion_time - p["arrival"]

        waiting_time = turnaround_time - p["burst_time"]

        response_time = (
            p["first_response_time"] - p["arrival"]
        )

        results.append({
            "name": p["name"],
            "arrival": p["arrival"],
            "burst_time": p["burst_time"],
            "completion_time": completion_time,
            "turnaround_time": turnaround_time,
            "waiting_time": waiting_time,
            "response_time": response_time
        })

    return results

#FCFS non-preemptive

def fcfs_scheduling(processes):

    processes = prepare_processes(processes)
    gantt_chart = []

    current_time = 0

    # Sort processes by arrival time, then process name
    processes.sort(
        key=lambda x: (x["arrival"], x["name"])
    )

    for process in processes:

        # Check if the CPU is idle
        if process["arrival"] > current_time:

            add_gantt_chart_entry(
                gantt_chart,
                "IDLE",
                current_time,
                process["arrival"]
            )

            current_time = process["arrival"]

        # Record the first time the process gets CPU access
        if process["first_response_time"] is None:
            process["first_response_time"] = current_time

        start_time = current_time

        # Calculate when the process finishes
        end_time = start_time + process["burst_time"]

        add_gantt_chart_entry(
            gantt_chart,
            process["name"],
            start_time,
            end_time
        )

        current_time = end_time

        process["completion_time"] = current_time

    results = calculate_average_times(processes)

    return results, gantt_chart

#SJF non-preemptive

def sjf_non_preemptive_scheduling(processes):
    processes = prepare_processes(processes)
    gantt_chart = []
    current_time = 0
    completed_processes = 0
    n = len(processes)

    while completed_processes < n:
        available_processes = [p for p in processes if p["arrival"] is not None and p["arrival"] <= current_time and p["remaining_time"] > 0]

        if not available_processes:
            current_time += 1
            continue

        next_process = min(available_processes, key=lambda x: x["burst_time"])

        if next_process["first_response_time"] is None:
            next_process["first_response_time"] = current_time

        start_time = current_time
        end_time = start_time + next_process["burst_time"]
        add_gantt_chart_entry(gantt_chart, next_process["name"], start_time, end_time)

        current_time = end_time
        next_process["completion_time"] = current_time
        next_process["remaining_time"] = 0
        completed_processes += 1

    results = calculate_average_times(processes)
    return results, gantt_chart

#SRTF (Shortest Remaining Time) Preemptive

def srtf_preemptive_scheduling(processes):

    processes = prepare_processes(processes)
    gantt_chart = []

    current_time = 0
    completed_processes = 0
    n = len(processes)

    while completed_processes < n:

        # Find processes that have arrived and are not completed
        available_processes = [
            p for p in processes
            if p["arrival"] <= current_time
            and p["completion_time"] is None
        ]

        # If no process is available, CPU must wait
        if not available_processes:

            next_arrival = min(
                p["arrival"] for p in processes
                if p["completion_time"] is None
            )

            add_gantt_chart_entry(
                gantt_chart,
                "IDLE",
                current_time,
                next_arrival
            )

            current_time = next_arrival
            continue

        # Select the shortest available burst time
        # Break ties using arrival time, then process name
        next_process = min(
            available_processes,
            key=lambda x: (
                x["remaining_time"],
                x["arrival"],
                x["name"]
            )
        )
        # Record first response time
        if next_process["first_response_time"] is None:
            next_process["first_response_time"] = current_time

        add_gantt_chart_entry(
            gantt_chart,
            next_process["name"],
            current_time,
            current_time + 1
        )

        current_time += 1
        next_process["remaining_time"] -= 1

        # If the process has completed
        if next_process["remaining_time"] == 0:
            next_process["completion_time"] = current_time
            completed_processes += 1
            

       

    results = calculate_average_times(processes)

    return results, gantt_chart

#Round Robin Scheduling Preemptive
def round_robin_scheduling(processes, quantum=QUANTUM):

    if quantum <= 0:
        raise ValueError("Quantum must be greater than zero.")

    processes = prepare_processes(processes)

    # Sort by arrival time, then process name
    processes.sort(
        key=lambda x: (x["arrival"], x["name"])
    )

    gantt_chart = []
    process_queue = deque()

    current_time = 0
    completed_processes = 0
    n = len(processes)

    # Tracks which process should arrive next
    next_process = 0

    while completed_processes < n:

        # Add processes that have arrived
        while (
            next_process < n
            and processes[next_process]["arrival"] <= current_time
        ):
            process_queue.append(processes[next_process])
            next_process += 1

        # If the queue is empty, CPU is idle
        if not process_queue:

            next_arrival = processes[next_process]["arrival"]

            add_gantt_chart_entry(
                gantt_chart,
                "IDLE",
                current_time,
                next_arrival
            )

            current_time = next_arrival
            continue

        # Remove the first process from the queue
        process = process_queue.popleft()

        # Record first response time
        if process["first_response_time"] is None:
            process["first_response_time"] = current_time

        start_time = current_time

        # Determine how long the process can execute
        time_slice = min(
            quantum,
            process["remaining_time"]
        )

        end_time = current_time + time_slice

        add_gantt_chart_entry(
            gantt_chart,
            process["name"],
            start_time,
            end_time
        )

        current_time = end_time

        # Update remaining CPU time
        process["remaining_time"] -= time_slice

        # Add newly arrived processes BEFORE re-enqueuing
        # the process whose quantum has expired
        while (
            next_process < n
            and processes[next_process]["arrival"] <= current_time
        ):
            process_queue.append(processes[next_process])
            next_process += 1

        # Check if process has finished
        if process["remaining_time"] == 0:

            process["completion_time"] = current_time
            completed_processes += 1

        else:
            # Process goes to the back of the queue
            process_queue.append(process)

    results = calculate_average_times(processes)

    return results, gantt_chart


#Gant Chart Visualization
def visualize_gantt_chart(gantt_chart):
    if not gantt_chart:
        print("No processes to display.")
        return

    # Display process names
    print("\nGantt Chart:")
    print("|", end="")

    for entry in gantt_chart:
        print(f" {entry['process_name']:^4}|", end="")

    print()

    # Display time markers
    print(gantt_chart[0]["start_time"], end="")

    for entry in gantt_chart:
        print(f"{entry['end_time']:>{6}}", end="")

    print()

#Metrics table
def display_metrics_table(results):
    """Display the metrics table."""
    if not results:
        print("No results to display.")
        return

    print("\nMetrics Table:")
    print(f"{'Process':<10}{'Arrival':<10}{'Burst':<10}{'Completion':<15}{'Turnaround':<15}{'Waiting':<15}{'Response':<15}")
    for result in results:
        print(f"{result['name']:<10}{result['arrival']:<10}{result['burst_time']:<10}{result['completion_time']:<15}{result['turnaround_time']:<15}{result['waiting_time']:<15}{result['response_time']:<15}")

#Average calculations
def calculate_average_metrics(results):
    """Calculate average metrics."""
    if not results:
        return {}

    total_processes = len(results)
    total_turnaround_time = sum(result["turnaround_time"] for result in results)
    total_waiting_time = sum(result["waiting_time"] for result in results)
    total_response_time = sum(result["response_time"] for result in results if result["response_time"] is not None)

    average_metrics = {
        "average_turnaround_time": total_turnaround_time / total_processes,
        "average_waiting_time": total_waiting_time / total_processes,
        "average_response_time": total_response_time / total_processes if total_processes > 0 else None
    }
    return average_metrics

#Run simulation
def run_simulation(scheduling_algorithm, processes, quantum=QUANTUM):
    """Run the scheduling simulation."""
    print(f"Running {scheduling_algorithm} Scheduling Simulation...\n")
    if scheduling_algorithm == "FCFS":
        results, gantt_chart = fcfs_scheduling(processes)
    elif scheduling_algorithm == "SJF":
        results, gantt_chart = sjf_non_preemptive_scheduling(processes)
    elif scheduling_algorithm == "SRTF":
        results, gantt_chart = srtf_preemptive_scheduling(processes)
    elif scheduling_algorithm == "RR":
        results, gantt_chart = round_robin_scheduling(processes, quantum)
    else:
        raise ValueError("Invalid scheduling algorithm. Choose from 'FCFS', 'SJF', 'SRTF', or 'RR'.")

    visualize_gantt_chart(gantt_chart)
    display_metrics_table(results)
    average_metrics = calculate_average_metrics(results)

    print("\nAverage Metrics:")
    print(f"Average Turnaround Time: {average_metrics['average_turnaround_time']:.2f}")
    print(f"Average Waiting Time: {average_metrics['average_waiting_time']:.2f}")
    print(f"Average Response Time: {average_metrics['average_response_time']:.2f}" if average_metrics['average_response_time'] is not None else "Average Response Time: N/A")

def main():
    """Main function to run the scheduling simulation."""
    print("Process Scheduling Simulation")
    print("Available Scheduling Algorithms:")
    print("1. First-Come, First-Served (FCFS)")
    print("2. Shortest Job First (SJF) Non-Preemptive")
    print("3. Shortest Remaining Time First (SRTF) Preemptive")
    print("4. Round Robin (RR) Preemptive")

    choice = input("Select a scheduling algorithm (1-4): ")

    if choice == "1":
        run_simulation("FCFS", processes)

    elif choice == "2":
        run_simulation("SJF", processes)

    elif choice == "3":
        run_simulation("SRTF", processes)

    elif choice == "4":
        try:
            quantum_input = int(input("Enter time quantum for Round Robin (default is 3): "))
            if quantum_input <= 0:
                raise ValueError("Quantum must be greater than zero.")
            run_simulation("RR", processes, quantum_input)
        
        except ValueError:
            print("Invalid input for time quantum. Using default value.")
            run_simulation("RR", processes, QUANTUM)

    else:
        print("Invalid choice. Please select a valid scheduling algorithm.")
if __name__ == "__main__":
    main()


 

 
