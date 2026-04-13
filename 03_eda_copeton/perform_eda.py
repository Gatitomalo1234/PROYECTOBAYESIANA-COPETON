import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Directorios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'copeton_occupancy_ready.csv')
PLOT_DIR = os.path.join(BASE_DIR, '03_eda_copeton', 'plots')
os.makedirs(PLOT_DIR, exist_ok=True)
OUT_TXT = os.path.join(BASE_DIR, '03_eda_copeton', 'eda_summary.txt')

def run_eda():
    df = pd.read_csv(DATA_FILE)
    
    with open(OUT_TXT, 'w', encoding='utf-8') as f:
        f.write("=== EDA SUMMARY ===\n")
        f.write(f"Total Registros: {len(df)}\n\n")
        
        # 1. Nulls
        f.write("--- VALORES NULOS ---\n")
        cols = ['co_ppm', 'no2_ppb', 'o3_ppb', 'pm10_ugm3', 'pm25_ugm3', 'so2_ugm3']
        for c in cols:
            pct = df[c].isna().sum() / len(df) * 100
            f.write(f"{c}: {pct:.2f}% nulos\n")
            
        # 2. Outliers
        f.write("\n--- OUTLIERS (IQR) ---\n")
        for c in cols:
            q1 = df[c].quantile(0.25)
            q3 = df[c].quantile(0.75)
            iqr = q3 - q1
            outliers = df[(df[c] < q1 - 1.5*iqr) | (df[c] > q3 + 1.5*iqr)]
            pct_out = len(outliers) / len(df[c].dropna()) * 100 if len(df[c].dropna())>0 else 0
            f.write(f"{c}: {pct_out:.2f}% atipicos\n")
            
        # 3. Correlations (Spearman)
        f.write("\n--- CORRELACIONES (Spearman) ---\n")
        corr = df[cols].corr(method='spearman')
        f.write(corr.to_string())
        f.write("\n")
        
        # Plot Correlations
        plt.figure(figsize=(8,6))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Correlación Spearman (Contaminantes)')
        plt.tight_layout()
        plt.savefig(os.path.join(PLOT_DIR, 'correlation_matrix.png'))
        plt.close()
        
        # 4. Bivariate Analysis (Y vs Variables)
        f.write("\n--- RELACIÓN DETECCIÓN VS POLUCIÓN (Medianas) ---\n")
        for c in cols:
            median_abs = df[df['y_copeton']==0][c].median()
            median_det = df[df['y_copeton']==1][c].median()
            f.write(f"{c} -> Ausencia (0): {median_abs:.2f} | Detección (1): {median_det:.2f}\n")
            
        # Plot Bivariate
        # Let's plot PM10 and PM2.5 boxplots
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        sns.boxplot(x='y_copeton', y='pm10_ugm3', data=df, ax=axes[0], palette='Set2')
        axes[0].set_title('PM10 vs Detección')
        sns.boxplot(x='y_copeton', y='pm25_ugm3', data=df, ax=axes[1], palette='Set2')
        axes[1].set_title('PM2.5 vs Detección')
        plt.tight_layout()
        plt.savefig(os.path.join(PLOT_DIR, 'bivariate_pm.png'))
        plt.close()

if __name__ == "__main__":
    run_eda()
