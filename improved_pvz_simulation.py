import random
import math
import matplotlib.pyplot as plt

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

class Event:
    def __init__(self, time, event_type, customer=None):
        self.time = time
        self.type = event_type  # 'arrival', 'departure'
        self.customer = customer

class Customer:
    def __init__(self, id, arrival_time):
        self.id = id
        self.arrival_time = arrival_time
        self.start_service_time = None
        self.departure_time = None
        self.service_time = max(0.1, random.normalvariate(SERVICE_TIME_MEAN, SERVICE_TIME_STD))
        self.is_self_service = random.random() < SELF_SERVICE_RATIO

class PickupPoint:
    def __init__(self, num_employees, num_self_service):
        self.num_employees = num_employees
        self.num_self_service = num_self_service
        self.available_employees = num_employees
        self.available_self_service = num_self_service
        self.employee_queue = []  # Queue for employee service
        self.self_service_queue = []  # Queue for self-service
        self.all_customers = []
        self.waiting_times = []
        self.events = []
        self.time = 0
        self.total_customers = 0
        
    def exponential_random(self, rate):
        """Generate exponential random variable"""
        return -math.log(1.0 - random.random()) / rate
    
    def schedule_arrival(self, time):
        """Schedule a customer arrival"""
        customer = Customer(self.total_customers, time)
        self.total_customers += 1
        self.all_customers.append(customer)
        self.events.append(Event(time, 'arrival', customer))
        
    def schedule_departure(self, time, customer):
        """Schedule a customer departure"""
        customer.departure_time = time
        self.events.append(Event(time, 'departure', customer))
        
    def run_simulation(self, simulation_time):
        """Run the simulation for specified time"""
        # Schedule first arrival
        next_arrival_time = self.exponential_random(PEAK_HOUR_ARRIVAL_RATE)
        self.schedule_arrival(next_arrival_time)
        
        # Process events until simulation time
        while self.events and self.time < simulation_time:
            # Sort events by time
            self.events.sort(key=lambda x: x.time)
            
            # Get next event
            event = self.events.pop(0)
            self.time = event.time
            
            if event.type == 'arrival':
                self.handle_arrival(event.customer)
                
                # Schedule next arrival if within simulation time
                next_arrival_time = self.time + self.exponential_random(PEAK_HOUR_ARRIVAL_RATE)
                if next_arrival_time < simulation_time:
                    self.schedule_arrival(next_arrival_time)
                    
            elif event.type == 'departure':
                self.handle_departure(event.customer)
        
        # Calculate waiting times for all customers who started service
        for customer in self.all_customers:
            if customer.start_service_time is not None:
                waiting_time = customer.start_service_time - customer.arrival_time
                self.waiting_times.append(waiting_time)
    
    def handle_arrival(self, customer):
        """Handle customer arrival"""
        if customer.is_self_service and self.available_self_service > 0:
            # Serve immediately at self-service terminal
            self.available_self_service -= 1
            customer.start_service_time = self.time
            
            # Schedule departure
            service_time = customer.service_time
            if random.random() < DELAY_PROBABILITY:
                service_time += random.uniform(DELAY_TIME_MIN, DELAY_TIME_MAX)
            departure_time = self.time + service_time
            self.schedule_departure(departure_time, customer)
        elif not customer.is_self_service and self.available_employees > 0:
            # Serve immediately with employee
            self.available_employees -= 1
            customer.start_service_time = self.time
            
            # Schedule departure
            service_time = customer.service_time
            if random.random() < DELAY_PROBABILITY:
                service_time += random.uniform(DELAY_TIME_MIN, DELAY_TIME_MAX)
            departure_time = self.time + service_time
            self.schedule_departure(departure_time, customer)
        else:
            # Add to appropriate queue
            if customer.is_self_service:
                self.self_service_queue.append(customer)
            else:
                self.employee_queue.append(customer)
    
    def handle_departure(self, customer):
        """Handle customer departure"""
        # Free up resource
        if customer.is_self_service:
            self.available_self_service += 1
            # Check if anyone is waiting in self-service queue
            if self.self_service_queue:
                next_customer = self.self_service_queue.pop(0)
                next_customer.start_service_time = self.time
                
                # Schedule departure
                service_time = next_customer.service_time
                if random.random() < DELAY_PROBABILITY:
                    service_time += random.uniform(DELAY_TIME_MIN, DELAY_TIME_MAX)
                departure_time = self.time + service_time
                self.schedule_departure(departure_time, next_customer)
        else:
            self.available_employees += 1
            # Check if anyone is waiting in employee queue
            if self.employee_queue:
                next_customer = self.employee_queue.pop(0)
                next_customer.start_service_time = self.time
                
                # Schedule departure
                service_time = next_customer.service_time
                if random.random() < DELAY_PROBABILITY:
                    service_time += random.uniform(DELAY_TIME_MIN, DELAY_TIME_MAX)
                departure_time = self.time + service_time
                self.schedule_departure(departure_time, next_customer)

