import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
n = 55000

regions = ['North', 'South', 'East', 'West', 'Central']
teams = ['Team A', 'Team B', 'Team C', 'Team D', 'Team E']
categories = ['Logistics', 'Finance', 'Operations', 'HR', 'Sales']
statuses = ['Completed', 'Delayed', 'Pending', 'Cancelled', 'Escalated']

df = pd.DataFrame({
    'order_id': range(1001, n + 1001),
    'date': [datetime(2023, 1, 1) + timedelta(hours=i * 0.85) for i in range(n)],
    'region': np.random.choice(regions, n, p=[0.25, 0.20, 0.22, 0.18, 0.15]),
    'team': np.random.choice(teams, n),
    'category': np.random.choice(categories, n),
    'revenue': np.random.normal(3200, 800, n).round(2),
    'cost': np.random.normal(1800, 500, n).round(2),
    'processing_time_hrs': np.random.exponential(4, n).round(2),
    'units_processed': np.random.randint(5, 200, n),
    'customer_id': np.random.randint(10000, 99999, n),
    'status': np.random.choice(statuses, n, p=[0.60, 0.15, 0.12, 0.08, 0.05]),
    'sla_breach': np.random.choice([0, 1], n, p=[0.82, 0.18]),
})

# Inject anomalies
anomaly_idx = np.random.choice(n, 800, replace=False)
df.loc[anomaly_idx[:400], 'revenue'] *= 4.5
df.loc[anomaly_idx[400:], 'processing_time_hrs'] *= 8

# Inject missing data
for col in ['revenue', 'processing_time_hrs', 'team']:
    null_idx = np.random.choice(n, int(n * 0.03), replace=False)
    df.loc[null_idx, col] = np.nan

import os
os.makedirs('../Data/raw', exist_ok=True)
df.to_csv('../Data/raw/operations_raw.csv', index=False)
print(f"Done! Generated {len(df):,} records")
print(f"Anomalies injected: {len(anomaly_idx)}")
print(df.head(3))