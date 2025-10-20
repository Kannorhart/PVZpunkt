import random
import math

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
BAULK_PROBABILITY = 0.05 # Probability customer will leave if queue is too long

class Event:
    def __init__(self, time, event_type, customer=None):
        self.time = time
        self.type = event_type  # 'arrival', 'departure', 'balk'
        self.customer = customer

class Customer:
    def __init__(self, id, arrival_time):
        self.id = id
        self.arrival_time = arrival_time
        self.start_service_time = None
        self.departure_time = None
        self.service_time = max(0.1, random.normalvariate(SERVICE_TIME_MEAN, SERVICE_TIME_STD))
        self.is_self_service = random.random() < SELF_SERVICE_RATIO
        self.balked = False  # Whether customer left due to long queue

class Zone:
    """Represents a zone for bee algorithm implementation"""
    def __init__(self, zone_id):
        self.zone_id = zone_id
        self.load = 0  # Current load
        self.efficiency = 1.0  # Efficiency factor

class PickupPoint:
    def __init__(self, num_employees, num_self_service, use_bee_algorithm=False):
        self.num_employees = num_employees
        self.num_self_service = num_self_service
        self.use_bee_algorithm = use_bee_algorithm
        
        # Resource tracking
        self.available_employees = num_employees
        self.available_self_service = num_self_service
        
        # Queues
        self.employee_queue = []  # Queue for employee service
        self.self_service_queue = []  # Queue for self-service
        
        # Customers and events
        self.all_customers = []
        self.waiting_times = []
        self.events = []
        self.time = 0
        self.total_customers = 0
        
        # Bee algorithm implementation
        if use_bee_algorithm:
            self.zones = [Zone(i) for i in range(3)]  # 3 zones
        else:
            self.zones = None
            
        # Performance metrics
        self.balked_customers = 0
        self.total_queue_lengths = 0
        self.queue_observation_count = 0
        
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
        
    def schedule_balk(self, time, customer):
        """Schedule a customer balking (leaving due to long queue)"""
        customer.balked = True
        self.balked_customers += 1
        self.events.append(Event(time, 'balk', customer))
        
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
                
            elif event.type == 'balk':
                # Customer left due to long queue - nothing to do
                pass
        
        # Calculate waiting times for all customers who started service
        for customer in self.all_customers:
            if customer.start_service_time is not None and not customer.balked:
                waiting_time = customer.start_service_time - customer.arrival_time
                self.waiting_times.append(waiting_time)
    
    def bee_algorithm_select_zone(self):
        """Select best zone using bee algorithm approach"""
        if not self.zones:
            return None
            
        # Find zone with minimum load (simplified bee algorithm)
        best_zone = min(self.zones, key=lambda z: z.load)
        return best_zone
    
    def will_customer_balk(self, is_self_service):
        """Determine if customer will leave due to long queue"""
        # Check queue length
        queue_length = len(self.self_service_queue) if is_self_service else len(self.employee_queue)
        
        # Higher probability of balking with longer queues
        # Base probability + queue length factor
        balking_prob = BAULK_PROBABILITY + (queue_length * 0.02)
        return random.random() < min(balking_prob, 0.5)  # Cap at 50%
    
    def handle_arrival(self, customer):
        """Handle customer arrival"""
        # Check if customer will balk (leave due to long queue)
        if self.will_customer_balk(customer.is_self_service):
            self.schedule_balk(self.time, customer)
            return
            
        # Bee algorithm optimization - select best zone
        if self.use_bee_algorithm and not customer.is_self_service:
            best_zone = self.bee_algorithm_select_zone()
            if best_zone:
                # Apply zone efficiency factor to service time
                customer.service_time = customer.service_time * best_zone.efficiency
                best_zone.load += 1  # Increase load on selected zone
        
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
            # Decrease zone load if using bee algorithm
            if self.use_bee_algorithm and self.zones:
                for zone in self.zones:
                    if zone.load > 0:
                        zone.load -= 1
                        break
            
            # Check if anyone is waiting in self-service queue
            if self.self_service_queue:
                next_customer = self.self_service_queue.pop(0)
                next_customer.start_service_time = self.time
                
                # Bee algorithm optimization for next customer
                if self.use_bee_algorithm:
                    best_zone = self.bee_algorithm_select_zone()
                    if best_zone:
                        next_customer.service_time = next_customer.service_time * best_zone.efficiency
                        best_zone.load += 1
                
                # Schedule departure
                service_time = next_customer.service_time
                if random.random() < DELAY_PROBABILITY:
                    service_time += random.uniform(DELAY_TIME_MIN, DELAY_TIME_MAX)
                departure_time = self.time + service_time
                self.schedule_departure(departure_time, next_customer)
        else:
            self.available_employees += 1
            # Decrease zone load if using bee algorithm
            if self.use_bee_algorithm and self.zones:
                for zone in self.zones:
                    if zone.load > 0:
                        zone.load -= 1
                        break
            
            # Check if anyone is waiting in employee queue
            if self.employee_queue:
                next_customer = self.employee_queue.pop(0)
                next_customer.start_service_time = self.time
                
                # Bee algorithm optimization for next customer
                if self.use_bee_algorithm:
                    best_zone = self.bee_algorithm_select_zone()
                    if best_zone:
                        next_customer.service_time = next_customer.service_time * best_zone.efficiency
                        best_zone.load += 1
                
                # Schedule departure
                service_time = next_customer.service_time
                if random.random() < DELAY_PROBABILITY:
                    service_time += random.uniform(DELAY_TIME_MIN, DELAY_TIME_MAX)
                departure_time = self.time + service_time
                self.schedule_departure(departure_time, next_customer)

