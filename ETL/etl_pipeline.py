import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
load_dotenv()
from data_quality import run_quality_checks
import numpy as np


# I'm setting up the file paths first so I don't hardcode them
base_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw_file = os.path.join(base_folder, 'Data', 'Raw', 'operations_raw.csv')
output_folder = os.path.join(base_folder, 'Data', 'Processed')

# Create the processed folder if it doesn't exist yet
os.makedirs(output_folder, exist_ok=True)

# STEP 1 - Load the raw data
print("Loading raw data...")
df = pd.read_csv(raw_file)
print(f"Total records loaded: {len(df)}")

# STEP 2 - Run quality checks before cleaning anything
print("\nRunning data quality checks...")
run_quality_checks(df, output_folder)

# STEP 3 - Start cleaning the data

# Fix the date column so pandas understands it properly
df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=True)

# Remove any duplicate orders
duplicates = df.duplicated(subset='order_id').sum()
df = df.drop_duplicates(subset='order_id')
print(f"\nDuplicates removed: {duplicates}")

# Fill missing revenue with the median of that region
# (using regional median is more accurate than overall median)
df['revenue'] = df.groupby('region')['revenue'].transform(
    lambda x: x.fillna(x.median())
)

# Fill missing processing time with overall median
df['processing_time_hrs'] = df['processing_time_hrs'].fillna(
    df['processing_time_hrs'].median()
)

# Fill missing team names
df['team'] = df['team'].fillna('Unassigned')

print(f"Nulls remaining after cleaning: {df.isnull().sum().sum()}")

# STEP 4 - Flag revenue anomalies
# Anything above 99th percentile is suspicious
p99 = df['revenue'].quantile(0.99)
df['revenue_flag'] = (df['revenue'] > p99).astype(int)
df['revenue_clean'] = df['revenue'].clip(upper=p99)
print(f"Revenue anomalies flagged: {df['revenue_flag'].sum()}")

# STEP 5 - Create new columns that help with analysis
df['profit'] = df['revenue_clean'] - df['cost']
df['profit_margin'] = (df['profit'] / df['revenue_clean'] * 100).round(2)

# Extract time-based columns from date
df['month'] = df['date'].dt.to_period('M').astype(str)
df['quarter'] = df['date'].dt.to_period('Q').astype(str)
df['week'] = df['date'].dt.isocalendar().week.astype(int)

# Create a simple delay flag (1 = delayed, 0 = not delayed)
df['is_delayed'] = (df['status'] == 'Delayed').astype(int)

# Efficiency = how many units processed per hour
df['efficiency_score'] = (
    df['units_processed'] / df['processing_time_hrs']
).round(2)

# working on inf values 
df['profit_margin'] = np.where(
    df['revenue_clean'] == 0,
    0,
    (df['profit'] / df['revenue_clean'] * 100)
)
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df['profit_margin'] = df['profit_margin'].fillna(0)
"""
debug lines for inf values check
print(df.isin([np.inf, -np.inf]).sum())
print(df.columns)
"""
print(df.isin([np.inf, -np.inf]).sum())
print(df.columns)

print(f"New columns added: profit, profit_margin, month, quarter,")
print(f"week, is_delayed, efficiency_score")
print(f"Final clean records: {len(df)}")

# STEP 6 - Save the cleaned data
clean_file = os.path.join(output_folder, 'operations_clean.csv')
df.to_csv(clean_file, index=False)
print(f"\nClean CSV saved to: {clean_file}")

# STEP 7 - Load into MySQL database
print("\nConnecting to MySQL...")
try:
    password = os.getenv('MYSQL_PASSWORD')
    engine = create_engine(
    f'mysql+mysqlconnector://root:{password}@127.0.0.1:3306/risk_monitoring'
    )
    df.to_sql('operations', engine, if_exists='replace',
              index=False, chunksize=5000)
    print("Data loaded into MySQL successfully!")
except Exception as e:
    print(f"MySQL connection failed: {e}")
    print("Don't worry - clean CSV is already saved.")

print("\nDone! ETL pipeline finished.") 
