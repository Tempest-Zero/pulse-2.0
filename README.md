# OpenMP-Accelerated Image Filtering and Edge Detection

**CS-361L - Computer Architecture & Parallel Programming Laboratory**
**Fall 2025**

**Author:** Muhammad Bilal (2023394)

## Project Overview

This project implements an OpenMP-parallel image filtering pipeline that demonstrates multi-core performance optimization and shared-memory parallelism. The application supports grayscale and RGB image processing with various convolution filters including blur, sharpen, and edge detection.

### Features

- **Multiple Convolution Kernels:**
  - Box blur (3x3, 5x5)
  - Gaussian blur (3x3, 5x5)
  - Sharpening filters
  - Sobel edge detection (X, Y, combined magnitude)
  - Prewitt edge detection
  - Laplacian edge detection
  - Emboss effect
  - Unsharp mask

- **Parallelization Options:**
  - Serial baseline implementation
  - OpenMP parallel implementation
  - Multiple scheduling strategies (static, dynamic, guided)
  - Configurable thread counts and chunk sizes
  - Cache-aware tiled implementation

- **Image Format Support:**
  - PGM (Portable GrayMap) - grayscale
  - PPM (Portable PixelMap) - RGB color

- **Benchmarking Suite:**
  - Automated performance testing
  - Speedup and efficiency measurements
  - CSV export for analysis
  - Python visualization scripts

## Prerequisites

### Required
- GCC 7+ or Clang 6+ with C++17 support
- OpenMP support (included with GCC/Clang)
- GNU Make

### Optional (for plotting)
- Python 3.6+
- matplotlib
- pandas
- numpy

## Project Setup

### 1. Clone and Build

```bash
# Navigate to project directory
cd pulse-2.0

# Build the project (release mode)
make

# Or build debug version
make debug

# Verify build
./bin/image_filter --help
```

### 2. Verify OpenMP Installation

```bash
# Check compiler supports OpenMP
echo | g++ -fopenmp -dM -E - | grep _OPENMP

# Should output something like:
# #define _OPENMP 201511
```

### 3. Generate Test Images

```bash
# Generate sample test images
make generate-tests

# This creates various test patterns in data/input/
```

### 4. Install Python Dependencies (Optional)

```bash
# For visualization
pip install matplotlib pandas numpy
```

## Usage

### Basic Usage

```bash
# Apply Gaussian blur to an image
./bin/image_filter -i input.pgm -o output.pgm -f gaussian

# Apply edge detection
./bin/image_filter -i photo.pgm -o edges.pgm -f sobel

# Generate and process test image
./bin/image_filter --generate 1024x1024 --pattern 1 -f sharpen -o sharp.pgm
```

### Parallel Execution Options

```bash
# Specify number of threads
./bin/image_filter -i input.pgm -o output.pgm -f blur -t 8

# Use dynamic scheduling
./bin/image_filter -i input.pgm -o output.pgm -f gaussian -s dynamic

# Use tiled implementation
./bin/image_filter -i input.pgm -o output.pgm -f blur --tiled --tile-size 64

# Compare serial vs parallel
./bin/image_filter -i input.pgm -f blur --compare
```

### Running Benchmarks

```bash
# Run full benchmark suite
make benchmark
# or
./bin/image_filter -b

# Generate plots from results
make plots
# or
python3 scripts/plot_results.py
```

### Quick Tests

```bash
# Quick functionality test
make quick-test

# Test all filter types
make test-filters

# Test thread scaling
make test-scaling

# Test scheduling strategies
make test-schedules
```

## Command-Line Options

