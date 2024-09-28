
from lib_3d import utils_3d
import math


def _toroid_quads_factory(vertices: list[utils_3d.Face], resolution: int) -> list[utils_3d.Face]:
    """
    Given a 2D grid of vertices, this function transforms them into quads,
    defining the faces of a 3D object.
    """
    faces = []
    for i in range(resolution):
        for j in range(resolution):
            # Get vertices in cyclic order to close the surface
            v1 = vertices[i][j]
            v2 = vertices[i][(j + 1) % resolution]
            v3 = vertices[(i + 1) % resolution][(j + 1) % resolution]
            v4 = vertices[(i + 1) % resolution][j]
            faces.append(utils_3d.Face(v1, v2, v3, v4))
    return faces


def toroid_factory(R: float, r: float, resolution:float=20) -> utils_3d.Model:
    """
    This function returns the vertices and faces of a torus.
    """

    theta_steps = [2 * math.pi * i / resolution for i in range(resolution)]
    phi_steps = [2 * math.pi * j / resolution for j in range(resolution)]

    # Organize vertices in a 2D grid for face creation
    vertices = [[None] * resolution for _ in range(resolution)]

    for i in range(resolution):
        T = theta_steps[i]
        for j in range(resolution):
            P = phi_steps[j]
            x = (R + r * math.cos(P)) * math.cos(T)
            y = (R + r * math.cos(P)) * math.sin(T)
            z = r * math.sin(P)
            vertex = utils_3d.Vertex(x, y, z)
            vertices[i][j] = vertex

    # Create faces using quads_factory
    faces = _toroid_quads_factory(vertices, resolution)
    model = utils_3d.Model(faces)
    return model


def cube_factory(size: float) -> utils_3d.Model:
    """
    Generates a cube with a given size.
    """
    # Half size to center the cube at the origin
    half_size = size / 2

    # Define vertices of the cube
    vertices = [
        utils_3d.Vertex(-half_size, -half_size, -half_size),  # V0
        utils_3d.Vertex(half_size, -half_size, -half_size),   # V1
        utils_3d.Vertex(half_size, half_size, -half_size),    # V2
        utils_3d.Vertex(-half_size, half_size, -half_size),   # V3
        utils_3d.Vertex(-half_size, -half_size, half_size),   # V4
        utils_3d.Vertex(half_size, -half_size, half_size),    # V5
        utils_3d.Vertex(half_size, half_size, half_size),     # V6
        utils_3d.Vertex(-half_size, half_size, half_size),    # V7
    ]

    # Define faces (each face is a quad made up of 4 vertices)
    faces = [
        utils_3d.Face(vertices[0], vertices[1], vertices[2], vertices[3]),  # Bottom face
        utils_3d.Face(vertices[4], vertices[5], vertices[6], vertices[7]),  # Top face
        utils_3d.Face(vertices[0], vertices[1], vertices[5], vertices[4]),  # Front face
        utils_3d.Face(vertices[2], vertices[3], vertices[7], vertices[6]),  # Back face
        utils_3d.Face(vertices[1], vertices[2], vertices[6], vertices[5]),  # Right face
        utils_3d.Face(vertices[0], vertices[3], vertices[7], vertices[4]),  # Left face
    ]

    # Create and return the cube model
    model = utils_3d.Model(faces)
    return model