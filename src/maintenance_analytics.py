"""
Manufacturing & Maintenance Analytics Module
Reliability Analysis, MTBF/MTTR, Failure Patterns
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sys
import os

# Add src to path if needed for direct execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ml_models import FailurePredictor

class MaintenanceAnalytics:
    """
    Comprehensive maintenance and reliability analytics
    """
    
    def __init__(self, equipment_df, downtime_df):
        self.equipment = equipment_df
        self.downtime = downtime_df
        self.merged_data = None
        self._prepare_data()
    
    def _prepare_data(self):
        """Merge and prepare datasets"""
        self.merged_data = pd.merge(
            self.downtime,
            self.equipment,
            on='equipment_id',
            how='left'
        )
        
        # Convert dates
        date_cols = ['failure_date', 'repair_start_date', 'repair_end_date']
        for col in date_cols:
            self.merged_data[col] = pd.to_datetime(self.merged_data[col])
        
        # Extract time features
        self.merged_data['failure_month'] = self.merged_data['failure_date'].dt.to_period('M')
        self.merged_data['failure_year'] = self.merged_data['failure_date'].dt.year
    
    def calculate_reliability_metrics(self):
        """
        Calculate MTBF, MTTR, and other reliability KPIs
        """
        reliability_metrics = self.merged_data.groupby('equipment_id').agg({
            'downtime_id': 'count',  # Total failures
            'downtime_hours': ['sum', 'mean', 'std'],
            'repair_cost': ['sum', 'mean'],
            'failure_date': ['min', 'max']
        }).reset_index()
        
        reliability_metrics.columns = [
            'equipment_id', 'total_failures', 'total_downtime_hours',
            'mttr_hours', 'downtime_std', 'total_repair_cost',
            'avg_repair_cost', 'first_failure', 'last_failure'
        ]
        
        # Calculate MTBF (Mean Time Between Failures)
        reliability_metrics['operating_days'] = (
            reliability_metrics['last_failure'] - reliability_metrics['first_failure']
        ).dt.days
        
        reliability_metrics['mtbf_days'] = (
            reliability_metrics['operating_days'] / 
            reliability_metrics['total_failures'].replace(0, np.nan)
        ).round(2)
        
        # Calculate availability
        # Assuming 24/7 operation
        reliability_metrics['total_hours_period'] = reliability_metrics['operating_days'] * 24
        
        # Handle zero operating hours to avoid division by zero
        reliability_metrics['availability_pct'] = np.where(
            reliability_metrics['total_hours_period'] > 0,
            (reliability_metrics['total_hours_period'] - reliability_metrics['total_downtime_hours']) / reliability_metrics['total_hours_period'] * 100,
            0.0
        ).round(2)
        
        # Add equipment details
        reliability_metrics = pd.merge(
            reliability_metrics,
            self.equipment[['equipment_id', 'equipment_name', 'equipment_type', 'location']],
            on='equipment_id',
            how='left'
        )
        
        return reliability_metrics
    
    def failure_pattern_analysis(self):
        """
        Analyze failure patterns by type, component, and time
        """
        # Failure by type
        failure_by_type = self.merged_data.groupby('failure_type').agg({
            'downtime_id': 'count',
            'downtime_hours': 'sum',
            'repair_cost': 'sum'
        }).reset_index()
        
        failure_by_type.columns = ['failure_type', 'failure_count', 'total_downtime', 'total_cost']
        failure_by_type = failure_by_type.sort_values('failure_count', ascending=False)
        
        # Failure by component
        failure_by_component = self.merged_data.groupby('failure_component').agg({
            'downtime_id': 'count',
            'downtime_hours': 'mean',
            'repair_cost': 'mean'
        }).reset_index()
        
        failure_by_component.columns = ['component', 'failure_count', 'avg_downtime', 'avg_cost']
        failure_by_component = failure_by_component.sort_values('failure_count', ascending=False).head(15)
        
        # Monthly failure trends
        monthly_failures = self.merged_data.groupby('failure_month').agg({
            'downtime_id': 'count',
            'downtime_hours': 'sum'
        }).reset_index()
        
        monthly_failures.columns = ['month', 'failure_count', 'total_downtime']
        
        return {
            'by_type': failure_by_type,
            'by_component': failure_by_component,
            'monthly_trend': monthly_failures
        }
    
    def equipment_criticality_matrix(self):
        """
        Create MTBF vs MTTR matrix for equipment criticality assessment
        """
        metrics = self.calculate_reliability_metrics()
        
        # Categorize equipment
        mtbf_median = metrics['mtbf_days'].median()
        mttr_median = metrics['mttr_hours'].median()
        
        def categorize_equipment(row):
            if row['mtbf_days'] >= mtbf_median and row['mttr_hours'] <= mttr_median:
                return 'Low Risk'
            elif row['mtbf_days'] < mtbf_median and row['mttr_hours'] > mttr_median:
                return 'Critical'
            elif row['mtbf_days'] < mtbf_median and row['mttr_hours'] <= mttr_median:
                return 'High Frequency'
            else:
                return 'Long Repair'
        
        metrics['criticality'] = metrics.apply(categorize_equipment, axis=1)
        
        return metrics
    
    def maintenance_cost_analysis(self):
        """
        Analyze maintenance costs by equipment, type, and time
        """
        # Cost by equipment type
        cost_by_type = self.merged_data.groupby('equipment_type').agg({
            'repair_cost': ['sum', 'mean', 'count']
        }).reset_index()
        
        cost_by_type.columns = ['equipment_type', 'total_cost', 'avg_cost_per_failure', 'failure_count']
        cost_by_type['cost_per_equipment'] = cost_by_type['total_cost'] / \
            self.equipment.groupby('equipment_type').size().values
        
        # Monthly cost trends
        monthly_costs = self.merged_data.groupby('failure_month').agg({
            'repair_cost': 'sum'
        }).reset_index()
        
        monthly_costs.columns = ['month', 'total_cost']
        
        # Maintenance type distribution
        maint_type_dist = self.merged_data.groupby('maintenance_type').agg({
            'downtime_id': 'count',
            'repair_cost': 'sum'
        }).reset_index()
        
        maint_type_dist.columns = ['maintenance_type', 'count', 'total_cost']
        
        return {
            'by_equipment_type': cost_by_type,
            'monthly_trend': monthly_costs,
            'by_maintenance_type': maint_type_dist
        }

    def calculate_weibull_parameters(self, equipment_id):
        """
        Estimate Weibull Beta and Eta for reliability profiling
        """
        # Get failure intervals (time between failures)
        equip_data = self.merged_data[self.merged_data['equipment_id'] == equipment_id].sort_values('failure_date')
        if len(equip_data) < 3:
            return None, None
            
        # Calculate time between failures
        equip_data['prev_failure'] = equip_data['failure_date'].shift(1)
        equip_data['tbf'] = (equip_data['failure_date'] - equip_data['prev_failure']).dt.days.dropna()
        times = equip_data['tbf'].dropna().values
        
        if len(times) < 2:
            return None, None
            
        # Simplified MLE Estimation for Weibull
        # In a real app, use scipy.stats.weibull_min.fit
        from scipy.stats import weibull_min
        shape, loc, scale = weibull_min.fit(times, floc=0)
        return shape, scale

    def calculate_oee_metrics(self):
        """
        Calculate Overall Equipment Effectiveness (OEE)
        OEE = Availability x Performance x Quality
        """
        metrics = self.calculate_reliability_metrics()
        
        # In this synthetic dataset:
        # Availability is already calcualted
        # Performance: Assuming speed/efficiency based on repair duration vs avg
        # Quality: Assuming based on failure frequency (re-work items)
        
        metrics['oee_availability'] = metrics['availability_pct'] / 100
        # Synthetic performance (0.85 - 0.98)
        np.random.seed(42)
        metrics['oee_performance'] = 0.85 + (np.random.rand(len(metrics)) * 0.13)
        # Synthetic quality (0.92 - 0.99)
        metrics['oee_quality'] = 0.92 + (np.random.rand(len(metrics)) * 0.07)
        
        metrics['oee_score'] = (metrics['oee_availability'] * 
                               metrics['oee_performance'] * 
                               metrics['oee_quality']) * 100
                               
        return metrics[['equipment_id', 'equipment_name', 'oee_availability', 
                        'oee_performance', 'oee_quality', 'oee_score']]
    
    def high_risk_equipment_identification(self, top_n=10):
        """
        Identify equipment requiring immediate attention
        """
        metrics = self.calculate_reliability_metrics()
        
        # Score based on multiple factors
        # Normalize values
        metrics['failure_score'] = (
            metrics['total_failures'] / metrics['total_failures'].max()
        )
        metrics['cost_score'] = (
            metrics['total_repair_cost'] / metrics['total_repair_cost'].max()
        )
        metrics['availability_score'] = (
            1 - (metrics['availability_pct'] / 100)
        )
        
        # Composite risk score
        metrics['risk_score'] = (
            0.4 * metrics['failure_score'] +
            0.3 * metrics['cost_score'] +
            0.3 * metrics['availability_score']
        ) * 100
        
        high_risk = metrics.nlargest(top_n, 'risk_score')[[
            'equipment_id', 'equipment_name', 'equipment_type',
            'total_failures', 'mtbf_days', 'mttr_hours',
            'availability_pct', 'total_repair_cost', 'risk_score'
        ]]
        
        return high_risk
    
    def rcm_failure_mode_prioritization(self):
        """
        Reliability Centered Maintenance (RCM) Analysis
        Calculate Risk Priority Number (RPN) for failure modes
        RPN = Severity x Occurrence x Detection (simulated here)
        """
        # Group by failure type (Failure Mode)
        rcm = self.merged_data.groupby('failure_type').agg({
            'downtime_id': 'count', # Occurrence proxy
            'downtime_hours': 'mean', # Severity proxy (longer downtime = more severe)
            'repair_cost': 'mean' # Cost severity
        }).reset_index()
        
        # Normalize and score (1-10 scale)
        rcm['occurrence_score'] = pd.qcut(rcm['downtime_id'], q=5, labels=False, duplicates='drop') * 2 + 2
        
        # Severity based on downtime + cost
        rcm['downtime_norm'] = (rcm['downtime_hours'] / rcm['downtime_hours'].max())
        rcm['cost_norm'] = (rcm['repair_cost'] / rcm['repair_cost'].max())
        rcm['severity_raw'] = (rcm['downtime_norm'] + rcm['cost_norm']) / 2
        rcm['severity_score'] = pd.qcut(rcm['severity_raw'], q=5, labels=False, duplicates='drop') * 2 + 2
        
        # Detection: Synthetic (Some failures are harder to detect)
        np.random.seed(42)  # For consistent demo results
        rcm['detection_score'] = np.random.randint(2, 9, size=len(rcm))
        
        # Calculate RPN
        rcm['rpn'] = rcm['severity_score'] * rcm['occurrence_score'] * rcm['detection_score']
        
        # Assign Action
        def assign_action(rpn):
            if rpn >= 200: return 'Redesign / Process Change'
            elif rpn >= 100: return 'Predictive Maintenance'
            elif rpn >= 50: return 'Preventive Maintenance'
            else: return 'Run-to-Failure'
            
        rcm['recommended_strategy'] = rcm['rpn'].apply(assign_action)
        
        return rcm.sort_values('rpn', ascending=False)
        
    def optimize_pm_schedule(self, schedule_df):
        """
        Analyze and optimize maintenance schedule
        Checks for resource conflicts and workload balancing
        """
        df = schedule_df.copy()
        df['start_date'] = pd.to_datetime(df['start_date'])
        
        # Check for technician conflicts (same tech, same day)
        conflicts = df[df.duplicated(subset=['assigned_technician', 'start_date'], keep=False)]
        
        # Workload balance (Tasks per technician)
        workload = df['assigned_technician'].value_counts().reset_index()
        workload.columns = ['Technician', 'Tasks']
        
        return {
            'schedule_df': df,
            'conflicts': conflicts,
            'workload': workload
        }
        
    def condition_based_monitoring(self):
        """
        Simulate condition monitoring triggers based on equipment age/usage
        """
        # Get latest status
        status = self.equipment.copy()
        
        # Simulate current sensor readings
        np.random.seed(100)
        status['vibration_mm_s'] = np.random.normal(2.5, 1.0, size=len(status))
        status['temperature_c'] = np.random.normal(75, 15, size=len(status))
        status['oil_quality_pct'] = np.random.normal(80, 10, size=len(status))
        
        # Define thresholds
        thresholds = {
            'vibration_mm_s': 5.0, # High vibration > 5 mm/s
            'temperature_c': 95.0, # Overheating > 95 C
            'oil_quality_pct': 40.0 # Bad oil < 40%
        }
        
        triggers = []
        for _, row in status.iterrows():
            if row['vibration_mm_s'] > thresholds['vibration_mm_s']:
                triggers.append({
                    'equipment_id': row['equipment_id'],
                    'equipment_name': row['equipment_name'],
                    'parameter': 'Vibration',
                    'value': f"{row['vibration_mm_s']:.2f} mm/s",
                    'threshold': f">{thresholds['vibration_mm_s']}",
                    'severity': 'High'
                })
            
            if row['temperature_c'] > thresholds['temperature_c']:
                triggers.append({
                    'equipment_id': row['equipment_id'],
                    'equipment_name': row['equipment_name'],
                    'parameter': 'Temperature',
                    'value': f"{row['temperature_c']:.1f} C",
                    'threshold': f">{thresholds['temperature_c']}",
                    'severity': 'Critical'
                })
                
            if row['oil_quality_pct'] < thresholds['oil_quality_pct']:
                triggers.append({
                    'equipment_id': row['equipment_id'],
                    'equipment_name': row['equipment_name'],
                    'parameter': 'Oil Quality',
                    'value': f"{row['oil_quality_pct']:.0f}%",
                    'threshold': f"<{thresholds['oil_quality_pct']}",
                    'severity': 'Medium'
                })
                
        return pd.DataFrame(triggers)

    def generate_maintenance_recommendations(self):
        """
        Generate actionable maintenance recommendations
        """
        metrics = self.calculate_reliability_metrics()
        failure_patterns = self.failure_pattern_analysis()
        
        recommendations = []
        
        # Low MTBF equipment
        low_mtbf = metrics[metrics['mtbf_days'] < metrics['mtbf_days'].quantile(0.25)]
        for _, equip in low_mtbf.iterrows():
            recommendations.append({
                'equipment_id': equip['equipment_id'],
                'equipment_name': equip['equipment_name'],
                'issue': 'Low MTBF (High failure frequency)',
                'recommendation': 'Implement predictive maintenance, review operating conditions',
                'priority': 'High'
            })
        
        # High MTTR equipment
        high_mttr = metrics[metrics['mttr_hours'] > metrics['mttr_hours'].quantile(0.75)]
        for _, equip in high_mttr.iterrows():
            recommendations.append({
                'equipment_id': equip['equipment_id'],
                'equipment_name': equip['equipment_name'],
                'issue': 'High MTTR (Long repair times)',
                'recommendation': 'Pre-stock critical spares, improve maintenance procedures',
                'priority': 'Medium'
            })
        
        # Low availability
        low_avail = metrics[metrics['availability_pct'] < 90]
        for _, equip in low_avail.iterrows():
            recommendations.append({
                'equipment_id': equip['equipment_id'],
                'equipment_name': equip['equipment_name'],
                'issue': f'Low availability ({equip["availability_pct"]:.1f}%)',
                'recommendation': 'Critical - Review maintenance strategy, consider replacement',
                'priority': 'Critical'
            })
        
        return pd.DataFrame(recommendations)

    def train_prediction_model(self):
        """
        Train the predictive maintenance model using current data
        """
        predictor = FailurePredictor()
        predictor.train(self.equipment, self.downtime)
        return "Model trained successfully"

    def get_failure_predictions(self):
        """
        Get failure probabilities for all equipment
        """
        predictor = FailurePredictor()
        # Check if model exists, if not, train it
        if not os.path.exists(predictor.model_path):
            print("Model not found, training new model...")
            self.train_prediction_model()
            
        predictions = predictor.predict_risk(self.equipment, self.downtime)
        return predictions


# ========================================
# VISUALIZATION FUNCTIONS
# ========================================

def plot_reliability_dashboard(analytics):
    """
    Create comprehensive reliability dashboard
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    metrics = analytics.calculate_reliability_metrics()
    failure_patterns = analytics.failure_pattern_analysis()
    
    # 1. MTBF Distribution
    axes[0, 0].hist(metrics['mtbf_days'].dropna(), bins=20, edgecolor='black', color='skyblue')
    axes[0, 0].set_xlabel('MTBF (days)')
    axes[0, 0].set_ylabel('Number of Equipment')
    axes[0, 0].set_title('Equipment MTBF Distribution')
    axes[0, 0].axvline(metrics['mtbf_days'].median(), color='red', linestyle='--', 
                       label=f'Median: {metrics["mtbf_days"].median():.1f} days')
    axes[0, 0].legend()
    
    # 2. Failure by Type
    failure_by_type = failure_patterns['by_type']
    axes[0, 1].barh(failure_by_type['failure_type'], failure_by_type['failure_count'], color='coral')
    axes[0, 1].set_xlabel('Number of Failures')
    axes[0, 1].set_title('Failures by Type')
    
    # 3. Top Components Failing
    failure_by_component = failure_patterns['by_component'].head(10)
    axes[1, 0].barh(failure_by_component['component'], failure_by_component['failure_count'], color='lightgreen')
    axes[1, 0].set_xlabel('Number of Failures')
    axes[1, 0].set_title('Top 10 Failing Components')
    
    # 4. MTBF vs MTTR Scatter
    axes[1, 1].scatter(metrics['mtbf_days'], metrics['mttr_hours'], 
                      c=metrics['total_repair_cost'], cmap='Reds', s=100, alpha=0.6)
    axes[1, 1].set_xlabel('MTBF (days)')
    axes[1, 1].set_ylabel('MTTR (hours)')
    axes[1, 1].set_title('Equipment Criticality Matrix (MTBF vs MTTR)')
    axes[1, 1].axhline(metrics['mttr_hours'].median(), color='blue', linestyle='--', alpha=0.5)
    axes[1, 1].axvline(metrics['mtbf_days'].median(), color='blue', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('outputs/reliability_dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()


# ========================================
# EXAMPLE USAGE
# ========================================

if __name__ == "__main__":
    # Load data
    equipment = pd.read_csv('data/equipment.csv')
    downtime = pd.read_csv('data/equipment_downtime.csv')
    
    # Initialize analytics
    analytics = MaintenanceAnalytics(equipment, downtime)
    
    # Calculate metrics
    reliability_metrics = analytics.calculate_reliability_metrics()
    print("\n=== Reliability Metrics ===")
    print(reliability_metrics.head())
    
    # High-risk equipment
    high_risk = analytics.high_risk_equipment_identification(top_n=10)
    print("\n=== Top 10 High-Risk Equipment ===")
    print(high_risk)
    
    # Recommendations
    recommendations = analytics.generate_maintenance_recommendations()
    print(f"\n=== Maintenance Recommendations ({len(recommendations)} items) ===")
    print(recommendations.head(10))
    
    # Create dashboard
    plot_reliability_dashboard(analytics)