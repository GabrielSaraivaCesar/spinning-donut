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
    
    @staticmethod
    def three_vertex_angle(v1, v2, v3):
        """
        Calculates the angle at vertex v1, formed by vectors v1->v2 and v1->v3 in 3D space.
        """
        # Vector from v1 to v2
        AB = (v2.x - v1.x, v2.y - v1.y, v2.z - v1.z)
        # Vector from v1 to v3
        AC = (v3.x - v1.x, v3.y - v1.y, v3.z - v1.z)

        # Dot product of AB and AC
        dot_product = (AB[0] * AC[0]) + (AB[1] * AC[1]) + (AB[2] * AC[2])

        # Magnitudes of AB and AC
        d_v2 = Vertex.distance(v1, v2)
        d_v3 = Vertex.distance(v1, v3)

        # Calculate cosine of the angle
        cos_theta = dot_product / (d_v2 * d_v3)

        # Clamp the cosine value to avoid precision errors
        cos_theta = max(-1, min(1, cos_theta))

        # Calculate the angle in radians and convert to degrees
        radians = math.acos(cos_theta)
        degrees = math.degrees(radians)
        return degrees

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
        self.rotation = Vertex()
        self.light_value = 0 # 0 to 1
        self.normal = Vertex()

    
    def __str__(self) -> str:
        return f"<Face: {self.v1}, {self.v2}, {self.v3}, {self.v4}>"

    def calculate_normal(self, model_center=None):
        # Calculate edge vectors for the normal calculation
        v1 = self.v1
        v2 = self.v2
        v3 = self.v3
        
        # Vector u from v1 to v2
        u = (v2.x - v1.x, v2.y - v1.y, v2.z - v1.z)
        # Vector v from v1 to v3
        v = (v3.x - v1.x, v3.y - v1.y, v3.z - v1.z)
        
        # Cross product to find the normal vector
        n_x = u[1] * v[2] - u[2] * v[1]
        n_y = u[2] * v[0] - u[0] * v[2]
        n_z = u[0] * v[1] - u[1] * v[0]
        
        # Normalize the normal vector
        length = math.sqrt(n_x**2 + n_y**2 + n_z**2)
        if length != 0:
            n_x /= length
            n_y /= length
            n_z /= length
        
        # If model center is provided, check if the normal needs to be flipped
        if model_center:
            # Vector from the face center to the model center
            to_model_center = (
                model_center.x - self.center.x,
                model_center.y - self.center.y,
                model_center.z - self.center.z
            )

            # Dot product between normal and vector to model center
            dot_product = (n_x * to_model_center[0]) + (n_y * to_model_center[1]) + (n_z * to_model_center[2])
            
            # If the dot product is positive, flip the normal
            if dot_product > 0:
                n_x = -n_x
                n_y = -n_y
                n_z = -n_z

        # Set the normal vector 0.01 units away from the center
        offset_length = 0.01
        self.normal.x = self.center.x + n_x * offset_length
        self.normal.y = self.center.y + n_y * offset_length
        self.normal.z = self.center.z + n_z * offset_length
        
        return self
    
    def recalculate_normal(self, model, flip=False):
        self.force_normal_flip = flip
        self.calculate_normal(model.center)

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

        # To avoid recalculating the normal, we can put it on the list as a vertex. it will be rotated as it is supposed to
        vertices_list = [*self.vertices, self.normal]

        # Rotate each vertex
        for vertex in vertices_list:
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
            face.calculate_normal(self.center)
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
        def backface_culling(face:Face):
            face_angle_to_camera = Vertex.three_vertex_angle(face.center, face.normal, camera.position)
            if face_angle_to_camera < 120:
                return True
            return False

        def score_face(face:Face):
            
            d_s = 0
            d_s += Vertex.distance(face.v1, camera.position)
            d_s += Vertex.distance(face.v2, camera.position)
            d_s += Vertex.distance(face.v3, camera.position)
            if face.v4:
                d_s += Vertex.distance(face.v4, camera.position)
            return d_s


        # faces = []
        # for f in self.faces:
        #     if backface_culling(f):
        #         faces.append(f)
        return sorted(self.faces, key=lambda x: score_face(x), reverse=True)
    
    def apply_light_source(self, source:Vertex, intensity:float=1):
        distance_modifier = 0.15
        for face in self.faces:
            adjusted_intensity = float(intensity)
            if adjusted_intensity > 1:
                adjusted_intensity = 1
            d = Vertex.distance(face.center, source)
            adjusted_intensity = adjusted_intensity / (d * distance_modifier)
            
            # A narrow angle means that the face is looking at the light, a broad angle means it's facing away from the light source
            angle = Vertex.three_vertex_angle(face.center, face.normal, source)
            angle_modifier = angle/180
            adjusted_intensity = adjusted_intensity*angle_modifier
            face.light_value = adjusted_intensity

