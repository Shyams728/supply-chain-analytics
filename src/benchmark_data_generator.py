"""
Benchmark Data Generator
Industry benchmarks and performance standards for construction equipment
"""

import pandas as pd
import numpy as np

def generate_industry_benchmarks():
    """Generate industry benchmark data for heavy equipment"""
    
    benchmarks = [
        # Equipment Availability Benchmarks
        {'metric_name': 'Equipment Availability', 'equipment_class': 'Excavator', 
         'industry_average': 85.0, 'best_in_class': 95.0, 'acceptable_range': '80-90'},
        {'metric_name': 'Equipment Availability', 'equipment_class': 'Bulldozer',
         'industry_average': 83.0, 'best_in_class': 93.0, 'acceptable_range': '78-88'},
        {'metric_name': 'Equipment Availability', 'equipment_class': 'Dump Truck',
         'industry_average': 88.0, 'best_in_class': 96.0, 'acceptable_range': '85-92'},
        {'metric_name': 'Equipment Availability', 'equipment_class': 'Crane',
         'industry_average': 80.0, 'best_in_class': 92.0, 'acceptable_range': '75-88'},
        {'metric_name': 'Equipment Availability', 'equipment_class': 'Loader',
         'industry_average': 86.0, 'best_in_class': 94.0, 'acceptable_range': '82-90'},
        
        # OEE Benchmarks
        {'metric_name': 'Overall Equipment Effectiveness (OEE)', 'equipment_class': 'Excavator',
         'industry_average': 65.0, 'best_in_class': 85.0, 'acceptable_range': '60-75'},
        {'metric_name': 'Overall Equipment Effectiveness (OEE)', 'equipment_class': 'Bulldozer',
         'industry_average': 62.0, 'best_in_class': 82.0, 'acceptable_range': '58-72'},
        {'metric_name': 'Overall Equipment Effectiveness (OEE)', 'equipment_class': 'Dump Truck',
         'industry_average': 70.0, 'best_in_class': 88.0, 'acceptable_range': '65-78'},
        {'metric_name': 'Overall Equipment Effectiveness (OEE)', 'equipment_class': 'Crane',
         'industry_average': 58.0, 'best_in_class': 80.0, 'acceptable_range': '55-70'},
        {'metric_name': 'Overall Equipment Effectiveness (OEE)', 'equipment_class': 'Loader',
         'industry_average': 67.0, 'best_in_class': 85.0, 'acceptable_range': '62-75'},
        
        # MTBF Benchmarks (days)
        {'metric_name': 'MTBF (days)', 'equipment_class': 'Excavator',
         'industry_average': 45.0, 'best_in_class': 75.0, 'acceptable_range': '35-60'},
        {'metric_name': 'MTBF (days)', 'equipment_class': 'Bulldozer',
         'industry_average': 42.0, 'best_in_class': 70.0, 'acceptable_range': '32-55'},
        {'metric_name': 'MTBF (days)', 'equipment_class': 'Dump Truck',
         'industry_average': 55.0, 'best_in_class': 85.0, 'acceptable_range': '45-70'},
        {'metric_name': 'MTBF (days)', 'equipment_class': 'Crane',
         'industry_average': 38.0, 'best_in_class': 65.0, 'acceptable_range': '30-50'},
        {'metric_name': 'MTBF (days)', 'equipment_class': 'Loader',
         'industry_average': 48.0, 'best_in_class': 72.0, 'acceptable_range': '38-60'},
        
        # MTTR Benchmarks (hours)
        {'metric_name': 'MTTR (hours)', 'equipment_class': 'Excavator',
         'industry_average': 12.0, 'best_in_class': 6.0, 'acceptable_range': '6-15'},
        {'metric_name': 'MTTR (hours)', 'equipment_class': 'Bulldozer',
         'industry_average': 14.0, 'best_in_class': 7.0, 'acceptable_range': '7-18'},
        {'metric_name': 'MTTR (hours)', 'equipment_class': 'Dump Truck',
         'industry_average': 8.0, 'best_in_class': 4.0, 'acceptable_range': '4-12'},
        {'metric_name': 'MTTR (hours)', 'equipment_class': 'Crane',
         'industry_average': 16.0, 'best_in_class': 8.0, 'acceptable_range': '8-20'},
        {'metric_name': 'MTTR (hours)', 'equipment_class': 'Loader',
         'industry_average': 10.0, 'best_in_class': 5.0, 'acceptable_range': '5-14'},
        
        # Supply Chain Metrics
        {'metric_name': 'On-Time Delivery %', 'equipment_class': 'All',
         'industry_average': 85.0, 'best_in_class': 98.0, 'acceptable_range': '80-95'},
        {'metric_name': 'Fill Rate %', 'equipment_class': 'All',
         'industry_average': 92.0, 'best_in_class': 99.0, 'acceptable_range': '90-97'},
        {'metric_name': 'Perfect Order Rate %', 'equipment_class': 'All',
         'industry_average': 88.0, 'best_in_class': 96.0, 'acceptable_range': '85-93'},
        {'metric_name': 'Inventory Turnover (times/year)', 'equipment_class': 'All',
         'industry_average': 6.0, 'best_in_class': 12.0, 'acceptable_range': '4-8'},
        {'metric_name': 'Days of Supply', 'equipment_class': 'All',
         'industry_average': 60.0, 'best_in_class': 30.0, 'acceptable_range': '30-75'},
        {'metric_name': 'Cash-to-Cash Cycle (days)', 'equipment_class': 'All',
         'industry_average': 45.0, 'best_in_class': 20.0, 'acceptable_range': '20-60'},
        
        # Quality Metrics
        {'metric_name': 'DPMO', 'equipment_class': 'All',
         'industry_average': 15000.0, 'best_in_class': 3400.0, 'acceptable_range': '3400-25000'},
        {'metric_name': 'Sigma Level', 'equipment_class': 'All',
         'industry_average': 3.8, 'best_in_class': 6.0, 'acceptable_range': '3.0-4.5'},
        {'metric_name': 'First Pass Yield %', 'equipment_class': 'All',
         'industry_average': 92.0, 'best_in_class': 99.5, 'acceptable_range': '90-96'},
        
        # Cost Metrics
        {'metric_name': 'Maintenance Cost as % of Asset Value', 'equipment_class': 'All',
         'industry_average': 4.5, 'best_in_class': 2.5, 'acceptable_range': '2.5-6.0'},
        {'metric_name': 'Cost per Operating Hour (₹)', 'equipment_class': 'Excavator',
         'industry_average': 850.0, 'best_in_class': 600.0, 'acceptable_range': '600-1000'},
        {'metric_name': 'Cost per Operating Hour (₹)', 'equipment_class': 'Bulldozer',
         'industry_average': 920.0, 'best_in_class': 650.0, 'acceptable_range': '650-1100'},
    ]
    
    df = pd.DataFrame(benchmarks)
    df['source'] = 'Construction Equipment Industry Standards 2024'
    df['last_updated'] = '2024-01-01'
    
    return df

