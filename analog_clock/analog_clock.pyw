import math
import pygame
from pygame.locals import *
from PIL import Image, ImageFilter
from datetime import datetime
from ctypes import windll
import win32gui
import win32con
import win32api
import json
import sys
import os

# initializing pygame and mixer
pygame.init()

# getting and setting last position
with open('./assets/position.json') as file:
    data = json.load(file)
    file.close()

pos_x = data['position']["x_pos"]
pos_y = data['position']["y_pos"]
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (pos_x, pos_y)


# creating required variables
fps = 60

screen_resize_width = screen_width = data['screen_size']
screen_resize_height = screen_height = data['screen_size']

clock_face_size = data['clock_face_size']
clock_img_count = data['clock_img_count']
clock_img_path = f'./assets/clock{clock_img_count}.png'

dot_width1 = data['dot_width1']
dot_width2 = data['dot_width2']

hour_hand_width = data['hour_hand_width']
hour_hand_height = data['hour_hand_height']
hour_hand_pivot_width = data['hour_hand_pivot_width']
hour_hand_pivot_height = data['hour_hand_pivot_height']

minutes_hand_width = data['minutes_hand_width']
minutes_hand_height = data['minutes_hand_height']
minutes_hand_pivot_width = data['minutes_hand_pivot_width']
minutes_hand_pivot_height = data['minutes_hand_pivot_height']

seconds_hand_width = data['seconds_hand_width']
seconds_hand_height = data['seconds_hand_height']
seconds_hand_pivot_width = data['seconds_hand_pivot_width']
seconds_hand_pivot_height = data['seconds_hand_pivot_height']

resize_and_noframe = pygame.NOFRAME

ctrl_pressed = False
window_resizing = False
run = True

clock = pygame.time.Clock()
timer = 0
dt = 0
running = True

pressed = False
start_pos = (0, 0)
window_coords = [-pos_x, -pos_y]


# defining colours
BG = (0, 51, 102)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (66, 81, 245)
YELLOW = (245, 237, 12)


# creating pygame display window
screen = pygame.display.set_mode((screen_width, screen_height), resize_and_noframe)

# logic for transparent window
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
# Set window transparency color
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*BG), 0, win32con.LWA_COLORKEY)

# function for resize the window
def moveWin(coordinates):
    hwnd = pygame.display.get_wm_info()['window']
    w, h = pygame.display.get_surface().get_size()
    windll.user32.MoveWindow(hwnd, -coordinates[0], -coordinates[1], w, h, False)

moveWin(window_coords)

# scaling the image
def scale_smooth(path, size):
    loaded_image = pygame.image.load(path)
    return pygame.transform.smoothscale(loaded_image, size)

# function to change pygame image to PIL image then rotate it and change back to pygame image
def pygameTO_pil_rotate_TOpygame(image, angle):
    pil_string_image = pygame.image.tostring(image, "RGBA",False)
    pil_image = Image.frombytes("RGBA", image.get_size(), pil_string_image)
    pil_rotated_img = pil_image.rotate(angle, Image.BICUBIC, expand=True)
    rotated_image = pygame.image.fromstring(pil_rotated_img.tobytes(), pil_rotated_img.size, pil_rotated_img.mode)
    return rotated_image

