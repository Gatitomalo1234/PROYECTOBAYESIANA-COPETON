import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu, chi2_contingency
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'copeton_occupancy_ready.csv')
OUT_FILE = os.path.join(BASE_DIR, '03_eda_copeton', 'hypothesis_results.txt')
PLOT_DIR = os.path.join(BASE_DIR, '03_eda_copeton', 'plots')
os.makedirs(PLOT_DIR, exist_ok=True)

def run_tests():
    df = pd.read_csv(DATA_FILE)
    
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=== PRUEBAS DE SIGNIFICANCIA ESTADÍSTICA ===\n")
        f.write("H0: No hay diferencia entre los grupos de Detección (y=0 vs y=1)\n")
        f.write("H1: Hay diferencia estadística significativa (p < 0.05)\n\n")
        
        # 1. Variables de Contaminación (Mann-Whitney U) - Expanded
        f.write("--- VARIABLES AMBIENTALES (Mann-Whitney U) ---\n")
        pollutants = ['pm10_ugm3', 'pm25_ugm3', 'co_ppm', 'no2_ppb', 'o3_ppb', 'so2_ugm3']
        p_values = {}
        
        for var in pollutants:
            group0 = df[df['y_copeton']==0][var].dropna()
            group1 = df[df['y_copeton']==1][var].dropna()
            if len(group0) > 0 and len(group1) > 0:
                stat, p = mannwhitneyu(group0, group1, alternative='two-sided')
                f.write(f"{var}: p-value = {p:.4f} -> {'SIGNIFICATIVO' if p < 0.05 else 'No significativo'}\n")
                p_values[var] = p
            else:
                p_values[var] = np.nan
                
        # Graficar p-values de los contaminantes
        plt.figure(figsize=(10,6))
        # Sort values
        sorted_p = dict(sorted(p_values.items(), key=lambda item: item[1]))
        vars_sorted = list(sorted_p.keys())
        vals_sorted = list(sorted_p.values())
        
        colors = ['red' if p < 0.05 else 'gray' for p in vals_sorted]
        sns.barplot(x=vals_sorted, y=vars_sorted, palette=colors)
        plt.axvline(0.05, color='orange', linestyle='--', linewidth=2, label='Umbral Significancia (0.05)')
        plt.title('Valores p (Mann-Whitney U) para Contaminantes vs Detección\n< 0.05 indica que afecta crudamente la detección')
        plt.xlabel('p-value')
        plt.xlim(0, max(1.0, max(vals_sorted) + 0.1) if max(vals_sorted) + 0.1 <= 1 else 1.0)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(PLOT_DIR, 'pvalues_mannwhitney.png'))
        plt.close()
            
        # 2. Variables de Esfuerzo de Muestreo (Numéricas - Mann-Whitney U)
        f.write("\n--- VARIABLES DE ESFUERZO HUMANO (Mann-Whitney U) ---\n")
        for var in ['DURATION MINUTES', 'EFFORT DISTANCE KM', 'NUMBER OBSERVERS']:
            group0 = df[df['y_copeton']==0][var].dropna()
            group1 = df[df['y_copeton']==1][var].dropna()
            if len(group0) > 0 and len(group1) > 0:
                stat, p = mannwhitneyu(group0, group1, alternative='two-sided')
                f.write(f"{var}: p-value = {p:.4f} -> {'SIGNIFICATIVO' if p < 0.05 else 'No significativo'}\n")
                
        # 3. Variables Categóricas (Chi-Cuadrado)
        f.write("\n--- VARIABLES CATEGÓRICAS vs y_copeton (Chi-Cuadrado) ---\n")
        for var in ['PROTOCOL NAME', 'month', 'nearest_station']:
            contingency_table = pd.crosstab(df['y_copeton'], df[var])
            stat, p, dof, expected = chi2_contingency(contingency_table)
            f.write(f"{var}: p-value = {p:.4f} -> {'SIGNIFICATIVO' if p < 0.05 else 'No significativo'}\n")

if __name__ == "__main__":
    run_tests()