def generate_maintenance_schedule():
    """Generate synthetic maintenance schedule for Gantt charts"""
    
    records = []
    
    # Load equipment data
    equipment_df = pd.read_csv('data/equipment.csv')
    
    # Maintenance task types
    task_types = {
        'PM-Monthly': {'duration': 1, 'frequency': 30},
        'PM-Quarterly': {'duration': 2, 'frequency': 90},
        'PM-Annual': {'duration': 5, 'frequency': 365},
        'Overhaul': {'duration': 10, 'frequency': 730},
        'Inspection': {'duration': 0.5, 'frequency': 14}
    }
    
    technicians = ['Tech-A', 'Tech-B', 'Tech-C', 'Tech-D', 'Tech-E']
    
    task_id = 1
    start_date = pd.to_datetime('2025-01-01')
    
    for _, equipment in equipment_df.iterrows():
        for task_type, params in task_types.items():
            # Schedule tasks for next 6 months
            for i in range(6):
                task_start = start_date + pd.Timedelta(days=i * params['frequency'])
                task_end = task_start + pd.Timedelta(days=params['duration'])
                
                # Dependencies (quarterly depends on monthly)
                if task_type == 'PM-Quarterly' and i > 0:
                    dependency = f"TASK{task_id - 5}"  # Depends on previous monthly
                else:
                    dependency = None
                
                records.append({
                    'task_id': f"TASK{task_id:05d}",
                    'equipment_id': equipment['equipment_id'],
                    'equipment_name': equipment['equipment_name'],
                    'equipment_type': equipment['equipment_type'],
                    'task_name': f"{task_type} - {equipment['equipment_name']}",
                    'task_type': task_type,
                    'start_date': task_start,
                    'end_date': task_end,
                    'duration_days': params['duration'],
                    'assigned_technician': np.random.choice(technicians),
                    'status': np.random.choice(['Scheduled', 'In Progress', 'Completed'], p=[0.6, 0.2, 0.2]),
                    'dependencies': dependency,
                    'priority': np.random.choice(['High', 'Medium', 'Low'], p=[0.2, 0.5, 0.3])
                })
                
                task_id += 1
                
                if task_id > 500:  # Limit to 500 tasks for demo
                    break
            if task_id > 500:
                break
        if task_id > 500:
            break
    
    return pd.DataFrame(records)

def main():
    """Generate and save benchmark and schedule data"""
    
    print("Generating industry benchmark data...")
    benchmarks = generate_industry_benchmarks()
    benchmarks.to_csv('data/industry_benchmarks.csv', index=False)
    print(f"[SUCCESS] Generated {len(benchmarks)} benchmark records")
    
    print("\nGenerating maintenance schedule data...")
    schedule = generate_maintenance_schedule()
    schedule.to_csv('data/maintenance_schedule.csv', index=False)
    print(f"[SUCCESS] Generated {len(schedule)} scheduled maintenance tasks")
    
    print("\n[COMPLETE] Benchmark and schedule data generation complete!")
    
    # Display sample benchmarks
    print("\nSample Industry Benchmarks:")
    print(benchmarks.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
