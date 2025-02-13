"""
This is the main entry of your program. Almost all things you need to implement is in this file.
The main class Sketch inherit from CanvasBase. For the parts you need to implement, they all marked TODO.
First version Created on 09/28/2018

:author: micou(Zezhou Sun)
:version: 2021.2.1

"""

import os

import wx
import math
import random
import numpy as np

from Buff import Buff
from Point import Point
from ColorType import ColorType
from CanvasBase import CanvasBase

try:
    # From pip package "Pillow"
    from PIL import Image
except Exception:
    print("Need to install PIL package. Pip package name is Pillow")
    raise ImportError


class Sketch(CanvasBase):
    """
    Please don't forget to override interrupt methods, otherwise NotImplementedError will throw out
    
    Class Variable Explanation:

    * debug(int): Define debug level for log printing

        * 0 for stable version, minimum log is printed
        * 1 will print general logs for lines and triangles
        * 2 will print more details and do some type checking, which might be helpful in debugging
    
    * texture(Buff): loaded texture in Buff instance
    * random_color(bool): Control flag of random color generation of point.
    * doTexture(bool): Control flag of doing texture mapping
    * doSmooth(bool): Control flag of doing smooth
    * doAA(bool): Control flag of doing anti-aliasing
    * doAAlevel(int): anti-alising super sampling level
        
    Method Instruction:

    * Interrupt_MouseL(R): Used to deal with mouse click interruption. Canvas will be refreshed with updated buff
    * Interrupt_Keyboard: Used to deal with key board press interruption. Use this to add new keys or new methods
    * drawPoint: method to draw a point
    * drawLine: method to draw a line
    * drawTriangle: method to draw a triangle with filling and smoothing
    
    List of methods to override the ones in CanvasBase:

    * Interrupt_MouseL
    * Interrupt_MouseR
    * Interrupt_Keyboard
        
    Here are some public variables in parent class you might need:

    * points_r: list<Point>. to store all Points from Mouse Right Button
    * points_l: list<Point>. to store all Points from Mouse Left Button
    * buff    : Buff. buff of current frame. Change on it will change display on screen
    * buff_last: Buff. Last frame buffer
        
    """

    debug = 0
    texture_file_path = "./pattern.jpg"
    texture = None

    # control flags
    randomColor = False
    doTexture = False
    doSmooth = False
    doAA = False
    doAAlevel = 4

    # test case status
    MIN_N_STEPS = 6
    MAX_N_STEPS = 192
    n_steps = 12  # For test case only
    test_case_index = 0
    test_case_list = []  # If you need more test case, write them as a method and add it to list

    def __init__(self, parent):
        """
        Initialize the instance, load texture file to Buff, and load test cases.

        :param parent: wxpython frame
        :type parent: wx.Frame
        """
        super(Sketch, self).__init__(parent)
        self.test_case_list = [lambda _: self.clear(),
                               self.testCaseLine01,
                               self.testCaseLine02,
                               self.testCaseTri01,
                               self.testCaseTri02,
                               self.testCaseTriTexture01]  # method at here must accept one argument, n_steps
        # Try to read texture file
        if os.path.isfile(self.texture_file_path):
            # Read image and make it to an ndarray
            texture_image = Image.open(self.texture_file_path)
            texture_array = np.array(texture_image).astype(np.uint8)
            # Because imported image is upside down, reverse it
            texture_array = np.flip(texture_array, axis=0)
            # Store texture image in our Buff format
            self.texture = Buff(texture_array.shape[1], texture_array.shape[0])
            self.texture.setStaticBuffArray(np.transpose(texture_array, (1, 0, 2)))
            if self.debug > 0:
                print("Texture Loaded with shape: ", texture_array.shape)
                print("Texture Buff have size: ", self.texture.size)
        else:
            raise ImportError("Cannot import texture file")

    def __addPoint2Pointlist(self, pointlist, x, y):
        if self.randomColor:
            p = Point((x, y), ColorType(random.random(), random.random(), random.random()))
        else:
            p = Point((x, y), ColorType(1, 0, 0))
        pointlist.append(p)

    # Deal with Mouse Left Button Pressed Interruption
    def Interrupt_MouseL(self, x, y):
        self.__addPoint2Pointlist(self.points_l, x, y)
        # Draw a point when one point provided or a line when two ends provided
        if len(self.points_l) % 2 == 1:
            if self.debug > 0:
                print("draw a point", self.points_l[-1])
            self.drawPoint(self.buff, self.points_l[-1])
        elif len(self.points_l) % 2 == 0 and len(self.points_l) > 0:
            if self.debug > 0:
                print("draw a line from ", self.points_l[-1], " -> ", self.points_l[-2])
            # self.drawPoint(self.buff, self.points_l[-1])
            self.drawLine(self.buff, self.points_l[-2], self.points_l[-1], doSmooth=self.doSmooth)
            self.points_l.clear()

    # Deal with Mouse Right Button Pressed Interruption
    def Interrupt_MouseR(self, x, y):
        self.__addPoint2Pointlist(self.points_r, x, y)
        if len(self.points_r) % 3 == 1:
            if self.debug > 0:
                print("draw a point", self.points_r[-1])
            self.drawPoint(self.buff, self.points_r[-1])
        elif len(self.points_r) % 3 == 2:
            if self.debug > 0:
                print("draw a line from ", self.points_r[-1], " -> ", self.points_r[-2])
            self.drawLine(self.buff, self.points_r[-2], self.points_r[-1], doSmooth=self.doSmooth)
        elif len(self.points_r) % 3 == 0 and len(self.points_r) > 0:
            if self.debug > 0:
                print("draw a triangle {} -> {} -> {}".format(self.points_r[-3], self.points_r[-2], self.points_r[-1]))
            self.drawTriangle(self.buff, self.points_r[-3], self.points_r[-2], self.points_r[-1], doSmooth=self.doSmooth, doTexture=self.doTexture)
            self.points_r.clear()

    def Interrupt_Keyboard(self, keycode):
        """
        keycode Reference: https://docs.wxpython.org/wx.KeyCode.enumeration.html#wx-keycode

        * r, R: Generate Random Color point
        * c, C: clear buff and screen
        * LEFT, UP: Last Test case
        * t, T, RIGHT, DOWN: Next Test case
        """
        # Trigger for test cases
        if keycode in [wx.WXK_LEFT, wx.WXK_UP]:  # Last Test Case
            self.clear()
            if len(self.test_case_list) != 0:
                self.test_case_index = (self.test_case_index - 1) % len(self.test_case_list)
            self.test_case_list[self.test_case_index](self.n_steps)
            print("Display Test case: ", self.test_case_index, "n_steps: ", self.n_steps)
        if keycode in [ord("t"), ord("T"), wx.WXK_RIGHT, wx.WXK_DOWN]:  # Next Test Case
            self.clear()
            if len(self.test_case_list) != 0:
                self.test_case_index = (self.test_case_index + 1) % len(self.test_case_list)
            self.test_case_list[self.test_case_index](self.n_steps)
            print("Display Test case: ", self.test_case_index, "n_steps: ", self.n_steps)
        if chr(keycode) in ",<":
            self.clear()
            self.n_steps = max(self.MIN_N_STEPS, round(self.n_steps / 2))
            self.test_case_list[self.test_case_index](self.n_steps)
            print("Display Test case: ", self.test_case_index, "n_steps: ", self.n_steps)
        if chr(keycode) in ".>":
            self.clear()
            self.n_steps = min(self.MAX_N_STEPS, round(self.n_steps * 2))
            self.test_case_list[self.test_case_index](self.n_steps)
            print("Display Test case: ", self.test_case_index, "n_steps: ", self.n_steps)

        # Switches
        if chr(keycode) in "rR":
            self.randomColor = not self.randomColor
            print("Random Color: ", self.randomColor)
        if chr(keycode) in "cC":
            self.clear()
            print("clear Buff")
        if chr(keycode) in "sS":
            self.doSmooth = not self.doSmooth
            print("Do Smooth: ", self.doSmooth)
        if chr(keycode) in "aA":
            self.doAA = not self.doAA
            print("Do Anti-Aliasing: ", self.doAA)
        if chr(keycode) in "mM":
            self.doTexture = not self.doTexture
            print("texture mapping: ", self.doTexture)

    def queryTextureBuffPoint(self, texture: Buff, x: int, y: int) -> Point:
        """
        Query a point at texture buff, should only be used in texture buff query

        :param texture: The texture buff you want to query from
        :type texture: Buff
        :param x: The query point x coordinate
        :type x: int
        :param y: The query point y coordinate
        :type y: int
        :rtype: Point
        """
        if self.debug > 1:
            if x != min(max(0, int(x)), texture.width - 1):
                print("Warning: Texture Query x coordinate outbound")
            if y != min(max(0, int(y)), texture.height - 1):
                print("Warning: Texture Query y coordinate outbound")
        return texture.getPointFromPointArray(x, y)

    @staticmethod
    def drawPoint(buff, point):
        """
        Draw a point on buff

        :param buff: The buff to draw point on
        :type buff: Buff
        :param point: A point to draw on buff
        :type point: Point
        :rtype: None
        """
        x, y = point.coords
        c = point.color
        # because we have already specified buff.buff has data type uint8, type conversion will be done in numpy
        buff.buff[x, y, 0] = c.r * 255
        buff.buff[x, y, 1] = c.g * 255
        buff.buff[x, y, 2] = c.b * 255

    def drawRectangle(self, buff, p1, p2, doSmooth=True, doAA=False, doAAlevel=4):
        x1, y1 = p1.coords
        x2, y2 = p2.coords
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.drawPoint(buff, Point((x, y), p1.color))

    def drawLine(self, buff, p1, p2, doSmooth=True, doAA=False, doAAlevel=4):
        """
        Draw a line between p1 and p2 on buff

        :param buff: The buff to edit
        :type buff: Buff
        :param p1: One end point of the line
        :type p1: Point
        :param p2: Another end point of the line
        :type p2: Point
        :param doSmooth: Control flag of color smooth interpolation
        :type doSmooth: bool
        :param doAA: Control flag of doing anti-aliasing
        :type doAA: bool
        :param doAAlevel: anti-aliasing super sampling level
        :type doAAlevel: int
        :rtype: None
        """
        ##### TODO 1: Use Bresenham algorithm to draw a line between p1 and p2 on buff.
        # Requirements:
        #   1. Only integer is allowed in interpolate point coordinates between p1 and p2
        #   2. Float number is allowed in interpolate point color
        def applyAntiAliasing( buff, x, y, r, g, b, aa_level):
            # Define the neighboring pixel offsets
            neighbors = [(-1, -1), (-1, 1), (1, -1), (1, 1),
                        (-1, 0), (1, 0), (0, -1), (0, 1)]

            # Intensity factor based on anti-aliasing level
            intensity = 1.0 / (aa_level + 1)

            for dx, dy in neighbors:
                nx, ny = x + dx, y + dy
                # Retrieve current color at the neighbor
                existing_point = buff.getPoint(nx, ny)
                if existing_point:
                    # Blend the existing color with the line color
                    blended_color = ColorType(
                        existing_point.color.r * (1 - intensity) + r * intensity,
                        existing_point.color.g * (1 - intensity) + g * intensity,
                        existing_point.color.b * (1 - intensity) + b * intensity
                    )
                    self.drawPoint(buff, Point((nx, ny), blended_color))

        x1, y1 = p1.coords
        x2, y2 = p2.coords

        dx = x2 - x1
        dy = y2 - y1

        x_inc = 1 if dx >= 0 else -1
        y_inc = 1 if dy >= 0 else -1

        dx = abs(dx)
        dy = abs(dy)

        # Handle the special case when the line is a single point
        if dx == 0 and dy == 0:
            self.drawPoint(buff, Point((x1, y1), p1.color))
            return

        # Determine the driving axis
        is_steep = dy > dx

        if is_steep:
            dx, dy = dy, dx
            x_inc, y_inc = y_inc, x_inc

        # Decision variable and increments
        d = 2 * dy - dx
        incrE = 2 * dy
        incrNE = 2 * (dy - dx)

        # Initialize starting points
        x = x1
        y = y1

        if is_steep:
            x, y = y1, x1
            end_x, end_y = y2, x2
        else:
            end_x, end_y = x2, y2

        # Calculate color steps if smoothing is enabled
        if doSmooth:
            color_diff = [
                p2.color.r - p1.color.r,
                p2.color.g - p1.color.g,
                p2.color.b - p1.color.b
            ]
            steps = dx if dx > dy else dy
            color_step = [c / steps for c in color_diff]
            r, g, b = p1.color.r, p1.color.g, p1.color.b
        else:
            r, g, b = p1.color.r, p1.color.g, p1.color.b
            color_step = [0, 0, 0]

        for _ in range(dx + 1):
            # Determine the actual coordinates based on the driving axis
            plot_x, plot_y = (y, x) if is_steep else (x, y)

            # Anti-aliasing handling
            if doAA:
                applyAntiAliasing(buff, plot_x, plot_y, r, g, b, doAAlevel)

            # Plot the main point
            self.drawPoint(buff, Point((plot_x, plot_y), ColorType(r, g, b)))

            # Update the decision variable and coordinates
            if d <= 0:
                d += incrE
            else:
                d += incrNE
                y += y_inc
            x += x_inc

            # Update color if smoothing is enabled
            if doSmooth:
                r += color_step[0]
                g += color_step[1]
                b += color_step[2]
        return

    def drawTriangle(self, buff, p1, p2, p3, doSmooth=True, doAA=False, doAAlevel=4, doTexture=False):
        """
        draw Triangle to buff. apply smooth color filling if doSmooth set to true, otherwise fill with first point color
        if doAA is true, apply anti-aliasing to triangle based on doAAlevel given.

        :param buff: The buff to edit
        :type buff: Buff
        :param p1: First triangle vertex
        :param p2: Second triangle vertex
        :param p3: Third triangle vertex
        :type p1: Point
        :type p2: Point
        :type p3: Point
        :param doSmooth: Color smooth filling control flag
        :type doSmooth: bool
        :param doAA: Anti-aliasing control flag
        :type doAA: bool
        :param doAAlevel: Anti-aliasing super sampling level
        :type doAAlevel: int
        :param doTexture: Draw triangle with texture control flag
        :type doTexture: bool
        :rtype: None
        """
        ##### TODO 2: Write a triangle rendering function, which support smooth bilinear interpolation of the vertex color
        ##### TODO 3(For CS680 Students): Implement texture-mapped fill of triangle. Texture is stored in self.texture
        # Requirements:
        #   1. For flat shading of the triangle, use the first vertex color.
        #   2. Polygon scan fill algorithm and the use of barycentric coordinate are not allowed in this function
        #   3. You should be able to support both flat shading and smooth shading, which is controlled by doSmooth
        #   4. For texture-mapped fill of triangles, it should be controlled by doTexture flag.
        # Sort the vertices by y-coordinate ascending (p0.y <= p1.y <= p2.y)
        def bresenham_line_points(p_start, p_end, doSmooth):
            """
            Generate points along a line using Bresenham's algorithm.

            :param p_start: Start point
            :param p_end: End point
            :param doSmooth: Flag for color interpolation
            :return: List of points along the line
            """
            x0, y0 = p_start.coords
            x1, y1 = p_end.coords

            x0 = int(round(x0))
            y0 = int(round(y0))
            x1 = int(round(x1))
            y1 = int(round(y1))

            points = []

            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            x_inc = 1 if x1 > x0 else -1
            y_inc = 1 if y1 > y0 else -1

            if dx > dy:
                d = 2 * dy - dx
                incrE = 2 * dy
                incrNE = 2 * (dy - dx)
                x, y = x0, y0

                steps = dx
                # Initialize color interpolation variables
                if doSmooth:
                    color_diff = [
                        (p_end.color.r - p_start.color.r) / steps if steps != 0 else 0,
                        (p_end.color.g - p_start.color.g) / steps if steps != 0 else 0,
                        (p_end.color.b - p_start.color.b) / steps if steps != 0 else 0
                    ]
                    r, g, b = p_start.color.r, p_start.color.g, p_start.color.b
                else:
                    r, g, b = p_start.color.r, p_start.color.g, p_start.color.b
                    color_diff = [0, 0, 0]

                for _ in range(dx + 1):
                    point = Point((x, y), ColorType(r, g, b))
                    points.append(point)
                    if d <= 0:
                        d += incrE
                    else:
                        d += incrNE
                        y += y_inc
                    x += x_inc

                    # Update color
                    r += color_diff[0]
                    g += color_diff[1]
                    b += color_diff[2]

            else:
                d = 2 * dx - dy
                incrE = 2 * dx
                incrNE = 2 * (dx - dy)
                x, y = x0, y0

                steps = dy
                # Initialize color interpolation variables
                if doSmooth:
                    color_diff = [
                        (p_end.color.r - p_start.color.r) / steps if steps != 0 else 0,
                        (p_end.color.g - p_start.color.g) / steps if steps != 0 else 0,
                        (p_end.color.b - p_start.color.b) / steps if steps != 0 else 0
                    ]
                    r, g, b = p_start.color.r, p_start.color.g, p_start.color.b
                else:
                    r, g, b = p_start.color.r, p_start.color.g, p_start.color.b
                    color_diff = [0, 0, 0]

                for _ in range(dy + 1):
                    point = Point((x, y), ColorType(r, g, b))
                    points.append(point)
                    if d <= 0:
                        d += incrE
                    else:
                        d += incrNE
                        x += x_inc
                    y += y_inc

                    # Update color
                    r += color_diff[0]
                    g += color_diff[1]
                    b += color_diff[2]

            return points
        # Texture coordinates mapping from triangle bounding box to texture
        # Flat shading uses the color of the first vertex
        flat_color = p1.color

        
        
        # Sort the vertices by y-coordinate ascending (p0.y <= p1.y <= p2.y)
        vertices = sorted([p1, p2, p3], key=lambda p: p.coords[1])
        p0, p1, p2 = vertices
        x0, y0 = p0.coords
        x1, y1 = p1.coords
        x2, y2 = p2.coords

        # Use Bresenham's algorithm to generate the edge points
        # Generate edge lists
        edge0 = bresenham_line_points(p0, p1, doSmooth)
        edge1 = bresenham_line_points(p1, p2, doSmooth)
        edge2 = bresenham_line_points(p0, p2, doSmooth)

        # Combine all edge points
        edge_points = edge0 + edge1 + edge2

        # Create a dictionary to hold x-values for each y-coordinate
        y_dict = {}
        for point in edge_points:
            x, y = point.coords
            y = int(y)
            if y not in y_dict:
                y_dict[y] = []
            y_dict[y].append(point)

        # Get all y values
        y_values = sorted(y_dict.keys())


        # Fill the triangle by drawing horizontal lines between edge points
        for y in y_values:
            x_points = y_dict[y]
            x_coords = [point.coords[0] for point in x_points]
            x_min = int(min(x_coords))
            x_max = int(max(x_coords))

            # Modify the condition to exclude doAA from affecting flat shading
            if doSmooth or doTexture:
                # For each pixel between x_min and x_max
                for x in range(x_min, x_max + 1):
                    # Calculate barycentric weights (without using barycentric coordinates explicitly)
                    denom = ((x1 - x2) * (y0 - y2) - (x0 - x2) * (y1 - y2))
                    if denom == 0:
                        # Avoid division by zero; skip this pixel
                        continue
                    w0 = ((x1 - x2) * (y - y2) - (x - x2) * (y1 - y2)) / denom
                    w1 = ((x2 - x0) * (y - y2) - (x - x2) * (y2 - y0)) / denom
                    w2 = 1 - w0 - w1

                    # Clamp weights
                    w0 = max(0, min(w0, 1))
                    w1 = max(0, min(w1, 1))
                    w2 = max(0, min(w2, 1))
                    
                    if doTexture:
                        # Get bounding box of the triangle
                        min_x = max(int(min(x0, x1, x2)), 0)
                        max_x = min(int(max(x0, x1, x2)), buff.width - 1)
                        min_y = max(int(min(y0, y1, y2)), 0)
                        max_y = min(int(max(y0, y1, y2)), buff.height - 1)

                        # Texture size
                        tex_width = self.texture.width - 1
                        tex_height = self.texture.height - 1

                        # Triangle bounding box in screen space
                        tri_min_x = min_x
                        tri_max_x = max_x
                        tri_min_y = min_y
                        tri_max_y = max_y

                        # Prevent division by zero and ensure denominator is at least 1
                        tri_width = tri_max_x - tri_min_x
                        tri_height = tri_max_y - tri_min_y
                        tri_width = tri_width if tri_width != 0 else 1
                        tri_height = tri_height if tri_height != 0 else 1

                        def get_texture_color(x, y):
                            u = (x - tri_min_x) / tri_width
                            v = (y - tri_min_y) / tri_height
                            u = max(0, min(u, 1))  # Clamp u to [0,1]
                            v = max(0, min(v, 1))  # Clamp v to [0,1]
                            tex_x = int(u * tex_width)
                            tex_y = int(v * tex_height)
                            # Ensure tex_x and tex_y are within valid range
                            tex_x = min(tex_x, tex_width)
                            tex_y = min(tex_y, tex_height)
                            tex_point = self.queryTextureBuffPoint(self.texture, tex_x, tex_y)
                            return tex_point.color
                        # Texture mapping (if applicable)
                        color = get_texture_color(x, y)
                    else:
                        if doSmooth:
                            # Interpolate color
                            r = w0 * p0.color.r + w1 * p1.color.r + w2 * p2.color.r
                            g = w0 * p0.color.g + w1 * p1.color.g + w2 * p2.color.g
                            b = w0 * p0.color.b + w1 * p1.color.b + w2 * p2.color.b
                            color = ColorType(r, g, b)
                        else:
                            # Flat shading: use the first vertex's color
                            color = flat_color

                    # Apply anti-aliasing if enabled and smooth shading is not used
                    if doAA and not doSmooth:
                        # Implement simple anti-aliasing by blending the color with the background
                        # For simplicity, assume background color is black
                        # A more sophisticated approach would use supersampling
                        existing_point = buff.getPoint(x, y)
                        if existing_point:
                            alpha = 0.5  # Example alpha value for blending
                            color = ColorType(
                                r=(1 - alpha) * existing_point.color.r + alpha * color.r,
                                g=(1 - alpha) * existing_point.color.g + alpha * color.g,
                                b=(1 - alpha) * existing_point.color.b + alpha * color.b
                            )

                    # Clamp color values to [0, 1]
                    clamped_color = ColorType(
                        r=min(1.0, max(0.0, color.r)),  
                        g=min(1.0, max(0.0, color.g)),  
                        b=min(1.0, max(0.0, color.b))  
                    )
                    # Draw the pixel
                    self.drawPoint(buff, Point((x, y), clamped_color))
            else:
                # Flat shading: fill with the first vertex's color
                for x in range(x_min, x_max + 1):
                    self.drawPoint(buff, Point((x, y), flat_color))
        return
    
    # test for lines lines in all directions
    def testCaseLine01(self, n_steps):
        center_x = int(self.buff.width / 2)
        center_y = int(self.buff.height / 2)
        radius = int(min(self.buff.width, self.buff.height) * 0.45)

        v0 = Point([center_x, center_y], ColorType(1, 1, 0))
        for step in range(0, n_steps):
            theta = math.pi * step / n_steps
            v1 = Point([center_x + int(math.sin(theta) * radius), center_y + int(math.cos(theta) * radius)],
                       ColorType(0, 0, (1 - step / n_steps)))
            v2 = Point([center_x - int(math.sin(theta) * radius), center_y - int(math.cos(theta) * radius)],
                       ColorType(0, (1 - step / n_steps), 0))
            self.drawLine(self.buff, v2, v0, doSmooth=True)
            self.drawLine(self.buff, v0, v1, doSmooth=True)

    # test for lines: drawing circle and petal 
    def testCaseLine02(self, n_steps):
        n_steps = 2 * n_steps
        d_theta = 2 * math.pi / n_steps
        d_petal = 12 * math.pi / n_steps
        cx = int(self.buff.width / 2)
        cy = int(self.buff.height / 2)
        radius = (0.75 * min(cx, cy))
        p = radius * 0.25

        # Outer petals
        for i in range(n_steps + 2):
            self.drawLine(self.buff,
                          Point((math.floor(0.5 + radius * math.sin(d_theta * i) + p * math.sin(d_petal * i)) + cx,
                                 math.floor(0.5 + radius * math.cos(d_theta * i) + p * math.cos(d_petal * i)) + cy),
                                ColorType(1, (128 + math.sin(d_theta * i * 5) * 127) / 255,
                                          (128 + math.cos(d_theta * i * 5) * 127) / 255)),
                          Point((math.floor(
                              0.5 + radius * math.sin(d_theta * (i + 1)) + p * math.sin(d_petal * (i + 1))) + cx,
                                 math.floor(0.5 + radius * math.cos(d_theta * (i + 1)) + p * math.cos(
                                     d_petal * (i + 1))) + cy),
                                ColorType(1, (128 + math.sin(d_theta * 5 * (i + 1)) * 127) / 255,
                                          (128 + math.cos(d_theta * 5 * (i + 1)) * 127) / 255)),
                          doSmooth=True, doAA=self.doAA, doAAlevel=self.doAAlevel)

        # Draw circle
        for i in range(n_steps + 1):
            v0 = Point((math.floor(0.5 * radius * math.sin(d_theta * i)) + cx,
                        math.floor(0.5 * radius * math.cos(d_theta * i)) + cy), ColorType(1, 97. / 255, 0))
            v1 = Point((math.floor(0.5 * radius * math.sin(d_theta * (i + 1))) + cx,
                        math.floor(0.5 * radius * math.cos(d_theta * (i + 1))) + cy), ColorType(1, 97. / 255, 0))
            self.drawLine(self.buff, v0, v1, doSmooth=True, doAA=self.doAA, doAAlevel=self.doAAlevel)

    # test for smooth filling triangle
    def testCaseTri01(self, n_steps):
        n_steps = int(n_steps / 2)
        delta = 2 * math.pi / n_steps
        radius = int(min(self.buff.width, self.buff.height) * 0.45)
        cx = int(self.buff.width / 2)
        cy = int(self.buff.height / 2)
        theta = 0

        for _ in range(n_steps):
            theta += delta
            v0 = Point((cx, cy), ColorType(1, 1, 1))
            v1 = Point((int(cx + math.sin(theta) * radius), int(cy + math.cos(theta) * radius)),
                       ColorType((127. + 127. * math.sin(theta)) / 255,
                                 (127. + 127. * math.sin(theta + 2 * math.pi / 3)) / 255,
                                 (127. + 127. * math.sin(theta + 4 * math.pi / 3)) / 255))
            v2 = Point((int(cx + math.sin(theta + delta) * radius), int(cy + math.cos(theta + delta) * radius)),
                       ColorType((127. + 127. * math.sin(theta + delta)) / 255,
                                 (127. + 127. * math.sin(theta + delta + 2 * math.pi / 3)) / 255,
                                 (127. + 127. * math.sin(theta + delta + 4 * math.pi / 3)) / 255))
            self.drawTriangle(self.buff, v1, v0, v2, False, self.doAA, self.doAAlevel)

    def testCaseTri02(self, n_steps):
        # Test case for no smooth color filling triangle
        n_steps = int(n_steps / 2)
        delta = 2 * math.pi / n_steps
        radius = int(min(self.buff.width, self.buff.height) * 0.45)
        cx = int(self.buff.width / 2)
        cy = int(self.buff.height / 2)
        theta = 0

        for _ in range(n_steps):
            theta += delta
            v0 = Point((cx, cy), ColorType(1, 1, 1))
            v1 = Point((int(cx + math.sin(theta) * radius), int(cy + math.cos(theta) * radius)),
                       ColorType((127. + 127. * math.sin(theta)) / 255,
                                 (127. + 127. * math.sin(theta + 2 * math.pi / 3)) / 255,
                                 (127. + 127. * math.sin(theta + 4 * math.pi / 3)) / 255))
            v2 = Point((int(cx + math.sin(theta + delta) * radius), int(cy + math.cos(theta + delta) * radius)),
                       ColorType((127. + 127. * math.sin(theta + delta)) / 255,
                                 (127. + 127. * math.sin(theta + delta + 2 * math.pi / 3)) / 255,
                                 (127. + 127. * math.sin(theta + delta + 4 * math.pi / 3)) / 255))
            self.drawTriangle(self.buff, v0, v1, v2, True, self.doAA, self.doAAlevel)

    def testCaseTriTexture01(self, n_steps):
        # Test case for no smooth color filling triangle
        n_steps = int(n_steps / 2)
        delta = 2 * math.pi / n_steps
        radius = int(min(self.buff.width, self.buff.height) * 0.45)
        cx = int(self.buff.width / 2)
        cy = int(self.buff.height / 2)
        theta = 0

        triangleList = []
        for _ in range(n_steps):
            theta += delta
            v0 = Point((cx, cy), ColorType(1, 1, 1))
            v1 = Point((int(cx + math.sin(theta) * radius), int(cy + math.cos(theta) * radius)),
                       ColorType((127. + 127. * math.sin(theta)) / 255,
                                 (127. + 127. * math.sin(theta + 2 * math.pi / 3)) / 255,
                                 (127. + 127. * math.sin(theta + 4 * math.pi / 3)) / 255))
            v2 = Point((int(cx + math.sin(theta + delta) * radius), int(cy + math.cos(theta + delta) * radius)),
                       ColorType((127. + 127. * math.sin(theta + delta)) / 255,
                                 (127. + 127. * math.sin(theta + delta + 2 * math.pi / 3)) / 255,
                                 (127. + 127. * math.sin(theta + delta + 4 * math.pi / 3)) / 255))
            triangleList.append([v0, v1, v2])

        for t in triangleList:
            self.drawTriangle(self.buff, *t, doTexture=True)


if __name__ == "__main__":
    def main():
        print("This is the main entry! ")
        app = wx.App(False)
        # Set FULL_REPAINT_ON_RESIZE will repaint everything when scaling the frame
        # here is the style setting for it: wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE
        # wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER will disable canvas resize.
        frame = wx.Frame(None, size=(500, 500), title="Test", style=wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)

        canvas = Sketch(frame)
        canvas.debug = 0

        frame.Show()
        app.MainLoop()


    def codingDebug():
        """
        If you are still working on the assignment, we suggest to use this as the main call.
        There will be more strict type checking in this version, which might help in locating your bugs.
        """
        print("This is the debug entry! ")
        import cProfile
        import pstats
        profiler = cProfile.Profile()
        profiler.enable()

        app = wx.App(False)
        # Set FULL_REPAINT_ON_RESIZE will repaint everything when scaling the frame
        # here is the style setting for it: wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE
        # wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER will disable canvas resize.
        frame = wx.Frame(None, size=(500, 500), title="Test", style=wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)
        canvas = Sketch(frame)
        canvas.debug = 2
        frame.Show()
        app.MainLoop()

        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime').reverse_order()
        stats.print_stats()

    main()
    # codingDebug()
