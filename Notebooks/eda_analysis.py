import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Load the clean data that ETL pipeline created
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
clean_file = os.path.join(base, 'Data', 'Processed', 'operations_clean.csv')
output_folder = os.path.join(base, 'Data', 'Processed')
assets_folder = os.path.join(base, 'Assets')


os.makedirs(assets_folder, exist_ok=True)

df = pd.read_csv(clean_file)
print(f"Loaded {len(df)} records")
print(f"Columns: {list(df.columns)}")

#  handiling numerical fields and infinity values 
df['efficiency_score'] = pd.to_numeric(df['efficiency_score'], errors='coerce')
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df['efficiency_score'] = df['efficiency_score'].fillna(df['efficiency_score'].median())

# converting month to datetime for better handling in charts
df['month_date'] = pd.to_datetime(df['month'])
df = df.sort_values('month_date')

# PART 1 - RISK SCORING
# The score is based on 3 things:
# 1. How often they delay orders (worth 40 points)
# 2. How often they breach SLA (worth 35 points)
# 3. How inefficient they are (worth 25 points)

print("\nCalculating risk score for each team...")

results = []

for team_name in df['team'].unique():

    # Get only this team's data
    team_df = df[df['team'] == team_name]

    # Calculate delay score
    delay_pct = team_df['is_delayed'].mean()
    delay_score = delay_pct * 40

    # Calculate SLA breach score
    breach_pct = team_df['sla_breach'].mean()
    breach_score = breach_pct * 35

    # Calculate efficiency score
    # If team is below average efficiency, give them 25 risk points
    team_efficiency = team_df['efficiency_score'].mean()
    overall_efficiency = df['efficiency_score'].mean()
    if team_efficiency < overall_efficiency:
        efficiency_score = 25
    else:
        efficiency_score = 0

    # Add up the total risk score
    total_score = round(delay_score + breach_score + efficiency_score, 1)

    # Assign a label based on the score
    if total_score >= 60:
        level = 'High'
    elif total_score >= 30:
        level = 'Medium'
    else:
        level = 'Low'

    results.append({
        'team': team_name,
        'risk_score': total_score,
        'risk_level': level,
        'delay_rate_pct': round(delay_pct * 100, 1),
        'sla_breach_pct': round(breach_pct * 100, 1),
        'avg_efficiency': round(team_efficiency, 2)
    })

# Convert list to dataframe
risk_df = pd.DataFrame(results)
risk_df = risk_df.sort_values('risk_score', ascending=False)

print("\nRisk scores per team:")
print(risk_df)

# Save risk scores CSV
risk_file = os.path.join(output_folder, 'team_risk_scores.csv')
risk_df.to_csv(risk_file, index=False)
print(f"\nSaved: {risk_file}")

# PART 2 - BOTTLENECK ANALYSIS
# Find orders that took way longer than normal
# I am using the 90th percentile as my threshold
# Anything above that is considered a bottleneck

print("\nFinding bottlenecks...")

top_10_pct = df['processing_time_hrs'].quantile(0.90)
slow_orders = df[df['processing_time_hrs'] > top_10_pct]

# Group by region and team to see where bottlenecks happen most
bottleneck_df = slow_orders.groupby(['region', 'team']).agg(
    bottleneck_orders=('order_id', 'count'),
    avg_delay_hrs=('processing_time_hrs', 'mean'),
    revenue_at_risk=('revenue_clean', 'sum')
).round(2).reset_index()

bottleneck_df = bottleneck_df.sort_values('revenue_at_risk', ascending=False)

print("Top bottleneck areas:")
print(bottleneck_df.head())

bottleneck_file = os.path.join(output_folder, 'bottleneck_report.csv')
bottleneck_df.to_csv(bottleneck_file, index=False)
print(f"Saved: {bottleneck_file}")

# PART 3 - CHARTS
# I am making 4 simple charts to understand the data visually
# These will also go into the README as screenshots

print("\nMaking charts...")

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle('Operational Risk Intelligence - EDA Summary')

# Chart 1 - Which region delays the most?
delay_by_region = df.groupby('region')['is_delayed'].mean() * 100
delay_by_region.plot(kind='bar', ax=axes[0, 0], color='tomato')
axes[0, 0].set_title('Delay rate by region %')
axes[0, 0].set_xlabel('')

# Chart 2 - Risk score per team
risk_df.set_index('team')['risk_score'].plot(
    kind='barh', ax=axes[0, 1], color='orange'
)
axes[0, 1].set_title('Risk score by team')

# Chart 3 - SLA breach trend over time
df.groupby('month')['sla_breach'].mean().plot(
    ax=axes[1, 0], marker='o', color='red'
)
axes[1, 0].set_title('SLA breach rate by month')

# Chart 4 - Efficiency score spread
df['efficiency_score'].hist(bins=40, ax=axes[1, 1], color='green')
axes[1, 1].set_title('Efficiency score distribution')

plt.tight_layout()
chart_path = os.path.join(assets_folder, 'eda_summary.png')
plt.savefig(chart_path, dpi=150)
print(f"Charts saved to: {chart_path}")

print(f"Files created:")
print(f"  - team_risk_scores.csv")
print(f"  - bottleneck_report.csv")
print(f"  - eda_summary.png")
