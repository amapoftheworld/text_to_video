import os
import textwrap
import math
import re
import glob
import time
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

FONT_PATH = '/Library/Fonts/genshingothic-20150607/GenShinGothic-Bold.ttf'
FONT_SIZE = 72
TEXT_COLOR = (255, 255, 255)
BORDER_COLOR = (0, 0, 0)
IMAGE_SIZE = (1920, 1080)
MAX_WORD_NUM = 100 # temp
WORD_NUM_PER_LINE = 20

insert_image_path = None
speaker = 'Kyoko'


def generate_aiff(s, i):
    aiff_path = 'temp/sound/' + '{0:04d}'.format(i) + '.aiff'
    os.system('say -v {0} '.format(speaker) + s + ' -o ' + aiff_path)
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
    command = 'ffmpeg -loglevel quiet -framerate 30 -i {0} -i {1} {2}'.format(png_path, mp3_path, mp4_path)
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
        W, H = img.size
        w, h = insert_image.size
        offset = (0, 0)

        # horizontal image
        if W / H < w / h:
            print('insert horizontal image')
            new_width = W
            new_height = math.floor(h * W / w)
            insert_image = insert_image.resize([new_width, new_height])
            offset = (0, (H - new_height) // 2)
        # vertical image
        else:
            print('insert vertical image')
            new_height = H
            new_width = math.floor(w * H / h)
            insert_image = insert_image.resize([new_width, new_height])
            offset = ((W - new_width) // 2, 0)
        img.paste(insert_image, offset)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    lines = textwrap.wrap(s, width = WORD_NUM_PER_LINE)

    # for text centering
    word_width, word_height = font.getsize('あ')
    row_num = len(lines)
    if row_num % 2 == 0:
        text_y = IMAGE_SIZE[1] // 2 - word_height * (row_num // 2)
    else:
        text_y = IMAGE_SIZE[1] // 2 - word_height * (row_num // 2) - word_height // 2

    # black image
    black_image = Image.new('RGBA', IMAGE_SIZE)
    black_draw = ImageDraw.Draw(black_image)
    draw_start = (0, text_y)
    draw_end = (img.size[0], text_y + row_num * word_height + 20)
    black_draw.rectangle((draw_start, draw_end), fill=(0, 0, 0, 127))
    img = Image.alpha_composite(img, black_image)

    draw = ImageDraw.Draw(img)
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
    global insert_image_path, speaker
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
            command = text[1:-1]
            print('command', i, command)
            if 'image:' in command:
                print('image insert command', command)
                image_path = command.split(':')[-1]
                if image_path == 'None':
                    print('None image')
                    insert_image_path = None
                else:
                    insert_image_path = image_path
            elif 'speaker:' in command:
                print('speaker change command', command)
                speaker = command.split(':')[-1]
            else:
                print('command error')
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
        mp4_path = mp4_path.replace('temp/', '')
        f.write('file ' + mp4_path + '\n')
    f.close()
    # concatenate all mp4
    start_time = time.time()
    os.system('ffmpeg -f concat -i {0} {1}'.format(text_path, 'temp/output/{0}.mp4'.format(file_name)))
    print('merge time', time.time() - start_time, 'sec')

if __name__ == '__main__':
    make_movie('news_20171011.txt')
