 # -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import time, praw, urllib, requests, os
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
import subprocess

#######     SETTINGS        #######
FONT = "Roboto-Light.ttf"
IMAGE_SUBREDDIT = "EarthPorn"
TEXT_SUBREDDIT = "Showerthoughts"
LIM = 10
MIN_RESOLUTION = (1920,1080)
#Tolerence is out of 0 to 100 (Percentage)
ASPECT_TOLERENCE = 18
###################################

reddit = praw.Reddit(user_agent="Chromecast_Showerthoughts")
images = reddit.get_subreddit(IMAGE_SUBREDDIT).get_top(limit=LIM)
thoughts = reddit.get_subreddit(TEXT_SUBREDDIT).get_top(limit=LIM)
env = Environment(loader=FileSystemLoader('templates'))

def get_image_size(url):
    """
    Gets the dimensions of a web image. url must be a direct link to the image,
    currently little support around this. Will timeout if

    Args:
        url (string): The url of the hosted image

    Returns:
        tuple(float, float): (image width, image height)
    """
    data = requests.get(url, timeout=(1, 1)).content
    im = Image.open(BytesIO(data))
    return float(im.size[0]), float(im.size[1])

def verify_image_sizing(img_H, img_W, min_RES, tolerance):
	#Returns boolean value of whether image being pulled conforms to contraints.

	#Set default response
	verified = False
	
	#Ensure Tolerance value is within required range (0-100)
	if tolerance >= 0 and tolerance <= 100:
		tolerance = tolerance / 100.0
	else:
		print "Tolerence entered does not meet requirements, must be a whole value between 0-100. Quit script."
		quit()

	#Load H and W into seperate variables
	min_RES_W = float(min_RES[0])
	min_RES_H = float(min_RES[1])

	#Get aspect decimal for image being pulled and pixel count
	img_aspect = float(img_H)/float(img_W)
	img_pixel = img_H*img_W

	#Get high and low for tolerance against aspect ratio's
	req_aspect_min = (min_RES_H/min_RES_W) * ( 1 - tolerance)
	req_aspect_max = (min_RES_H/min_RES_W) * (1 + tolerance)

	#Get minimum pixel count in image
	req_pixel_min = min_RES_H*min_RES_W

	if req_aspect_min <= img_aspect and img_aspect <= req_aspect_max and img_pixel >= req_pixel_min:
		#Image is within tolerance specified and has more pixels then the min stated.
		verified = True
	
	return verified	

def multiline_text(text, image_width, image_height):
    """
    Splits large text up into multiple lines by using newlines so
    that it fits onto the given image dimensions.
    The text is to fit within 2/3 of the image width. There
    is currently no restraint on the number of lines so it can spill
    off the image. The font size is dependent on the image height -
    it's 3% of the height. This is an arbitrary value and still
    being decided.

    Args:
        text (string): the single line text to fit into multiple lines
        image_width (int): the width of the image to fit the text onto
        image_height (int): the height of the image to fit the text onto

    Returns:
        string: the given text with added newlines
    """
    tail = text
    length = 0
    while font.getsize(tail)[0] > 2*image_width/3:
        head = tail
        while font.getsize(head)[0] > 2*image_width/3:
            head = head.rsplit(' ', 1)[0]
        length += len(head)
        tail = tail[length:]
        text = text[:length] + '\n' + text[length:]
        length += len("\n")
    return text

def fill_template_url(template, image_url, text):
    """
    Uses jinja2 to fill a given template with the image and text.

    Args:
        template (string): the html file to edit
        image_url (string): the url for the image to place in the template
        text (string): the text to put in the centre of the image
    """
    template = env.get_template(template)
    output = template.render(image=image_url, showerthought=text)
    with open("test.html", "wb") as fh:
        fh.write(output)

def capture_template(filename):
    return subprocess.call(r"wkhtmltopdf\bin\wkhtmltoimage --height 1080" +
    "--width 1920 test.html" + os.getcwd() + "\\" + filename , shell=True)

def draw_my_text(image, text):
    """
    Draws the text over the given image.

    Args:
        image (ImageDraw): the actual image to draw the text over. note that
            this is not the file but the actual ImageDraw object created
            from the image file.
        text (string): the text to draw over the image.
        w (int): this is the x position of where to put the top left corner of
            the text. Different for single line and multiline text.
        h (int): this is the y position of where to put the top left corner of
        the text.

    """
    h = (image.size[1] - ((text.count('\n')+1) * (font.getsize(text)[1] + 5)))/2
    if text.count('\n') > 0:
        w = image.size[0]/6
    else:
        w =(image.size[0]-font.getsize(text)[0])/2
    draw.multiline_text((w + 1, h + 1), text, font=font,
                        align='center', spacing=5, fill="black")
    draw.multiline_text((w - 1, h + 1), text, font=font,
                        align='center', spacing=5, fill="black")
    draw.multiline_text((w + 1, h - 1), text, font=font,
                        align='center', spacing=5, fill="black")
    draw.multiline_text((w - 1, h - 1), text, font=font,
                        align='center', spacing=5, fill="black")
    draw.multiline_text((w, h), text, font=font,
                        align='center', spacing=5, fill="white")
    img.save(imageName, "JPEG", quality=100, optimize=True, progressive=True)

if __name__ == "__main__":
    for i in range(LIM):
        image = next(images)
        "Handle a non direct imgur link"
        if "imgur" in image.url and "." not in image.url:
            image.url += ".jpg"
        try:
            W, H = get_image_size(image.url)
        except IOError:
            continue

	if verify_image_sizing(H, W, MIN_RESOLUTION, ASPECT_TOLERENCE) == True:
            "Label image using current date and image in sequence."
            imageName = time.strftime("%d%m%y"+ str(i) + ".jpg")
            urllib.urlretrieve(image.url, imageName)
            "Wait for download"
            time.sleep(15)
            img = Image.open(imageName)
            thought = next(thoughts).title
            font = ImageFont.truetype(FONT, int(H*.03))
            draw = ImageDraw.Draw(img)
            thought = multiline_text(thought, W, H)
            draw_my_text(img, thought)
            #fi
            Uses jinja2 to fill a given template with the image and text.

            Args:
                template (string): the html file to edit
                image_url (string): the url for the image to place in the template
                text (string): the text to put in the centre of the image

("template.html",
            """image.url, thought)
            #capture_template(imageName)
os.system("uploadr.py")
