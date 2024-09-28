import math

class Vertex:

    def __init__(self, x:float=0, y:float=0, z:float=0) -> None:
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self) -> str:
        return f"<({self.x}, {self.y}, {self.z})>"
    
    def move_to(self, x:float, y:float, z:float):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def distance(v1, v2):
        return math.sqrt((v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2)

class Face:
    """
    Defines a face of a 3D object as a quad.
    """
    
    @property
    def v1(self):
        return self.vertices[0]
    @property
    def v2(self):
        return self.vertices[1]
    @property
    def v3(self):
        return self.vertices[2]
    @property
    def v4(self):   
        return self.vertices[3] if len(self.vertices) == 4 else None 


    def __init__(self, v1:Vertex, v2:Vertex, v3:Vertex, v4:Vertex=None) -> None:
        self.vertices = [v1, v2, v3] + ([v4] if v4 else [])
        self.center = self.calculate_center()
        self.computed_distance_from_model_center = None
        self.rotation = Vertex()

    def __str__(self) -> str:
        return f"<Face: {self.v1}, {self.v2}, {self.v3}, {self.v4}>"
        
    def calculate_center(self):
        vertices = 4 if self.v4 else 3
        x = (self.v1.x + self.v2.x + self.v3.x + (self.v4.x if self.v4 else 0)) / vertices
        y = (self.v1.y + self.v2.y + self.v3.y + (self.v4.y if self.v4 else 0)) / vertices
        z = (self.v1.z + self.v2.z + self.v3.z + (self.v4.z if self.v4 else 0)) / vertices
        return Vertex(x, y, z)
    
    def update_center(self):
        self.center = self.calculate_center()

    def move_to(self, x:float, y:float, z:float):
        relative_change = Vertex(x - self.center.x, y - self.center.y, z - self.center.z)
        self.center.x = x
        self.center.y = y
        self.center.z = z
        for vertex in self.vertices:
            new_vertex_x = vertex.x + relative_change.x
            new_vertex_y = vertex.y + relative_change.y
            new_vertex_z = vertex.z + relative_change.z
            vertex.move_to(new_vertex_x, new_vertex_y, new_vertex_z)

    def rotate_to(self, x: float = None, y: float = None, z: float = None):
        x_diff, y_diff, z_diff = 0, 0, 0
        
        # Calculate rotation differences
        if x is not None:
            x_diff = (x - self.rotation.x) * math.pi / 180  # Convert to radians
            self.rotation.x = x
        
        if y is not None:
            y_diff = (y - self.rotation.y) * math.pi / 180  # Convert to radians
            self.rotation.y = y
        
        if z is not None:
            z_diff = (z - self.rotation.z) * math.pi / 180  # Convert to radians
            self.rotation.z = z

        # Rotate each vertex
        for vertex in self.vertices:
            # Translate vertex to origin (relative to center)
            dx = vertex.x - self.center.x
            dy = vertex.y - self.center.y
            dz = vertex.z - self.center.z
            
            # Rotate around Z-axis (affects x and y)
            if z_diff:
                new_dx = dx * math.cos(z_diff) - dy * math.sin(z_diff)
                new_dy = dx * math.sin(z_diff) + dy * math.cos(z_diff)
                dx, dy = new_dx, new_dy
            
            # Rotate around Y-axis (affects x and z)
            if y_diff:
                new_dx = dx * math.cos(y_diff) + dz * math.sin(y_diff)
                new_dz = -dx * math.sin(y_diff) + dz * math.cos(y_diff)
                dx, dz = new_dx, new_dz

            # Rotate around X-axis (affects y and z)
            if x_diff:
                new_dy = dy * math.cos(x_diff) - dz * math.sin(x_diff)
                new_dz = dy * math.sin(x_diff) + dz * math.cos(x_diff)
                dy, dz = new_dy, new_dz

            # Translate vertex back to original position relative to center
            vertex.x = dx + self.center.x
            vertex.y = dy + self.center.y
            vertex.z = dz + self.center.z

    
class Camera:

    def __init__(self, position:Vertex=None) -> None:
        
        self.position = position or Vertex()
        self.rotation = Vertex()
        self.display_size = Vertex(1, 1)
        self.recording_surface_size = Vertex(1.6, 1.6, 0.5)

    def move_to(self, x:float, y:float, z:float) -> None:
        self.position.x = x
        self.position.y = y
        self.position.z = z
    
    def project_vertex(self, vertex:Vertex, return_relative_coords=False) -> Vertex:
        """
        Projects a 3D vertex to a 2D vertex.
        """
        # relative pos
        r = Vertex(vertex.x - self.position.x, vertex.y - self.position.y, vertex.z - self.position.z)
        rotation_sin = Vertex(x=math.sin(self.rotation.x), y=math.sin(self.rotation.y), z=math.sin(self.rotation.z))
        rotation_cos = Vertex(x=math.cos(self.rotation.x), y=math.cos(self.rotation.y), z=math.cos(self.rotation.z))

        # D is the relative position of the vertex considering camera rotation. Check https://en.wikipedia.org/wiki/3D_projection
        d = Vertex()
        d.x = rotation_cos.y * (rotation_sin.z * r.y + rotation_cos.z * r.x) - rotation_sin.y * r.z
        d.y = rotation_sin.x * (rotation_cos.y * r.z + rotation_sin.y * (rotation_sin.z * r.y + rotation_cos.z * r.x)) + rotation_cos.x * (rotation_cos.z * r.y - rotation_sin.z * r.x)
        d.z = rotation_cos.x * (rotation_cos.y * r.z + rotation_sin.y * (rotation_sin.z * r.y + rotation_cos.z * r.x)) - rotation_sin.x * (rotation_cos.z * r.y - rotation_sin.z * r.x)

        # Calculate 2D projection
        s = self.display_size
        r = self.recording_surface_size
        b = Vertex()
        b.x = (d.x * s.x) / (d.z * r.x+ 0.00001) * r.z
        b.y = (d.y * s.y) / (d.z * r.y+ 0.00001) * r.z

        if return_relative_coords:
            return Vertex(b.x/r.x, b.y/r.y, d.z)
        return b
    
class Model:

    def __init__(self, faces:list[Face]) -> None:
        self.faces = faces
        self.center = self.calculate_center()
        for face in faces:
            face.computed_distance_from_model_center = Vertex.distance(face.center, self.center)
        self.rotation = Vertex()
        self.name = ""

    def __str__(self) -> str:
        return f"<Model with {len(self.faces)} faces>"

    def calculate_center(self):
        x = 0
        y = 0
        z = 0
        for face in self.faces:
            x += face.center.x
            y += face.center.y
            z += face.center.z
        x /= len(self.faces)
        y /= len(self.faces)
        z /= len(self.faces)
        return Vertex(x, y, z)
    
    def update_center(self):
        self.center = self.calculate_center()

    def move_to(self, x:float=0, y:float=0, z:float=0):
        relative_change = Vertex(x - self.center.x, y - self.center.y, z - self.center.z)
        self.center.x = x
        self.center.y = y
        self.center.z = z
        for face in self.faces:
            new_face_x = face.center.x + relative_change.x
            new_face_y = face.center.y + relative_change.y
            new_face_z = face.center.z + relative_change.z
            face.move_to(new_face_x, new_face_y, new_face_z)

    def rotate_to(self, x: float = None, y: float = None, z: float = None):
        x_diff, y_diff, z_diff = 0, 0, 0
        
        # Calculate rotation differences in radians
        if x is not None:
            x_diff = (x - self.rotation.x) * math.pi / 180
            self.rotation.x = x
        
        if y is not None:
            y_diff = (y - self.rotation.y) * math.pi / 180
            self.rotation.y = y
        
        if z is not None:
            z_diff = (z - self.rotation.z) * math.pi / 180
            self.rotation.z = z

        # Rotate each face of the model
        for face in self.faces:
            # Translate face center to origin relative to model center
            dx = face.center.x - self.center.x
            dy = face.center.y - self.center.y
            dz = face.center.z - self.center.z
            
            # Rotate around Z-axis (affects x and y)
            if z_diff:
                new_dx = dx * math.cos(z_diff) - dy * math.sin(z_diff)
                new_dy = dx * math.sin(z_diff) + dy * math.cos(z_diff)
                dx, dy = new_dx, new_dy
            
            # Rotate around Y-axis (affects x and z)
            if y_diff:
                new_dx = dx * math.cos(y_diff) + dz * math.sin(y_diff)
                new_dz = -dx * math.sin(y_diff) + dz * math.cos(y_diff)
                dx, dz = new_dx, new_dz
            
            # Rotate around X-axis (affects y and z)
            if x_diff:
                new_dy = dy * math.cos(x_diff) - dz * math.sin(x_diff)
                new_dz = dy * math.sin(x_diff) + dz * math.cos(x_diff)
                dy, dz = new_dy, new_dz

            # Translate face center back to original position relative to model center
            face.move_to(dx + self.center.x, dy + self.center.y, dz + self.center.z)
            
            # Now rotate the face itself around its own center
            face.rotate_to(x, y, z)
    def depth_sort_faces(self, camera:Camera):
        self.faces = sorted(self.faces, key=lambda x: Vertex.distance(x.center, camera.position), reverse=True)
        return self.faces