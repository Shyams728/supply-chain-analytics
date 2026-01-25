"""
Financial Analytics Data Generator
Generates synthetic financial data for inventory valuation, budgets, and ROI analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

class FinancialDataGenerator:
    """Generate synthetic financial tracking data"""
    
    def __init__(self, inventory_df, equipment_df, start_date='2022-01-01', end_date='2024-12-31'):
        self.inventory_df = inventory_df
        self.equipment_df = equipment_df
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        
    def generate_maintenance_budget(self):
        """Generate monthly maintenance budgets vs actuals"""
        
        records = []
        
        # Equipment types with annual budget allocations
        budget_allocation = {
            'Excavator': 5000000,
            'Bulldozer': 4500000,
            'Dump Truck': 3500000,
            'Crane': 6000000,
            'Loader': 3000000
        }
        
        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='MS')
        
        for date in date_range:
            for eq_type, annual_budget in budget_allocation.items():
                monthly_budget = annual_budget / 12
                
                # Actual varies from budget (realistic variance)
                variance_pct = np.random.normal(0, 0.15)  # Mean 0%, std 15%
                actual = monthly_budget * (1 + variance_pct)
                
                # Add some seasonality - higher costs in summer
                month = date.month
                if month in [5, 6, 7, 8]:  # Summer months
                    actual *= random.uniform(1.05, 1.15)
                elif month in [12, 1, 2]:  # Winter months
                    actual *= random.uniform(0.90, 0.95)
                
                variance = actual - monthly_budget
                
                records.append({
                    'period': date.strftime('%Y-%m'),
                    'year': date.year,
                    'month': date.month,
                    'equipment_type': eq_type,
                    'budget_amount': round(monthly_budget, 2),
                    'actual_amount': round(actual, 2),
                    'variance': round(variance, 2),
                    'variance_pct': round((variance / monthly_budget) * 100, 2),
                    'category': 'Maintenance'
                })
        
        return pd.DataFrame(records)
    
    def generate_inventory_valuation_data(self, spare_parts_df):
        """Generate inventory transactions with FIFO/LIFO tracking"""
        
        records = []
        
        # For each part, generate purchase history with varying costs
        for _, part in spare_parts_df.iterrows():
            base_cost = part['unit_cost']
            
            # Generate 10-20 purchases over time period
            num_purchases = random.randint(10, 20)
            dates = sorted(random.sample(list(pd.date_range(self.start_date, self.end_date, freq='D')), num_purchases))
            
            for i, date in enumerate(dates):
                # Cost increases over time with inflation
                days_elapsed = (date - self.start_date).days
                inflation_factor = 1 + (days_elapsed / 365) * 0.05  # 5% annual inflation
                cost_variance = random.uniform(0.95, 1.05)  # 5% random variance
                
                unit_cost = base_cost * inflation_factor * cost_variance
                quantity = random.randint(10, 100)
                
                records.append({
                    'transaction_id': f"PUR{len(records)+1:06d}",
                    'transaction_date': date,
                    'part_id': part['part_id'],
                    'part_name': part['part_name'],
                    'transaction_type': 'Purchase',
                    'quantity': quantity,
                    'unit_cost': round(unit_cost, 2),
                    'total_cost': round(unit_cost * quantity, 2),
                    'batch_id': f"BATCH{len(records)+1:05d}"
                })
        
        return pd.DataFrame(records)
    
    def generate_maintenance_investment_projects(self):
        """Generate maintenance improvement investment cases for ROI analysis"""
        
        projects = [
            {
                'name': 'Predictive Maintenance System - Excavators',
                'investment': 2500000,
                'annual_savings': 800000,
                'equipment_type': 'Excavator'
            },
            {
                'name': 'Automated Lubrication System - All Equipment',
                'investment': 1500000,
                'annual_savings': 450000,
                'equipment_type': 'All'
            },
            {
                'name': 'Hydraulic System Upgrade - Cranes',
                'investment': 3000000,
                'annual_savings': 950000,
                'equipment_type': 'Crane'
            },
            {
                'name': 'Engine Overhaul Program - Dump Trucks',
                'investment': 1800000,
                'annual_savings': 550000,
                'equipment_type': 'Dump Truck'
            },
            {
                'name': 'Condition Monitoring Sensors - Bulldozers',
                'investment': 1200000,
                'annual_savings': 380000,
                'equipment_type': 'Bulldozer'
            },
            {
                'name': 'CMMS Software Implementation',
                'investment': 500000,
                'annual_savings': 200000,
                'equipment_type': 'All'
            }
        ]
        
        records = []
        
        for i, project in enumerate(projects):
            # Calculate financial metrics
            payback_period = project['investment'] / project['annual_savings']
            
            # NPV calculation (5 year horizon, 10% discount rate)
            discount_rate = 0.10
            years = 5
            npv = -project['investment']
            for year in range(1, years + 1):
                npv += project['annual_savings'] / ((1 + discount_rate) ** year)
            
            # IRR approximation
            irr = (project['annual_savings'] / project['investment']) - discount_rate
            
            # ROI
            roi = ((project['annual_savings'] * years) - project['investment']) / project['investment'] * 100
            
            records.append({
                'project_id': f"PROJ{i+1:03d}",
                'project_name': project['name'],
                'equipment_type': project['equipment_type'],
                'investment_amount': project['investment'],
                'annual_savings': project['annual_savings'],
                'payback_period_years': round(payback_period, 2),
                'npv_5year': round(npv, 2),
                'irr_pct': round(irr * 100, 2),
                'roi_pct': round(roi, 2),
                'status': random.choice(['Proposed', 'Approved', 'In Progress', 'Completed']),
                'implementation_date': self.start_date + timedelta(days=random.randint(0, 730))
            })
        
        return pd.DataFrame(records)
    
    def generate_cost_breakdown(self):
        """Generate detailed cost breakdown for variance analysis"""
        
        records = []
        
        cost_categories = {
            'Labor': {'base': 1200000, 'variance': 0.10},
            'Spare Parts': {'base': 800000, 'variance': 0.20},
            'Consumables': {'base': 300000, 'variance': 0.15},
            'External Services': {'base': 500000, 'variance': 0.25},
            'Tools & Equipment': {'base': 200000, 'variance': 0.12},
            'Transportation': {'base': 150000, 'variance': 0.18}
        }
        
        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='MS')
        
        for date in date_range:
            for category, params in cost_categories.items():
                monthly_budget = params['base'] / 12
                
                # Generate variance with specific reasons
                variance_pct = np.random.normal(0, params['variance'])
                
                if variance_pct > 0.15:
                    reason = 'Unplanned Breakdown'
                elif variance_pct > 0.08:
                    reason = 'Price Increase'
                elif variance_pct < -0.08:
                    reason = 'Efficiency Improvement'
                else:
                    reason = 'Normal Variance'
                
                actual = monthly_budget * (1 + variance_pct)
                
                records.append({
                    'period': date.strftime('%Y-%m'),
                    'cost_category': category,
                    'budget': round(monthly_budget, 2),
                    'actual': round(actual, 2),
                    'variance': round(actual - monthly_budget, 2),
                    'variance_pct': round(variance_pct * 100, 2),
                    'variance_reason': reason
                })
        
        return pd.DataFrame(records)

def main():
    """Generate and save financial data"""
    
    print("Loading base data...")
    inventory = pd.read_csv('data/inventory_transactions.csv')
    equipment = pd.read_csv('data/equipment.csv')
    spare_parts = pd.read_csv('data/spare_parts.csv')
    
    print("Initializing Financial Data Generator...")
    generator = FinancialDataGenerator(inventory, equipment)
    
    print("Generating maintenance budget data...")
    budget_data = generator.generate_maintenance_budget()
    budget_data.to_csv('data/maintenance_budget.csv', index=False)
    print(f"[SUCCESS] Generated {len(budget_data)} budget records")
    
    print("Generating inventory valuation data...")
    valuation_data = generator.generate_inventory_valuation_data(spare_parts)
    valuation_data.to_csv('data/inventory_valuation.csv', index=False)
    print(f"[SUCCESS] Generated {len(valuation_data)} valuation transactions")
    
    print("Generating investment project data...")
    project_data = generator.generate_maintenance_investment_projects()
    project_data.to_csv('data/maintenance_projects.csv', index=False)
    print(f"[SUCCESS] Generated {len(project_data)} investment projects")
    
    print("Generating cost breakdown data...")
    cost_data = generator.generate_cost_breakdown()
    cost_data.to_csv('data/cost_breakdown.csv', index=False)
    print(f"[SUCCESS] Generated {len(cost_data)} cost breakdown records")
    
    print("\n[COMPLETE] Financial data generation complete!")
    
    # Summary statistics
    total_budget = budget_data['budget_amount'].sum()
    total_actual = budget_data['actual_amount'].sum()
    print(f"\nSummary:")
    print(f"  Total Budget (3 years): Rs.{total_budget:,.0f}")
    print(f"  Total Actual (3 years): Rs.{total_actual:,.0f}")
    print(f"  Overall Variance: Rs.{total_actual - total_budget:,.0f} ({((total_actual/total_budget - 1) * 100):.1f}%)")

if __name__ == "__main__":
    main()
