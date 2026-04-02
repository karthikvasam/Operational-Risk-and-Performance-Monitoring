import streamlit as st
import pandas as pd
import plotly.express as px
import os

# This is the browser title 
st.set_page_config(page_title="Risk Intelligence System", layout="wide")

st.title("Operational Performance & Risk Intelligence System")
st.write("Detects operational problems early using data from 55,000+ records")

# loading the data 
this_file = os.path.abspath(__file__)

streamlit_app_folder = os.path.dirname(this_file)

root_folder = os.path.dirname(streamlit_app_folder)

processed_folder = os.path.join(root_folder, 'Data', 'Processed')

# loading the 3 CSV files from that folder
df = pd.read_csv(os.path.join(processed_folder, 'operations_clean.csv'))
risk_df = pd.read_csv(os.path.join(processed_folder, 'team_risk_scores.csv'))
bt_df = pd.read_csv(os.path.join(processed_folder, 'bottleneck_report.csv'))

# creating the sidebar filters
st.sidebar.title("Filters")

all_regions = df['region'].unique().tolist()
selected_regions = st.sidebar.multiselect(
    "Choose Region",
    options=all_regions,
    default=all_regions  
)

all_months = sorted(df['month'].unique().tolist())
selected_months = st.sidebar.multiselect(
    "Choose Month",
    options=all_months,
    default=all_months[-3:]  
)

# applying the filters to the main dataframe so all charts and tables respond to the sidebar selections
filtered_df = df[
    df['region'].isin(selected_regions) &
    df['month'].isin(selected_months)
]

st.divider()

# SECTION 1: creating kpi snapshot at the top
st.subheader("Snapshot")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Orders", f"{len(filtered_df):,}")
c2.metric("Avg Profit Margin", f"{round(filtered_df['profit_margin'].mean(), 1)}%")
c3.metric("Delay Rate", f"{round(filtered_df['is_delayed'].mean() * 100, 1)}%")
c4.metric("SLA Breaches", f"{int(filtered_df['sla_breach'].sum()):,}")

st.divider()

# SECTION 2: creating the early warning panel with risk scores for each team 
st.subheader("Early Warning Panel")

for i, row in risk_df.iterrows():
    if row['risk_level'] == 'High':
        st.error(
            f"HIGH RISK — {row['team']} | "
            f"Score: {row['risk_score']}/100 | "
            f"Delays: {row['delay_rate_pct']}% | "
            f"SLA Breach: {row['sla_breach_pct']}%"
        )
    elif row['risk_level'] == 'Medium':
        st.warning(
            f"MEDIUM RISK — {row['team']} | "
            f"Score: {row['risk_score']}/100 | "
            f"Delays: {row['delay_rate_pct']}% | "
            f"SLA Breach: {row['sla_breach_pct']}%"
        )
    else:
        st.success(
            f"LOW RISK — {row['team']} | "
            f"Score: {row['risk_score']}/100"
        )

st.divider()

# SECTION 3: two charts side by side - delay rate by region, and risk score by team
st.subheader("Analysis")

left_col, right_col = st.columns(2)

with left_col:
    st.write("Delay rate by region")
    # Calculating delay percentage by region
    region_delay = filtered_df.groupby('region')['is_delayed'].mean().reset_index()
    region_delay['delay_pct'] = (region_delay['is_delayed'] * 100).round(1)
    fig1 = px.bar(
        region_delay,
        x='region',
        y='delay_pct',
        color='delay_pct',
        color_continuous_scale='Reds',
        labels={'delay_pct': 'Delay %', 'region': 'Region'}
    )
    st.plotly_chart(fig1, use_container_width=True)

with right_col:
    st.write("Risk score by team")
    # Sort teams by risk score for better visualization
    sorted_risk = risk_df.sort_values('risk_score', ascending=True)
    fig2 = px.bar(
        sorted_risk,
        x='risk_score',
        y='team',
        orientation='h',
        color='risk_level',
        color_discrete_map={
            'Low': 'green',
            'Medium': 'orange',
            'High': 'red'
        },
        labels={'risk_score': 'Risk Score', 'team': 'Team'}
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# SECTION 4: creating monthly revenue trend
st.subheader("Monthly Revenue Trend")

monthly = filtered_df.groupby('month')['revenue_clean'].sum().reset_index()
monthly.columns = ['month', 'total_revenue']

fig3 = px.line(
    monthly,
    x='month',
    y='total_revenue',
    markers=True,
    labels={'total_revenue': 'Total Revenue', 'month': 'Month'}
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# SECTION 5: creating bottlenec report table
st.subheader("Bottleneck Report")
st.write("Region and team combinations with most processing delays")
st.dataframe(bt_df.head(10), use_container_width=True)

st.divider()

# SECTION 6: creating anamoly table
st.subheader("Flagged Anomalies")
st.write("Orders with unusually high revenue flagged during ETL pipeline")

anomaly_df = filtered_df[filtered_df['revenue_flag'] == 1]

cols_to_show = ['order_id', 'date', 'region', 'team',
                'revenue', 'revenue_clean', 'status']

st.dataframe(anomaly_df[cols_to_show].head(50), use_container_width=True)