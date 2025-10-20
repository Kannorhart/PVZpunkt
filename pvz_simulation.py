import simpy
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import random

# Model parameters
SIMULATION_TIME = 120  # 2 hours in minutes
PEAK_HOUR_ARRIVAL_RATE = 1.0  # 1 customer per minute on average
SERVICE_TIME_MEAN = 2.0  # Average service time in minutes
SERVICE_TIME_STD = 0.5   # Standard deviation of service time
DELAY_PROBABILITY = 0.1  # Probability of delay/problem
DELAY_TIME_MIN = 1.0     # Minimum delay time
DELAY_TIME_MAX = 5.0     # Maximum delay time
NUM_EMPLOYEES = 3        # Number of employees
SELF_SERVICE_RATIO = 0.5 # Ratio of customers using self-service
NUM_SELF_SERVICE = 2     # Number of self-service terminals

class PickupPoint:
    def __init__(self, env, num_employees, num_self_service):
        self.env = env
        self.employee_queue = simpy.Resource(env, num_employees)
        self.self_service_terminals = simpy.Resource(env, num_self_service)
        self.waiting_times = []
        self.queue_lengths = []
        self.customer_count = 0
        self.bee_zones = {}  # For bee algorithm implementation
        
    def serve_customer(self, service_time):
        """Serve a customer with potential delays"""
        # Base service time
        yield self.env.timeout(service_time)
        
        # Random delay with certain probability
        if random.random() < DELAY_PROBABILITY:
            delay_time = random.uniform(DELAY_TIME_MIN, DELAY_TIME_MAX)
            yield self.env.timeout(delay_time)
            
    def serve_with_bee_algorithm(self, service_time, zone_loads):
        """
        Serve customer using bee algorithm approach
        Distribute orders to least loaded zones
        """
        # Find least loaded zone (simplified implementation)
        min_load_zone = min(zone_loads, key=zone_loads.get)
        zone_loads[min_load_zone] += 1
        
        # Serve customer
        yield self.env.timeout(service_time)
        
        # Update zone load after service
        zone_loads[min_load_zone] -= 1

def customer_arrival(env, pickup_point, bee_zones=None):
    """Generate customers arriving at the pickup point"""
    while True:
        # Exponential distribution for inter-arrival times
        inter_arrival_time = np.random.exponential(1/PEAK_HOUR_ARRIVAL_RATE)
        yield env.timeout(inter_arrival_time)
        
        # Normal distribution for service times
        service_time = np.random.normal(SERVICE_TIME_MEAN, SERVICE_TIME_STD)
        # Ensure service time is positive
        service_time = max(0.1, service_time)
        
        # Decide if customer uses self-service or employee assistance
        if random.random() < SELF_SERVICE_RATIO and bee_zones is None:
            # Self-service customer
            env.process(handle_self_service_customer(env, pickup_point, service_time))
        else:
            # Employee-assisted customer
            env.process(handle_employee_customer(env, pickup_point, service_time, bee_zones))

def handle_self_service_customer(env, pickup_point, service_time):
    """Handle a customer using self-service terminal"""
    arrival_time = env.now
    with pickup_point.self_service_terminals.request() as request:
        yield request
        start_service_time = env.now
        yield env.process(pickup_point.serve_customer(service_time))
        departure_time = env.now
        waiting_time = start_service_time - arrival_time
        pickup_point.waiting_times.append(waiting_time)

def handle_employee_customer(env, pickup_point, service_time, bee_zones):
    """Handle a customer with employee assistance"""
    arrival_time = env.now
    
    # If bee algorithm is implemented
    if bee_zones is not None:
        with pickup_point.employee_queue.request() as request:
            yield request
            start_service_time = env.now
            yield env.process(pickup_point.serve_with_bee_algorithm(service_time, bee_zones))
            departure_time = env.now
            waiting_time = start_service_time - arrival_time
            pickup_point.waiting_times.append(waiting_time)
    else:
        # Regular queue handling
        with pickup_point.employee_queue.request() as request:
            yield request
            start_service_time = env.now
            yield env.process(pickup_point.serve_customer(service_time))
            departure_time = env.now
            waiting_time = start_service_time - arrival_time
            pickup_point.waiting_times.append(waiting_time)

def monitor_queue(env, pickup_point):
    """Monitor queue length over time"""
    while True:
        pickup_point.queue_lengths.append(
            len(pickup_point.employee_queue.queue) + 
            len(pickup_point.self_service_terminals.queue)
        )
        yield env.timeout(1)  # Check every minute

def run_simulation(num_employees=NUM_EMPLOYEES, num_self_service=NUM_SELF_SERVICE, 
                   bee_algorithm=False, simulation_time=SIMULATION_TIME):
    """Run the PVZ simulation"""
    # Create simulation environment
    env = simpy.Environment()
    
    # Create pickup point
    pickup_point = PickupPoint(env, num_employees, num_self_service)
    
    # Initialize bee zones if using bee algorithm
    bee_zones = {'zone1': 0, 'zone2': 0, 'zone3': 0} if bee_algorithm else None
    
    # Start customer generation
    env.process(customer_arrival(env, pickup_point, bee_zones))
    
    # Start queue monitoring
    env.process(monitor_queue(env, pickup_point))
    
    # Execute simulation
    env.run(until=simulation_time)
    
    return pickup_point

