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
shuttle = factory_3d.import_mesh("3d_models/shuttle.obj")
flower = factory_3d.import_mesh("3d_models/flower.obj")


AVAILABLE_MODELS = {
    config.AvailableMeshes.CUBE: cube,
    config.AvailableMeshes.TOROID: toroid,
    config.AvailableMeshes.TOROID_HIGH_POLY: toroid_high_poly,
    config.AvailableMeshes.PYRAMID: pyramid,
    config.AvailableMeshes.SHUTTLE: shuttle,
    config.AvailableMeshes.FLOWER: flower,

}

def draw(mesh, cam, fps=None):
    global screen, last_frame_dirty_pixels
    faces = mesh.depth_sort_faces(cam)
    affected_coords = []
    for face in faces:
        if face:
            dirty_pixels = terminal_drawing.draw_face_on_screen(face, cam, screen, ASCII_LIST)
            if config.ENABLE_DIRTY_RECTANGLES:
                affected_coords += dirty_pixels
    
    if fps is not None and config.ENABLE_FPS_COUNTER:
        terminal_drawing.draw_fps(fps, screen)



    terminal_drawing.draw_screen(screen)
    last_frame_dirty_pixels = affected_coords

    screen = terminal_drawing.get_screen_matrix()

def start():
    global TARGET_FPS, ASCII_LIST, cam, light_source, light_intensity, active_mesh, rx, ry, rz, real_fps, frame_count, execution_start, last_time, screen

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

    #-- mesh data --#
    active_mesh = AVAILABLE_MODELS[config.ACTIVE_MODEL]
    rx = 0
    ry = 0
    rz = 0

    #-- FPS Measure --#
    real_fps = 0
    frame_count = 0
    execution_start = time.time()
    last_time = None
    screen = terminal_drawing.get_screen_matrix()


def update():
    update_rotation_values()
    active_mesh.rotate_to(x=rx, y=ry, z=rz)
    active_mesh.apply_light_source(light_source, light_intensity)

    draw(active_mesh, cam, real_fps)

    

def sgint_handler(signal, frame):
    terminal_drawing.show_cursor()
    if config.ENABLE_SAVE_LOGS:
        faces = len(active_mesh.faces)
        name = active_mesh.name
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

    cam_speed = config.CAMERA_SETTINGS.get('SPEED', 10)
    cam_rot_speed = config.CAMERA_SETTINGS.get('ROTATION_SPEED', 10)
    if keyboard.is_pressed('w'):
        # cam.relative_move(0, 0, cam_speed*delta_time)
        cam.recording_surface_size.z += cam_speed*delta_time
    elif keyboard.is_pressed('s'):
        # cam.relative_move(0, 0, -cam_speed*delta_time)
        cam.recording_surface_size.z -= cam_speed*delta_time
    if keyboard.is_pressed('a'):
        utils_3d.Vertex.rotate_vertices_based_on_pivot_point(active_mesh.center, [cam.position], 0, cam_rot_speed*delta_time, 0)
        cam.look_at_target(active_mesh.center)
    elif keyboard.is_pressed('d'):
        utils_3d.Vertex.rotate_vertices_based_on_pivot_point(active_mesh.center, [cam.position], 0, -cam_rot_speed*delta_time, 0)
        cam.look_at_target(active_mesh.center)


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

    update()
    frame_count+=1