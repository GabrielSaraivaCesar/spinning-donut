import os
import sys
from PIL import Image, ImageDraw, ImageFont
import string
from lib_3d.utils_3d import Camera, Vertex, Face

def generate_ascii_list():
    # Font settings (default system font)
    font_size = 16
    try:
        font = ImageFont.load_default()
    except IOError:
        print("Error loading default font.")

    def get_white_pixels_value(character, font, font_size):
        image = Image.new('L', (font_size, font_size), color=0)
        draw = ImageDraw.Draw(image)
        
        # Draw the character onto the image
        draw.text((0, 0), character, fill=255, font=font)  # White text (255)
        
        # Count white pixels (value 255)
        white_pixels = sum(pixel for pixel in image.getdata() if pixel > 0)
        return white_pixels

    ascii_chars = string.printable.strip()
    char_pixel_values = [(char, get_white_pixels_value(char, font, font_size)) for char in ascii_chars]
    char_pixel_values_sorted = sorted(char_pixel_values, key=lambda x: x[1])

    # Create a sorted list of characters
    sorted_chars = [char for char, _ in char_pixel_values_sorted]

    return [" "] + sorted_chars


def get_screen_matrix():
    size = os.get_terminal_size()
    columns = size.columns
    rows = size.lines
    return [[None] * columns for _ in range(rows)]


def is_point_in_triangle(x, y, triangle:list[Vertex]):
    """
    User a barycentric coordinates approach to determin if a point is inside a triangle 
    """
    # Unpack triangle vertices
    v1 = triangle[0]
    v2 = triangle[1]
    v3 = triangle[2]
    EPSILON = 1e-9  # A small value to account for precision errors
    # Calculate the denominator of the barycentric coordinates
    denom = (v2.y - v3.y) * (v1.x - v3.x) + (v3.x - v2.x) * (v1.y - v3.y) + EPSILON
    
    # Calculate the barycentric coordinates
    alpha = ((v2.y - v3.y) * (x - v3.x) + (v3.x - v2.x) * (y - v3.y)) / denom
    beta = ((v3.y - v1.y) * (x - v3.x) + (v1.x - v3.x) * (y - v3.y)) / denom
    gamma = 1 - alpha - beta
    
    # Check if the point is inside the triangle
    return (0 <= alpha <= 1) and (0 <= beta <= 1) and (0 <= gamma <= 1)


def get_bounding_box_from_virtual_vertices(vertices):
    min_x = min(vertices, key=lambda x: x.x).x
    max_x = max(vertices, key=lambda x: x.x).x
    min_y = min(vertices, key=lambda x: x.y).y
    max_y = max(vertices, key=lambda x: x.y).y
    return {'min_x': min_x, 'max_x': max_x, 'min_y': min_y, 'max_y':max_y}


def draw_face_on_screen(face: Face, cam:Camera, screen, ascii_list):
    h, w = (len(screen), len(screen[0]))

    affected_coords = []

    ascii_char = ascii_list[int(face.light_value * (len(ascii_list) - 1))]

    vertices_screen_virtual_coords = []
    for vertex in face.vertices:
        projection = cam.project_vertex(vertex, return_relative_coords=True)
        translated_range = Vertex()
        # projection returns a range from -1 to 1, so we need to translate it to 0 - 1
        translated_range.x = (projection.x + 1) / 2
        translated_range.y = (projection.y + 1) / 2
        
        screen_x = int(translated_range.x * w)
        screen_y = int(translated_range.y * h)
        vertices_screen_virtual_coords.append(
            Vertex(x=screen_x, y=screen_y)
        )
        if screen_y >= h or screen_x >= w or screen_y < 0 or screen_x < 0:
            continue
        screen[screen_y][screen_x] = ascii_char
        affected_coords.append((screen_x, screen_y))
    
    triangles = []
    if len(vertices_screen_virtual_coords) == 3:
        triangles.append(vertices_screen_virtual_coords)
    else: # Take quads into account
        triangles.append(vertices_screen_virtual_coords[:3])
        triangles.append(vertices_screen_virtual_coords[2:] + vertices_screen_virtual_coords[:1])

    # Virtual vertices have the coordinates relative to the screen
    # Calculate the center
    virtual_center = Vertex()
    virtual_center.x = sum([v.x for v in vertices_screen_virtual_coords]) / len(vertices_screen_virtual_coords)
    virtual_center.y = sum([v.y for v in vertices_screen_virtual_coords]) / len(vertices_screen_virtual_coords)

    # Get the bounding box relative to the pixels where the vertices are
    bounding_box = get_bounding_box_from_virtual_vertices(vertices_screen_virtual_coords)
    if bounding_box['max_x'] >= w:
        bounding_box['max_x'] = w-1
    if bounding_box['max_y'] >= h:
        bounding_box['max_y'] = h-1
    if bounding_box['min_x'] < 0:
        bounding_box['min_x'] = 0
    if bounding_box['min_y'] < 0:
        bounding_box['min_y'] = 0
    x_range = bounding_box['max_x'] - bounding_box['min_x']
    y_range = bounding_box['max_y'] - bounding_box['min_y']
    
    # For each pixel inside that bounding box, we consider it as virtual vertex
    extra_virtual_vertex = Vertex()
    for _x in range(x_range):
        x = _x + bounding_box['min_x']
        extra_virtual_vertex.x = x
        for _y in range(y_range):
            y = _y + bounding_box['min_y']
            extra_virtual_vertex.y = y
            is_inside_face = False
            for triangle in triangles:
                if is_point_in_triangle(x,y, triangle):
                    is_inside_face = True
                    break
            if is_inside_face:
                screen[y][x] = ascii_char
                affected_coords.append((x, y))

    return affected_coords

def draw_fps(real_fps, screen):
    text = "FPS: {value}".format(value="{:.2f}".format(real_fps))
    size = len(text)
    for idx, char in enumerate(text):
        screen[len(screen)-10][len(screen[-1])-size+idx-10] = char


def draw_screen(screen_data):
    h, w = (len(screen_data), len(screen_data[0]))
    # sys.stdout.write("\033[2J")  # Clear the terminal screen
    sys.stdout.write("\033[0;0H")  # Move cursor to top-left

    for y in range(h):
        for x in range(w):
            if screen_data[y][x] is not None:
                sys.stdout.write(screen_data[y][x])
            else:
                sys.stdout.write(' ')
    sys.stdout.flush()

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()
