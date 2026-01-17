"""
Supply Chain & Inventory Analytics Module
Inventory Optimization, ABC Analysis, Demand Forecasting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

class SupplyChainAnalytics:
    """
    Comprehensive supply chain and inventory analytics
    """
    
    def __init__(self, spare_parts_df, inventory_df, po_df, suppliers_df):
        self.spare_parts = spare_parts_df
        self.inventory = inventory_df
        self.purchase_orders = po_df
        self.suppliers = suppliers_df
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare and merge datasets"""
        # Convert dates
        self.inventory['transaction_date'] = pd.to_datetime(self.inventory['transaction_date'])
        self.purchase_orders['order_date'] = pd.to_datetime(self.purchase_orders['order_date'])
        self.purchase_orders['expected_delivery_date'] = pd.to_datetime(
            self.purchase_orders['expected_delivery_date']
        )
        self.purchase_orders['actual_delivery_date'] = pd.to_datetime(
            self.purchase_orders['actual_delivery_date']
        )
        
        # Extract time features
        self.inventory['month'] = self.inventory['transaction_date'].dt.to_period('M')
        self.inventory['year'] = self.inventory['transaction_date'].dt.year
    
    def abc_analysis(self):
        """
        Perform ABC classification of spare parts based on consumption value
        """
        # Calculate consumption value per part
        consumption = self.inventory[self.inventory['transaction_type'] == 'Issue'].groupby('part_id').agg({
            'quantity': 'sum'
        }).reset_index()
        
        consumption = pd.merge(consumption, self.spare_parts[['part_id', 'part_name', 'unit_cost']], 
                              on='part_id', how='left')
        
        consumption['total_value'] = consumption['quantity'] * consumption['unit_cost']
        consumption = consumption.sort_values('total_value', ascending=False)
        
        # Calculate cumulative percentage
        consumption['cumulative_value'] = consumption['total_value'].cumsum()
        consumption['cumulative_pct'] = (
            consumption['cumulative_value'] / consumption['total_value'].sum() * 100
        )
        
        # ABC Classification
        def classify_abc(pct):
            if pct <= 80:
                return 'A'
            elif pct <= 95:
                return 'B'
            else:
                return 'C'
        
        consumption['abc_class'] = consumption['cumulative_pct'].apply(classify_abc)
        
        # Summary
        abc_summary = consumption.groupby('abc_class').agg({
            'part_id': 'count',
            'total_value': 'sum'
        }).reset_index()
        
        abc_summary.columns = ['abc_class', 'num_parts', 'total_value']
        abc_summary['pct_value'] = (abc_summary['total_value'] / abc_summary['total_value'].sum() * 100).round(2)
        abc_summary['pct_parts'] = (abc_summary['num_parts'] / abc_summary['num_parts'].sum() * 100).round(2)
        
        return consumption, abc_summary
    
    def inventory_health_check(self):
        """
        Identify stock-out risks, excess inventory, and below reorder point items
        """
        # Get latest stock level for each part
        latest_stock = self.inventory.sort_values('transaction_date').groupby('part_id').last().reset_index()
        
        latest_stock = pd.merge(
            latest_stock[['part_id', 'stock_after_transaction', 'transaction_date']],
            self.spare_parts[['part_id', 'part_name', 'part_category', 'reorder_point', 'unit_cost']],
            on='part_id',
            how='left'
        )
        
        latest_stock.columns = ['part_id', 'current_stock', 'last_transaction_date', 
                               'part_name', 'part_category', 'reorder_point', 'unit_cost']
        
        # Calculate stock status
        def get_stock_status(row):
            if row['current_stock'] == 0:
                return 'Stock Out'
            elif row['current_stock'] <= row['reorder_point']:
                return 'Below Reorder Point'
            elif row['current_stock'] > row['reorder_point'] * 3:
                return 'Excess Stock'
            else:
                return 'Healthy'
        
        latest_stock['stock_status'] = latest_stock.apply(get_stock_status, axis=1)
        latest_stock['stock_value'] = latest_stock['current_stock'] * latest_stock['unit_cost']
        
        # Summary by status
        status_summary = latest_stock.groupby('stock_status').agg({
            'part_id': 'count',
            'stock_value': 'sum'
        }).reset_index()
        
        status_summary.columns = ['stock_status', 'num_parts', 'total_value']
        
        # Critical parts at risk
        critical_at_risk = latest_stock[
            (latest_stock['part_category'] == 'Critical') & 
            (latest_stock['stock_status'].isin(['Stock Out', 'Below Reorder Point']))
        ]
        
        return latest_stock, status_summary, critical_at_risk
    
    def demand_pattern_analysis(self):
        """
        Analyze consumption patterns and trends
        """
        # Monthly consumption by part
        monthly_demand = self.inventory[
            self.inventory['transaction_type'] == 'Issue'
        ].groupby(['part_id', 'month']).agg({
            'quantity': 'sum'
        }).reset_index()
        
        # Add part details
        monthly_demand = pd.merge(
            monthly_demand,
            self.spare_parts[['part_id', 'part_name', 'part_category']],
            on='part_id',
            how='left'
        )
        
        # Calculate demand variability
        demand_stats = monthly_demand.groupby('part_id').agg({
            'quantity': ['mean', 'std', 'min', 'max']
        }).reset_index()
        
        demand_stats.columns = ['part_id', 'avg_monthly_demand', 'demand_std', 'min_demand', 'max_demand']
        
        # Coefficient of variation (CV) - measure of demand variability
        demand_stats['demand_cv'] = (demand_stats['demand_std'] / demand_stats['avg_monthly_demand']).round(2)
        
        # Classify demand pattern
        def classify_demand(cv):
            if pd.isna(cv) or cv < 0.5:
                return 'Stable'
            elif cv < 1.0:
                return 'Moderate'
            else:
                return 'Erratic'
        
        demand_stats['demand_pattern'] = demand_stats['demand_cv'].apply(classify_demand)
        
        return monthly_demand, demand_stats
    
    def supplier_performance_analysis(self):
        """
        Evaluate supplier performance on delivery and quality
        """
        # Merge PO data with supplier info
        po_analysis = pd.merge(
            self.purchase_orders,
            self.suppliers[['supplier_id', 'supplier_name', 'location']],
            on='supplier_id',
            how='left'
        )
        
        # Calculate lead time variance
        po_analysis['actual_lead_time'] = (
            po_analysis['actual_delivery_date'] - po_analysis['order_date']
        ).dt.days
        
        po_analysis['expected_lead_time'] = (
            po_analysis['expected_delivery_date'] - po_analysis['order_date']
        ).dt.days
        
        po_analysis['lead_time_variance'] = (
            po_analysis['actual_lead_time'] - po_analysis['expected_lead_time']
        )
        
        # On-time delivery
        po_analysis['on_time'] = (
            po_analysis['actual_delivery_date'] <= po_analysis['expected_delivery_date']
        ).astype(int)
        
        # Supplier performance metrics
        supplier_metrics = po_analysis.groupby('supplier_id').agg({
            'po_id': 'count',
            'total_cost': 'sum',
            'on_time': 'mean',
            'actual_lead_time': 'mean',
            'lead_time_variance': 'mean'
        }).reset_index()
        
        supplier_metrics.columns = [
            'supplier_id', 'total_orders', 'total_spend',
            'on_time_delivery_pct', 'avg_lead_time', 'avg_lead_time_variance'
        ]
        
        supplier_metrics['on_time_delivery_pct'] = (supplier_metrics['on_time_delivery_pct'] * 100).round(2)
        supplier_metrics = pd.merge(
            supplier_metrics,
            self.suppliers[['supplier_id', 'supplier_name', 'location', 'rating']],
            on='supplier_id',
            how='left'
        )
        
        # Categorize suppliers
        def categorize_supplier(row):
            if row['on_time_delivery_pct'] >= 90 and row['avg_lead_time_variance'] <= 2:
                return 'Preferred'
            elif row['on_time_delivery_pct'] >= 75:
                return 'Acceptable'
            else:
                return 'Review Required'
        
        supplier_metrics['supplier_category'] = supplier_metrics.apply(categorize_supplier, axis=1)
        
        return supplier_metrics
    
    def stockout_impact_analysis(self):
        """
        Analyze stock-out events and their potential impact
        """
        # Identify stock-out events
        stockouts = self.inventory[
            self.inventory['stock_after_transaction'] == 0
        ].copy()
        
        stockouts = pd.merge(
            stockouts,
            self.spare_parts[['part_id', 'part_name', 'part_category', 'unit_cost']],
            on='part_id',
            how='left'
        )
        
        # Count stock-out frequency per part
        stockout_frequency = stockouts.groupby('part_id').agg({
            'transaction_id': 'count',
            'part_name': 'first',
            'part_category': 'first'
        }).reset_index()
        
        stockout_frequency.columns = ['part_id', 'stockout_count', 'part_name', 'part_category']
        stockout_frequency = stockout_frequency.sort_values('stockout_count', ascending=False)
        
        # Critical parts with stock-outs
        critical_stockouts = stockout_frequency[
            stockout_frequency['part_category'] == 'Critical'
        ]
        
        return stockouts, stockout_frequency, critical_stockouts
    
    def inventory_turnover_analysis(self):
        """
        Calculate inventory turnover metrics
        """
        # Total consumption (issues) per part
        total_consumption = self.inventory[
            self.inventory['transaction_type'] == 'Issue'
        ].groupby('part_id').agg({
            'quantity': 'sum'
        }).reset_index()
        
        total_consumption.columns = ['part_id', 'total_consumed']
        
        # Average inventory level
        avg_inventory = self.inventory.groupby('part_id').agg({
            'stock_after_transaction': 'mean'
        }).reset_index()
        
        avg_inventory.columns = ['part_id', 'avg_stock_level']
        
        # Merge and calculate turnover
        turnover = pd.merge(total_consumption, avg_inventory, on='part_id', how='left')
        turnover = pd.merge(
            turnover,
            self.spare_parts[['part_id', 'part_name', 'part_category', 'unit_cost']],
            on='part_id',
            how='left'
        )
        
        # Calculate annual turnover (assuming 3 years of data)
        turnover['annual_consumption'] = turnover['total_consumed'] / 3
        turnover['turnover_ratio'] = (
            turnover['annual_consumption'] / turnover['avg_stock_level'].replace(0, np.nan)
        ).round(2)
        
        # Categorize turnover
        def categorize_turnover(ratio):
            if pd.isna(ratio):
                return 'No Data'
            elif ratio >= 12:
                return 'Fast Moving'
            elif ratio >= 4:
                return 'Medium Moving'
            else:
                return 'Slow Moving'
        
        turnover['movement_category'] = turnover['turnover_ratio'].apply(categorize_turnover)
        
        return turnover

    def calculate_eoq_rop(self, service_level=0.95):
        """
        Calculate Economic Order Quantity and Reorder Point
        """
        from scipy.stats import norm
        
        # Costs (Assumptions if not in data)
        ordering_cost = 500  # Fixed cost per order
        holding_cost_rate = 0.20  # 20% of unit cost per year
        
        # Demand statistics
        _, demand_stats = self.demand_pattern_analysis()
        
        # Supplier stats for lead time
        sup_metrics = self.supplier_performance_analysis()
        avg_lead_time = sup_metrics['avg_lead_time'].mean()
        std_lead_time = sup_metrics['avg_lead_time'].std()
        
        eoq_data = pd.merge(demand_stats, self.spare_parts[['part_id', 'unit_cost']], on='part_id')
        
        # 1. EOQ Calculation
        # EOQ = sqrt( (2 * Annual Demand * Ordering Cost) / (Unit Cost * Holding Rate) )
        eoq_data['annual_demand'] = eoq_data['avg_monthly_demand'] * 12
        eoq_data['eoq'] = np.sqrt(
            (2 * eoq_data['annual_demand'] * ordering_cost) / 
            (eoq_data['unit_cost'] * holding_cost_rate)
        ).round(0)
        
        # 2. Safety Stock & ROP
        # ROP = (Avg Demand * Avg Lead Time) + Z * sigma_demand_during_lt
        z_score = norm.ppf(service_level)
        
        # Lead time in months for calculation
        lt_months = avg_lead_time / 30
        
        # Sigma Demand during Lead Time = sqrt( (LT * sigma_demand^2) + (avg_demand^2 * sigma_lt^2) )
        # Using simplified: sigma_d * sqrt(LT)
        eoq_data['safety_stock'] = (z_score * eoq_data['demand_std'] * np.sqrt(lt_months)).round(0)
        eoq_data['reorder_point_opt'] = (
            (eoq_data['avg_monthly_demand'] * lt_months) + eoq_data['safety_stock']
        ).round(0)
        
        return eoq_data[['part_id', 'annual_demand', 'eoq', 'safety_stock', 'reorder_point_opt']]
    
    def generate_procurement_recommendations(self):
        """
        Generate actionable procurement and inventory recommendations
        """
        inventory_health, _, critical_at_risk = self.inventory_health_check()
        _, demand_stats = self.demand_pattern_analysis()
        supplier_metrics = self.supplier_performance_analysis()
        
        recommendations = []
        
        # Stock-out risks
        for _, item in critical_at_risk.iterrows():
            recommendations.append({
                'part_id': item['part_id'],
                'part_name': item['part_name'],
                'issue': f'Critical part - {item["stock_status"]}',
                'recommendation': 'Emergency procurement required - contact preferred supplier immediately',
                'priority': 'Critical'
            })
        
        # Erratic demand parts
        erratic_demand = demand_stats[demand_stats['demand_pattern'] == 'Erratic']
        for _, item in erratic_demand.head(5).iterrows():
            recommendations.append({
                'part_id': item['part_id'],
                'part_name': 'See part master',
                'issue': f'Erratic demand pattern (CV: {item["demand_cv"]})',
                'recommendation': 'Implement safety stock buffer, review forecasting model',
                'priority': 'Medium'
            })
        
        # Poor performing suppliers
        poor_suppliers = supplier_metrics[supplier_metrics['supplier_category'] == 'Review Required']
        for _, supplier in poor_suppliers.head(3).iterrows():
            recommendations.append({
                'part_id': 'Multiple',
                'part_name': f'Supplier: {supplier["supplier_name"]}',
                'issue': f'Low on-time delivery ({supplier["on_time_delivery_pct"]:.1f}%)',
                'recommendation': 'Review supplier contract, identify alternative suppliers',
                'priority': 'High'
            })
        
        return pd.DataFrame(recommendations)


