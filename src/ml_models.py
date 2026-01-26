import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

from src.feature_engineering import FeaturePipeline

class FailurePredictor:
    """
    Predictive maintenance model using Machine Learning.
    Predicts probability of equipment failure in the next 30 days.
    """
    
    def __init__(self, model_path='models/failure_prediction_model.joblib'):
        self.model_path = model_path
        self.model = None
        self.feature_pipeline = None
        
    def train(self, equipment_df, downtime_df, force_retrain=False):
        """
        Train the failure prediction model.
        """
        print("Initializing Feature Pipeline...")
        self.feature_pipeline = FeaturePipeline(equipment_df, downtime_df)
        
        print("Creating training dataset...")
        train_df = self.feature_pipeline.create_training_features()
        
        # Prepare X and y
        drop_cols = ['equipment_id', 'equipment_type', 'location', 'snapshot_date', 
                     'is_failure_next_30_days', 'failure_date'] # exclude non-features
        
        X = train_df.drop(columns=[c for c in drop_cols if c in train_df.columns])
        # Handle categorical variables if any (currently manual encoding might be needed, 
        # but feature engineering output implies numeric mostly. 
        # Equipment Type is categorical - let's one-hot encode it if present)
        
        if 'equipment_type' in train_df.columns: # Should be in drop_cols but if we kept it:
             X = pd.get_dummies(X)
             
        y = train_df['is_failure_next_30_days']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Model
        print(f"Training model on {len(X_train)} samples...")
        if HAS_XGB:
            self.model = xgb.XGBClassifier(
                n_estimators=100, 
                max_depth=5, 
                learning_rate=0.1, 
                random_state=42,
                eval_metric='logloss'
            )
        else:
            print("XGBoost not found, falling back to RandomForest.")
            self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
            
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        print("\nModel Evaluation:")
        print(classification_report(y_test, y_pred))
        print(f"ROC-AUC Score: {roc_auc_score(y_test, y_prob):.4f}")
        
        # Save
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"Model saved to {self.model_path}")
        
        return self.model
    
    def predict_risk(self, equipment_df, downtime_df):
        """
        Generate risk scores (0-100) for all equipment based on current state.
        """
        # Load model if not in memory
        if self.model is None:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            else:
                print("Model not found. Please train first.")
                return None
                
        # Prepare features for today
        if self.feature_pipeline is None:
            self.feature_pipeline = FeaturePipeline(equipment_df, downtime_df)
            
        today = datetime.now()
        features_df = self.feature_pipeline.create_training_features(target_date=today)
        
        # Align columns with training data
        # (In a robust system, we'd save the column list during training)
        # For now, we assume consistent schema from FeaturePipeline
        drop_cols = ['equipment_id', 'equipment_type', 'location', 'snapshot_date', 
                     'is_failure_next_30_days']
        
        X_pred = features_df.drop(columns=[c for c in drop_cols if c in features_df.columns])
        
        # Get probabilities
        probs = self.model.predict_proba(X_pred)[:, 1]
        
        results = features_df[['equipment_id', 'equipment_type', 'location']].copy()
        results['failure_probability'] = probs
        results['risk_score'] = (probs * 100).round(1)
        results['risk_category'] = pd.cut(
            results['risk_score'], 
            bins=[-1, 20, 50, 80, 100], 
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        return results.sort_values('risk_score', ascending=False)