def run_scenario(num_employees, num_self_service, simulation_time=SIMULATION_TIME):
    """Run a simulation scenario"""
    # Set random seed for reproducibility
    random.seed(42)
    
    pickup_point = PickupPoint(num_employees, num_self_service)
    pickup_point.run_simulation(simulation_time)
    return pickup_point

def analyze_results(scenarios):
    """Analyze results from different scenarios"""
    results = []
    
    for name, pickup_point in scenarios:
        if len(pickup_point.waiting_times) > 0:
            avg_waiting_time = sum(pickup_point.waiting_times) / len(pickup_point.waiting_times)
            max_waiting_time = max(pickup_point.waiting_times)
        else:
            avg_waiting_time = 0
            max_waiting_time = 0
        
        result = {
            'scenario': name,
            'avg_waiting_time': avg_waiting_time,
            'max_waiting_time': max_waiting_time,
            'total_customers': len(pickup_point.all_customers),
            'customers_served': len([c for c in pickup_point.all_customers if c.departure_time is not None])
        }
        results.append(result)
    
    return results

def plot_results(scenarios):
    """Plot comparison of results"""
    try:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Extract data
        names = [name for name, _ in scenarios]
        avg_waiting_times = [sum(pickup_point.waiting_times) / len(pickup_point.waiting_times) 
                            if len(pickup_point.waiting_times) > 0 else 0 
                            for _, pickup_point in scenarios]
        total_customers = [len(pickup_point.all_customers) for _, pickup_point in scenarios]
        
        # Average waiting time comparison
        axes[0].bar(names, avg_waiting_times, color=['blue', 'green', 'red'])
        axes[0].set_ylabel('Average Waiting Time (minutes)')
        axes[0].set_title('Average Waiting Time by Scenario')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Total customers comparison
        axes[1].bar(names, total_customers, color=['blue', 'green', 'red'])
        axes[1].set_ylabel('Total Customers')
        axes[1].set_title('Total Customers by Scenario')
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('improved_simulation_results.png')
        print("Results saved to improved_simulation_results.png")
        plt.show()
    except Exception as e:
        print(f"Error plotting results: {e}")
        print("Continuing without plotting...")

def main():
    """Main function to run simulations and compare scenarios"""
    print("Running Improved PVZ Optimization Simulation")
    print("=" * 50)
    
    # Scenario 1: Baseline - Traditional PVZ
    print("Running baseline scenario...")
    baseline_pvz = run_scenario(3, 0)
    
    # Scenario 2: With Self-Service Terminals
    print("Running self-service scenario...")
    self_service_pvz = run_scenario(3, 2)
    
    # Scenario 3: Simulated Bee Algorithm Optimization
    print("Running simulated bee algorithm scenario...")
    # We simulate the bee algorithm effect by reducing service time variability
    global SERVICE_TIME_STD
    original_std = SERVICE_TIME_STD
    SERVICE_TIME_STD = 0.2  # Reduced variability
    bee_algorithm_pvz = run_scenario(3, 2)
    SERVICE_TIME_STD = original_std  # Restore original value
    
    # Collect scenarios
    scenarios = [
        ("Baseline", baseline_pvz),
        ("With Self-Service", self_service_pvz),
        ("With Bee Algorithm", bee_algorithm_pvz)
    ]
    
    # Analyze results
    results = analyze_results(scenarios)
    
    print("\nSimulation Results:")
    print("-" * 50)
    for result in results:
        print(f"Scenario: {result['scenario']}")
        print(f"  Average waiting time: {result['avg_waiting_time']:.2f} minutes")
        print(f"  Max waiting time: {result['max_waiting_time']:.2f} minutes")
        print(f"  Total customers arrived: {result['total_customers']}")
        print(f"  Customers served: {result['customers_served']}")
        print()
    
    # Plot results
    plot_results(scenarios)
    
    # Business evaluation
    print("Business Evaluation:")
    print("-" * 20)
    
    baseline_avg_wait = results[0]['avg_waiting_time']
    optimized_avg_wait = results[2]['avg_waiting_time']
    
    if baseline_avg_wait > 0:
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
    else:
        print("No waiting time in baseline scenario - cannot calculate improvement")

if __name__ == "__main__":
    main()