from lib_3d import factory_3d, utils_3d
import os
import terminal_drawing
import time
import sys, signal
import keyboard
import config


cube = factory_3d.cube_factory(3)
toroid = factory_3d.toroid_factory(2, 1, resolution=20)
toroid_high_poly = factory_3d.toroid_factory(2, 1, resolution=50)
pyramid = factory_3d.pyramid_factory(4, 3)
shuttle = factory_3d.import_model("3d_models/shuttle.obj")

AVAILABLE_MODELS = {
    config.AvailableModels.CUBE: cube,
    config.AvailableModels.TOROID: toroid,
    config.AvailableModels.TOROID_HIGH_POLY: toroid_high_poly,
    config.AvailableModels.PYRAMID: pyramid,
    config.AvailableModels.SHUTTLE: shuttle
}

def draw(model, cam, fps=None):
    global screen, last_frame_dirty_pixels
    faces = model.depth_sort_faces(cam)
    affected_coords = []
    for face in faces:
        if face:
            dirty_pixels = terminal_drawing.draw_face_on_screen(face, cam, screen, ASCII_LIST)
            if config.ENABLE_DIRTY_RECTANGLES:
                affected_coords += dirty_pixels
    
    if fps is not None:
        dirty_pixels = terminal_drawing.draw_fps(fps, screen)
        if config.ENABLE_DIRTY_RECTANGLES:
            affected_coords += dirty_pixels

    if not config.ENABLE_DIRTY_RECTANGLES:
        terminal_drawing.draw_screen(screen)
        screen = terminal_drawing.get_screen_matrix()

    # Clean last frame dirty pixels
    negative_dirty_pixels = []
    # if last_frame_dirty_pixels:
    #     for coord in last_frame_dirty_pixels:
    #         pixel = screen[coord[1]][coord[0]]
    #         if pixel is None:
    #             continue
    #         if len(pixel) == 1: # Pixel is not marked to draw in this frame, so we can clear it
    #             negative_dirty_pixels.append(coord)
                

    terminal_drawing.draw_screen(screen, affected_coords, negative_dirty_pixels)
    last_frame_dirty_pixels = affected_coords


def start():
    global TARGET_FPS, ASCII_LIST, cam, light_source, light_intensity, active_model, rx, ry, rz, real_fps, frame_count, execution_start, last_time, screen, last_frame_dirty_pixels
    TARGET_FPS = 1000 # TODO - REMOVE

    #-- terminal configs --#
    ASCII_LIST = terminal_drawing.generate_ascii_list()
    terminal_drawing.hide_cursor()
    signal.signal(signal.SIGINT, sgint_handler)

    #-- camera --#
    cam = utils_3d.Camera(
        utils_3d.Vertex(
            *config.CAMERA_SETTINGS.get('POSITION', (0,0,-5))
            )
        )
    utils_3d.setup_camera(cam)

    #-- light source --#
    light_source = utils_3d.Vertex(*config.LIGHT_SOURCE.get('POSITION', (0,0,-5)))
    light_intensity = config.LIGHT_SOURCE.get('INTENSITY', 1)

    #-- model data --#
    active_model = AVAILABLE_MODELS[config.ACTIVE_MODEL]
    rx = 0
    ry = 0
    rz = 0

    #-- FPS Measure --#
    real_fps = 0
    frame_count = 0
    execution_start = time.time()
    last_time = None
    screen = terminal_drawing.get_screen_matrix()
    last_frame_dirty_pixels=[]

def update():
    update_rotation_values()
    active_model.rotate_to(x=rx, y=ry, z=rz)
    active_model.apply_light_source(light_source, light_intensity)

    draw(active_model, cam, real_fps)

    

def sgint_handler(signal, frame):
    terminal_drawing.show_cursor()
    if config.ENABLE_SAVE_LOGS:
        faces = len(active_model.faces)
        name = active_model.name
        fps = "{:.2f}".format(frame_count / (time.time() - execution_start))
        log_line = f"\n| {name} | {faces} | {fps} |"
        with open('./performance_logs.md', '+a') as file:
            file.write(log_line)
    sys.exit(0)


def update_rotation_values():
    global rx, ry, rz, delta_time
    if config.ENABLE_USER_CONTROL is False:
        rx += config.ROTATION_SPPEED * delta_time
        ry += config.ROTATION_SPPEED * delta_time
        rz += config.ROTATION_SPPEED * delta_time
        return
    d_x = 0
    if keyboard.is_pressed('down'):
        d_x = config.ROTATION_SPPEED * delta_time
    elif keyboard.is_pressed('up'):
        d_x = config.ROTATION_SPPEED * delta_time * -1
    rx += d_x
    
    d_y = 0
    if keyboard.is_pressed('left'):
        d_y = config.ROTATION_SPPEED * delta_time
    elif keyboard.is_pressed('right'):
        d_y = config.ROTATION_SPPEED * delta_time * -1
    ry += d_y
    
    d_z = 0
    if keyboard.is_pressed(','):
        d_z = config.ROTATION_SPPEED * delta_time
    elif keyboard.is_pressed('.'):
        d_z = config.ROTATION_SPPEED * delta_time * -1
    rz += d_z



start()
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
    
    update()
    exec_time = time.time()-exec_time
    frame_count+=1
    sleep_time = 1/TARGET_FPS
    if exec_time < sleep_time:
        sleep_time -= exec_time # Account for execution time

    # time.sleep(sleep_time)