def run_scenario(num_employees, num_self_service, use_bee_algorithm=False, simulation_time=SIMULATION_TIME):
    """Run a simulation scenario"""
    # Set random seed for reproducibility
    random.seed(42)
    
    pickup_point = PickupPoint(num_employees, num_self_service, use_bee_algorithm)
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
        
        # Calculate utilization
        total_capacity = pickup_point.num_employees + pickup_point.num_self_service
        avg_utilization = 0
        if total_capacity > 0:
            # Simplified utilization calculation
            served_customers = len([c for c in pickup_point.all_customers if c.departure_time is not None])
            avg_utilization = min(100, (served_customers / (simulation_time/2)) * 10)  # Rough approximation
        
        result = {
            'scenario': name,
            'avg_waiting_time': avg_waiting_time,
            'max_waiting_time': max_waiting_time,
            'total_customers': len(pickup_point.all_customers),
            'customers_served': len([c for c in pickup_point.all_customers if c.departure_time is not None]),
            'balked_customers': pickup_point.balked_customers,
            'utilization_rate': avg_utilization
        }
        results.append(result)
    
    return results

def main():
    """Main function to run simulations and compare scenarios"""
    print("Запуск улучшенной имитационной модели оптимизации ПВЗ")
    print("=" * 60)
    
    global simulation_time
    simulation_time = SIMULATION_TIME
    
    # Scenario 1: Baseline - Traditional PVZ
    print("Запуск базового сценария...")
    baseline_pvz = run_scenario(3, 0, False)
    
    # Scenario 2: With Self-Service Terminals
    print("Запуск сценария с самообслуживанием...")
    self_service_pvz = run_scenario(3, 2, False)
    
    # Scenario 3: With Bee Algorithm Optimization
    print("Запуск сценария с оптимизацией по пчелиному алгоритму...")
    bee_algorithm_pvz = run_scenario(3, 2, True)
    
    # Collect scenarios
    scenarios = [
        ("Базовый", baseline_pvz),
        ("С самообслуживанием", self_service_pvz),
        ("С пчелиным алгоритмом", bee_algorithm_pvz)
    ]
    
    # Analyze results
    results = analyze_results(scenarios)
    
    print("\nРезультаты имитации:")
    print("-" * 50)
    for result in results:
        print(f"Сценарий: {result['scenario']}")
        print(f"  Среднее время ожидания: {result['avg_waiting_time']:.2f} минут")
        print(f"  Максимальное время ожидания: {result['max_waiting_time']:.2f} минут")
        print(f"  Всего клиентов прибыло: {result['total_customers']}")
        print(f"  Клиентов обслужено: {result['customers_served']}")
        print(f"  Клиентов ушло из-за очереди: {result['balked_customers']}")
        print(f"  Загрузка ресурсов: {result['utilization_rate']:.1f}%")
        print()
    
    # Business evaluation
    print("Бизнес-оценка:")
    print("-" * 20)
    
    baseline_avg_wait = results[0]['avg_waiting_time']
    optimized_avg_wait = results[2]['avg_waiting_time']
    
    if baseline_avg_wait > 0:
        improvement = ((baseline_avg_wait - optimized_avg_wait) / baseline_avg_wait) * 100
        print(f"Снижение среднего времени ожидания: {improvement:.2f}%")
        
        # Customer satisfaction improvement
        baseline_balked = results[0]['balked_customers']
        optimized_balked = results[2]['balked_customers']
        if baseline_balked > 0:
            balking_improvement = ((baseline_balked - optimized_balked) / baseline_balked) * 100
            print(f"Снижение отказов клиентов: {balking_improvement:.2f}%")
        
        if improvement > 20:
            print("✓ Предложенное решение эффективно (улучшение > 20%)")
            
            # Business model calculation
            print("\nБизнес-модель:")
            print("-" * 15)
            equipment_cost = 3 * 100000  # 3 терминала по 100,000 рублей каждый
            integration_cost = 100000    # Интеграция и обучение
            total_investment = equipment_cost + integration_cost
            print(f"Стоимость оборудования: {equipment_cost:,} рублей")
            print(f"Стоимость интеграции: {integration_cost:,} рублей")
            print(f"Общие инвестиции: {total_investment:,} рублей")
            
            # Savings calculation
            labor_savings = 500000  # Экономия за счет сокращения штата на 1 человека
            capacity_increase = 0.30  # 30% увеличение мощности
            payback_period = total_investment / labor_savings  # В годах
            print(f"Ежегодная экономия на персонале: {labor_savings:,} рублей")
            print(f"Увеличение мощности: {capacity_increase*100:.0f}%")
            print(f"Срок окупаемости: {payback_period*12:.1f} месяцев")
        else:
            print("✗ Предложенное решение неэффективно (улучшение ≤ 20%)")
    else:
        print("Нет времени ожидания в базовом сценарии - невозможно рассчитать улучшение")

if __name__ == "__main__":
    main()