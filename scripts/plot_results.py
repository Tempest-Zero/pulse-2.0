#!/usr/bin/env python3
"""
Benchmark Results Visualization Script
CS-361L Computer Architecture Lab
Author: Muhammad Bilal (2023394)

Generates plots for:
- Speedup vs. number of threads
- Efficiency vs. number of threads
- Scheduling strategy comparison
- Image size scaling
- Throughput analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Plot style configuration
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
FIG_SIZE = (10, 6)
DPI = 150


def load_results(filename='benchmark_results.csv'):
    """Load benchmark results from CSV file."""
    if not os.path.exists(filename):
        print(f"Error: {filename} not found. Run 'make benchmark' first.")
        sys.exit(1)

    df = pd.read_csv(filename)
    print(f"Loaded {len(df)} benchmark results from {filename}")
    return df


def plot_speedup_vs_threads(df, output_dir='plots'):
    """Plot speedup vs number of threads for different filters."""
    os.makedirs(output_dir, exist_ok=True)

    # Filter parallel results only
    parallel_df = df[df['name'] == 'Parallel']

    # Get unique image sizes
    sizes = parallel_df.groupby(['width', 'height']).size().reset_index()[['width', 'height']]

    for _, row in sizes.iterrows():
        w, h = row['width'], row['height']
        size_df = parallel_df[(parallel_df['width'] == w) & (parallel_df['height'] == h)]

        fig, ax = plt.subplots(figsize=FIG_SIZE)

        filters = size_df['filter'].unique()
        for i, filt in enumerate(filters):
            filter_df = size_df[size_df['filter'] == filt]
            # Use static schedule for comparison
            static_df = filter_df[filter_df['schedule'] == 'static']
            static_df = static_df.sort_values('threads')

            ax.plot(static_df['threads'], static_df['speedup'],
                   marker='o', color=COLORS[i % len(COLORS)],
                   label=filt, linewidth=2, markersize=8)

        # Ideal speedup line
        max_threads = parallel_df['threads'].max()
        ax.plot([1, max_threads], [1, max_threads], 'k--',
               alpha=0.5, label='Ideal (linear)')

        ax.set_xlabel('Number of Threads', fontsize=12)
        ax.set_ylabel('Speedup', fontsize=12)
        ax.set_title(f'Speedup vs. Thread Count ({w}x{h})', fontsize=14)
        ax.legend(loc='upper left')
        ax.set_xlim(0, max_threads + 1)
        ax.set_ylim(0, max_threads + 1)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        filename = f'{output_dir}/speedup_{w}x{h}.png'
        plt.savefig(filename, dpi=DPI)
        print(f"Saved: {filename}")
        plt.close()


def plot_efficiency_vs_threads(df, output_dir='plots'):
    """Plot parallel efficiency vs number of threads."""
    os.makedirs(output_dir, exist_ok=True)

    parallel_df = df[df['name'] == 'Parallel']
    sizes = parallel_df.groupby(['width', 'height']).size().reset_index()[['width', 'height']]

    for _, row in sizes.iterrows():
        w, h = row['width'], row['height']
        size_df = parallel_df[(parallel_df['width'] == w) & (parallel_df['height'] == h)]

        fig, ax = plt.subplots(figsize=FIG_SIZE)

        filters = size_df['filter'].unique()
        for i, filt in enumerate(filters):
            filter_df = size_df[size_df['filter'] == filt]
            static_df = filter_df[filter_df['schedule'] == 'static']
            static_df = static_df.sort_values('threads')

            efficiency_pct = static_df['efficiency'] * 100
            ax.plot(static_df['threads'], efficiency_pct,
                   marker='s', color=COLORS[i % len(COLORS)],
                   label=filt, linewidth=2, markersize=8)

        ax.axhline(y=100, color='k', linestyle='--', alpha=0.5, label='Ideal (100%)')

        ax.set_xlabel('Number of Threads', fontsize=12)
        ax.set_ylabel('Efficiency (%)', fontsize=12)
        ax.set_title(f'Parallel Efficiency ({w}x{h})', fontsize=14)
        ax.legend(loc='upper right')
        ax.set_ylim(0, 110)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        filename = f'{output_dir}/efficiency_{w}x{h}.png'
        plt.savefig(filename, dpi=DPI)
        print(f"Saved: {filename}")
        plt.close()


def plot_schedule_comparison(df, output_dir='plots'):
    """Compare different OpenMP scheduling strategies."""
    os.makedirs(output_dir, exist_ok=True)

    parallel_df = df[df['name'] == 'Parallel']

    # Use largest image size for comparison
    max_pixels = (parallel_df['width'] * parallel_df['height']).max()
    large_df = parallel_df[parallel_df['width'] * parallel_df['height'] == max_pixels]

    if large_df.empty:
        print("No data for schedule comparison")
        return

    # Get max thread count results
    max_threads = large_df['threads'].max()
    compare_df = large_df[large_df['threads'] == max_threads]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    schedules = ['static', 'dynamic', 'guided']
    filters = compare_df['filter'].unique()

    x = np.arange(len(filters))
    width = 0.25

    for i, sched in enumerate(schedules):
        sched_df = compare_df[compare_df['schedule'] == sched]
        times = [sched_df[sched_df['filter'] == f]['time_ms'].values[0]
                 if len(sched_df[sched_df['filter'] == f]) > 0 else 0
                 for f in filters]
        ax.bar(x + i * width, times, width, label=sched.capitalize(),
               color=COLORS[i])

    ax.set_xlabel('Filter Type', fontsize=12)
    ax.set_ylabel('Execution Time (ms)', fontsize=12)
    w = int(np.sqrt(max_pixels))
    ax.set_title(f'Scheduling Strategy Comparison ({w}x{w}, {max_threads} threads)', fontsize=14)
    ax.set_xticks(x + width)
    ax.set_xticklabels(filters, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    filename = f'{output_dir}/schedule_comparison.png'
    plt.savefig(filename, dpi=DPI)
    print(f"Saved: {filename}")
    plt.close()


def plot_image_size_scaling(df, output_dir='plots'):
    """Plot performance scaling with image size."""
    os.makedirs(output_dir, exist_ok=True)

    # Compare serial vs best parallel for each size
    serial_df = df[df['name'] == 'Serial']
    parallel_df = df[df['name'] == 'Parallel']

    # Get one filter for comparison
    if 'gaussian' in df['filter'].str.lower().values:
        filter_name = df[df['filter'].str.lower().str.contains('gaussian')]['filter'].iloc[0]
    else:
        filter_name = df['filter'].iloc[0]

    serial_filter = serial_df[serial_df['filter'] == filter_name]
    parallel_filter = parallel_df[parallel_df['filter'] == filter_name]

    # Get best parallel time per size (max threads, static schedule)
    max_threads = parallel_filter['threads'].max()
    best_parallel = parallel_filter[
        (parallel_filter['threads'] == max_threads) &
        (parallel_filter['schedule'] == 'static')
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Compute megapixels for x-axis
    serial_filter = serial_filter.copy()
    serial_filter['megapixels'] = serial_filter['width'] * serial_filter['height'] / 1e6
    serial_filter = serial_filter.sort_values('megapixels')

    best_parallel = best_parallel.copy()
    best_parallel['megapixels'] = best_parallel['width'] * best_parallel['height'] / 1e6
    best_parallel = best_parallel.sort_values('megapixels')

    # Execution time plot
    ax1.plot(serial_filter['megapixels'], serial_filter['time_ms'],
            marker='o', color=COLORS[0], label='Serial', linewidth=2, markersize=8)
    ax1.plot(best_parallel['megapixels'], best_parallel['time_ms'],
            marker='s', color=COLORS[1], label=f'Parallel ({max_threads} threads)',
            linewidth=2, markersize=8)

    ax1.set_xlabel('Image Size (Megapixels)', fontsize=12)
    ax1.set_ylabel('Execution Time (ms)', fontsize=12)
    ax1.set_title(f'Execution Time vs. Image Size ({filter_name})', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Speedup plot
    if len(serial_filter) == len(best_parallel):
        merged = pd.merge(serial_filter[['megapixels', 'time_ms']],
                         best_parallel[['megapixels', 'time_ms']],
                         on='megapixels', suffixes=('_serial', '_parallel'))
        merged['speedup'] = merged['time_ms_serial'] / merged['time_ms_parallel']

        ax2.plot(merged['megapixels'], merged['speedup'],
                marker='o', color=COLORS[2], linewidth=2, markersize=8)
        ax2.axhline(y=max_threads, color='k', linestyle='--', alpha=0.5,
                   label=f'Ideal ({max_threads}x)')

    ax2.set_xlabel('Image Size (Megapixels)', fontsize=12)
    ax2.set_ylabel('Speedup', fontsize=12)
    ax2.set_title(f'Speedup vs. Image Size ({max_threads} threads)', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    filename = f'{output_dir}/size_scaling.png'
    plt.savefig(filename, dpi=DPI)
    print(f"Saved: {filename}")
    plt.close()


def plot_throughput(df, output_dir='plots'):
    """Plot throughput (megapixels per second) analysis."""
    os.makedirs(output_dir, exist_ok=True)

    parallel_df = df[df['name'] == 'Parallel']

    # Get results for max image size
    max_pixels = (parallel_df['width'] * parallel_df['height']).max()
    large_df = parallel_df[parallel_df['width'] * parallel_df['height'] == max_pixels]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    filters = large_df['filter'].unique()
    for i, filt in enumerate(filters):
        filter_df = large_df[large_df['filter'] == filt]
        static_df = filter_df[filter_df['schedule'] == 'static']
        static_df = static_df.sort_values('threads')

        ax.plot(static_df['threads'], static_df['throughput_mpps'],
               marker='o', color=COLORS[i % len(COLORS)],
               label=filt, linewidth=2, markersize=8)

    ax.set_xlabel('Number of Threads', fontsize=12)
    ax.set_ylabel('Throughput (MP/s)', fontsize=12)
    w = int(np.sqrt(max_pixels))
    ax.set_title(f'Throughput vs. Thread Count ({w}x{w})', fontsize=14)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    filename = f'{output_dir}/throughput.png'
    plt.savefig(filename, dpi=DPI)
    print(f"Saved: {filename}")
    plt.close()


def plot_tiled_comparison(df, output_dir='plots'):
    """Compare tiled vs non-tiled implementations."""
    os.makedirs(output_dir, exist_ok=True)

    parallel_df = df[df['name'] == 'Parallel']
    tiled_df = df[df['name'] == 'Tiled']

    if tiled_df.empty:
        print("No tiled results to compare")
        return

    # Get max threads results for parallel
    max_threads = parallel_df['threads'].max()
    compare_parallel = parallel_df[
        (parallel_df['threads'] == max_threads) &
        (parallel_df['schedule'] == 'static')
    ]

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    # Group by filter
    filters = compare_parallel['filter'].unique()
    x = np.arange(len(filters))
    width = 0.35

    parallel_times = [compare_parallel[compare_parallel['filter'] == f]['time_ms'].mean()
                      for f in filters]
    tiled_times = [tiled_df[tiled_df['filter'] == f]['time_ms'].mean()
                   if len(tiled_df[tiled_df['filter'] == f]) > 0 else 0
                   for f in filters]

    ax.bar(x - width/2, parallel_times, width, label='Standard Parallel', color=COLORS[0])
    ax.bar(x + width/2, tiled_times, width, label='Tiled (64x64)', color=COLORS[1])

    ax.set_xlabel('Filter Type', fontsize=12)
    ax.set_ylabel('Execution Time (ms)', fontsize=12)
    ax.set_title(f'Tiled vs. Standard Parallel ({max_threads} threads)', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(filters, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    filename = f'{output_dir}/tiled_comparison.png'
    plt.savefig(filename, dpi=DPI)
    print(f"Saved: {filename}")
    plt.close()


def generate_summary_table(df, output_dir='plots'):
    """Generate a summary statistics table."""
    os.makedirs(output_dir, exist_ok=True)

    # Best speedup per configuration
    parallel_df = df[df['name'] == 'Parallel']

    summary = []
    for size in parallel_df.groupby(['width', 'height']).groups:
        w, h = size
        size_df = parallel_df[(parallel_df['width'] == w) & (parallel_df['height'] == h)]

        best = size_df.loc[size_df['speedup'].idxmax()]
        summary.append({
            'Image Size': f'{w}x{h}',
            'Best Filter': best['filter'],
            'Threads': best['threads'],
            'Schedule': best['schedule'],
            'Time (ms)': f"{best['time_ms']:.2f}",
            'Speedup': f"{best['speedup']:.2f}x",
            'Efficiency': f"{best['efficiency']*100:.1f}%",
            'Throughput': f"{best['throughput_mpps']:.1f} MP/s"
        })

    summary_df = pd.DataFrame(summary)

    # Save as markdown table
    with open(f'{output_dir}/summary_table.md', 'w') as f:
        f.write("# Benchmark Summary\n\n")
        f.write(summary_df.to_markdown(index=False))
        f.write("\n")

    print(f"Saved: {output_dir}/summary_table.md")

    # Also print to console
    print("\n" + "="*80)
    print("BENCHMARK SUMMARY")
    print("="*80)
    print(summary_df.to_string(index=False))
    print("="*80)


def main():
    """Main function to generate all plots."""
    print("OpenMP Image Filtering - Benchmark Visualization")
    print("=" * 50)

    # Check for custom CSV file
    csv_file = 'benchmark_results.csv'
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]

    # Load results
    df = load_results(csv_file)

    # Output directory
    output_dir = 'plots'

    # Generate all plots
    print("\nGenerating plots...")
    plot_speedup_vs_threads(df, output_dir)
    plot_efficiency_vs_threads(df, output_dir)
    plot_schedule_comparison(df, output_dir)
    plot_image_size_scaling(df, output_dir)
    plot_throughput(df, output_dir)
    plot_tiled_comparison(df, output_dir)

    # Generate summary
    generate_summary_table(df, output_dir)

    print(f"\nAll plots saved to '{output_dir}/' directory")
    print("Done!")


if __name__ == '__main__':
    main()
