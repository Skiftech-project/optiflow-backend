from flask import Flask, render_template, request
from math import *

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        distance = float(request.form['distance']) * 1000
        option = request.form.get('plume_type')

        sensitivity = float(request.form['sensitivity'])
        power = float(request.form['power'])
        max_area = calculate_max_area(sensitivity, power)

        if option == 'ellipse':
            angle_width = radians(float(request.form['angle_width']))
            angle_height = radians(float(request.form['angle_height']))

            max_distance = calculate_max_distance(max_area, angle_width, angle_height)

        elif option == 'rectangle':
            plume_width = float(request.form['plume_width']) * 1000
            plume_height = float(request.form['plume_height']) * 1000

            angle_width = radians(calculate_divergence_angle(plume_width, distance))
            angle_height = radians(calculate_divergence_angle(plume_height, distance))

            max_distance = calculate_max_distance(max_area, angle_width, angle_height)

        else:
            error_message = "Будь ласка, оберіть тип плями."
            return render_template('index.html', error_message=error_message)

        return render_template('result.html', angle_width=degrees(angle_width), angle_height=degrees(angle_height),
                               max_area=max_area, max_distance=max_distance)

    return render_template('index.html')


def calculate_divergence_angle(size, distance):
    angle = 2 * atan(size / (2 * distance))
    return angle


def calculate_max_area(sensitivity, power):
    max_area = power / sensitivity
    return max_area


def calculate_max_distance(max_area, angle_width, angle_height):
    max_angle = max(angle_width, angle_height)
    max_distance = sqrt(max_area / (2 * pi * (1 - cos(max_angle / 2)) * min(angle_width, angle_height)/max_angle))
    return max_distance


def calculate_size(angle, distance):
    size = 2 * distance * tan(angle / 2)
    return size


# we need to calculate distance another way: get minSize and two angles for this
# it will be: distance = minSize / (2 * tan(min(angle_width, angle_height) / 2))
def calculate_distance(size, angle):
    distance = size / (2 * tan(angle / 2))
    return distance


if __name__ == '__main__':
    app.run(debug=True)
