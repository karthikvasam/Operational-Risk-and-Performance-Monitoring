import pandas as pd
import json
import os
from datetime import datetime

def run_quality_checks(df, output_path):
    report = {
        'timestamp': str(datetime.now()),
        'total_records': len(df),
        'checks': {}
    }

    null_counts = df.isnull().sum()
    report['checks']['null_fields'] = null_counts[null_counts > 0].to_dict()

    neg_rev = (df['revenue'] < 0).sum()
    report['checks']['negative_revenue'] = int(neg_rev)

    dupes = df.duplicated(subset='order_id').sum()
    report['checks']['duplicate_orders'] = int(dupes)

    mean = df['processing_time_hrs'].mean()
    std = df['processing_time_hrs'].std()
    outliers = (df['processing_time_hrs'] > mean + 3 * std).sum()
    report['checks']['processing_time_outliers'] = int(outliers)

    breach_rate = df['sla_breach'].mean() * 100
    report['checks']['sla_breach_pct'] = round(breach_rate, 2)

    passed = all(v == 0 for k, v in report['checks'].items()
                 if k in ['negative_revenue', 'duplicate_orders'])
    report['status'] = 'PASSED' if passed else 'ISSUES FOUND'

    os.makedirs(output_path, exist_ok=True)
    filepath = os.path.join(output_path, 'quality_report.json')
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    print(f"\nReport saved to: {filepath}")
    return report


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base, 'Data', 'Raw', 'operations_raw.csv')
    output_path = os.path.join(base, 'Data', 'processed')

    print(f"Looking for file at: {raw_path}")

    if not os.path.exists(raw_path):
        print("ERROR: operations_raw.csv not found!")
        print("Run generate_data.py first.")
    else:
        df = pd.read_csv(raw_path)
        print(f"Loaded {len(df):,} records")
        run_quality_checks(df, output_path)