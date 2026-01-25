"""
Financial Analytics Module
Handles inventory valuation, budget variance, and investment ROI analysis
"""

import pandas as pd
import numpy as np

class FinancialAnalytics:
    def __init__(self, valuation_data, budget_data, project_data, cost_data):
        self.valuation_data = valuation_data
        self.budget_data = budget_data
        self.project_data = project_data
        self.cost_data = cost_data
        
    def compare_inventory_valuation_methods(self):
        """
        Compare FIFO, LIFO, and Weighted Average inventory valuations
        Note: The synthetic data has 'unit_cost' which fluctuates.
        We will simulate valuation methods on this data.
        """
        # Group by part
        parts = self.valuation_data['part_id'].unique()
        
        results = []
        
        for part in parts:
            part_txns = self.valuation_data[self.valuation_data['part_id'] == part].sort_values('transaction_date')
            
            total_qty = part_txns['quantity'].sum()
            total_value_actual = part_txns['total_cost'].sum()
            
            if total_qty == 0:
                continue
                
            # Weighted Average
            wac_per_unit = total_value_actual / total_qty
            wac_value = total_value_actual 
            
            # FIFO (First In First Out) - Value based on oldest stock costs
            # For valuation, we assume 'current inventory' value. 
            # If we assume we hold X units, FIFO means we hold the MOST RECENTLY purchased units.
            # LIFO means we hold the OLDEST purchased units.
            # Let's assume current holding is 10% of total processed for simulation
            holding_qty = int(total_qty * 0.1)
            
            if holding_qty > 0:
                # FIFO Value: Sum of most recent 'holding_qty' costs
                # Reverse sort to get recent
                recent_txns = part_txns.sort_values('transaction_date', ascending=False)
                fifo_value = 0
                qty_needed = holding_qty
                
                for _, row in recent_txns.iterrows():
                    take = min(qty_needed, row['quantity'])
                    fifo_value += take * row['unit_cost']
                    qty_needed -= take
                    if qty_needed <= 0: break
                    
                # LIFO Value: Sum of oldest 'holding_qty' costs
                oldest_txns = part_txns.sort_values('transaction_date', ascending=True)
                lifo_value = 0
                qty_needed = holding_qty
                
                for _, row in oldest_txns.iterrows():
                    take = min(qty_needed, row['quantity'])
                    lifo_value += take * row['unit_cost']
                    qty_needed -= take
                    if qty_needed <= 0: break
                
                # WAC Value for holding
                wac_holding_value = holding_qty * wac_per_unit
                
                results.append({
                    'part_id': part,
                    'part_name': part_txns['part_name'].iloc[0],
                    'holding_qty': holding_qty,
                    'fifo_value': fifo_value,
                    'lifo_value': lifo_value,
                    'wac_value': wac_holding_value
                })
                
        return pd.DataFrame(results)

    def get_budget_variance_summary(self):
        """
        Summarize budget vs actuals
        """
        summary = self.budget_data.groupby('equipment_type').agg({
            'budget_amount': 'sum',
            'actual_amount': 'sum',
            'variance': 'sum'
        }).reset_index()
        
        summary['variance_pct'] = (summary['variance'] / summary['budget_amount']) * 100
        return summary

    def get_investment_portfolio(self):
        """
        Return investment projects with calculated metrics
        """
        return self.project_data.copy()

    def get_cost_breakdown_analysis(self):
        """
        Analyze cost variances by category
        """
        analysis = self.cost_data.groupby('cost_category').agg({
            'budget': 'sum',
            'actual': 'sum',
            'variance': 'sum'
        }).reset_index()
        
        analysis['variance_pct'] = (analysis['variance'] / analysis['budget']) * 100
        return analysis.sort_values('variance', ascending=False)
