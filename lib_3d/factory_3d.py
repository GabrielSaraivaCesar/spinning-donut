
from lib_3d import utils_3d
import trimesh
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


def toroid_factory(R: float, r: float, resolution:float=20) -> utils_3d.Mesh:
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
    mesh = utils_3d.Mesh(faces)
    mesh.name = "Toroid"
    return mesh


def cube_factory(size: float) -> utils_3d.Mesh:
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
        utils_3d.Face(vertices[0], vertices[1], vertices[2], vertices[3]),  # Front face
        utils_3d.Face(vertices[4], vertices[5], vertices[6], vertices[7]),  # Back face
        utils_3d.Face(vertices[0], vertices[1], vertices[5], vertices[4]),  # Top face
        utils_3d.Face(vertices[2], vertices[3], vertices[7], vertices[6]),  # Bottom face
        utils_3d.Face(vertices[1], vertices[2], vertices[6], vertices[5]),  # Right face
        utils_3d.Face(vertices[0], vertices[3], vertices[7], vertices[4])  # Left face
    ]

    # Create and return the cube mesh
    mesh = utils_3d.Mesh(faces)
    # faces[2].recalculate_normal(mesh, flip=True)

    mesh.name = "Cube"
    return mesh


def pyramid_factory(base_size:float, height:float) -> utils_3d.Mesh:
    """
    Generates a pyramid with a given base size and height.
    """
    
    # Half size to center the square at the origin
    half_size = base_size / 2
    half_height = height / 2
    top_vertex = utils_3d.Vertex(y=-half_height*2) # V0

    base_vertices = [
        utils_3d.Vertex(-half_size, half_height, -half_size),  # V0
        utils_3d.Vertex( half_size, half_height, -half_size),   # V1
        utils_3d.Vertex( half_size, half_height,  half_size),    # V2
        utils_3d.Vertex(-half_size, half_height,  half_size),   # V3
    ]

    faces = [
        utils_3d.Face(*base_vertices),
        utils_3d.Face(base_vertices[0], base_vertices[1], top_vertex),
        utils_3d.Face(base_vertices[1], base_vertices[2], top_vertex),
        utils_3d.Face(base_vertices[2], base_vertices[3], top_vertex),
        utils_3d.Face(base_vertices[3], base_vertices[0], top_vertex),
    ]

    mesh = utils_3d.Mesh(faces)
    faces[0].recalculate_normal(mesh, flip=True)
    mesh.name = "Pyramid"
    return mesh


def import_mesh(path):
    # Load the .obj file
    mesh = trimesh.load(path, force="mesh")
    vertices = []
    faces = []

    for vertex in mesh.vertices:
        vertices.append(
            utils_3d.Vertex(
                vertex[0],
                vertex[1],
                vertex[2],
            )
        )
    
    for face in mesh.faces:
        v1 = vertices[face[0]]
        v2 = vertices[face[1]]
        v3 = vertices[face[2]]
        faces.append(
            utils_3d.Face(
                v1, v2, v3
            )
        )
    
    mesh = utils_3d.Mesh(faces)
    mesh.name = path
    return mesh