| Option | Description |
|--------|-------------|
| `-i, --input <file>` | Input image file (PGM/PPM) |
| `-o, --output <file>` | Output image file |
| `-f, --filter <name>` | Filter to apply (see list below) |
| `-t, --threads <n>` | Number of threads (default: auto) |
| `-s, --schedule <type>` | OpenMP schedule: static, dynamic, guided |
| `-c, --chunk <size>` | Chunk size for scheduling |
| `--tiled` | Use cache-aware tiled implementation |
| `--tile-size <n>` | Tile size (default: 64) |
| `--serial` | Run serial implementation only |
| `--compare` | Compare serial vs parallel execution |
| `-b, --benchmark` | Run full benchmark suite |
| `--generate <WxH>` | Generate test image |
| `--pattern <n>` | Test pattern (0-4) |
| `-l, --list` | List available filters |
| `-h, --help` | Show help message |

## Available Filters

### 3x3 Kernels
- `blur`, `box_blur` - Box blur (average)
- `gaussian` - Gaussian blur
- `sharpen` - Sharpening
- `sharpen_strong` - Strong sharpening
- `sobel_x` - Sobel X gradient
- `sobel_y` - Sobel Y gradient
- `prewitt_x` - Prewitt X gradient
- `prewitt_y` - Prewitt Y gradient
- `laplacian` - Laplacian edge detection
- `emboss` - Emboss effect

### 5x5 Kernels
- `box_blur_5x5` - Larger box blur
- `gaussian_5x5` - Larger Gaussian blur
- `unsharp_mask` - Unsharp mask sharpening
- `sobel_x_5x5` - Enhanced Sobel X
- `sobel_y_5x5` - Enhanced Sobel Y
- `log_5x5` - Laplacian of Gaussian

### Special
- `sobel`, `edges` - Combined Sobel magnitude

## Project Structure

```
pulse-2.0/
├── include/           # Header files
│   ├── image.hpp      # Image data structures and I/O
│   ├── kernels.hpp    # Convolution kernel definitions
│   ├── filter.hpp     # Serial and parallel filter functions
│   └── benchmark.hpp  # Benchmarking utilities
├── src/               # Source files
│   ├── image.cpp      # Image I/O implementation
│   ├── kernels.cpp    # Kernel factory
│   ├── filter.cpp     # Filter implementations
│   ├── benchmark.cpp  # Benchmark utilities
│   └── main.cpp       # Main program entry
├── data/              # Data directory
│   ├── input/         # Input images
│   └── output/        # Processed images
├── scripts/           # Helper scripts
│   └── plot_results.py # Benchmark visualization
├── docs/              # Documentation
├── tests/             # Test files
├── Makefile           # Build system
└── README.md          # This file
```

## Performance Analysis

### Key Metrics

- **Speedup**: `T_serial / T_parallel`
- **Efficiency**: `Speedup / Number_of_threads`
- **Throughput**: Megapixels processed per second

### Expected Results

On a typical multi-core system:
- Near-linear speedup for large images (>1024x1024)
- Best performance with static scheduling for uniform workloads
- Dynamic scheduling helps with variable workloads
- Tiled implementation improves cache locality for large images

### Factors Affecting Performance

1. **Image Size**: Larger images provide more parallelism
2. **Kernel Size**: Larger kernels have more compute per pixel
3. **Thread Count**: Diminishing returns beyond physical cores
4. **Scheduling**: Static is fastest for uniform work
5. **Cache Effects**: Tiling improves locality for large images

## Troubleshooting

### Build Issues

```bash
# If OpenMP not found
sudo apt-get install libomp-dev  # Ubuntu/Debian
# or
brew install libomp              # macOS

# Check compiler version
g++ --version

# Clean and rebuild
make clean && make
```

### Runtime Issues

```bash
# Set thread count explicitly
export OMP_NUM_THREADS=4
./bin/image_filter -i input.pgm -o output.pgm -f blur

# Check available threads
./bin/image_filter --generate 100x100 -f identity --compare
```

## License

This project is developed for educational purposes as part of CS-361L coursework.

## References

- OpenMP Specification: https://www.openmp.org/specifications/
- PGM/PPM Format: http://netpbm.sourceforge.net/doc/pgm.html
- Image Processing Fundamentals: Digital Image Processing (Gonzalez & Woods)
