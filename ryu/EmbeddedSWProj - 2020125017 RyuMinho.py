import time
import random
import numpy as np
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont, ImageChops
import adafruit_rgb_display.st7789 as st7789

"""
    @@@@@ initial setting @@@@@
"""
# Create the display
cs_pin = DigitalInOut(board.CE0)
dc_pin = DigitalInOut(board.D25)
reset_pin = DigitalInOut(board.D24)
BAUDRATE = 24000000

spi = board.SPI()
disp = st7789.ST7789(
    spi,
    height=240,
    y_offset=80,
    rotation=180,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# Input pins:
button_A = DigitalInOut(board.D5)
button_A.direction = Direction.INPUT

button_B = DigitalInOut(board.D6)
button_B.direction = Direction.INPUT

button_L = DigitalInOut(board.D27)
button_L.direction = Direction.INPUT

button_R = DigitalInOut(board.D23)
button_R.direction = Direction.INPUT

button_U = DigitalInOut(board.D17)
button_U.direction = Direction.INPUT

button_D = DigitalInOut(board.D22)
button_D.direction = Direction.INPUT

button_C = DigitalInOut(board.D4)
button_C.direction = Direction.INPUT

# Turn on the Backlight
backlight = DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = True

# Create blank image for drawing.
# Make sure to create image with mode 'RGBA' for color.
width = disp.width
height = disp.height
image = Image.new("RGBA", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)

# Loading display. and 
doraemon = Image.open("bamboo_dor.png")
doraemon_bg = doraemon.resize((width, height))
disp.image(doraemon_bg)
time.sleep(1)

# Game Start display
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
rcolor = tuple(int(x * 255) for x in hsv_to_rgb(random.random(), 1, 1))
draw.text((-1, 100), "[[GAME START]]", font=fnt, fill=rcolor)
disp.image(image)
time.sleep(2)

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)
disp.image(image)

#BackGround
bg_temp = Image.open("background.png")
bg = bg_temp.resize((240, 240))

#Doraemon
doraemon_character = doraemon.resize((50, 50))

#Jin Gu
jingu_temp = Image.open("bamboo_njg.png")
jingu_character = jingu_temp.resize((30, 30))

#ultimate skill 1 : defenses all attacks for 10sec
ultimate_1_temp = Image.open("ultimate_skill1.png")
ultimate_1 = ultimate_1_temp.resize((30, 30))
last_ultimate_1 = time.time()

#ultimate skill 2 : increase the velocity of doraemon
ultimate_2_temp = Image.open("ultimate_skill2.png")
ultimate_2 = ultimate_2_temp.resize((30, 30))
last_ultimate_2 = time.time()


"""
        @@@@@Global Variables@@@@@
"""

#initializing DORAEMON LOCATION
dor_loc_x = 120
dor_loc_y = 120
dor_velocity = 5

#initializing laser location
rand_float = 1 # this variable decides the area of laser
velocity_of_laser = 10
laser_loc_x = random.randint(15, 225)
laser_loc_y = 0
root_rand_float = 1

# 1 stage per 10 scores
stage = 1
stage_up_available = False

#score
prev_score = -1
score = 0

#Variables Related to ultimate skill 1
prev_time_1 = time.time()
curr_time_skill_1 = 0
lasting_time_1 = 5

#Variables Related to ultimate skill 2
prev_time_2 = time.time()
button_pressed_2 = True
curr_time_skill_2 = 0
lasting_time_2 = 5


"""
        @@@@@FUNCTIONS@@@@@
"""
# the function that draws doraemon
def Doraemon(x_dor, y_dor, doraemon):
    #draw.rectangle((x_dor - 20, y_dor - 20, x_dor + 20, y_dor + 20), outline=(255, 255, 255), fill=(70, 161, 222))
    image.paste(doraemon, (x_dor - 20,y_dor - 20), doraemon)


