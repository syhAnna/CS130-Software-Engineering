import string
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import random


def generate_validate_picture(num_chars = 5):
    candidate_char_set = string.digits + string.ascii_letters
    width, heighth = num_chars * 30, 40    # size of picture 130 x 50

    # generate an image object and set the fonts
    im = Image.new('RGB',(width, heighth), 'White')
    font = ImageFont.truetype("/Library/Fonts/Arial", 28)
    draw = ImageDraw.Draw(im)
    generated_string = ''
    # output each char
    for item in range(num_chars):
        text = random.choice(candidate_char_set)
        generated_string += text
        draw.text((13 + random.randint(4, 7) + 20*item, random.randint(3, 7)), text=text, fill='Black', font=font)

    # draw several lines
    for num in range(8):
        x1 = random.randint(0, width/2)
        y1 = random.randint(0, heighth/2)
        x2 = random.randint(0, width)
        y2 = random.randint(heighth/2, heighth)
        draw.line(((x1, y1), (x2, y2)), fill='black', width=1)

    # Vague
    im = im.filter(ImageFilter.FIND_EDGES)
    return im, generated_string
