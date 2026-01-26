import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FeaturePipeline:
    """
    Feature engineering pipeline for predictive maintenance models.
    """
    
    def __init__(self, equipment_df, downtime_df):
        self.equipment = equipment_df.copy()
        self.downtime = downtime_df.copy()
        self._preprocess_dates()
        
    def _preprocess_dates(self):
        """Convert date columns to datetime objects"""
        date_cols = ['failure_date', 'repair_start_date', 'repair_end_date']
        for col in date_cols:
            if col in self.downtime.columns:
                self.downtime[col] = pd.to_datetime(self.downtime[col])
                
    def create_training_features(self, target_date=None):
        """
        Create features for training/prediction as of target_date.
        If target_date is None, creates a historical dataset for training.
        """
        if target_date is None:
            # Create training data from history
            return self._create_historical_dataset()
        else:
            # Create prediction features for a specific date
            return self._create_prediction_features(target_date)

    def _create_historical_dataset(self):
        """
        Generate training examples from historical failures.
        Target: 1 if failure occurred in next N days (e.g., 30), 0 otherwise.
        """
        # Sort by date
        df = self.downtime.sort_values('failure_date')
        
        features = []
        
        # We'll generate a snapshot for every equipment at regular intervals
        # For simplicity in this demo, we'll take snapshots at each failure event
        # and some random non-failure dates
        
        for _, failure in df.iterrows():
            # Features at the time just before failure
            snapshot_date = failure['failure_date'] - timedelta(days=1)
            equip_id = failure['equipment_id']
            
            feat = self._calculate_features(equip_id, snapshot_date)
            feat['is_failure_next_30_days'] = 1 # Positive sample
            features.append(feat)
            
        # Add negative samples (random dates where no failure occurred soon)
        # Simplify: Add current status as negative samples if recently healthy
        for equip_id in self.equipment['equipment_id'].unique():
            current_date = datetime.now()
            # Check if failure in next 30 days (impossible for "now", but for historical negative samples we check forward)
            # Here we just take "now" and assume no failure tomorrow for the sake of negative example structure
            # In a real pipeline, we'd sample historical dates strictly.
            
            feat = self._calculate_features(equip_id, current_date)
            feat['is_failure_next_30_days'] = 0 
            features.append(feat)
            
        return pd.DataFrame(features)

    def _create_prediction_features(self, target_date):
        """Create features for all equipment for a specific prediction date"""
        features = []
        for equip_id in self.equipment['equipment_id'].unique():
            feat = self._calculate_features(equip_id, target_date)
            features.append(feat)
        return pd.DataFrame(features)

    def _calculate_features(self, equip_id, snapshot_date):
        """Calculate feature vector for a specific equipment at a point in time"""
        
        # Filter history strictly before snapshot_date
        history = self.downtime[
            (self.downtime['equipment_id'] == equip_id) & 
            (self.downtime['failure_date'] < snapshot_date)
        ].copy()
        
        equip_info = self.equipment[self.equipment['equipment_id'] == equip_id].iloc[0]
        
        # 1. Base Features
        feat = {
            'equipment_id': equip_id,
            'equipment_type': equip_info['equipment_type'],
            'location': equip_info.get('location', 'Unknown'),
            'snapshot_date': snapshot_date
        }
        
        # 2. Failure History
        feat['total_failures'] = len(history)
        
        if len(history) > 0:
            last_failure_date = history['failure_date'].max()
            feat['days_since_last_failure'] = (snapshot_date - last_failure_date).days
            feat['avg_downtime_hours'] = history['downtime_hours'].mean()
            feat['total_repair_cost'] = history['repair_cost'].sum()
        else:
            feat['days_since_last_failure'] = 365 * 2 # Default high number
            feat['avg_downtime_hours'] = 0
            feat['total_repair_cost'] = 0
            
        # 3. Recent History (Last 90 days)
        recent_history = history[history['failure_date'] >= (snapshot_date - timedelta(days=90))]
        feat['failures_last_90d'] = len(recent_history)
        
        # 4. Synthesized Sensor Features (Mocking real-time data)
        # In prod, this would join with a sensor_readings table
        np.random.seed(int(snapshot_date.timestamp()) + int(str(equip_id)[-1]))
        
        # Trend: increasing vibration as failures approach?
        risk_factor = 1.0
        if feat['days_since_last_failure'] < 30: # Just failed recently
             risk_factor = 0.5
        elif feat['days_since_last_failure'] > 100: # Long time no fail
             risk_factor = 1.5
             
        feat['current_vibration'] = np.random.normal(2.5, 0.5) * risk_factor
        feat['current_temperature'] = np.random.normal(65, 10) * risk_factor
        feat['oil_quality'] = np.clip(100 - (feat['days_since_last_failure'] * 0.2) + np.random.normal(0, 5), 0, 100)
        
        return feat