def analyze_results(pickup_points, labels):
    """Analyze and compare results from different scenarios"""
    results = []
    
    for i, pickup_point in enumerate(pickup_points):
        waiting_times = np.array(pickup_point.waiting_times)
        queue_lengths = np.array(pickup_point.queue_lengths)
        
        result = {
            'scenario': labels[i],
            'avg_waiting_time': np.mean(waiting_times),
            'std_waiting_time': np.std(waiting_times),
            'max_waiting_time': np.max(waiting_times),
            'avg_queue_length': np.mean(queue_lengths),
            'max_queue_length': np.max(queue_lengths),
            'total_customers': len(pickup_point.waiting_times)
        }
        results.append(result)
    
    return pd.DataFrame(results)

def plot_results(pickup_points, labels):
    """Plot comparison of results"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Waiting time distributions
    for i, pickup_point in enumerate(pickup_points):
        axes[0, 0].hist(pickup_point.waiting_times, alpha=0.7, label=labels[i], bins=30)
    axes[0, 0].set_xlabel('Waiting Time (minutes)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Distribution of Waiting Times')
    axes[0, 0].legend()
    
    # Average waiting time comparison
    avg_waiting_times = [np.mean(pickup_point.waiting_times) for pickup_point in pickup_points]
    axes[0, 1].bar(labels, avg_waiting_times, color=['blue', 'green', 'red'])
    axes[0, 1].set_ylabel('Average Waiting Time (minutes)')
    axes[0, 1].set_title('Average Waiting Time by Scenario')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Queue length over time (for first scenario as example)
    axes[1, 0].plot(pickup_points[0].queue_lengths)
    axes[1, 0].set_xlabel('Time (minutes)')
    axes[1, 0].set_ylabel('Queue Length')
    axes[1, 0].set_title('Queue Length Over Time')
    
    # Service efficiency comparison
    efficiency = []
    for pickup_point in pickup_points:
        # Simplified efficiency metric: 1 / (avg_wait_time * avg_queue_length)
        avg_wait = np.mean(pickup_point.waiting_times)
        avg_queue = np.mean(pickup_point.queue_lengths)
        eff = 1 / (avg_wait * avg_queue) if avg_wait * avg_queue > 0 else 0
        efficiency.append(eff)
    
    axes[1, 1].bar(labels, efficiency, color=['blue', 'green', 'red'])
    axes[1, 1].set_ylabel('Efficiency Metric')
    axes[1, 1].set_title('Service Efficiency by Scenario')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('simulation_results.png')
    plt.show()

def main():
    """Main function to run simulations and compare scenarios"""
    print("Running PVZ Optimization Simulation")
    print("=" * 40)
    
    # Scenario 1: Baseline - Traditional PVZ
    print("Running baseline scenario...")
    baseline_pvz = run_simulation(num_employees=3, num_self_service=0, bee_algorithm=False)
    
    # Scenario 2: With Self-Service Terminals
    print("Running self-service scenario...")
    self_service_pvz = run_simulation(num_employees=3, num_self_service=2, bee_algorithm=False)
    
    # Scenario 3: With Bee Algorithm Optimization
    print("Running bee algorithm scenario...")
    bee_algorithm_pvz = run_simulation(num_employees=3, num_self_service=2, bee_algorithm=True)
    
    # Analyze results
    pickup_points = [baseline_pvz, self_service_pvz, bee_algorithm_pvz]
    labels = ['Baseline', 'With Self-Service', 'With Bee Algorithm']
    
    results_df = analyze_results(pickup_points, labels)
    print("\nSimulation Results:")
    print(results_df.to_string(index=False))
    
    # Plot results
    plot_results(pickup_points, labels)
    
    # Business evaluation
    print("\nBusiness Evaluation:")
    print("-" * 20)
    
    baseline_avg_wait = np.mean(baseline_pvz.waiting_times)
    optimized_avg_wait = np.mean(bee_algorithm_pvz.waiting_times)
    
    improvement = ((baseline_avg_wait - optimized_avg_wait) / baseline_avg_wait) * 100
    print(f"Average waiting time reduction: {improvement:.2f}%")
    
    if improvement > 20:
        print("✓ Proposed solution is effective (improvement > 20%)")
        
        # Business model calculation
        print("\nBusiness Model:")
        print("-" * 15)
        equipment_cost = 3 * 100000  # 3 terminals at 100,000 rubles each
        integration_cost = 100000    # Integration and training
        total_investment = equipment_cost + integration_cost
        print(f"Equipment cost: {equipment_cost:,} rubles")
        print(f"Integration cost: {integration_cost:,} rubles")
        print(f"Total investment: {total_investment:,} rubles")
        
        # Savings calculation
        labor_savings = 500000  # Savings from reducing staff by 1 person
        capacity_increase = 0.30  # 30% increase in capacity
        payback_period = total_investment / labor_savings  # In years
        print(f"Annual labor savings: {labor_savings:,} rubles")
        print(f"Capacity increase: {capacity_increase*100:.0f}%")
        print(f"Payback period: {payback_period*12:.1f} months")
    else:
        print("✗ Proposed solution is not effective (improvement <= 20%)")

if __name__ == "__main__":
    main()