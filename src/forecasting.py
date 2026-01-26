import pandas as pd
import numpy as np
import logging

try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False
    
from statsmodels.tsa.statespace.sarimax import SARIMAX

class DemandForecaster:
    """
    Demand forecasting using Prophet (preferred) or SARIMA.
    """
    
    def __init__(self, inventory_transactions_df):
        self.transactions = inventory_transactions_df.copy()
        
    def forecast_demand(self, part_id, periods=12, freq='M'):
        """
        Forecast demand for a specific part.
        
        Args:
            part_id: ID of the spare part
            periods: Number of periods to forecast
            freq: Frequency ('D', 'W', 'M')
            
        Returns:
            DataFrame with dates and forecasted usage including confidence intervals.
        """
        # Filter for 'Issue' transactions (consumption)
        part_data = self.transactions[
            (self.transactions['part_id'] == part_id) & 
            (self.transactions['transaction_type'] == 'Issue')
        ].copy()
        
        if len(part_data) < 5:
            return None # Not enough data
            
        # Aggregate by time period
        part_data['transaction_date'] = pd.to_datetime(part_data['transaction_date'])
        
        # Resample to ensure continuous time series
        ts_data = part_data.set_index('transaction_date').resample(freq)['quantity'].sum().reset_index()
        
        if HAS_PROPHET:
            return self._forecast_prophet(ts_data, periods, freq)
        else:
            return self._forecast_sarima(ts_data, periods, freq)
            
    def _forecast_prophet(self, df, periods, freq):
        """Use Facebook Prophet for forecasting"""
        # Prepare for Prophet: ds, y
        df_prophet = df.rename(columns={'transaction_date': 'ds', 'quantity': 'y'})
        
        try:
            m = Prophet(daily_seasonality=False, weekly_seasonality=False, yearly_seasonality=True)
            # Disable output suppression for debugging if needed, but keep clean for now
            m.fit(df_prophet)
            
            future = m.make_future_dataframe(periods=periods, freq=freq)
            forecast = m.predict(future)
            
            return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
        except Exception as e:
            logging.error(f"Prophet forecast failed: {e}")
            return None

    def _forecast_sarima(self, df, periods, freq):
        """Fallback to SARIMA"""
        try:
            # Simple ARIMA(1,1,1) for fallback
            model = SARIMAX(df['quantity'], order=(1, 1, 1), seasonal_order=(0, 0, 0, 0))
            results = model.fit(disp=False)
            
            # Forecast
            forecast = results.get_forecast(steps=periods)
            predicted_mean = forecast.predicted_mean
            conf_int = forecast.conf_int()
            
            # Construct result DataFrame
            dates = pd.date_range(start=df['transaction_date'].iloc[-1], periods=periods+1, freq=freq)[1:]
            
            result_df = pd.DataFrame({
                'ds': dates,
                'yhat': predicted_mean.values,
                'yhat_lower': conf_int.iloc[:, 0].values,
                'yhat_upper': conf_int.iloc[:, 1].values
            })
            
            return result_df
        except Exception as e:
            logging.error(f"SARIMA forecast failed: {e}")
            return None
            
    def generate_all_forecasts(self, top_n=20):
        """Generate forecasts for top N parts by volume"""
        # Identify top parts
        top_parts = self.transactions[self.transactions['transaction_type'] == 'Issue']\
            .groupby('part_id')['quantity'].sum()\
            .sort_values(ascending=False).head(top_n).index.tolist()
            
        forecasts = {}
        for part_id in top_parts:
            f = self.forecast_demand(part_id)
            if f is not None:
                forecasts[part_id] = f
                
        return forecasts
