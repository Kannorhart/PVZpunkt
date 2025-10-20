import matplotlib.pyplot as plt
import numpy as np

# Sample data from our simulation results
scenarios = ['Baseline', 'With Self-Service', 'With Bee Algorithm']
avg_waiting_times = [2.1, 1.3, 1.2]  # in minutes
max_waiting_times = [5.2, 3.1, 2.8]  # in minutes
customers_served = [69, 113, 113]
utilization_rates = [92, 75, 65]  # in percent

def create_comprehensive_visualization():
    """Create comprehensive visualization of simulation results"""
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('PVZ Optimization Simulation Results', fontsize=16)
    
    # 1. Average Waiting Time Comparison
    bars1 = axes[0, 0].bar(scenarios, avg_waiting_times, color=['red', 'orange', 'green'])
    axes[0, 0].set_ylabel('Average Waiting Time (minutes)')
    axes[0, 0].set_title('Average Waiting Time by Scenario')
    axes[0, 0].set_ylim(0, max(avg_waiting_times) * 1.2)
    
    # Add value labels on bars
    for bar, value in zip(bars1, avg_waiting_times):
        axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                       f'{value:.1f}', ha='center', va='bottom')
    
    # 2. Customers Served Comparison
    bars2 = axes[0, 1].bar(scenarios, customers_served, color=['red', 'orange', 'green'])
    axes[0, 1].set_ylabel('Customers Served')
    axes[0, 1].set_title('Customers Served by Scenario')
    axes[0, 1].set_ylim(0, max(customers_served) * 1.2)
    
    # Add value labels on bars
    for bar, value in zip(bars2, customers_served):
        axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                       f'{value}', ha='center', va='bottom')
    
    # 3. Resource Utilization
    bars3 = axes[1, 0].bar(scenarios, utilization_rates, color=['red', 'orange', 'green'])
    axes[1, 0].set_ylabel('Resource Utilization (%)')
    axes[1, 0].set_title('Employee Utilization Rate')
    axes[1, 0].set_ylim(0, 100)
    axes[1, 0].axhline(y=80, color='r', linestyle='--', label='Target Utilization (80%)')
    axes[1, 0].legend()
    
    # Add value labels on bars
    for bar, value in zip(bars3, utilization_rates):
        axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                       f'{value}%', ha='center', va='bottom')
    
    # 4. Improvement Visualization
    improvements = [0, 38, 43]  # Percentage improvements
    bars4 = axes[1, 1].bar(scenarios, improvements, color=['gray', 'orange', 'green'])
    axes[1, 1].set_ylabel('Improvement (%)')
    axes[1, 1].set_title('Waiting Time Reduction')
    axes[1, 1].set_ylim(0, max(improvements) * 1.2)
    
    # Add value labels on bars
    for bar, value in zip(bars4, improvements):
        axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                       f'{value}%', ha='center', va='bottom')
    
    # Adjust layout
    plt.tight_layout()
    plt.savefig('comprehensive_results.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_business_case_visualization():
    """Create visualization for business case"""
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # Investment and savings data
    categories = ['Equipment', 'Integration', 'Annual Savings']
    values = [300000, 100000, 500000]  # in rubles
    colors = ['red', 'orange', 'green']
    
    bars = ax.bar(categories, values, color=colors)
    ax.set_ylabel('Amount (Rubles)')
    ax.set_title('PVZ Optimization Investment and ROI')
    
    # Add value labels
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10000,
               f'{value:,}', ha='center', va='bottom')
    
    # Add payback period annotation
    ax.annotate('Payback: 4-6 months', xy=(1, 100000), xytext=(1.5, 300000),
                arrowprops=dict(arrowstyle='->'), fontsize=12, ha='center')
    
    plt.tight_layout()
    plt.savefig('business_case.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Generate all visualizations"""
    print("Generating comprehensive visualization...")
    create_comprehensive_visualization()
    
    print("Generating business case visualization...")
    create_business_case_visualization()
    
    print("Visualizations saved as 'comprehensive_results.png' and 'business_case.png'")

if __name__ == "__main__":
    main()