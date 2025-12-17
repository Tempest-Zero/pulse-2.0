/**
 * @file image.hpp
 * @brief Image data structures and I/O operations for PGM/PPM formats
 * @author Muhammad Bilal (2023394)
 * @course CS-361L - Computer Architecture Lab
 */

#ifndef IMAGE_HPP
#define IMAGE_HPP

#include <string>
#include <vector>
#include <cstdint>
#include <stdexcept>

namespace img {

/**
 * @brief Grayscale image class using row-major storage
 */
class GrayscaleImage {
public:
    int width;
    int height;
    int max_val;
    std::vector<uint8_t> data;  // Row-major storage

    GrayscaleImage() : width(0), height(0), max_val(255) {}

    GrayscaleImage(int w, int h, int maxv = 255)
        : width(w), height(h), max_val(maxv), data(w * h, 0) {}

    // Access pixel at (x, y) - bounds checked
    uint8_t& at(int x, int y) {
        if (x < 0 || x >= width || y < 0 || y >= height) {
            throw std::out_of_range("Pixel coordinates out of bounds");
        }
        return data[y * width + x];
    }

    const uint8_t& at(int x, int y) const {
        if (x < 0 || x >= width || y < 0 || y >= height) {
            throw std::out_of_range("Pixel coordinates out of bounds");
        }
        return data[y * width + x];
    }

    // Fast unchecked access for performance-critical code
    uint8_t& pixel(int x, int y) {
        return data[y * width + x];
    }

    const uint8_t& pixel(int x, int y) const {
        return data[y * width + x];
    }

    // Get pixel with boundary clamping (for convolution)
    uint8_t clamped_pixel(int x, int y) const {
        x = std::max(0, std::min(x, width - 1));
        y = std::max(0, std::min(y, height - 1));
        return data[y * width + x];
    }

    size_t size() const { return data.size(); }
    bool empty() const { return data.empty(); }
};

/**
 * @brief RGB image class using interleaved storage (RGBRGBRGB...)
 */
class RGBImage {
public:
    int width;
    int height;
    int max_val;
    std::vector<uint8_t> data;  // Interleaved RGB, row-major

    RGBImage() : width(0), height(0), max_val(255) {}

    RGBImage(int w, int h, int maxv = 255)
        : width(w), height(h), max_val(maxv), data(w * h * 3, 0) {}

    // Access RGB components at (x, y)
    uint8_t& r(int x, int y) { return data[(y * width + x) * 3 + 0]; }
    uint8_t& g(int x, int y) { return data[(y * width + x) * 3 + 1]; }
    uint8_t& b(int x, int y) { return data[(y * width + x) * 3 + 2]; }

    const uint8_t& r(int x, int y) const { return data[(y * width + x) * 3 + 0]; }
    const uint8_t& g(int x, int y) const { return data[(y * width + x) * 3 + 1]; }
    const uint8_t& b(int x, int y) const { return data[(y * width + x) * 3 + 2]; }

    // Get component with boundary clamping
    uint8_t clamped_r(int x, int y) const {
        x = std::max(0, std::min(x, width - 1));
        y = std::max(0, std::min(y, height - 1));
        return data[(y * width + x) * 3 + 0];
    }

    uint8_t clamped_g(int x, int y) const {
        x = std::max(0, std::min(x, width - 1));
        y = std::max(0, std::min(y, height - 1));
        return data[(y * width + x) * 3 + 1];
    }

    uint8_t clamped_b(int x, int y) const {
        x = std::max(0, std::min(x, width - 1));
        y = std::max(0, std::min(y, height - 1));
        return data[(y * width + x) * 3 + 2];
    }

    size_t size() const { return data.size(); }
    bool empty() const { return data.empty(); }
};

// I/O Functions

/**
 * @brief Read a PGM (grayscale) image file
 * @param filename Path to the PGM file
 * @return GrayscaleImage object
 * @throws std::runtime_error if file cannot be read
 */
GrayscaleImage read_pgm(const std::string& filename);

/**
 * @brief Write a PGM (grayscale) image file
 * @param filename Path to output file
 * @param img GrayscaleImage to write
 * @throws std::runtime_error if file cannot be written
 */
void write_pgm(const std::string& filename, const GrayscaleImage& img);

/**
 * @brief Read a PPM (RGB) image file
 * @param filename Path to the PPM file
 * @return RGBImage object
 * @throws std::runtime_error if file cannot be read
 */
RGBImage read_ppm(const std::string& filename);

/**
 * @brief Write a PPM (RGB) image file
 * @param filename Path to output file
 * @param img RGBImage to write
 * @throws std::runtime_error if file cannot be written
 */
void write_ppm(const std::string& filename, const RGBImage& img);

/**
 * @brief Convert RGB image to grayscale
 * @param rgb Source RGB image
 * @return GrayscaleImage using luminosity method
 */
GrayscaleImage rgb_to_grayscale(const RGBImage& rgb);

/**
 * @brief Convert grayscale image to RGB
 * @param gray Source grayscale image
 * @return RGBImage with equal R, G, B values
 */
RGBImage grayscale_to_rgb(const GrayscaleImage& gray);

/**
 * @brief Generate a test pattern image
 * @param width Image width
 * @param height Image height
 * @param pattern Pattern type: 0=gradient, 1=checkerboard, 2=circles
 * @return Generated grayscale image
 */
GrayscaleImage generate_test_image(int width, int height, int pattern = 0);

} // namespace img

#endif // IMAGE_HPP
