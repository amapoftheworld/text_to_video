import os
import textwrap
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from mutagen.mp3 import MP3

FONT_PATH = '/Library/Fonts/genshingothic-20150607/GenShinGothic-Bold.ttf'
FONT_SIZE = 72
TEXT_COLOR = (255, 0, 0)
BORDER_COLOR = (255, 255, 0) # yellow
IMAGE_SIZE = (1920, 1080)
MAX_WORD_NUM = 100 # temp
WORD_NUM_PER_LINE = 20

def generate_aiff(s, i):
    aiff_path = 'temp/sound/' + '{0:04d}'.format(i) + '.aiff'
    os.system('say -v Kyoko ' + s + ' -o ' + aiff_path)
    mp3_path = aiff_to_mp3(aiff_path)
    mp3_length = get_mp3_length(mp3_path)
    return mp3_length

def aiff_to_mp3(aiff_path):
    mp3_path = aiff_path.replace('.aiff', '.mp3')
    command = 'lame -m m ' + aiff_path + ' ' + mp3_path
    os.system(command)
    return mp3_path

def get_mp3_length(mp3_path):
    audio = MP3(mp3_path)
    return audio.info.length

def generate_png(s, i):
    output_path = 'temp/image/' + '{0:04d}'.format(i) + '.png'
    print(output_path)
    img = Image.new('RGBA', IMAGE_SIZE)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    lines = textwrap.wrap(s, width = WORD_NUM_PER_LINE)
    text_y = 0

    # for centering, get info
    word_width, word_height = font.getsize('あ')
    text_y = IMAGE_SIZE[1] // 2 - word_height - word_height // 2

    for line in lines:
        width, height = font.getsize(line)
        text_x = IMAGE_SIZE[0] // 2 - width // 2

        position = (text_x, text_y)
        text_y += height

        # outline
        offset = height // 10
        x_list = [-1, 0, 1]
        y_list = [-1, 0, 1]
        for x in x_list:
            for y in y_list:
                new_x = position[0] + x * offset
                new_y = position[1] + y * offset
                draw.text((new_x, new_y), line, BORDER_COLOR, font=font)
        draw.text(position, line, TEXT_COLOR, font=font)

        # main text
        draw.text(position, line, TEXT_COLOR, font=font)
    img.save(output_path)

def make_movie(file_name):
    path = 'input/' + file_name
    print(path)
    text_list = []
    with open(path) as f:
        for line in f:
            text_list.append(line.strip())
    print(text_list)

    mp3_length_list = []
    for i, t in enumerate(text_list):
        mp3_length = generate_aiff(t, i)
        print('mp3_length', mp3_length)
        mp3_length_list.append(mp3_length)
        generate_png(t, i)

if __name__ == '__main__':
    make_movie('sample.txt')
    #say_command('こんにちは', 3)