# this function draws laser with jingu, and judges whether doraemon was damaged or not
def Laser(jingu):
    global dor_loc_x
    global dor_lox_y
    global laser_loc_x
    global laser_loc_y
    global velocity_of_laser
    global score
    global root_rand_float
    
    # the x coordinate of laser. the random coordinate is designated in the range +- 80 of doraemon
    # the y coordinate of laser. if y >= 240 (laser arrives at the bottom, user get 1 score)
    laser_loc_y += velocity_of_laser
    if laser_loc_y >= 240:
        if dor_loc_x - 80 <= 15:
            laser_loc_x = random.randint(15, dor_loc_x + 80)
        elif dor_loc_x + 80 >= 225:
            laser_loc_x = random.randint(dor_loc_x - 80, 225)
        else:
            laser_loc_x = random.randint(dor_loc_x - 80, dor_loc_x + 80)
        laser_loc_y = 0
        score += 1
    
    # if over stage 1, difficulty goes up for every stage
    if stage > 1:
        root_rand_float = np.sqrt(random.uniform(0.8, 1.2) * stage)
    #this part draws laser. variables below are used to draw triangle coordinate
    top_x = laser_loc_x
    top_y = laser_loc_y
    left_x = laser_loc_x - 5 * root_rand_float
    bottom_y = laser_loc_y + 8.66 * root_rand_float
    right_x = laser_loc_x + 5 * root_rand_float
    
    #jingu appears at the top of the display. and laser comes out on his center
    image.paste(jingu, (laser_loc_x - 15, 0), jingu)
    
    #laser drawing
    draw.polygon([(top_x, top_y), (left_x, bottom_y), (right_x, bottom_y)],
                 outline=(random.randint(-100, 100) % 256, random.randint(-100, 100) % 256, random.randint(-100, 100) % 256),
                 fill=(255, 0, 0))
    
    #judging box
    #draw.rectangle((dor_loc_x - 15, dor_loc_y - 15, dor_loc_x + 20, dor_loc_y + 25), outline=0, fill=(255, 255, 255))
    
    # if laser touches doraemon, exit the game
    end_game(top_x, top_y, left_x, bottom_y, right_x)


# Ultimate Skill 1 is to avoid all the attacks from doraemon.
def ultimate_skill_1(dor_loc_x, dor_loc_y):
    
    global curr_time_skill_1
    global prev_time_1
    global lasting_time_1
    
    # if user used skill and no time remaining
    if lasting_time_1 < 0.1:
        prev_time_1 = time.time()
        curr_time_skill_1 = time.time()
        lasting_time_1 = 5
        image.paste(ultimate_1, (210, 240), ultimate_1)
        return False
    
    #if there is time remaining
    if lasting_time_1 >= 0.1 and curr_time_skill_1 - prev_time_1 >= 30:
        image.paste(ultimate_1, (210, 210), ultimate_1)
        # if #5 button pressed
        if not button_A.value:
            draw.ellipse((dor_loc_x - 25, dor_loc_y - 25, dor_loc_x + 25, dor_loc_y + 35),
                 fill = (random.randint(-100, 100) % 256, random.randint(-100, 100) % 256, random.randint(-100, 100) % 256),
                 outline = (255, 255, 0))
            #because this function is called twice, here and in end_game, so the using time is half
            #it lasts for 5 secs.
            lasting_time_1 = lasting_time_1 - 0.05
            curr_time_skill_1 = time.time()
            return True
        return False
    else :
        return False
    
    
def ultimate_skill_2():
    
    global dor_velocity
    global prev_time_2
    global curr_time_skill_2
    global lasting_time_2
    global button_pressed_2
    
    # if user used skill and no time remaining
    if lasting_time_2 < 0.1: 
        prev_time_2 = time.time()
        curr_time_skill_2 = time.time()
        lasting_time_2 = 5
        dor_velocity = 5
        button_pressed_2 = True
        image.paste(ultimate_2, (210, 240), ultimate_2)
    
    # if there is time remaining
    if lasting_time_2 >= 0.1 and curr_time_skill_2 - prev_time_2 >= 30:
        image.paste(ultimate_2, (180, 210), ultimate_2)
        # if #6 button pressed
        if not button_B.value:
            if button_pressed_2:
                dor_velocity = dor_velocity * 2
                button_pressed_2 = False
            # it lasts for 5s
            lasting_time_2 = lasting_time_2 - 0.1
            curr_time_skill_2 = time.time()
        else:
            dor_velocity = 5
            button_pressed_2 = True
            
                
