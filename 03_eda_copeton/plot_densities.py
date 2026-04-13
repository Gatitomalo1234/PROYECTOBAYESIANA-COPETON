import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'copeton_occupancy_ready.csv')
PLOT_DIR = os.path.join(BASE_DIR, '03_eda_copeton', 'plots')
os.makedirs(PLOT_DIR, exist_ok=True)

def plot_all_densities():
    df = pd.read_csv(DATA_FILE)
    
    # Lista de todas las variables
    variables = [
        'pm10_ugm3', 'pm25_ugm3', 'co_ppm', 'no2_ppb', 
        'o3_ppb', 'so2_ugm3', 'DURATION MINUTES', 'EFFORT DISTANCE KM'
    ]
    
    titles = [
        'PM10 (µg/m³)', 'PM2.5 (µg/m³)', 'CO (ppm)', 'NO2 (ppb)',
        'O3 (ppb)', 'SO2 (µg/m³)', 'Minutos de Muestreo', 'Distancia Caminada (Km)'
    ]
    
    colors = ['skyblue', 'salmon', 'lightgreen', 'orange', 'purple', 'gray', 'gold', 'teal']
    
    f, axes = plt.subplots(2, 4, figsize=(20, 10))
    f.suptitle('Histogramas y Curvas de Densidad (KDE) - Análisis Exploratorio Completo', fontsize=20, y=1.02)
    
    axes = axes.flatten()
    
    for i, var in enumerate(variables):
        data = df[var].dropna()
        if len(data) > 0:
            sns.histplot(data, kde=True, color=colors[i], ax=axes[i], stat="density")
        axes[i].set_title(titles[i])
        axes[i].set_xlabel('')
        axes[i].set_ylabel('Densidad')
        
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, 'density_plots_all.png'), bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    plot_all_densities()
