"""
Benchmarking Analytics Module
Compares internal KPIs against industry standards and peer groups
"""

import pandas as pd
import numpy as np

class BenchmarkingAnalytics:
    def __init__(self, benchmark_data):
        self.benchmark_data = benchmark_data

    def get_available_benchmarks(self):
        return self.benchmark_data['metric_name'].unique().tolist()
        
    def compare_against_industry(self, internal_metric_name, internal_value, equipment_class='All'):
        """
        Compare an internal KPI value against industry benchmark
        Returns dict with comparison details
        """
        # Find matching benchmark
        match = self.benchmark_data[
            (self.benchmark_data['metric_name'] == internal_metric_name) & 
            (self.benchmark_data['equipment_class'] == equipment_class)
        ]
        
        if match.empty:
            # Fallback to 'All' if specific class not found
            match = self.benchmark_data[
                (self.benchmark_data['metric_name'] == internal_metric_name) & 
                (self.benchmark_data['equipment_class'] == 'All')
            ]
            
        if match.empty:
            return None
            
        benchmark = match.iloc[0]
        
        # Determine direction (Higher is better? or Lower is better?)
        # Typically Cost, Defects, MTTR -> Lower is better
        # OEE, Availability, MTBF -> Higher is better
        lower_is_better = any(x in internal_metric_name.lower() for x in ['cost', 'mttr', 'defect', 'dpmo'])
        
        industry_avg = benchmark['industry_average']
        best_in_class = benchmark['best_in_class']
        
        gap = best_in_class - internal_value
        if lower_is_better:
            gap = internal_value - best_in_class # Gap is how much we are OVER the target
            percent_diff_industry = ((internal_value - industry_avg) / industry_avg) * 100
        else:
            percent_diff_industry = ((internal_value - industry_avg) / industry_avg) * 100
            
        status = 'On Track'
        if lower_is_better:
            if internal_value <= best_in_class: status = 'World Class'
            elif internal_value <= industry_avg: status = 'Above Average'
            else: status = 'Below Average'
        else:
            if internal_value >= best_in_class: status = 'World Class'
            elif internal_value >= industry_avg: status = 'Above Average'
            else: status = 'Below Average'
            
        return {
            'metric': internal_metric_name,
            'internal_value': internal_value,
            'industry_average': industry_avg,
            'best_in_class': best_in_class,
            'gap_to_best': gap,
            'vs_industry_pct': percent_diff_industry,
            'status': status,
            'acceptable_range': benchmark['acceptable_range']
        }
        
    def peer_equipment_comparison(self, maintenance_metrics_df):
        """
        Rank equipment based on composite maintenance score
        Expects dataframe with: equipment_id, availability, mtbf, cost
        """
        df = maintenance_metrics_df.copy()
        
        # Normalize metrics (0-1 scale)
        # Higher availability is good
        df['avail_norm'] = (df['availability_pct'] - df['availability_pct'].min()) / (df['availability_pct'].max() - df['availability_pct'].min())
        
        # Higher MTBF is good
        df['mtbf_norm'] = (df['mtbf_days'] - df['mtbf_days'].min()) / (df['mtbf_days'].max() - df['mtbf_days'].min())
        
        # Lower Cost is good -> Invert
        cost_min = df['total_repair_cost'].min()
        cost_max = df['total_repair_cost'].max()
        df['cost_norm'] = 1 - ((df['total_repair_cost'] - cost_min) / (cost_max - cost_min))
        
        # Composite Score (weighted)
        # 40% Avail, 30% MTBF, 30% Cost
        df['composite_score'] = (0.4 * df['avail_norm'] + 0.3 * df['mtbf_norm'] + 0.3 * df['cost_norm']) * 100
        
        df = df.sort_values('composite_score', ascending=False)
        df['rank'] = range(1, len(df) + 1)
        
        return df[['equipment_name', 'equipment_type', 'composite_score', 'rank', 'availability_pct', 'mtbf_days', 'total_repair_cost']]