def stage_up():
    global score
    global prev_score
    global stage
    
    if score % 10 == 0 and score > 0 and not score == prev_score:
        stage = stage + 1
        
        
def end_game(top_x, top_y, left_x, bottom_y, right_x):
    
    if not ultimate_skill_1(dor_loc_x, dor_loc_y):
        if dor_loc_y - 15 <= bottom_y and dor_loc_y + 25 >= top_y:
            if right_x >= dor_loc_x - 15 and left_x <= dor_loc_x + 20:
                for i in range(5):
                    draw.rectangle((0, 0, width, height), outline=0, fill=0)
                    draw.text((45, 80), "|| JIN GU ||",font=fnt, fill=rcolor)
                    disp.image(image)
                    time.sleep(0.3)
                    draw.text((30, 140),"||GOT YOU||", font=fnt, fill=rcolor)
                    time.sleep(0.3)
                    draw.text((40, 200), "SCORE", font=fnt, fill=rcolor)
                    draw.text((150, 200), str(score), font=fnt, fill=rcolor)
                    disp.image(image)
                time.sleep(2)
                exit()
                

def Up(y):
    if y <= 30:
       y = 30
    else:
        global dor_loc_y
        global dor_velocity
        dor_loc_y -= dor_velocity
        y -= dor_velocity
    return y


def Down(y):
    if y >= 210:
        y = 210
    else:
        global dor_loc_y
        global dor_velocity
        dor_loc_y += dor_velocity
        y += dor_velocity
    return y


def Left(x):
    if x <= 30:
        x = 30
    else:
        global dor_loc_x
        global dor_velocity
        dor_loc_x -= dor_velocity
        x -= dor_velocity
    return x


def Right(x):
    if x >= 210:
        x = 210
    else:
        global dor_loc_x
        global dor_velocity
        dor_loc_x += dor_velocity
        x += dor_velocity
    return x


"""
    @@@@@LOOP@@@@@
"""
while True:
    #background
    image.paste(bg, (0, 0), bg)
    
    #score board
    draw.text((0, 0), str(score), font=fnt, fill=(0, 0, 0))
    #draw.text((0, 200), str(stage), font=fnt, fill=(0, 0, 0))
    
    curr_time_skill_1 = time.time()
    curr_time_skill_2 = time.time()
    
    # buttons moving doraemon
    if not button_U.value:  # up pressed
        Up(dor_loc_y)
    
    if not button_D.value:  # down pressed
        Down(dor_loc_y)
    
    if not button_L.value:  # left pressed
        Left(dor_loc_x)

    if not button_R.value:  # right pressed
        Right(dor_loc_x)
        
    if not button_C.value:  # center pressed
        pass
    
    # if curr_time_skill_1 - prev_time >= 30s, activete skill 1 button
    ultimate_skill_1(dor_loc_x, dor_loc_y)
    
     # if curr_time_skill_2 - prev_time >= 30s, activete skill 2 button
    ultimate_skill_2()
    
    # this function is to move doraemon
    Doraemon(dor_loc_x, dor_loc_y, doraemon_character)
    
    #this function draws laser
    Laser(jingu_character)
    
    # Display the Image
    disp.image(image)
    
    # Clear Display
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    
    # whenever user gets 10 scores, 1 stage level up
    stage_up()
    
    prev_score = score
    
    # check the weight changes of the laser area
    #print(root_rand_float)
    

    time.sleep(0.01)