/**
 * @file kernels.hpp
 * @brief Convolution kernel definitions for image filtering
 * @author Muhammad Bilal (2023394)
 * @course CS-361L - Computer Architecture Lab
 */

#ifndef KERNELS_HPP
#define KERNELS_HPP

#include <vector>
#include <string>
#include <cmath>

namespace kernels {

/**
 * @brief Convolution kernel structure
 */
struct Kernel {
    std::vector<float> data;
    int size;           // Kernel is size x size
    float divisor;      // Normalization divisor
    std::string name;

    Kernel() : size(0), divisor(1.0f) {}

    Kernel(const std::vector<float>& d, int s, float div = 1.0f, const std::string& n = "")
        : data(d), size(s), divisor(div), name(n) {}

    float at(int x, int y) const {
        return data[y * size + x];
    }

    int radius() const {
        return size / 2;
    }
};

// ============================================================================
// 3x3 Kernels
// ============================================================================

/**
 * @brief Box blur (average) 3x3 kernel
 * Smooths image by averaging neighboring pixels
 */
inline Kernel box_blur_3x3() {
    return Kernel(
        {1, 1, 1,
         1, 1, 1,
         1, 1, 1},
        3, 9.0f, "Box Blur 3x3"
    );
}

/**
 * @brief Gaussian-like blur 3x3 kernel
 * Weighted average favoring center pixels
 */
inline Kernel gaussian_blur_3x3() {
    return Kernel(
        {1, 2, 1,
         2, 4, 2,
         1, 2, 1},
        3, 16.0f, "Gaussian Blur 3x3"
    );
}

/**
 * @brief Sharpening 3x3 kernel
 * Enhances edges and fine details
 */
inline Kernel sharpen_3x3() {
    return Kernel(
        { 0, -1,  0,
         -1,  5, -1,
          0, -1,  0},
        3, 1.0f, "Sharpen 3x3"
    );
}

/**
 * @brief Strong sharpening 3x3 kernel
 * More aggressive edge enhancement
 */
inline Kernel sharpen_strong_3x3() {
    return Kernel(
        {-1, -1, -1,
         -1,  9, -1,
         -1, -1, -1},
        3, 1.0f, "Strong Sharpen 3x3"
    );
}

/**
 * @brief Sobel X gradient kernel (horizontal edges)
 * Detects vertical edges in the image
 */
inline Kernel sobel_x_3x3() {
    return Kernel(
        {-1, 0, 1,
         -2, 0, 2,
         -1, 0, 1},
        3, 1.0f, "Sobel X"
    );
}

/**
 * @brief Sobel Y gradient kernel (vertical edges)
 * Detects horizontal edges in the image
 */
inline Kernel sobel_y_3x3() {
    return Kernel(
        {-1, -2, -1,
          0,  0,  0,
          1,  2,  1},
        3, 1.0f, "Sobel Y"
    );
}

/**
 * @brief Prewitt X gradient kernel
 * Alternative edge detection kernel
 */
inline Kernel prewitt_x_3x3() {
    return Kernel(
        {-1, 0, 1,
         -1, 0, 1,
         -1, 0, 1},
        3, 1.0f, "Prewitt X"
    );
}

/**
 * @brief Prewitt Y gradient kernel
 * Alternative edge detection kernel
 */
inline Kernel prewitt_y_3x3() {
    return Kernel(
        {-1, -1, -1,
          0,  0,  0,
          1,  1,  1},
        3, 1.0f, "Prewitt Y"
    );
}

/**
 * @brief Laplacian edge detection kernel
 * Detects edges in all directions
 */
inline Kernel laplacian_3x3() {
    return Kernel(
        {0,  1, 0,
         1, -4, 1,
         0,  1, 0},
        3, 1.0f, "Laplacian"
    );
}

/**
 * @brief Emboss effect kernel
 * Creates a 3D embossed effect
 */
inline Kernel emboss_3x3() {
    return Kernel(
        {-2, -1, 0,
         -1,  1, 1,
          0,  1, 2},
        3, 1.0f, "Emboss"
    );
}

/**
 * @brief Identity kernel (no change)
 * Useful for testing
 */
inline Kernel identity_3x3() {
    return Kernel(
        {0, 0, 0,
         0, 1, 0,
         0, 0, 0},
        3, 1.0f, "Identity"
    );
}

// ============================================================================
// 5x5 Kernels
// ============================================================================

/**
 * @brief Box blur 5x5 kernel
 * Stronger smoothing effect
 */
inline Kernel box_blur_5x5() {
    return Kernel(
        {1, 1, 1, 1, 1,
         1, 1, 1, 1, 1,
         1, 1, 1, 1, 1,
         1, 1, 1, 1, 1,
         1, 1, 1, 1, 1},
        5, 25.0f, "Box Blur 5x5"
    );
}

/**
 * @brief Gaussian blur 5x5 kernel
 * Approximation of Gaussian distribution
 */
inline Kernel gaussian_blur_5x5() {
    return Kernel(
        {1,  4,  6,  4, 1,
         4, 16, 24, 16, 4,
         6, 24, 36, 24, 6,
         4, 16, 24, 16, 4,
         1,  4,  6,  4, 1},
        5, 256.0f, "Gaussian Blur 5x5"
    );
}

/**
 * @brief Unsharp mask 5x5 kernel
 * Sharpening via Gaussian subtraction
 */
inline Kernel unsharp_mask_5x5() {
    return Kernel(
        {-1, -4,  -6, -4, -1,
         -4, -16, -24, -16, -4,
         -6, -24, 476, -24, -6,
         -4, -16, -24, -16, -4,
         -1, -4,  -6, -4, -1},
        5, 256.0f, "Unsharp Mask 5x5"
    );
}

/**
 * @brief Sobel X 5x5 kernel (enhanced)
 * Larger receptive field for edge detection
 */
inline Kernel sobel_x_5x5() {
    return Kernel(
        {-1, -2, 0, 2, 1,
         -4, -8, 0, 8, 4,
         -6, -12, 0, 12, 6,
         -4, -8, 0, 8, 4,
         -1, -2, 0, 2, 1},
        5, 1.0f, "Sobel X 5x5"
    );
}

/**
 * @brief Sobel Y 5x5 kernel (enhanced)
 */
inline Kernel sobel_y_5x5() {
    return Kernel(
        {-1, -4, -6, -4, -1,
         -2, -8, -12, -8, -2,
          0,  0,  0,  0,  0,
          2,  8, 12,  8,  2,
          1,  4,  6,  4,  1},
        5, 1.0f, "Sobel Y 5x5"
    );
}

/**
 * @brief Laplacian of Gaussian (LoG) 5x5 kernel
 * Combined smoothing and edge detection
 */
inline Kernel log_5x5() {
    return Kernel(
        {0,  0, -1,  0, 0,
         0, -1, -2, -1, 0,
        -1, -2, 16, -2, -1,
         0, -1, -2, -1, 0,
         0,  0, -1,  0, 0},
        5, 1.0f, "LoG 5x5"
    );
}

// ============================================================================
// Kernel Factory
// ============================================================================

/**
 * @brief Get kernel by name
 * @param name Kernel name (case-insensitive)
 * @return Corresponding kernel
 */
Kernel get_kernel_by_name(const std::string& name);

/**
 * @brief List all available kernel names
 * @return Vector of kernel names
 */
std::vector<std::string> list_kernels();

} // namespace kernels

#endif // KERNELS_HPP
