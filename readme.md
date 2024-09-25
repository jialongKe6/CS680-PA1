# README_Student

**Name**: Jialong Ke

**Collaborators**: None

**Class**: CS680

**Assignment Number**: PA1

## Brief Summary

In this assignment, I implemented two primary rendering functions in `Sketch.py`: `drawLine()` and `drawTriangle()`. These functions fulfill the requirements specified for PA1, including line drawing using Bresenham’s algorithm, triangle rendering without using barycentric coordinates, anti-aliasing techniques, and texture mapping for triangles.

### `drawLine()`

- **Bresenham’s Algorithm**: Implemented integer-based calculations to draw lines between two points without using floating-point arithmetic for point positions.

- **Smooth Color Interpolation**: When `doSmooth` is `True`, the function interpolates the RGB color components linearly along the line using floating-point arithmetic for colors.

- **Flat Shading**: If `doSmooth` is `False`, the line is drawn using the color of the first vertex (`p1`).

- **Anti-Aliasing**: Implemented an anti-aliasing method controlled by `doAA` and `doAAlevel`. The `applyAntiAliasing()` function blends the line color with neighboring pixels based on the anti-aliasing level to reduce aliasing effects.

#### Variables and Data Structures

- `x1, y1, x2, y2`: Coordinates of the line endpoints.
- `dx, dy`: Absolute differences in x and y coordinates.
- `x_inc, y_inc`: Increments for x and y based on the line direction.
- `d, incrE, incrNE`: Decision variables for Bresenham's algorithm.
- `is_steep`: Boolean to determine if the line is steep (slope > 1) for efficient iteration.
- `color_step`: The incremental change in color for smooth shading.
- **Internal Function**:
  - `applyAntiAliasing(buff, x, y, r, g, b, aa_level)`: Blends the current pixel color with neighboring pixels.

#### Error Conditions and Handling

- **Zero-Length Line**: Handled by checking if `dx == 0` and `dy == 0` and drawing a single point if true.

### `drawTriangle()`

- **Triangle Filling Using Edge Walking**: Implemented triangle filling by generating edge points using Bresenham's algorithm and filling spans between edges for each scanline.

- **Smooth Color Interpolation**: When `doSmooth` is `True`, the function interpolates colors across the triangle surface using linear interpolation.

- **Flat Shading**: If `doSmooth` is `False`, the triangle is filled with the color of the first vertex (`p0`).

- **Texture Mapping**: When `doTexture` is `True`, the triangle is filled using a texture image. Texture coordinates are mapped from the triangle's bounding box to the texture space.

- **Anti-Aliasing**: Implemented anti-aliasing by calculating barycentric weights and using supersampling techniques controlled by `doAA` and `doAAlevel`.

#### Variables and Data Structures

- `p0, p1, p2`: Triangle vertices sorted by y-coordinate.
- `bresenham_line_points(p_start, p_end, doSmooth)`: Internal function to generate points along the edges using Bresenham's algorithm.
- `edge0, edge1, edge2`: Lists of points along the triangle's edges.
- `edge_points`: Combined list of edge points.
- `y_dict`: Dictionary mapping y-coordinates to lists of edge points.
- **Texture Mapping Variables**:
  - `tex_width`, `tex_height`: Dimensions of the texture.
  - `tri_min_x`, `tri_max_x`, `tri_min_y`, `tri_max_y`: Bounding box of the triangle.
  - `get_texture_color(x, y)`: Function to retrieve the texture color corresponding to screen coordinates.

#### Error Conditions and Handling

- **Degenerate Triangle**: Ensured by checking that the area of the triangle is non-zero before proceeding.
- **Division by Zero**: Prevented by checking denominators before divisions, especially in texture mapping and interpolation calculations.

### Additional Features

- **Texture Mapping**: Implemented texture mapping controlled by the `doTexture` flag. The texture is stored in `self.texture` and mapped to the triangle's bounding box.

- **Anti-Aliasing**: Enhanced anti-aliasing for both lines and triangles by blending pixel colors with neighboring pixels and using supersampling based on `doAAlevel`.

- **Edge Walking for Triangle Filling**: Used Bresenham's algorithm to generate edge points and filled the triangle by drawing horizontal spans between the edges.

- **Binding Functions to Mouse Events**: `drawLine()` is bound to the left mouse button, and `drawTriangle()` is bound to the right mouse button, replacing the default point drawing method.

### Implementation Details

#### `drawLine()` Function

- **Algorithm Steps**:
  1. Initialize variables based on the coordinates of `p1` and `p2`.
  2. Determine if the line is steep to optimize iteration.
  3. Use Bresenham's algorithm to calculate the line path.
  4. If `doSmooth` is `True`, interpolate the color along the line.
  5. If `doAA` is `True`, apply anti-aliasing by blending with neighboring pixels.
  6. Draw each point using the calculated coordinates and color.

- **Anti-Aliasing Technique**:
  - The `applyAntiAliasing()` function blends the color of the current pixel with its neighbors based on the anti-aliasing level (`doAAlevel`).
  - This reduces the jagged edges by smoothing the transition between the line and the background.

#### `drawTriangle()` Function

- **Algorithm Steps**:
  1. Sort the triangle vertices (`p0`, `p1`, `p2`) by their y-coordinates.
  2. Generate edge points using `bresenham_line_points()` for each edge of the triangle.
  3. Combine edge points and organize them by scanlines using `y_dict`.
  4. For each scanline, determine the span between the left and right edges.
  5. If `doSmooth` or `doTexture` is `True`, interpolate the color or apply texture mapping.
  6. If `doAA` is `True`, calculate barycentric weights and apply supersampling for anti-aliasing.
  7. Draw each point within the span using the calculated color.

- **Texture Mapping**:
  - Maps the texture coordinates from the triangle's bounding box to the texture image.
  - Uses linear interpolation to determine the texture color for each pixel within the triangle.

- **Anti-Aliasing Technique**:
  - Uses supersampling by calculating barycentric weights for more accurate color blending.
  - Reduces aliasing artifacts along the edges of the triangle.
