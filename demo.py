from src.logistics_analytics import LogisticsAnalytics
import pandas as pd

deliveries = pd.read_csv(r'data/delivery_orders.csv')
warehouses = pd.read_csv(r'data/warehouses.csv')

analytics = LogisticsAnalytics(deliveries, warehouses)
kpis = analytics.delivery_performance_analysis()
optimization_result = analytics.simple_route_optimization('2024-06-15')

print(kpis)