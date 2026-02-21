import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


def detect_csv_anomalies(file_path: Path, filename: str) -> Dict[str, Any]:
    """Detect anomalies in any uploaded CSV file."""
    try:
        df = pd.read_csv(file_path)
        
        if df.empty:
            return {
                "has_anomalies": False,
                "anomalies": [],
                "total_rows": 0,
                "analysis": "File is empty"
            }
        
        anomalies = []
        analysis_parts = []
        
        # Analyze numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_columns:
            for col in numeric_columns:
                col_data = df[col].dropna()
                
                if len(col_data) == 0:
                    continue
                
                # Z-score method
                mean_val = col_data.mean()
                std_val = col_data.std()
                
                if std_val > 0:
                    z_scores = np.abs((col_data - mean_val) / std_val)
                    outliers = df[z_scores > 2.5]
                    
                    for idx, row in outliers.iterrows():
                        anomalies.append({
                            "row_index": int(idx),
                            "column": col,
                            "value": float(row[col]),
                            "anomaly_type": "z-score outlier",
                            "z_score": float(z_scores.iloc[idx]),
                            "mean": float(mean_val),
                            "std": float(std_val)
                        })
                
                # IQR method
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                
                if IQR > 0:
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    iqr_outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                    
                    for idx, row in iqr_outliers.iterrows():
                        # Avoid duplicates
                        if not any(a['row_index'] == idx and a['column'] == col for a in anomalies):
                            anomalies.append({
                                "row_index": int(idx),
                                "column": col,
                                "value": float(row[col]),
                                "anomaly_type": "IQR outlier",
                                "z_score": float((row[col] - mean_val) / std_val) if std_val > 0 else 0.0,
                                "lower_bound": float(lower_bound),
                                "upper_bound": float(upper_bound)
                            })
            
            analysis_parts.append(f"Analyzed {len(numeric_columns)} numeric column(s)")
        
        # Analyze for missing values
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            analysis_parts.append(f"Found {missing_data.sum()} missing values")
            for col, count in missing_data[missing_data > 0].items():
                if count > len(df) * 0.1:  # More than 10% missing
                    anomalies.append({
                        "row_index": -1,
                        "column": col,
                        "value": None,
                        "anomaly_type": "high missing data",
                        "missing_count": int(count),
                        "missing_percentage": float(count / len(df) * 100)
                    })
        
        # Analyze for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            analysis_parts.append(f"Found {duplicates} duplicate row(s)")
            anomalies.append({
                "row_index": -1,
                "column": "all",
                "value": None,
                "anomaly_type": "duplicate rows",
                "duplicate_count": int(duplicates)
            })
        
        # Analyze date columns for anomalies
        date_columns = []
        for col in df.columns:
            try:
                pd.to_datetime(df[col], errors='raise')
                date_columns.append(col)
            except:
                pass
        
        if date_columns:
            for col in date_columns:
                try:
                    dates = pd.to_datetime(df[col], errors='coerce')
                    future_dates = dates[dates > pd.Timestamp.now()]
                    if len(future_dates) > 0:
                        analysis_parts.append(f"Found {len(future_dates)} future date(s) in {col}")
                except:
                    pass
        
        analysis = "; ".join(analysis_parts) if analysis_parts else "No significant anomalies detected"
        
        return {
            "has_anomalies": len(anomalies) > 0,
            "anomalies": anomalies[:50],  # Limit to 50 anomalies
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": numeric_columns,
            "analysis": analysis,
            "anomaly_count": len(anomalies)
        }
        
    except Exception as e:
        logger.error(f"Error detecting CSV anomalies: {e}")
        return {
            "has_anomalies": False,
            "anomalies": [],
            "total_rows": 0,
            "analysis": f"Error analyzing CSV: {str(e)}"
        }
