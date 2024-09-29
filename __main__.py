from lib_3d import factory_3d, utils_3d
import os
import terminal_drawing
import time
import sys, signal
import keyboard

def draw(model, cam, screen, fps=None):
    
    faces = model.depth_sort_faces(cam)
    affected_coords = []
    for face in faces:
        if face:
            affected_coords += terminal_drawing.draw_face_on_screen(face, cam, screen, ASCII_LIST)
    
    if fps is not None:
        terminal_drawing.draw_fps(fps, screen)
    terminal_drawing.draw_screen(screen)
    for coord in affected_coords: # No need to iterate through all the matrix. Only the pixels that were changed
        screen[coord[1]][coord[0]] = None

def sgint_handler(signal, frame):
    terminal_drawing.show_cursor()
    if SAVE_LOGS:
        faces = len(active_model.faces)
        name = active_model.name
        fps = "{:.2f}".format(frame_count / (time.time() - execution_start))
        log_line = f"\n| {name} | {faces} | {fps} |"
        with open('./performance_logs.md', '+a') as file:
            file.write(log_line)
    sys.exit(0)

def setup_camera(cam):
    # Camera settings
    terminal_size = os.get_terminal_size()
    w = terminal_size.columns
    h = terminal_size.lines
    aspect_ratio = w/h
    cam.display_size.y = 1 
    cam.display_size.x = cam.display_size.y / (aspect_ratio / 2)

    cam.recording_surface_size.x = 1
    cam.recording_surface_size.y = 1
    cam.recording_surface_size.z = 2


def update_rotation_values():
    global rx, ry, rz, delta_time
    d_x = 0
    if keyboard.is_pressed('down'):
        d_x = rotation_speed * delta_time
    elif keyboard.is_pressed('up'):
        d_x = rotation_speed * delta_time * -1
    rx += d_x
    
    d_y = 0
    if keyboard.is_pressed('left'):
        d_y = rotation_speed * delta_time
    elif keyboard.is_pressed('right'):
        d_y = rotation_speed * delta_time * -1
    ry += d_y
    
    d_z = 0
    if keyboard.is_pressed(','):
        d_z = rotation_speed * delta_time
    elif keyboard.is_pressed('.'):
        d_z = rotation_speed * delta_time * -1
    rz += d_z


SAVE_LOGS = False
TARGET_FPS = 1000
ASCII_LIST = terminal_drawing.generate_ascii_list()
terminal_drawing.hide_cursor()
signal.signal(signal.SIGINT, sgint_handler)

cube = factory_3d.cube_factory(3)
toroid = factory_3d.toroid_factory(2, 1, resolution=20)
pyramid = factory_3d.pyramid_factory(4, 3)
# shuttle = factory_3d.import_model("3d_models/shuttle.obj")
cam = utils_3d.Camera(utils_3d.Vertex(0, 0, -10))
light_source = utils_3d.Vertex(10, -10, -10)
light_intensity = 1
setup_camera(cam)


active_model = toroid
rx = 0
ry = 0
rz = 0
rotation_speed = 50

# FPS Measure
real_fps = 0
frame_count = 0
execution_start = time.time()
last_time = None
screen = terminal_drawing.get_screen_matrix()
while True:
    current_time = time.time()
    if last_time is None:
        delta_time = 0
    else:
        delta_time = current_time - last_time
    
    if delta_time > 0:
        real_fps = 1/delta_time
    last_time = current_time

    exec_time = time.time()
    update_rotation_values()
    active_model.rotate_to(x=rx, y=ry, z=rz)
    active_model.apply_light_source(light_source, light_intensity)

    draw(active_model, cam, screen, real_fps)
    
    
    


    exec_time = time.time()-exec_time
    sleep_time = 1/TARGET_FPS
    if exec_time < sleep_time:
        sleep_time -= exec_time # Account for execution time

    frame_count+=1
    time.sleep(sleep_time)