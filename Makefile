# ============================================================================
# OpenMP Image Filtering Project - Makefile
# CS-361L Computer Architecture Lab
# Author: Muhammad Bilal (2023394)
# ============================================================================

# Compiler settings
CXX      := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -Wpedantic
OMPFLAGS := -fopenmp
INCLUDES := -Iinclude

# Optimization flags
OPT_DEBUG   := -g -O0 -DDEBUG
OPT_RELEASE := -O3 -march=native -DNDEBUG -funroll-loops -ffast-math

# Directories
SRC_DIR   := src
INC_DIR   := include
BUILD_DIR := build
BIN_DIR   := bin
DATA_DIR  := data

# Source files
SOURCES := $(wildcard $(SRC_DIR)/*.cpp)
OBJECTS := $(SOURCES:$(SRC_DIR)/%.cpp=$(BUILD_DIR)/%.o)
DEPS    := $(OBJECTS:.o=.d)

# Target executable
TARGET := $(BIN_DIR)/image_filter

# Default build type
BUILD_TYPE ?= release

ifeq ($(BUILD_TYPE),debug)
    CXXFLAGS += $(OPT_DEBUG)
else
    CXXFLAGS += $(OPT_RELEASE)
endif

# ============================================================================
# Build targets
# ============================================================================

.PHONY: all clean debug release run benchmark test help dirs

# Default target
all: dirs $(TARGET)

# Create directories
dirs:
	@mkdir -p $(BUILD_DIR) $(BIN_DIR) $(DATA_DIR)/input $(DATA_DIR)/output

# Link executable
$(TARGET): $(OBJECTS)
	@echo "Linking: $@"
	$(CXX) $(CXXFLAGS) $(OMPFLAGS) -o $@ $^

# Compile source files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp
	@echo "Compiling: $<"
	$(CXX) $(CXXFLAGS) $(OMPFLAGS) $(INCLUDES) -MMD -MP -c -o $@ $<

# Include dependency files
-include $(DEPS)

# Debug build
debug:
	$(MAKE) BUILD_TYPE=debug all

# Release build
release:
	$(MAKE) BUILD_TYPE=release all

# Clean build artifacts
clean:
	@echo "Cleaning..."
	rm -rf $(BUILD_DIR) $(BIN_DIR)

# Deep clean (including generated data)
distclean: clean
	rm -f $(DATA_DIR)/input/*.pgm $(DATA_DIR)/output/*.pgm
	rm -f benchmark_results.csv

# ============================================================================
# Run targets
# ============================================================================

# Run with default options
run: all
	@echo "Running image filter..."
	./$(TARGET) --help

# Run benchmark suite
benchmark: all
	@echo "Running benchmark suite..."
	./$(TARGET) -b

# Generate test images
generate-tests: all
	@echo "Generating test images..."
	./$(TARGET) --generate 512x512 --pattern 0 -o $(DATA_DIR)/input/gradient_512.pgm
	./$(TARGET) --generate 512x512 --pattern 1 -o $(DATA_DIR)/input/checker_512.pgm
	./$(TARGET) --generate 512x512 --pattern 2 -o $(DATA_DIR)/input/circles_512.pgm
	./$(TARGET) --generate 1024x1024 --pattern 0 -o $(DATA_DIR)/input/gradient_1024.pgm
	./$(TARGET) --generate 1024x1024 --pattern 1 -o $(DATA_DIR)/input/checker_1024.pgm
	./$(TARGET) --generate 2048x2048 --pattern 4 -o $(DATA_DIR)/input/edges_2048.pgm
	@echo "Test images generated in $(DATA_DIR)/input/"

# Quick test with generated image
quick-test: all
	@echo "Running quick test..."
	./$(TARGET) --generate 1024x1024 --pattern 1 -f gaussian -o $(DATA_DIR)/output/test_blur.pgm --compare

# Test all filters
test-filters: all generate-tests
	@echo "Testing all filters..."
	@for filter in blur gaussian sharpen sobel_x sobel_y laplacian emboss; do \
		echo "Testing $$filter..."; \
		./$(TARGET) -i $(DATA_DIR)/input/checker_512.pgm -o $(DATA_DIR)/output/$$filter.pgm -f $$filter; \
	done
	@echo "Filter outputs saved to $(DATA_DIR)/output/"

# Test different thread counts
test-scaling: all
	@echo "Testing thread scaling..."
	@for threads in 1 2 4 8 16; do \
		echo "\nThreads: $$threads"; \
		./$(TARGET) --generate 2048x2048 -f gaussian -t $$threads --compare 2>/dev/null | grep -E "(Serial|Parallel|Speedup)"; \
	done

# Test different schedules
test-schedules: all
	@echo "Testing scheduling strategies..."
	@for sched in static dynamic guided; do \
		echo "\nSchedule: $$sched"; \
		./$(TARGET) --generate 2048x2048 -f gaussian -s $$sched --compare; \
	done

# ============================================================================
# Analysis targets
# ============================================================================

# Run with perf profiling (Linux)
perf: all
	@echo "Running with perf..."
	perf stat -e cycles,instructions,cache-references,cache-misses \
		./$(TARGET) --generate 2048x2048 -f gaussian -t 8

# Generate plots (requires Python + matplotlib)
plots: benchmark
	@echo "Generating plots..."
	python3 scripts/plot_results.py

# ============================================================================
# Installation
# ============================================================================

PREFIX ?= /usr/local

install: all
	install -d $(PREFIX)/bin
	install -m 755 $(TARGET) $(PREFIX)/bin/

uninstall:
	rm -f $(PREFIX)/bin/image_filter

# ============================================================================
# Help
# ============================================================================

help:
	@echo "OpenMP Image Filtering - Build System"
	@echo "======================================"
	@echo ""
	@echo "Build targets:"
	@echo "  make            - Build release version"
	@echo "  make debug      - Build debug version"
	@echo "  make release    - Build optimized release version"
	@echo "  make clean      - Remove build artifacts"
	@echo "  make distclean  - Remove all generated files"
	@echo ""
	@echo "Run targets:"
	@echo "  make run        - Show help message"
	@echo "  make benchmark  - Run full benchmark suite"
	@echo "  make quick-test - Quick functionality test"
	@echo "  make test-filters  - Test all filter types"
	@echo "  make test-scaling  - Test thread scaling"
	@echo "  make test-schedules - Test scheduling strategies"
	@echo ""
	@echo "Analysis:"
	@echo "  make perf       - Run with perf profiling"
	@echo "  make plots      - Generate benchmark plots"
	@echo ""
	@echo "Data generation:"
	@echo "  make generate-tests - Generate test images"
	@echo ""
	@echo "Options:"
	@echo "  BUILD_TYPE=debug|release (default: release)"
	@echo ""
	@echo "Example usage:"
	@echo "  ./bin/image_filter -i input.pgm -o output.pgm -f gaussian -t 4"
	@echo "  ./bin/image_filter --generate 1024x1024 -f sobel -o edges.pgm"
	@echo "  ./bin/image_filter -b  # Run benchmarks"
