# Operational Risk and Performance Monitoring System

> I built a decision-support system that identifies where and why operations are failing before they become a business problem.

## Live Demo
[Streamlit App](https://operational-risk-and-performance-monitoring-f7fvmpjjqpt3ziheqt.streamlit.app/) — click to view

## Project Demo Video
https://drive.google.com/file/d/1JmoMq9Sh6qV-AZV81YcuxVy0vSTR03Xq/view

---

## The Problem This Solves

Most companies find out something went wrong after it happened.

This system detects problems early by continuously monitoring:
- Which teams are declining in efficiency month over month
- Where processing delays are creating revenue risk
- Which orders have statistically anomalous revenue values
- Which region-team combinations breach SLA most frequently

Without this system:
> "Sales dropped this month."

This System helps explain:
> "Sales dropped because Region North had a 35% processing delay.
> Team A has been declining for 3 consecutive months.
> 550 high-revenue orders were flagged as anomalies.
> ₹9.8M in revenue is stuck in operational bottlenecks."

---

## 🚀 Key Features

- Data quality validation before processing  
- ETL pipeline with feature engineering  
- SQL-based anomaly detection and KPI tracking  
- Risk scoring system for teams  
- Bottleneck detection (revenue at risk)  
- Dual dashboards (Streamlit + Power BI)

---

## Project Workflow 

Raw Data → Data Cleaning & Transformation → SQL-Based Analysis → Business Dashboards

---

## System Architecture — 8 Layers
```
Raw Data Generation
      ↓
Data Quality Validation
      ↓
ETL Pipeline (Clean + Transform + Load)
      ↓
MySQL Database (55K records)
      ↓
SQL Queries + MySQL Views
      ↓
Python Risk Scoring + EDA
      ↓
Excel MIS Reconciliation
      ↓
Streamlit Dashboard ←→ Power BI Dashboard
```

---

## Layer by Layer Breakdown

### Layer 1 — Data Generation (ETL/generate_data.py)
Generated a random 55,000 row operational dataset using
Python with regions, teams, revenue, processing time, SLA
status and order categories. Intentionally added:
- 800 revenue anomalies
- Null values and delays

### Layer 2 — Data Quality Validation (ETL/data_quality.py)
Before cleaning ran automated quality checks and produced a JSON report:
- Number of Null fields
- Detecting Negative revenue
- Checking Duplicate order ID
- Processing time outlier (3-sigma)
- Calculating SLA breach rate

Result: 564 outliers detected, 4950 nulls flagged,
0 duplicates, status PASSED.

### Layer 3 — ETL Pipeline (ETL/etl_pipeline.py)
Full Extract → Validate → Transform → Load pipeline:
- Handling Nulls using median within the region
- Revenue anomaly flagging using 99th percentile threshold
- Feature engineering: profit margin, efficiency score,
  delay flag, month/quarter/week columns
- Loaded 55,000 clean records into MySQL

### Layer 4 — SQL Risk Detection (SQL/)
Three SQL files saved as MySQL Views for direct Power BI integration

**anomaly_detection.sql → anomaly_view**
- Detecting Revenue spike using 3-sigma statistical method
- Identifying and Processing delay outliers
- Calculating Month-over-Month delay rate change using LAG

**kpi_queries.sql → monthly_kpi_view, regional_kpi_view**
- Monthly performance trend with revenue, profit, efficiency
- Regional comparison across all 5 regions
- Team efficiency ranking using RANK window function

**risk_flags.sql → sla_risk_view, early_warning_view**
- Calculating SLA breach rate by team-region combination
- Early warning: detects teams declining 3 months in a row
  using LAG window function — Identifies them before the Risk
- High-value delayed orders (revenue × delay intersection)

### Layer 5 — Python Risk Scoring (Notebooks/eda_analysis.py)
Composite risk score per team calculated using weighted formula:
- Delay rate: 40% weight
- SLA breach rate: 35% weight  
- Efficiency below average: 25% weight

Output: Low, Medium, High risk level per team.
Bottleneck analysis identifies which region-team combination
has the most revenue stuck in processing delays.

### Layer 6 — Excel Reconciliation (Excel/reconciliation.xlsx)
MIS-style validation workbook with 4 sheets:
- Data Summary: pipeline metrics and record counts
- Quality Log: colour-coded quality checks
  (PASS = green, FLAGGED = red, MONITOR = yellow)
- KPI Summary: regional pivot table with delay rates
- Insights: key findings, business impact, recommendations

### Layer 7 — Streamlit Dashboard (Streamlit_app/app.py)
Interactive decision-support interface deployed publicly:
- Early warning panel showing High/Medium/Low risk teams
- Regional delay rate bar chart
- Team risk score horizontal bar chart
- Monthly revenue trend line chart
- Bottleneck report table showing revenue at risk
- Anomaly flags table showing clipped orders
- Sidebar filters by region and month

### Layer 8 — Power BI Dashboard (PowerBI/)
Executive-level dashboard connected to MySQL Views:
- Page 1: Professional Overview — KPI cards, efficiency
  trend, profit margin trend
- Page 2: Regional Performance — delay rates, revenue by
  region, SLA breach summary table
- Page 3: Anomaly Flags — flagged orders with original vs
  cleaned revenue and amount clipped
- Page 4: Risk and SLA — breach rate by team, early warning
  table with WARNING rows highlighted red

---

## Key Results

| Metric | Value |
|--------|-------|
| Records processed | 55,000 |
| Anomalies detected | 550 |
| Nulls cleaned | 4,950 |
| Revenue at risk (bottlenecks) | ₹9.8M+ |
| Teams flagged as medium risk | 3 |
| SQL Views created | 5 |
| Pipeline status | PASSED |

---

## Why Two Visualization Layers?

**Streamlit (Python-built dashboard)**
- Python Based Interactive Analysis

**Power BI (connected to MySQL Views)**
- Business Dashboard built on SQL views

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data generation | Python, NumPy, Pandas |
| Data validation | Python (automated quality checks) |
| ETL pipeline | Python, SQLAlchemy, MySQL |
| SQL analysis | MySQL (CTEs, window functions, LAG, RANK) |
| Risk scoring | Python (weighted composite formula) |
| Reconciliation | Excel (XLOOKUP, Pivot Tables, conditional formatting) |
| App dashboard | Streamlit, Plotly |
| BI dashboard | Power BI (connected to MySQL Views) |
| Version control | Git, GitHub |

---

## Project Structure
```
Operational-Risk-and-Performance-Monitoring/
├── ETL/
│   ├── generate_data.py      # creates 55K dataset
│   ├── data_quality.py       # automated validation
│   └── etl_pipeline.py       # cleans and loads to MySQL
├── SQL/
│   ├── anomaly_detection.sql # 3-sigma detection + view
│   ├── kpi_queries.sql       # KPI trends + views
│   └── risk_flags.sql        # risk + early warning + views
├── Notebooks/
│   └── eda_analysis.py       # risk scoring + bottlenecks
├── Excel/
│   └── reconciliation.xlsx   # MIS validation workbook
├── Streamlit_app/
│   ├── app.py                # deployed dashboard
│   └── requirements.txt
├── PowerBI/
│   └── operation_powerbi_dashboard.pbix
├── Data/                
│   └── Processed/            # cleaned CSVs
├── Assets/
│   ├──  Anomalies Flags.png
|   ├──  eda_summary.png
|   ├──  Professional Summary.png
|   ├──  Regional Performance.png
|   ├──  Risk and SLA Filters.png
|   └── Risk and SLA.png
└── README.md
```

---

## How to Run Locally
```bash
# Install dependencies
pip install pandas numpy sqlalchemy mysql-connector-python streamlit plotly matplotlib

# Step 1 - Generate dataset
cd ETL
python generate_data.py

# Step 2 - Validate data quality
python data_quality.py

# Step 3 - Run ETL pipeline (requires MySQL running)
python etl_pipeline.py

# Step 4 - Run risk scoring
cd ../Notebooks
python eda_analysis.py

# Step 5 - Launch Streamlit dashboard
cd ../Streamlit_app
streamlit run app.py
```

---

**Connect with me on LinkedIn:** https://www.linkedin.com/in/vasam-karthik-/
**GitHub:** https://github.com/karthikvasam
```

