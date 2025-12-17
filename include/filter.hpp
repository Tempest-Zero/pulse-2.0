/**
 * @file filter.hpp
 * @brief Serial and OpenMP parallel image filtering functions
 * @author Muhammad Bilal (2023394)
 * @course CS-361L - Computer Architecture Lab
 */

#ifndef FILTER_HPP
#define FILTER_HPP

#include "image.hpp"
#include "kernels.hpp"
#include <omp.h>

namespace filter {

// ============================================================================
// Configuration
// ============================================================================

/**
 * @brief OpenMP scheduling strategy
 */
enum class Schedule {
    STATIC,
    DYNAMIC,
    GUIDED
};

/**
 * @brief Filter configuration options
 */
struct FilterConfig {
    int num_threads = 0;          // 0 = use OMP_NUM_THREADS or max available
    Schedule schedule = Schedule::STATIC;
    int chunk_size = 0;           // 0 = auto (let OpenMP decide)
    bool use_tiling = false;      // Enable cache-aware tiling
    int tile_size = 64;           // Tile size for tiled implementation
};

// ============================================================================
// Serial Filtering
// ============================================================================

/**
 * @brief Apply convolution filter to grayscale image (serial)
 * @param input Source image
 * @param kernel Convolution kernel
 * @return Filtered image
 */
img::GrayscaleImage apply_filter_serial(
    const img::GrayscaleImage& input,
    const kernels::Kernel& kernel
);

/**
 * @brief Apply convolution filter to RGB image (serial)
 * @param input Source image
 * @param kernel Convolution kernel
 * @return Filtered image
 */
img::RGBImage apply_filter_serial(
    const img::RGBImage& input,
    const kernels::Kernel& kernel
);

/**
 * @brief Compute Sobel edge magnitude (serial)
 * @param input Source grayscale image
 * @return Edge magnitude image (0-255 normalized)
 */
img::GrayscaleImage sobel_edge_detection_serial(
    const img::GrayscaleImage& input
);

// ============================================================================
// OpenMP Parallel Filtering
// ============================================================================

/**
 * @brief Apply convolution filter to grayscale image (parallel)
 * @param input Source image
 * @param kernel Convolution kernel
 * @param config OpenMP configuration
 * @return Filtered image
 */
img::GrayscaleImage apply_filter_parallel(
    const img::GrayscaleImage& input,
    const kernels::Kernel& kernel,
    const FilterConfig& config = FilterConfig()
);

/**
 * @brief Apply convolution filter to RGB image (parallel)
 * @param input Source image
 * @param kernel Convolution kernel
 * @param config OpenMP configuration
 * @return Filtered image
 */
img::RGBImage apply_filter_parallel(
    const img::RGBImage& input,
    const kernels::Kernel& kernel,
    const FilterConfig& config = FilterConfig()
);

/**
 * @brief Compute Sobel edge magnitude (parallel)
 * @param input Source grayscale image
 * @param config OpenMP configuration
 * @return Edge magnitude image
 */
img::GrayscaleImage sobel_edge_detection_parallel(
    const img::GrayscaleImage& input,
    const FilterConfig& config = FilterConfig()
);

/**
 * @brief Apply filter with cache-aware tiling (parallel)
 * @param input Source image
 * @param kernel Convolution kernel
 * @param config OpenMP configuration (tile_size used)
 * @return Filtered image
 */
img::GrayscaleImage apply_filter_tiled(
    const img::GrayscaleImage& input,
    const kernels::Kernel& kernel,
    const FilterConfig& config = FilterConfig()
);

// ============================================================================
// Multi-pass Filtering
// ============================================================================

/**
 * @brief Apply multiple filters in sequence (serial)
 * @param input Source image
 * @param kernel_names List of kernel names to apply
 * @return Final filtered image
 */
img::GrayscaleImage apply_filter_chain_serial(
    const img::GrayscaleImage& input,
    const std::vector<std::string>& kernel_names
);

/**
 * @brief Apply multiple filters in sequence (parallel)
 * @param input Source image
 * @param kernel_names List of kernel names to apply
 * @param config OpenMP configuration
 * @return Final filtered image
 */
img::GrayscaleImage apply_filter_chain_parallel(
    const img::GrayscaleImage& input,
    const std::vector<std::string>& kernel_names,
    const FilterConfig& config = FilterConfig()
);

// ============================================================================
// Statistics (with OpenMP reductions)
// ============================================================================

/**
 * @brief Compute image statistics using OpenMP reduction
 * @param img Input grayscale image
 * @param[out] min_val Minimum pixel value
 * @param[out] max_val Maximum pixel value
 * @param[out] mean Mean pixel value
 * @param[out] variance Pixel variance
 */
void compute_statistics_parallel(
    const img::GrayscaleImage& img,
    double& min_val,
    double& max_val,
    double& mean,
    double& variance
);

/**
 * @brief Compute histogram using OpenMP (with privatization)
 * @param img Input grayscale image
 * @return Histogram array of 256 bins
 */
std::vector<int> compute_histogram_parallel(
    const img::GrayscaleImage& img
);

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * @brief Get schedule name as string
 */
std::string schedule_to_string(Schedule s);

/**
 * @brief Parse schedule from string
 */
Schedule string_to_schedule(const std::string& s);

/**
 * @brief Get number of available threads
 */
int get_max_threads();

/**
 * @brief Set number of threads
 */
void set_num_threads(int n);

} // namespace filter

#endif // FILTER_HPP
