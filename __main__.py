from lib_3d import factory_3d, utils_3d
import os
import terminal_drawing
import time
import sys, signal

def draw(model, cam, fps=None):
    screen = terminal_drawing.get_screen_matrix()
    faces = model.depth_sort_faces(cam)
    for face in faces:
        terminal_drawing.draw_face_on_screen(face, cam, screen, ASCII_LIST)
    
    if fps is not None:
        terminal_drawing.draw_fps(fps, screen)
    terminal_drawing.draw_screen(screen)

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
    cam.recording_surface_size.z = 0.5

SAVE_LOGS = False
TARGET_FPS = 1000
ASCII_LIST = terminal_drawing.generate_ascii_list()
terminal_drawing.hide_cursor()
signal.signal(signal.SIGINT, sgint_handler)

cube = factory_3d.cube_factory(2)
toroid = factory_3d.toroid_factory(2, 1, resolution=50)
cam = utils_3d.Camera(utils_3d.Vertex(0, 0, -4))
setup_camera(cam)


active_model = toroid
r = 0

# FPS Measure
real_fps = 0
frame_count = 0
execution_start = time.time()
last_time = 0

while True:
    current_time = time.time()
    delta_time = current_time - last_time
    real_fps = 1/delta_time
    last_time = current_time

    exec_time = time.time()
    screen = draw(active_model, cam, real_fps)
    active_model.rotate_to(y=r, x=r, z=-1*r)
    r+= 10 * delta_time
    exec_time = time.time()-exec_time

    sleep_time = 1/TARGET_FPS
    if exec_time < sleep_time:
        sleep_time -= exec_time # Account for execution time

    frame_count+=1
    time.sleep(sleep_time)