import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"


def detect_anomalies() -> List[Dict[str, Any]]:
    """Detect anomalies in transactions using z-score and IQR."""
    if not TRANSACTIONS_FILE.exists():
        logger.warning(f"Transactions file not found: {TRANSACTIONS_FILE}")
        return []
    
    try:
        df = pd.read_csv(TRANSACTIONS_FILE)
        
        if 'amount' not in df.columns:
            logger.warning("'amount' column not found in transactions.csv")
            return []
        
        anomalies = []
        
        # Z-score method
        mean_amount = df['amount'].mean()
        std_amount = df['amount'].std()
        
        if std_amount > 0:
            df['z_score'] = (df['amount'] - mean_amount) / std_amount
            z_anomalies = df[abs(df['z_score']) > 2.5]
            
            for _, row in z_anomalies.iterrows():
                anomalies.append({
                    "transaction_id": str(row.get('transaction_id', row.get('id', 'unknown'))),
                    "amount": float(row['amount']),
                    "date": str(row.get('date', row.get('timestamp', 'unknown'))),
                    "customer_id": str(row.get('customer_id', 'unknown')),
                    "anomaly_type": "z-score outlier",
                    "z_score": float(row['z_score'])
                })
        
        # IQR method
        Q1 = df['amount'].quantile(0.25)
        Q3 = df['amount'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        iqr_anomalies = df[(df['amount'] < lower_bound) | (df['amount'] > upper_bound)]
        
        for _, row in iqr_anomalies.iterrows():
            trans_id = str(row.get('transaction_id', row.get('id', 'unknown')))
            # Avoid duplicates
            if not any(a['transaction_id'] == trans_id for a in anomalies):
                anomalies.append({
                    "transaction_id": trans_id,
                    "amount": float(row['amount']),
                    "date": str(row.get('date', row.get('timestamp', 'unknown'))),
                    "customer_id": str(row.get('customer_id', 'unknown')),
                    "anomaly_type": "IQR outlier",
                    "z_score": float((row['amount'] - mean_amount) / std_amount) if std_amount > 0 else 0.0
                })
        
        return anomalies
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        return []
