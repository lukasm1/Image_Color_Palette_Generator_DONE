from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from colorthief import ColorThief
import webcolors
from PIL import Image
import numpy as np
from werkzeug.utils import secure_filename
import os

default_img_path = "static/assets/img/pokemon.jpg"


# Option 1 using colorthief and webcolors modules. We don't get the percentages, though:

# get the top ten hex colors:
def hex_color_palette(img_path):
    color_thief = ColorThief(img_path)
    rgb_color_palette = color_thief.get_palette(color_count=11)
    return [webcolors.rgb_to_hex(rgb_value) for rgb_value in rgb_color_palette]


# Option 2 using numpy. Works, but is too slow for images larger than 200x200px. Better to use option 1.
# It also returns very similar colors.


# count the percentage:
def count_percentage(value, out_of):
    return (value / out_of) * 100


# convert rgb to hex and format it:
def rgb_to_hex(r, g, b):
    return "#{:X}{:X}{:X}".format(r, g, b)


def img_to_hex_values(img):
    # open image:
    image = Image.open(img)
    # get array aka convert img into rgb values
    img_array = np.array(image)
    # get a list, containing lists of rows of all pixels = ig their rgb values::
    img_list = img_array.tolist()
    # get just a list of all rgb values:
    rgb_values_for_each_pixel = []
    # get the rows:
    for row in img_list:
        # get the columns of the rows, ig. each RGB value separately and add to the list:
        for column in row:
            rgb_values_for_each_pixel.append(column)
    # get a list of all unique rgb values = all unique colors:
    unique_colors = []
    for value in rgb_values_for_each_pixel:
        if value not in unique_colors:
            unique_colors.append(value)
    # next part:
    colors_information = []
    for color in unique_colors:
        # for each unique color count the number of occurrences in rgb_values_for_each_pixel:
        number_of_occurrences = rgb_values_for_each_pixel.count(color)
        # create dict w/ 2 values: 1) number of occurrences and 2) the unique rgb value = the unique color:
        dictionary = {"Number of occurrences": number_of_occurrences, "Color": color}
        # append the dictionary to the list:
        colors_information.append(dictionary)
    # next part, count the percentage:
    hundred_percent = 0
    for dict in colors_information:
        hundred_percent += dict["Number of occurrences"]
    # add the percentage info to the dictionary:
    for dict in colors_information:
        dict["Percentage"] = count_percentage(dict["Number of occurrences"], hundred_percent)
    # sort the list of dictionaries by its Percentage:
    colors_information = sorted(colors_information, key=lambda i: i['Percentage'], reverse=True)
    # slice the top ten colors:
    top_ten_colors = colors_information[:10]
    # convert the top ten colors to hex_values:
    hex_values = []
    for dictionary in top_ten_colors:
        for key, value in dictionary.items():
            # get the value of the "Color" key:
            if key == "Color":
                r = value[0]
                g = value[1]
                b = value[2]
                hex_value = rgb_to_hex(r, g, b)
                hex_values.append(hex_value)
    return hex_values


# App part:
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/assets/img/"
bootstrap = Bootstrap(app)


@app.route("/")
def home():
    # sending a list of hex_values, using option 1:
    return render_template("index.html", hex_values=hex_color_palette(default_img_path))


@app.route("/colors", methods=['GET', 'POST'])
def colors():
    # get the uploaded file:
    image = request.files['file']
    # get the uploaded file's name:
    filename = secure_filename(image.filename)
    # save the uploaded file:
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # get the path of the newly saved image:
    uploaded_image_path = f"static/assets/img/{image.filename}"

    return render_template("colors.html", image=uploaded_image_path, hex_values=hex_color_palette(uploaded_image_path))


if __name__ == '__main__':
    app.run(debug=True)