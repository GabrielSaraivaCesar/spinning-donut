import math
import config

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
        self.rotation = Vertex()
        self.light_value = 0 # 0 to 1
        self.normal = Vertex()
        self.center = Vertex()
        self.calculate_center()
        self.force_normal_flip = False

    def set_mesh(self, mesh):
        self.mesh:Mesh = mesh
    
    def __str__(self) -> str:
        return f"<Face: {self.v1}, {self.v2}, {self.v3}, {self.v4}>"

    def calculate_normal(self, mesh_center=None):
        """
        Calculate the normal vector of the face
        The current implementation has known issues for determining complex mesh normals. TODO: Try implementing a raycast algorithm to count intersections
        """
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
        
        # If mesh center is provided, check if the normal needs to be flipped
        if mesh_center:
            # Vector from the face center to the mesh center
            to_mesh_center = (
                mesh_center.x - self.center.x,
                mesh_center.y - self.center.y,
                mesh_center.z - self.center.z
            )

            # Dot product between normal and vector to mesh center
            dot_product = (n_x * to_mesh_center[0]) + (n_y * to_mesh_center[1]) + (n_z * to_mesh_center[2])
            
            # If the dot product is positive, flip the normal
            if dot_product > 0:
                n_x = -n_x
                n_y = -n_y
                n_z = -n_z
        
        if self.force_normal_flip == True:
            n_x = -n_x
            n_y = -n_y
            n_z = -n_z

        # Set the normal vector 0.01 units away from the center
        offset_length = 0.01
        self.normal.x = self.center.x + n_x * offset_length
        self.normal.y = self.center.y + n_y * offset_length
        self.normal.z = self.center.z + n_z * offset_length
        
        return self
    
    def recalculate_normal(self, mesh, flip=False):
        self.force_normal_flip = flip
        self.calculate_normal(mesh.center)

    def calculate_center(self):
        sum_x, sum_y, sum_z = 0,0,0
        amount_of_vertices = len(self.vertices)
        for vertex in self.vertices:
            sum_x += vertex.x
            sum_y += vertex.y
            sum_z += vertex.z
        
        sum_x /= amount_of_vertices
        sum_y /= amount_of_vertices
        sum_z /= amount_of_vertices

        self.center.x = sum_x
        self.center.y = sum_y
        self.center.z = sum_z
        
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
    