# function for set the image at pivot point on given position and draw the image at screen
def blitRotate(surf, image, origin, pivot, angle):
    image_rect = image.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
    offset_center_to_pivot = pygame.math.Vector2(origin) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
    rotated_image = pygameTO_pil_rotate_TOpygame(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    surf.blit(rotated_image, rotated_image_rect) # drawing the image

while run:
    clock.tick(fps) # setting fps
    pygame.draw.rect(screen, BG, (0, 0, screen_width, screen_height)) # drawing transparent rectangle

    # getting time
    now = datetime.now()
    hour = int(now.strftime("%I"))
    minute = int(now.strftime("%M"))
    seconds = int(now.strftime("%S"))

    # loading image
    clock_face_img = scale_smooth(clock_img_path, (clock_face_size, clock_face_size))
    h_hand_img = scale_smooth('./assets/hourpng.png', (hour_hand_width, hour_hand_height))
    m_hand_img = scale_smooth('./assets/minutepng.png', (minutes_hand_width, minutes_hand_height))
    s_hand_img = scale_smooth('./assets/secpng.png', (seconds_hand_width, seconds_hand_height))

    #drawing the clockface, hands and dot
    screen.blit(clock_face_img, ((screen_width-clock_face_img.get_width())//2, (screen_height-clock_face_img.get_height())//2))
    hour_angle = 360-(int(0.5*minute)+(hour*30))
    blitRotate(screen, h_hand_img, (screen_width//2, screen_height//2), (hour_hand_pivot_width, hour_hand_pivot_height), hour_angle)
    blitRotate(screen, m_hand_img, (screen_width//2, screen_height//2), (minutes_hand_pivot_width, minutes_hand_pivot_height), 360-minute*6)
    blitRotate(screen, s_hand_img, (screen_width//2, screen_height//2), (seconds_hand_pivot_width, seconds_hand_pivot_height), 360-seconds*6)
    pygame.draw.circle(screen, BLACK, (screen_width//2, screen_height//2), dot_width1)
    pygame.draw.circle(screen, RED, (screen_width//2, screen_height//2), dot_width2)

    # evevts listener
    for event in pygame.event.get():   
        #window moving logic
        if event.type == MOUSEBUTTONDOWN:
            # double click logic
            if event.button == 1:
                if timer == 0:  # First mouse click.
                    timer = 0.001  # Start the timer.
                # Click again before 0.5 seconds to double click.
                elif timer < 0.5:
                    if pygame.mouse.get_pos()[0] < screen_width//2:
                        clock_img_count -= 1
                    else:
                        clock_img_count += 1

                    if clock_img_count == 4:
                        clock_img_count = 1
                    elif clock_img_count == 0:
                        clock_img_count = 3
                    clock_img_path = f"./assets/clock{clock_img_count}.png"
                    timer = 0

            pressed = True
            start_pos = pygame.mouse.get_pos()

        elif event.type == MOUSEMOTION:
            if pressed:
                new_pos = pygame.mouse.get_pos()
                window_coords[0] += start_pos[0] - new_pos[0]
                window_coords[1] += start_pos[1] - new_pos[1]
                moveWin(window_coords)
        elif event.type == MOUSEBUTTONUP:
            pressed = False
            

        # key listener
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                ctrl_pressed = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                ctrl_pressed = True

            # quit window
            if event.key == pygame.K_ESCAPE:
                run = False
        
        # mouse wheel listener
        if event.type == MOUSEWHEEL and ctrl_pressed:
            # for one wheel rotation the width and height will chage by 25
            if event.y == 1:
                screen_resize_width += 25
                if screen_resize_width > 350: screen_resize_width = 350 # max size
            else:
                screen_resize_width -= 25
                if screen_resize_width < 200: screen_resize_width = 200 # min size
        

            resized_width = resized_height = screen_resize_width # setting new width and height
                

            # max and min size
            if resized_width > 350: resized_width = 350
            elif resized_width < 200: resized_width = 200

            # calculation for width or height change percentage
            change_percentage = round(((screen_width-resized_width)/screen_width)*100)
            
            # calculation for new clock face size
            resized_clock_face_size = round(-((change_percentage/100)*clock_face_size)+clock_face_size)
            clock_face_size = resized_clock_face_size
            
            # calculation for dot1 width size
            resized_dot_width1 = round(-((change_percentage/100)*dot_width1)+dot_width1)
            dot_width1 = resized_dot_width1
            
            # calculation for dot2 width size
            resized_dot_width2 = math.floor(dot_width1/2)+1
            dot_width2 = resized_dot_width2
            

            # function for dinamically calculating clock hands width, height, change percentage and pivot point
            def clock_hands_size_and_pivot_calculation(width_or_height, pivot_width_or_height):
                # calculating width or height
                resized_hands_width_or_height = round(-((change_percentage/100)*width_or_height)+width_or_height)
                # calulating width or height change percentage
                hand_pivot_width_change_percent = round((resized_hands_width_or_height/width_or_height)*100)
                # calculating clock hands pivot width and height
                resized_hand_pivot_point = abs(round(-((hand_pivot_width_change_percent/100)*pivot_width_or_height)))
                return resized_hands_width_or_height, hand_pivot_width_change_percent, resized_hand_pivot_point

            # seconds hand setting new width and height
            resized_seconds_hand_width, seconds_hand_pivot_width_change_percent, seconds_hand_pivot_width = clock_hands_size_and_pivot_calculation(seconds_hand_width, seconds_hand_pivot_width)
            resized_seconds_hand_height, seconds_hand_pivot_height_change_percent, seconds_hand_pivot_height = clock_hands_size_and_pivot_calculation(seconds_hand_height, seconds_hand_pivot_height)
            seconds_hand_width, seconds_hand_height = resized_seconds_hand_width, resized_seconds_hand_height # setting new width and height

            # minutes hand setting new width and height
            resized_minutes_hand_width, minutes_hand_pivot_width_change_percent, minutes_hand_pivot_width = clock_hands_size_and_pivot_calculation(minutes_hand_width, minutes_hand_pivot_width)
            resized_minutes_hand_height, minutes_hand_pivot_height_change_percent, minutes_hand_pivot_height = clock_hands_size_and_pivot_calculation(minutes_hand_height, minutes_hand_pivot_height)
            minutes_hand_width, minutes_hand_height = resized_minutes_hand_width, resized_minutes_hand_height # setting new width and height

            # hour hand setting new width and height
            resized_hour_hand_width, hour_hand_pivot_width_change_percent, hour_hand_pivot_width = clock_hands_size_and_pivot_calculation(hour_hand_width, hour_hand_pivot_width)
            resized_hour_hand_height, hour_hand_pivot_height_change_percent, hour_hand_pivot_height = clock_hands_size_and_pivot_calculation(hour_hand_height, hour_hand_pivot_height)
            hour_hand_width, hour_hand_height = resized_hour_hand_width, resized_hour_hand_height # setting new width and height


            # resetting original height, width and pivot point for all the image when window in max size
            if resized_width > 330:
                clock_face_size = 300
                dot_width1 = 13
                dot_width2 = 7
                hour_hand_width = 26
                hour_hand_height = 120
                hour_hand_pivot_width = 13
                hour_hand_pivot_height = 107
                minutes_hand_width = 30
                minutes_hand_height = 135
                minutes_hand_pivot_width = 15
                minutes_hand_pivot_height = 123
                seconds_hand_width = 18
                seconds_hand_height = 185
                seconds_hand_pivot_width = 10
                seconds_hand_pivot_height = 139


            # setting new screen size
            screen_width, screen_height = resized_width, resized_width
            screen = pygame.display.set_mode((screen_width, screen_height), resize_and_noframe)
            
            
        #quit window
        if event.type == pygame.QUIT:
            run = False

    # Increase timer after mouse was pressed the first time.
    if timer != 0:
        timer += dt
        # Reset after 0.5 seconds.
        if timer >= 0.5:
            timer = 0
    dt = clock.tick(30) / 1000


    # updating pygame display
    pygame.display.update()


# changing new window spawn position and size
data['position']["x_pos"] = -window_coords[0]
data['position']["y_pos"] = -window_coords[1]
data['screen_size'] = screen_width
data['clock_face_size'] = clock_face_size 
data['clock_img_count'] = clock_img_count
data['dot_width1'] = dot_width1 
data['dot_width2'] = dot_width2 
data['hour_hand_width'] = hour_hand_width 
data['hour_hand_height'] = hour_hand_height 
data['hour_hand_pivot_width'] = hour_hand_pivot_width         
data['hour_hand_pivot_height'] = hour_hand_pivot_height       
data['minutes_hand_width'] = minutes_hand_width 
data['minutes_hand_height'] = minutes_hand_height 
data['minutes_hand_pivot_width'] = minutes_hand_pivot_width   
data['minutes_hand_pivot_height'] = minutes_hand_pivot_height 
data['seconds_hand_width'] = seconds_hand_width 
data['seconds_hand_height'] = seconds_hand_height
data['seconds_hand_pivot_width'] = seconds_hand_pivot_width
data['seconds_hand_pivot_height'] = seconds_hand_pivot_height
# rewriting position.json
with open('./assets/position.json', 'w') as file:
    json.dump(data, file, indent= 4)
    file.close()


# quit pygame
pygame.quit()
sys.exit()