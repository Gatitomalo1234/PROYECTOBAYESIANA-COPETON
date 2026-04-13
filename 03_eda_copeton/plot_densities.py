import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'copeton_occupancy_ready.csv')
PLOT_DIR = os.path.join(BASE_DIR, '03_eda_copeton', 'plots')
os.makedirs(PLOT_DIR, exist_ok=True)

def plot_densities():
    df = pd.read_csv(DATA_FILE)
    
    # Set up the matplotlib figure
    f, axes = plt.subplots(1, 3, figsize=(15, 5))
    f.suptitle('Histogramas y Curvas de Densidad (KDE) - Variables Seleccionadas', fontsize=16)

    # Plot PM10
    sns.histplot(df['pm10_ugm3'].dropna(), kde=True, color="skyblue", ax=axes[0], stat="density")
    axes[0].set_title('Material Particulado (PM10)')
    axes[0].set_xlabel('PM10 (µg/m³)')
    
    # Plot O3
    sns.histplot(df['o3_ppb'].dropna(), kde=True, color="olive", ax=axes[1], stat="density")
    axes[1].set_title('Ozono (O3)')
    axes[1].set_xlabel('O3 (ppb)')
    
    # Plot DURATION MINUTES
    sns.histplot(df['DURATION MINUTES'].dropna(), kde=True, color="gold", ax=axes[2], stat="density")
    axes[2].set_title('Esfuerzo: Duración Muestreo')
    axes[2].set_xlabel('Minutos')
    
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, 'density_plots.png'))
    plt.close()

if __name__ == "__main__":
    plot_densities()
