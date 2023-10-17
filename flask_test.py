from flask import Flask, render_template, request
from math import *

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        distance = float(request.form['distance'])
        fixed_radius = float(request.form['fixed_radius'])

        option = request.form.get('option')

        if option == 'angles':
            angle_width = float(request.form['angle_width'])
            angle_height = float(request.form['angle_height'])

            if angle_width == angle_height:
                area = calculate_area(fixed_radius, angle_width)
            else:
                radius = fixed_radius
                larger_angle = max(angle_width, angle_height)
                area = calculate_area(radius, larger_angle) * (larger_angle / min(angle_width, angle_height))

        elif option == 'plume':
            plume_width = float(request.form['plume_width'])
            plume_height = float(request.form['plume_height'])

            angle_width = calculate_divergence_angle(plume_width, distance)
            angle_height = calculate_divergence_angle(plume_height, distance)

            # put into function
            if angle_width == angle_height:
                area = calculate_area(fixed_radius, angle_width)
            else:
                radius = fixed_radius
                larger_angle = max(angle_width, angle_height)
                area = calculate_area(radius, larger_angle) * (larger_angle / min(angle_width, angle_height))

        else:
            error_message = "Please select either 'Ввести кути' or 'Ввести ширину та висоту.'"
            return render_template('index.html', error_message=error_message)

        return render_template('result.html', angle_width=angle_width, angle_height=angle_height, area=area)

    return render_template('index.html')


def calculate_divergence_angle(size, distance):
    angle = 2 * atan(size / (2 * distance))
    return angle


# remake function, r - distance
def calculate_area(radius, angle):
    area = 2 * pi * (radius ** 2) * (1 - cos(angle))
    return area


def calculate_size(angle, distance):
    size = 2 * distance * tan(angle / 2)
    return size


# remake function
def calculate_distance(size, angle):
    distance = size / (2 * tan(angle / 2))
    return distance


if __name__ == '__main__':
    app.run(debug=True)
