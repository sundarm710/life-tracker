"""
CalloutSystem Module

This module provides functionality for analyzing time series data and generating callouts
for significant changes or threshold violations. It integrates with the expense and time
tracking dashboard to provide insights about unusual patterns in the data.

The system supports:
1. Rolling statistics calculation
2. Spike detection
3. Drop detection
4. Threshold-based condition checking
5. Time-based filtering of callouts

Classes:
    CalloutSystem: Main class for analyzing data and generating callouts
"""

import numpy as np
import pandas as pd
from datetime import timedelta, datetime
from typing import Optional, Dict, Any, List

class CalloutSystem:
    """
    A system for analyzing time series data and generating callouts for significant changes.

    This class provides methods to:
    - Calculate rolling statistics
    - Detect spikes and drops in metrics
    - Check for threshold violations
    - Filter and format callouts

    Attributes:
        df_grouped (pd.DataFrame): Input DataFrame containing grouped time series data
        callouts_df (pd.DataFrame): DataFrame storing generated callouts
    """

    def __init__(self, df_grouped: pd.DataFrame):
        """
        Initialize the CalloutSystem.

        Args:
            df_grouped (pd.DataFrame): DataFrame containing grouped time series data
                                     Must have 'KEY' and 'DATE' columns
        """
        self.df_grouped = df_grouped
        self._initialize_callouts_df()

    def _initialize_callouts_df(self) -> None:
        """Initialize the callouts DataFrame with required columns."""
        self.callouts_df = pd.DataFrame(columns=[
            'key', 'date', 'check', 'condition', 'more_info',
            'value', 'std_devs_away'
        ])

    def calculate_rolling_stats(self, target_column: str, window: int = 7) -> None:
        """
        Calculate rolling statistics for a target column.

        Args:
            target_column (str): Column name to calculate statistics for
            window (int, optional): Rolling window size in days. Defaults to 7.
        """
        group = self.df_grouped.groupby('KEY')[target_column]
        self.df_grouped[f'{target_column}_7_day_avg'] = (
            group.rolling(window=window, min_periods=1)
            .mean()
            .reset_index(0, drop=True)
        )
        self.df_grouped[f'{target_column}_7_day_std_dev'] = (
            group.rolling(window=window, min_periods=1)
            .std()
            .reset_index(0, drop=True)
        )

    @staticmethod
    def format_number(value: float) -> str:
        """
        Format numbers with K/M suffixes for better readability.

        Args:
            value (float): Number to format

        Returns:
            str: Formatted number string
        """
        if value >= 1_000_000:
            return f'{value / 1_000_000:.1f}M'
        elif value >= 1_000:
            return f'{value / 1_000:.1f}K'
        elif value >= 1:
            return f'{value:.0f}'
        return f'{value:.2f}'

    def _create_callout_dict(self, row: pd.Series, check_type: str,
                              condition: str, threshold_value: float,
                              key_column: str = 'KEY') -> Dict[str, Any]:
        """
        Create a dictionary for a single callout.

        Args:
            row (pd.Series): Data row
            check_type (str): Type of check performed
            condition (str): Condition description
            threshold_value (float): Threshold value used
            key_column (str): The column representing the key (default is 'KEY').

        Returns:
            dict: Dictionary containing callout information
        """
        # Calculate thresholds
        lower_threshold = self.df_grouped[f'{target_column}_7_day_avg'] - threshold * self.df_grouped[f'{target_column}_7_day_std_dev']
        upper_threshold = self.df_grouped[f'{target_column}_7_day_avg'] + threshold * self.df_grouped[f'{target_column}_7_day_std_dev']

        # Prepare rows to append to callouts_df
        new_callouts = row.apply(lambda row: {
            'key': row[key_column],
            'date': row['DATE'],
            'check': f'{check_type} in {target_column.replace("_", " ").lower()}',
            'condition': f"{target_column.replace('_', ' ').lower()} {condition} {threshold_value}",
            'more_info': f"Current value: {self.format_number(row[target_column])}",
            'value': str(row[target_column]),
            'std_devs_away': round((row[target_column] - self.df_grouped[f'{target_column}_7_day_avg']) / self.df_grouped[f'{target_column}_7_day_std_dev'], 2)
        }, axis=1)

        # Append the new callouts to the callouts_df attribute
        self.callouts_df = pd.concat([self.callouts_df, pd.DataFrame(new_callouts.tolist())], ignore_index=True)

    def check_drop_in_column(self, target_column: str, key_column: str = 'KEY', threshold: int = 2) -> None:
        """
        Check for drops in a column and create callouts based on the condition.

        Args:
            target_column (str): The column to check the condition on.
            key_column (str): The column representing the key (default is 'KEY').
            threshold (int, optional): The threshold to compare against. Defaults to 2.
        """
        # Filter rows where the value is below the threshold
        drops_df = self.df_grouped[self.df_grouped[target_column] < self.df_grouped[f'{target_column}_7_day_avg'] - threshold * self.df_grouped[f'{target_column}_7_day_std_dev']]

        # Prepare rows to append to callouts_df
        new_callouts = drops_df.apply(lambda row: {
            'key': row[key_column],
            'date': row['DATE'],
            'check': f'Drop in {target_column.replace("_", " ").lower()}',
            'condition': f"< {threshold} standard deviation from L7 average {target_column.replace('_', ' ').lower()}",
            'more_info': f"{self.format_number(row[target_column])} < {self.format_number(row[f'{target_column}_7_day_avg'] - threshold * row[f'{target_column}_7_day_std_dev'])} (L7 avg: {self.format_number(row[f'{target_column}_7_day_avg'])}, L7 std dev: {self.format_number(row[f'{target_column}_7_day_std_dev'])})",
            'value': str(row[target_column]),
            'std_devs_away': round((row[target_column] - row[f'{target_column}_7_day_avg']) / row[f'{target_column}_7_day_std_dev'], 2)
        }, axis=1)

        # Convert to DataFrame and concatenate with callouts_df
        self.callouts_df = pd.concat([self.callouts_df, pd.DataFrame(new_callouts.tolist())], ignore_index=True)

    def check_spike_in_column(self, target_column: str, key_column: str = 'KEY', threshold: int = 2) -> None:
        """
        Check for spikes in a column and create callouts based on the condition.

        Args:
            target_column (str): The column to check the condition on.
            key_column (str): The column representing the key (default is 'KEY').
            threshold (int, optional): The threshold to compare against. Defaults to 2.
        """
        # Filter rows where the value is above the threshold
        spikes_df = self.df_grouped[self.df_grouped[target_column] > self.df_grouped[f'{target_column}_7_day_avg'] + threshold * self.df_grouped[f'{target_column}_7_day_std_dev']]

        # Prepare rows to append to callouts_df
        new_callouts = spikes_df.apply(lambda row: {
            'key': row[key_column],
            'date': row['DATE'],
            'check': f'Spike in {target_column.replace("_", " ").lower()}',
            'condition': f"> {threshold} standard deviation from L7 average {target_column.replace('_', ' ').lower()}",
            'more_info': f"{self.format_number(row[target_column])} > {self.format_number(row[f'{target_column}_7_day_avg'] + threshold * row[f'{target_column}_7_day_std_dev'])} (L7 avg: {self.format_number(row[f'{target_column}_7_day_avg'])}, L7 std dev: {self.format_number(row[f'{target_column}_7_day_std_dev'])})",
            'value': str(row[target_column]),
            'std_devs_away': round((row[target_column] - row[f'{target_column}_7_day_avg']) / row[f'{target_column}_7_day_std_dev'], 2)
        }, axis=1)

        # Convert to DataFrame and concatenate with callouts_df
        self.callouts_df = pd.concat([self.callouts_df, pd.DataFrame(new_callouts.tolist())], ignore_index=True)

    def check_condition_in_column(self, target_column: str, condition: str, threshold: float, key_column: str = 'KEY') -> None:
        """
        Check for a condition in a column and create callouts based on the condition.

        Args:
            target_column (str): The column to check the condition on.
            condition (str): The condition to check. Can be '>' or '<'.
            threshold (float): The threshold to compare against.
            key_column (str): The column representing the key (default is 'KEY').

        Returns:
            None: Updates the callouts_df attribute.
        """
        # Apply the condition to filter rows
        if condition == '>':
            condition_df = self.df_grouped[self.df_grouped[target_column] > threshold]
            condition_text = f"> {self.format_number(threshold)}"
        elif condition == '<':
            condition_df = self.df_grouped[self.df_grouped[target_column] < threshold]
            condition_text = f"< {self.format_number(threshold)}"
        else:
            raise ValueError("Condition must be either '>' or '<'.")

        # Prepare rows to append to callouts_df
        new_callouts = condition_df.apply(lambda row: {
            'key': row[key_column],
            'date': row['DATE'],
            'check': f'{target_column.replace("_", " ").lower()} {condition_text}',
            'condition': f"{target_column.replace('_', ' ').lower()} {condition_text}",
            'more_info': f"Current value: {self.format_number(row[target_column])}",
            'value': str(row[target_column]),
        }, axis=1)

        # Append the new callouts to the callouts_df attribute
        self.callouts_df = pd.concat([self.callouts_df, pd.DataFrame(new_callouts.tolist())], ignore_index=True)
        

    def filter_last_week(self):
        # Filter for only the last 7 days excluding today
        today = datetime.now().date()
        start_date = today - timedelta(days=7)
        end_date = today - timedelta(days=1)
        self.callouts_df = self.callouts_df[(self.callouts_df['date'] >= start_date) & (self.callouts_df['date'] <= end_date)]


    def add_buffer_days(self, buffer_days = 3):
        # Filter for only the last 7 days excluding last buffer_days days
        today = datetime.now().date()
        start_date = today - timedelta(days=buffer_days+7)
        end_date = today - timedelta(days=buffer_days)
        self.callouts_df = self.callouts_df[(self.callouts_df['date'] >= start_date) & (self.callouts_df['date'] <= end_date)]

    def get_callouts(self):

        if 'date' in self.callouts_df.columns:
            if 'std_devs_away' in self.callouts_df.columns:
                self.callouts_df = self.callouts_df.sort_values(['date', 'std_devs_away'], ascending=[False, True])
                return self.callouts_df
            self.callouts_df = self.callouts_df.sort_values('date', ascending=False)
            return self.callouts_df

        if 'metric' in self.callouts_df.columns:
            self.callouts_df = self.callouts_df.sort_values('metric', ascending=True)
            return self.callouts_df
            
        return self.callouts_df