class Mesh:

    def __init__(self, faces:list[Face]) -> None:
        self.faces:list[Face] = faces
        self.computed_vertices_list:list[Vertex] = []
        self.computed_normals_list:list[Vertex] = []
        for face in faces:
            for vertex in face.vertices:
                if vertex not in self.computed_vertices_list:
                    self.computed_vertices_list.append(vertex)
            self.computed_normals_list.append(face.normal)
            face.set_mesh(self)

        self.center:Vertex = Vertex()
        self.calculate_center()
        for face in faces:
            face.calculate_normal(self.center)

        self.rotation = Vertex()
        self.name:str = ""

    def __str__(self) -> str:
        return f"<Mesh with {len(self.faces)} faces>"

    
    
    def calculate_center(self):
        sum_x, sum_y, sum_z = 0,0,0
        amount_of_vertices = len(self.computed_vertices_list)
        for vertex in self.computed_vertices_list:
            sum_x += vertex.x
            sum_y += vertex.y
            sum_z += vertex.z
        
        sum_x /= amount_of_vertices
        sum_y /= amount_of_vertices
        sum_z /= amount_of_vertices

        self.center.x = sum_x
        self.center.y = sum_y
        self.center.z = sum_z
        

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
        """
        Rotate the whole mesh based on rotation matrix https://en.wikipedia.org/wiki/Rotation_matrix (check the 3D Section)
        Rx = [
            [1  0      0 ]
            [0 cosθ -sinθ]
            [0 sinθ  cosθ]
        ]
        Ry = [
            [cosθ  0  sinθ]
            [0     1    0 ]
            [-sinθ 0  cosθ]
        ]
        Rz = [
            [cosθ -sinθ 0]
            [sinθ  cosθ 0]
            [0      0   1]
        ]
        """
        pivot = self.center
        theta_x, theta_y, theta_z = 0, 0, 0
        

        # Calculate rotation differences
        if x is not None:
            theta_x = (x - self.rotation.x) * math.pi / 180  # Convert to radians
            self.rotation.x = x
        
        if y is not None:
            theta_y = (y - self.rotation.y) * math.pi / 180  # Convert to radians
            self.rotation.y = y
        
        if z is not None:
            theta_z = (z - self.rotation.z) * math.pi / 180  # Convert to radians
            self.rotation.z = z


        # To avoid recalculating the normal, we can put it on the list as a vertex. it will be rotated as it is supposed to
        vertices_list = self.computed_normals_list + self.computed_vertices_list

        # Rotate each vertex
        for vertex in vertices_list:
            # Translate vertex to origin (relative to center)
            dx = vertex.x - pivot.x
            dy = vertex.y - pivot.y
            dz = vertex.z - pivot.z


            if theta_x != 0:
                cos_theta_x = math.cos(theta_x)
                sin_theta_x = math.sin(theta_x)
                ny = dy * cos_theta_x - dz * sin_theta_x
                nz = dy * sin_theta_x + dz * cos_theta_x
                dy = ny
                dz = nz
                
            if theta_y != 0:
                cos_theta_y = math.cos(theta_y)
                sin_theta_y = math.sin(theta_y)
                nx = dx * cos_theta_y + dz * sin_theta_y
                nz = -dx * sin_theta_y + dz * cos_theta_y
                dx = nx
                dz = nz
                
            if theta_z != 0:
                cos_theta_z = math.cos(theta_z)
                sin_theta_z = math.sin(theta_z)
                nx = dx * cos_theta_z - dy * sin_theta_z
                ny = dx * sin_theta_z + dy * cos_theta_z
                dx = nx
                dy = ny

            vertex.x = dx + pivot.x
            vertex.y = dy + pivot.y
            vertex.z = dz + pivot.z
        
        for face in self.faces:
            face.calculate_center()

    def depth_sort_faces(self, camera:Camera):
        def backface_culling(face:Face):
            face_angle_to_camera = Vertex.three_vertex_angle(face.center, face.normal, camera.position)
            if face_angle_to_camera < 90:
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


        faces = []
        if config.ENABLE_BACKFACE_CULLING:
            for f in self.faces:
                if backface_culling(f):
                    faces.append(f)
        else:
            faces = self.faces
        # print(f"{len(faces)}/{len(self.faces)}")
        return sorted(faces, key=lambda x: score_face(x), reverse=True)
    
    def apply_light_source(self, source:Vertex, intensity:float=1):
        distance_modifier = 0.1
        for face in self.faces:
            adjusted_intensity = float(intensity)
            d = Vertex.distance(face.center, source)
            adjusted_intensity = adjusted_intensity / (d * distance_modifier)
            
            # A narrow angle means that the face is looking at the light, a broad angle means it's facing away from the light source
            angle = Vertex.three_vertex_angle(face.center, face.normal, source)
            angle_modifier = angle/180
            adjusted_intensity = adjusted_intensity*angle_modifier
            face.light_value = adjusted_intensity


def setup_camera(cam):
    # Camera settings
    cam.display_size.y = config.CAMERA_SETTINGS.get('CHAR_HEIGHT/WIDTH_PROPORTION', 2)
    cam.display_size.x = 1
    sensor_size = config.CAMERA_SETTINGS.get('RECORDING_SENSOR_SIZE', (1, 1, 2))
    cam.recording_surface_size.x = sensor_size[0]
    cam.recording_surface_size.y = sensor_size[1]
    cam.recording_surface_size.z = sensor_size[2]