# ========================================
# VISUALIZATION FUNCTIONS
# ========================================

def plot_supply_chain_dashboard(analytics):
    """
    Create comprehensive supply chain dashboard
    """
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    
    # 1. ABC Analysis
    _, abc_summary = analytics.abc_analysis()
    axes[0, 0].bar(abc_summary['abc_class'], abc_summary['pct_value'], color=['red', 'orange', 'green'])
    axes[0, 0].set_ylabel('% of Total Value')
    axes[0, 0].set_title('ABC Analysis - Value Distribution')
    for i, v in enumerate(abc_summary['pct_value']):
        axes[0, 0].text(i, v + 2, f'{v:.1f}%', ha='center')
    
    # 2. Inventory Health
    inventory_health, status_summary, _ = analytics.inventory_health_check()
    axes[0, 1].pie(status_summary['num_parts'], labels=status_summary['stock_status'], 
                   autopct='%1.1f%%', startangle=90)
    axes[0, 1].set_title('Inventory Health Status')
    
    # 3. Supplier Performance
    supplier_metrics = analytics.supplier_performance_analysis()
    top_suppliers = supplier_metrics.nlargest(10, 'total_spend')
    axes[0, 2].barh(range(len(top_suppliers)), top_suppliers['on_time_delivery_pct'])
    axes[0, 2].set_yticks(range(len(top_suppliers)))
    axes[0, 2].set_yticklabels(top_suppliers['supplier_name'], fontsize=8)
    axes[0, 2].set_xlabel('On-Time Delivery %')
    axes[0, 2].set_title('Top 10 Suppliers - On-Time Delivery')
    axes[0, 2].axvline(90, color='red', linestyle='--', label='Target: 90%')
    axes[0, 2].legend()
    
    # 4. Stock-Out Frequency
    _, stockout_freq, _ = analytics.stockout_impact_analysis()
    top_stockouts = stockout_freq.head(10)
    axes[1, 0].barh(range(len(top_stockouts)), top_stockouts['stockout_count'], color='crimson')
    axes[1, 0].set_yticks(range(len(top_stockouts)))
    axes[1, 0].set_yticklabels(top_stockouts['part_name'], fontsize=8)
    axes[1, 0].set_xlabel('Number of Stock-Outs')
    axes[1, 0].set_title('Top 10 Parts with Stock-Outs')
    
    # 5. Inventory Turnover
    turnover = analytics.inventory_turnover_analysis()
    turnover_summary = turnover.groupby('movement_category').size()
    axes[1, 1].bar(turnover_summary.index, turnover_summary.values, 
                   color=['green', 'orange', 'red', 'gray'])
    axes[1, 1].set_ylabel('Number of Parts')
    axes[1, 1].set_title('Inventory Turnover Categories')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    # 6. Monthly Demand Trend (aggregate)
    monthly_demand, _ = analytics.demand_pattern_analysis()
    demand_trend = monthly_demand.groupby('month')['quantity'].sum().reset_index()
    demand_trend['month'] = demand_trend['month'].astype(str)
    axes[1, 2].plot(range(len(demand_trend)), demand_trend['quantity'], marker='o', linewidth=2)
    axes[1, 2].set_xlabel('Month')
    axes[1, 2].set_ylabel('Total Quantity Issued')
    axes[1, 2].set_title('Monthly Demand Trend')
    axes[1, 2].grid(True, alpha=0.3)
    axes[1, 2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('outputs/supply_chain_dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()


# ========================================
# EXAMPLE USAGE
# ========================================

if __name__ == "__main__":
    # Load data
    spare_parts = pd.read_csv('data/spare_parts.csv')
    inventory = pd.read_csv('data/inventory_transactions.csv')
    purchase_orders = pd.read_csv('data/purchase_orders.csv')
    suppliers = pd.read_csv('data/suppliers.csv')
    
    # Initialize analytics
    analytics = SupplyChainAnalytics(spare_parts, inventory, purchase_orders, suppliers)
    
    # ABC Analysis
    abc_data, abc_summary = analytics.abc_analysis()
    print("\n=== ABC Analysis Summary ===")
    print(abc_summary)
    
    # Inventory Health
    inventory_health, status_summary, critical_at_risk = analytics.inventory_health_check()
    print("\n=== Inventory Health Summary ===")
    print(status_summary)
    print(f"\nCritical parts at risk: {len(critical_at_risk)}")
    
    # Supplier Performance
    supplier_perf = analytics.supplier_performance_analysis()
    print("\n=== Top 5 Suppliers by Spend ===")
    print(supplier_perf.nlargest(5, 'total_spend')[
        ['supplier_name', 'total_spend', 'on_time_delivery_pct']
    ])
    
    # Recommendations
    recommendations = analytics.generate_procurement_recommendations()
    print(f"\n=== Procurement Recommendations ({len(recommendations)} items) ===")
    print(recommendations.head())
    
    # Create dashboard
    plot_supply_chain_dashboard(analytics)