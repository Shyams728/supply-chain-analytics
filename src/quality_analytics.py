"""
Quality & Six Sigma Analytics Module
Provides statistical process control (SPC) and quality management metrics
"""

import pandas as pd
import numpy as np

class QualityAnalytics:
    def __init__(self, spc_data, defect_data):
        self.spc_data = spc_data
        self.defect_data = defect_data
        # Ensure dates are datetime objects
        if 'inspection_date' in self.spc_data.columns:
            self.spc_data['inspection_date'] = pd.to_datetime(self.spc_data['inspection_date'])
        if 'defect_date' in self.defect_data.columns:
            self.defect_data['defect_date'] = pd.to_datetime(self.defect_data['defect_date'])

    def get_metrics_list(self):
        """Get list of available metrics for SPC analysis"""
        return self.spc_data['metric_name'].unique().tolist()

    def calculate_spc_charts(self, metric_name, window=25):
        """
        Calculate X-bar and R chart control limits
        Returns dataframe with CL, UCL, LCL
        """
        data = self.spc_data[self.spc_data['metric_name'] == metric_name].copy()
        data = data.sort_values('inspection_date')
        
        # Constants for n=5 (subgroup size)
        # A2 for X-bar limits, D3/D4 for R limits
        A2 = 0.577
        D3 = 0
        D4 = 2.114
        
        # Calculate Center Lines
        xbar_bar = data['xbar_value'].mean()
        r_bar = data['r_value'].mean()
        
        # Calculate Control Limits
        data['xbar_cl'] = xbar_bar
        data['xbar_ucl'] = xbar_bar + (A2 * r_bar)
        data['xbar_lcl'] = xbar_bar - (A2 * r_bar)
        
        data['r_cl'] = r_bar
        data['r_ucl'] = D4 * r_bar
        data['r_lcl'] = D3 * r_bar
        
        # Identify violations (Rule 1: Point beyond limits)
        data['xbar_violation'] = (data['xbar_value'] > data['xbar_ucl']) | (data['xbar_value'] < data['xbar_lcl'])
        data['r_violation'] = (data['r_value'] > data['r_ucl']) | (data['r_value'] < data['r_lcl'])
        
        return data

    def defect_pareto_analysis(self):
        """
        Generate Pareto analysis data for defects
        """
        defect_counts = self.defect_data['defect_type'].value_counts().reset_index()
        defect_counts.columns = ['defect_type', 'count']
        
        total_defects = defect_counts['count'].sum()
        defect_counts['percentage'] = (defect_counts['count'] / total_defects) * 100
        defect_counts['cumulative_percentage'] = defect_counts['percentage'].cumsum()
        
        return defect_counts

    def calculate_six_sigma_metrics(self):
        """
        Calculate DPMO and Sigma Level
        """
        total_defects = len(self.defect_data)
        # Assuming standardized opportunities per unit based on date range
        # Simplified estimation based on available data
        unique_dates = self.defect_data['defect_date'].nunique()
        estimated_units = unique_dates * 50 # Avg 50 units/day
        opportunities_per_unit = 50
        
        total_opportunities = estimated_units * opportunities_per_unit
        
        dpmo = (total_defects / total_opportunities) * 1_000_000 if total_opportunities > 0 else 0
        
        # Sigma conversion (simplified)
        # Yield = e^(-DPU)
        # Sigma approx = 0.8406 + sqrt(29.37 - 2.221 * ln(DPMO))
        if dpmo > 0:
            try:
                sigma_level = 0.8406 + np.sqrt(29.37 - 2.221 * np.log(dpmo))
            except:
                sigma_level = 0 # Fallback
        else:
            sigma_level = 6.0 # Perfect
            
        yield_pct = (1 - (total_defects / total_opportunities)) * 100 if total_opportunities > 0 else 100
        
        return {
            'dpmo': dpmo,
            'sigma_level': sigma_level,
            'yield_pct': yield_pct,
            'total_defects': total_defects,
            'total_opportunities': total_opportunities
        }
    
    def get_fishbone_data(self, defect_type):
        """
        Get root cause distribution for a specific defect type
        Structured for Fishbone (Ishikawa) diagram
        """
        data = self.defect_data[self.defect_data['defect_type'] == defect_type]
        
        fishbone = {
            'Man': [],
            'Machine': [],
            'Material': [],
            'Method': [],
            'Measurement': [],
            'Environment': []
        }
        
        # Get top causes per category
        for cat in fishbone.keys():
            causes = data[data['root_cause_category'] == cat]['root_cause'].value_counts().head(3)
            fishbone[cat] = [{'name': cause, 'value': count} for cause, count in causes.items()]
            
        return fishbone

    def defect_trend_analysis(self):
        """Monthly trend of defects"""
        trend = self.defect_data.copy()
        trend['month'] = trend['defect_date'].dt.to_period('M')
        monthly_counts = trend.groupby('month').size().reset_index(name='defect_count')
        monthly_counts['month'] = monthly_counts['month'].astype(str)
        return monthly_counts
