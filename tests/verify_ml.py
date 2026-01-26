import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.maintenance_analytics import MaintenanceAnalytics

def test_ml_pipeline():
    print("Testing ML Pipeline...")
    
    # Load data
    try:
        equipment = pd.read_csv('data/equipment.csv')
        downtime = pd.read_csv('data/equipment_downtime.csv')
        print(f"Loaded {len(equipment)} equipment and {len(downtime)} downtime records.")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Initialize analytics
    analytics = MaintenanceAnalytics(equipment, downtime)
    
    # Train/Predict
    print("\nRunning get_failure_predictions()...")
    try:
        predictions = analytics.get_failure_predictions()
        print("\nPredictions generated successfully:")
        print(predictions.head())
        
        # Check output structure
        assert 'risk_score' in predictions.columns
        assert 'failure_probability' in predictions.columns
        print("\nVerification Passed: Output structure correct.")
        
    except Exception as e:
        print(f"\nVerification Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ml_pipeline()
