import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.supply_chain_analytics import SupplyChainAnalytics

def test_forecasting():
    print("Testing Forecasting Module...")
    
    # Load data
    try:
        spare_parts = pd.read_csv('data/spare_parts.csv')
        inventory = pd.read_csv('data/inventory_transactions.csv')
        po = pd.read_csv('data/purchase_orders.csv')
        suppliers = pd.read_csv('data/suppliers.csv')
        print(f"Loaded data successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Initialize analytics
    analytics = SupplyChainAnalytics(spare_parts, inventory, po, suppliers)
    
    # Test Single Forecast
    # Find a part with data
    top_part = inventory[inventory['transaction_type'] == 'Issue']['part_id'].mode()[0]
    print(f"\nForecasting for Top Part: {top_part}")
    
    try:
        forecast = analytics.get_demand_forecast(top_part)
        if forecast is not None:
            print("Forecast generated:")
            print(forecast.head())
        else:
            print("No forecast generated (insufficient data?).")
            
    except Exception as e:
        print(f"Forecast Failed: {e}")
        import traceback
        traceback.print_exc()

    # Test Batch Forecast
    print("\nTesting Batch Forecast (Top 3)...")
    try:
        forecasts = analytics.get_batch_forecasts(top_n=3)
        print(f"Generated forecasts for {len(forecasts)} parts.")
        for pid, df in forecasts.items():
            print(f"- {pid}: {len(df)} periods")
            
    except Exception as e:
        print(f"Batch Forecast Failed: {e}")

if __name__ == "__main__":
    test_forecasting()
