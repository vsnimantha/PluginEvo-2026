import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

def plot_line_chart(x, y, save_path):
    plt.figure(figsize=(12,6))
    plt.plot(x, y, marker="o", linestyle="-", color="blue")
    plt.title("Line Chart: Index vs Fitness")
    plt.xlabel("Index")
    plt.ylabel("Fitness")
    plt.grid(True)
    plt.savefig(os.path.join(save_path, "line_chart.png"))
    plt.close()

def plot_scatter(x, y, save_path):
    plt.figure(figsize=(12,6))
    plt.scatter(x, y, color="green", alpha=0.6)
    plt.title("Scatter Plot: Index vs Fitness")
    plt.xlabel("Index")
    plt.ylabel("Fitness")
    plt.grid(True)
    plt.savefig(os.path.join(save_path, "scatter_plot.png"))
    plt.close()

def plot_histogram(y, save_path):
    plt.figure(figsize=(10,6))
    sns.histplot(y, bins=20, kde=True, color="purple")
    plt.title("Histogram: Distribution of Fitness Values")
    plt.xlabel("Fitness")
    plt.ylabel("Frequency")
    plt.savefig(os.path.join(save_path, "histogram.png"))
    plt.close()

def plot_boxplot(y, save_path):
    plt.figure(figsize=(6,8))
    sns.boxplot(y=y, color="orange")
    plt.title("Boxplot: Fitness Value Spread")
    plt.ylabel("Fitness")
    plt.savefig(os.path.join(save_path, "boxplot.png"))
    plt.close()

def plot_scatter_with_avg(x, y, save_path):
    plt.figure(figsize=(12,6))
    plt.scatter(x, y, color="green", alpha=0.6, label="Fitness")
    avg = sum(y)/len(y)
    plt.axhline(avg, color="red", linestyle="--", label=f"Average = {avg:.2f}")
    plt.title("Scatter Plot: Index vs Fitness (with Average)")
    plt.xlabel("Index")
    plt.ylabel("Fitness")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(save_path, "scatter_with_avg.png"))
    plt.close()


def plot_growth_line_chart(x, y, save_path):
    # Sort by fitness values
    sorted_pairs = sorted(zip(x, y), key=lambda p: p[1])
    sorted_x, sorted_y = zip(*sorted_pairs)

    plt.figure(figsize=(12,6))
    plt.plot(sorted_x, sorted_y, marker="o", linestyle="-", color="blue")
    plt.title("Growth Line Chart: Fitness from Low to High")
    plt.xlabel("Index (sorted by fitness)")
    plt.ylabel("Fitness")
    plt.grid(True)
    plt.savefig(os.path.join(save_path, "growth_line_chart.png"))
    plt.close()



def generate_charts_from_json(json_path, save_dir,chart_mode="Generation_All"):
    # Load JSON data
    with open(json_path, "r") as f:
        data = json.load(f)
    
    if chart_mode=="Generation_Single":
        indices = [item["index"] for item in data]
        fitness = [float(item["fitness"]) for item in data]
    elif chart_mode=="Generation_All":
        indices = [item["generation"] for item in data]
        fitness = [float(item["best_fitness"]) for item in data]

    plot_dir=os.path.join(
        save_dir,
        "charts"
    )
    os.makedirs(plot_dir, exist_ok=True)

    # Generate charts
    plot_line_chart(indices, fitness, plot_dir)
    plot_scatter(indices, fitness, plot_dir)
    plot_scatter_with_avg(indices, fitness, plot_dir)
    plot_histogram(fitness, plot_dir)
    plot_boxplot(fitness, plot_dir)


    

if __name__ == "__main__":
    # Example usage
    gdir = "/home/nimantha/Desktop/KU_Leuven_App_Gen/GP-Feedback-Analyser/seeds/run_1764839467/run_20251204_101135/"
    ranked_path="/home/nimantha/Desktop/KU_Leuven_App_Gen/GP-Feedback-Analyser/seeds/run_1764839467/run_20251204_101135/generation_log.json"

    generate_charts_from_json(ranked_path, gdir)



# python3 -m src.common.chart_generator