"""
Logistics & Transportation Optimization Module
Route Optimization, Delivery Performance, Cost Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pulp import *
from datetime import datetime, timedelta

class LogisticsAnalytics:
    """
    Comprehensive logistics and transportation analytics
    """
    
    def __init__(self, deliveries_df, warehouses_df):
        self.deliveries = deliveries_df
        self.warehouses = warehouses_df
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare logistics data"""
        # Convert dates
        self.deliveries['order_date'] = pd.to_datetime(self.deliveries['order_date'])
        self.deliveries['planned_delivery_date'] = pd.to_datetime(
            self.deliveries['planned_delivery_date']
        )
        self.deliveries['actual_delivery_date'] = pd.to_datetime(
            self.deliveries['actual_delivery_date']
        )
        
        # Calculate metrics
        self.deliveries['planned_lead_time'] = (
            self.deliveries['planned_delivery_date'] - self.deliveries['order_date']
        ).dt.days
        
        self.deliveries['actual_lead_time'] = (
            self.deliveries['actual_delivery_date'] - self.deliveries['order_date']
        ).dt.days
        
        self.deliveries['delivery_delay'] = (
            self.deliveries['actual_delivery_date'] - self.deliveries['planned_delivery_date']
        ).dt.days
        
        self.deliveries['on_time'] = (self.deliveries['delivery_delay'] <= 0).astype(int)
        
        # Extract time features
        self.deliveries['month'] = self.deliveries['order_date'].dt.to_period('M')
    
    def delivery_performance_analysis(self):
        """
        Analyze delivery performance metrics
        """
        # Overall KPIs
        total_deliveries = len(self.deliveries[self.deliveries['delivery_status'] == 'Delivered'])
        on_time_deliveries = self.deliveries['on_time'].sum()
        on_time_pct = (on_time_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        
        avg_lead_time = self.deliveries['actual_lead_time'].mean()
        avg_delay = self.deliveries[self.deliveries['delivery_delay'] > 0]['delivery_delay'].mean()
        
        kpis = {
            'total_deliveries': total_deliveries,
            'on_time_deliveries': on_time_deliveries,
            'on_time_percentage': round(on_time_pct, 2),
            'avg_lead_time_days': round(avg_lead_time, 2),
            'avg_delay_days': round(avg_delay, 2) if not pd.isna(avg_delay) else 0,
            'total_cost': self.deliveries['delivery_cost'].sum()
        }
        
        # Performance by transport mode
        mode_performance = self.deliveries.groupby('transport_mode').agg({
            'delivery_id': 'count',
            'on_time': 'mean',
            'actual_lead_time': 'mean',
            'delivery_cost': ['sum', 'mean'],
            'distance_km': 'mean'
        }).reset_index()
        
        mode_performance.columns = [
            'transport_mode', 'total_deliveries', 'on_time_pct',
            'avg_lead_time', 'total_cost', 'avg_cost', 'avg_distance'
        ]
        
        mode_performance['on_time_pct'] = (mode_performance['on_time_pct'] * 100).round(2)
        mode_performance['cost_per_km'] = (
            mode_performance['avg_cost'] / mode_performance['avg_distance']
        ).round(2)
        
        # Monthly trend
        monthly_performance = self.deliveries.groupby('month').agg({
            'delivery_id': 'count',
            'on_time': 'mean',
            'delivery_cost': 'sum'
        }).reset_index()
        
        monthly_performance.columns = ['month', 'deliveries', 'on_time_pct', 'total_cost']
        monthly_performance['on_time_pct'] = (monthly_performance['on_time_pct'] * 100).round(2)
        
        return kpis, mode_performance, monthly_performance
    
    def warehouse_performance_analysis(self):
        """
        Analyze warehouse-level logistics performance
        """
        warehouse_perf = self.deliveries.groupby('source_warehouse').agg({
            'delivery_id': 'count',
            'on_time': 'mean',
            'delivery_cost': 'sum',
            'distance_km': 'mean'
        }).reset_index()
        
        warehouse_perf.columns = [
            'warehouse_id', 'total_shipments', 'on_time_pct',
            'total_logistics_cost', 'avg_delivery_distance'
        ]
        
        warehouse_perf['on_time_pct'] = (warehouse_perf['on_time_pct'] * 100).round(2)
        
        # Add warehouse details
        warehouse_perf = pd.merge(
            warehouse_perf,
            self.warehouses[['warehouse_id', 'warehouse_name', 'location']],
            on='warehouse_id',
            how='left'
        )
        
        return warehouse_perf
    
    def cost_optimization_analysis(self):
        """
        Identify cost optimization opportunities
        """
        # Cost by distance bands
        self.deliveries['distance_band'] = pd.cut(
            self.deliveries['distance_km'],
            bins=[0, 100, 300, 500, 1000],
            labels=['<100km', '100-300km', '300-500km', '>500km']
        )
        
        cost_by_distance = self.deliveries.groupby(['distance_band', 'transport_mode']).agg({
            'delivery_cost': 'mean',
            'delivery_id': 'count'
        }).reset_index()
        
        cost_by_distance.columns = ['distance_band', 'transport_mode', 'avg_cost', 'delivery_count']
        
        # Identify expensive routes
        expensive_routes = self.deliveries.nlargest(20, 'delivery_cost')[[
            'delivery_id', 'source_warehouse', 'destination_site',
            'distance_km', 'transport_mode', 'delivery_cost'
        ]]
        
        # Cost per km analysis
        cost_per_km = self.deliveries.copy()
        cost_per_km['cost_per_km'] = cost_per_km['delivery_cost'] / cost_per_km['distance_km']
        
        # Find inefficient deliveries (high cost per km)
        inefficient = cost_per_km.nlargest(50, 'cost_per_km')[[
            'delivery_id', 'source_warehouse', 'destination_site',
            'transport_mode', 'distance_km', 'delivery_cost', 'cost_per_km'
        ]]
        
        return cost_by_distance, expensive_routes, inefficient
    
    def route_consolidation_opportunities(self):
        """
        Identify opportunities for route consolidation
        """
        # Group deliveries by destination and date
        consolidation_opps = self.deliveries.groupby(
            ['destination_site', self.deliveries['order_date'].dt.date]
        ).agg({
            'delivery_id': 'count',
            'quantity': 'sum',
            'delivery_cost': 'sum'
        }).reset_index()
        
        consolidation_opps.columns = [
            'destination', 'date', 'num_deliveries', 'total_quantity', 'total_cost'
        ]
        
        # Filter for potential consolidation (multiple deliveries same day)
        consolidation_opps = consolidation_opps[consolidation_opps['num_deliveries'] > 1]
        consolidation_opps['potential_savings'] = (
            consolidation_opps['total_cost'] * 0.25  # Assume 25% savings from consolidation
        ).round(2)
        
        return consolidation_opps
    
    def simple_route_optimization(self, delivery_date, max_deliveries=10):
        """
        Simple route optimization using linear programming
        Optimize delivery sequence to minimize total distance
        """
        # Filter deliveries for specific date
        day_deliveries = self.deliveries[
            self.deliveries['order_date'].dt.date == pd.to_datetime(delivery_date).date()
        ].head(max_deliveries)
        
        if len(day_deliveries) == 0:
            return None, "No deliveries found for this date"
        
        # Create distance matrix (simplified - using straight-line distance)
        n = len(day_deliveries)
        locations = day_deliveries[['destination_lat', 'destination_lon']].values
        
        # Add warehouse as starting point
        warehouse = self.warehouses.iloc[0]
        start_point = np.array([[warehouse['latitude'], warehouse['longitude']]])
        all_points = np.vstack([start_point, locations])
        
        # Calculate distance matrix
        dist_matrix = np.zeros((n + 1, n + 1))
        for i in range(n + 1):
            for j in range(n + 1):
                if i != j:
                    # Haversine distance approximation
                    lat1, lon1 = all_points[i]
                    lat2, lon2 = all_points[j]
                    dist_matrix[i][j] = self._haversine_distance(lat1, lon1, lat2, lon2)
        
        # Simple greedy nearest neighbor heuristic
        route = [0]  # Start at warehouse
        unvisited = list(range(1, n + 1))
        current = 0
        total_distance = 0
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: dist_matrix[current][x])
            total_distance += dist_matrix[current][nearest]
            route.append(nearest)
            current = nearest
            unvisited.remove(nearest)
        
        # Return to warehouse
        total_distance += dist_matrix[current][0]
        route.append(0)
        
        # Create optimized delivery sequence
        optimized_sequence = []
        for idx in route[1:-1]:  # Exclude warehouse start/end
            delivery = day_deliveries.iloc[idx - 1]
            optimized_sequence.append({
                'sequence': len(optimized_sequence) + 1,
                'delivery_id': delivery['delivery_id'],
                'destination': delivery['destination_site'],
                'quantity': delivery['quantity']
            })
        
        optimization_result = {
            'date': delivery_date,
            'total_deliveries': n,
            'original_total_cost': day_deliveries['delivery_cost'].sum(),
            'optimized_distance_km': round(total_distance, 2),
            'route_sequence': route,
            'delivery_sequence': pd.DataFrame(optimized_sequence)
        }
        
        return optimization_result, dist_matrix
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate haversine distance between two points
        """
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        distance = R * c
        
        return distance
    
    def generate_logistics_recommendations(self):
        """
        Generate actionable logistics recommendations
        """
        kpis, mode_performance, _ = self.delivery_performance_analysis()
        warehouse_perf = self.warehouse_performance_analysis()
        _, _, inefficient = self.cost_optimization_analysis()
        
        recommendations = []
        
        # Low on-time performance
        if kpis['on_time_percentage'] < 85:
            recommendations.append({
                'category': 'Delivery Performance',
                'issue': f'Overall on-time delivery at {kpis["on_time_percentage"]:.1f}% (Target: 90%)',
                'recommendation': 'Review transport mode selection, add buffer time for critical parts',
                'priority': 'High'
            })
        
        # Expensive transport modes
        expensive_mode = mode_performance.nlargest(1, 'cost_per_km').iloc[0]
        recommendations.append({
            'category': 'Cost Optimization',
            'issue': f'{expensive_mode["transport_mode"]} has high cost/km: ₹{expensive_mode["cost_per_km"]:.2f}',
            'recommendation': 'Consider alternative transport for non-urgent deliveries',
            'priority': 'Medium'
        })
        
        # Poor warehouse performance
        poor_warehouse = warehouse_perf[warehouse_perf['on_time_pct'] < 80]
        for _, wh in poor_warehouse.iterrows():
            recommendations.append({
                'category': 'Warehouse Operations',
                'issue': f'{wh["warehouse_name"]} on-time: {wh["on_time_pct"]:.1f}%',
                'recommendation': 'Investigate processing delays, review staffing levels',
                'priority': 'High'
            })
        
        # High-cost inefficient deliveries
        if len(inefficient) > 0:
            recommendations.append({
                'category': 'Route Optimization',
                'issue': f'{len(inefficient)} deliveries identified with high cost/km ratio',
                'recommendation': 'Implement route optimization, consider route consolidation',
                'priority': 'Medium'
            })
        
        return pd.DataFrame(recommendations)


# ========================================
# VISUALIZATION FUNCTIONS
# ========================================

def plot_logistics_dashboard(analytics):
    """
    Create comprehensive logistics dashboard
    """
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    
    kpis, mode_performance, monthly_performance = analytics.delivery_performance_analysis()
    warehouse_perf = analytics.warehouse_performance_analysis()
    
    # 1. KPI Summary
    kpi_data = pd.DataFrame({
        'Metric': ['On-Time %', 'Avg Lead Time (days)', 'Total Deliveries'],
        'Value': [kpis['on_time_percentage'], kpis['avg_lead_time_days'], kpis['total_deliveries']]
    })
    axes[0, 0].axis('tight')
    axes[0, 0].axis('off')
    table = axes[0, 0].table(cellText=kpi_data.values, colLabels=kpi_data.columns,
                            cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    axes[0, 0].set_title('Logistics KPIs', fontsize=12, fontweight='bold')
    
    # 2. Performance by Transport Mode
    axes[0, 1].bar(mode_performance['transport_mode'], mode_performance['on_time_pct'],
                   color=['green', 'orange', 'red'])
    axes[0, 1].axhline(90, color='blue', linestyle='--', label='Target: 90%')
    axes[0, 1].set_ylabel('On-Time Delivery %')
    axes[0, 1].set_title('Performance by Transport Mode')
    axes[0, 1].legend()
    axes[0, 1].set_ylim([0, 100])
    
    # 3. Cost per KM by Mode
    axes[0, 2].barh(mode_performance['transport_mode'], mode_performance['cost_per_km'],
                    color=['skyblue', 'lightcoral', 'lightgreen'])
    axes[0, 2].set_xlabel('Cost per KM (₹)')
    axes[0, 2].set_title('Cost Efficiency by Transport Mode')
    
    # 4. Monthly Delivery Volume
    monthly_performance['month'] = monthly_performance['month'].astype(str)
    axes[1, 0].plot(range(len(monthly_performance)), monthly_performance['deliveries'],
                   marker='o', linewidth=2, color='steelblue')
    axes[1, 0].set_xlabel('Month')
    axes[1, 0].set_ylabel('Number of Deliveries')
    axes[1, 0].set_title('Monthly Delivery Volume Trend')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 5. Warehouse Performance
    axes[1, 1].scatter(warehouse_perf['total_shipments'], warehouse_perf['on_time_pct'],
                      s=warehouse_perf['total_logistics_cost']/100, alpha=0.6, color='purple')
    axes[1, 1].set_xlabel('Total Shipments')
    axes[1, 1].set_ylabel('On-Time Delivery %')
    axes[1, 1].set_title('Warehouse Performance (size = cost)')
    axes[1, 1].axhline(90, color='red', linestyle='--', alpha=0.5)
    axes[1, 1].grid(True, alpha=0.3)
    
    # 6. Delivery Delay Distribution
    delays = analytics.deliveries[analytics.deliveries['delivery_delay'] > 0]['delivery_delay']
    axes[1, 2].hist(delays, bins=20, edgecolor='black', color='salmon')
    axes[1, 2].set_xlabel('Delay (days)')
    axes[1, 2].set_ylabel('Frequency')
    axes[1, 2].set_title('Delivery Delay Distribution')
    axes[1, 2].axvline(delays.median(), color='red', linestyle='--',
                      label=f'Median: {delays.median():.1f} days')
    axes[1, 2].legend()
    
    plt.tight_layout()
    plt.savefig('outputs/logistics_dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()


# ========================================
# EXAMPLE USAGE
# ========================================

if __name__ == "__main__":
    # Load data
    deliveries = pd.read_csv('data/delivery_orders.csv')
    warehouses = pd.read_csv('data/warehouses.csv')
    
    # Initialize analytics
    analytics = LogisticsAnalytics(deliveries, warehouses)
    
    # Performance analysis
    kpis, mode_perf, monthly_perf = analytics.delivery_performance_analysis()
    print("\n=== Logistics KPIs ===")
    for key, value in kpis.items():
        print(f"{key}: {value}")
    
    print("\n=== Performance by Transport Mode ===")
    print(mode_perf)
    
    # Route optimization example
    sample_date = deliveries['order_date'].iloc[100]
    optimization_result, _ = analytics.simple_route_optimization(sample_date)
    
    if optimization_result:
        print(f"\n=== Route Optimization for {sample_date.date()} ===")
        print(f"Total deliveries: {optimization_result['total_deliveries']}")
        print(f"Optimized distance: {optimization_result['optimized_distance_km']} km")
        print("\nOptimized sequence:")
        print(optimization_result['delivery_sequence'])
    
    # Recommendations
    recommendations = analytics.generate_logistics_recommendations()
    print(f"\n=== Logistics Recommendations ({len(recommendations)} items) ===")
    print(recommendations)
    
    # Create dashboard
    plot_logistics_dashboard(analytics)