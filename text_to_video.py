import os
import textwrap
import math
import re
import glob
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

FONT_PATH = '/Library/Fonts/genshingothic-20150607/GenShinGothic-Bold.ttf'
FONT_SIZE = 72
TEXT_COLOR = (255, 0, 0)
BORDER_COLOR = (255, 255, 0) # yellow
IMAGE_SIZE = (1920, 1080)
MAX_WORD_NUM = 100 # temp
WORD_NUM_PER_LINE = 20

insert_image_path = None

def generate_aiff(s, i):
    aiff_path = 'temp/sound/' + '{0:04d}'.format(i) + '.aiff'
    os.system('say -v Kyoko ' + s + ' -o ' + aiff_path)
    return aiff_path

def aiff_to_mp3(aiff_path):
    mp3_path = aiff_path.replace('.aiff', '.mp3')
    command = 'lame --silent -m m ' + aiff_path + ' ' + mp3_path
    os.system(command)
    return mp3_path

def generate_mp4(i):
    mp4_path = get_mp4_path(i)
    mp3_path = get_mp3_path(i)
    png_path = get_png_path(i)
    command = 'ffmpeg -loglevel quiet -framerate 60 -i {0} -i {1} {2}'.format(png_path, mp3_path, mp4_path)
    os.system(command)

def get_png_path(i):
    return 'temp/image/' + '{0:04d}'.format(i) + '.png'

def get_mp3_path(i):
    return 'temp/sound/' + '{0:04d}'.format(i) + '.mp3'

def get_mp4_path(i):
    return 'temp/video/' + '{0:04d}'.format(i) + '.mp4'

def generate_png(s, i):
    output_path = get_png_path(i)
    print(output_path)
    img = Image.new('RGBA', IMAGE_SIZE)
    if insert_image_path is not None:
        insert_image = Image.open(insert_image_path)

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    lines = textwrap.wrap(s, width = WORD_NUM_PER_LINE)

    # for centering, get info
    word_width, word_height = font.getsize('あ')
    text_y = IMAGE_SIZE[1] // 2 - word_height - word_height // 2

    for line in lines:
        width, height = font.getsize(line)
        text_x = IMAGE_SIZE[0] // 2 - width // 2

        position = (text_x, text_y)
        text_y += height

        # outline
        offset = height // 20
        x_list = y_list = [-1, -0.5, 0, 0.5, 1]
        for x in x_list:
            for y in y_list:
                new_x = position[0] + math.floor(x * offset)
                new_y = position[1] + math.floor(y * offset)
                draw.text((new_x, new_y), line, BORDER_COLOR, font=font)

        # main text
        draw.text(position, line, TEXT_COLOR, font=font)
    img.save(output_path)

def make_movie(file_name):
    os.system('rm temp/image/*.png')
    os.system('rm temp/sound/*')
    os.system('rm temp/video/*.mp4')
    os.system('rm temp/output/*.mp4')
    path = 'input/' + file_name
    text_list = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            # delete ruby
            s = re.sub(r'《[^》]+》', "", s)
            text_list.append(s)
    print(text_list)

    for i, text in enumerate(text_list):
        if text == '':
            continue

        if text[0] == '[' and text[-1] == ']':
            print('command', i)
            insert_image_path = text[1:-2]
            print('path', insert_image_path)
        else:
            aiff_path = generate_aiff(text, i)
            aiff_to_mp3(aiff_path)
            generate_png(text, i)
            generate_mp4(i)

    # generate text file
    text_path = 'temp/mp4_input_list.txt'
    mp4_path_list = glob.glob('temp/video/*.mp4')
    f = open(text_path, 'w')
    for mp4_path in mp4_path_list:
        f.write('file ' + mp4_path + '\n')
    f.close()
    # concatenate all mp4
    #os.system('ffmpeg -f concat -i {0} {1}'.format(text_path, 'temp/output/{0}.mp4'.format(file_name)))

if __name__ == '__main__':
    #make_movie('sample.txt')
    make_movie('news_20171011.txt')
