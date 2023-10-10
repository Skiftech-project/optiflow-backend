from flask import Flask, render_template, request
import math

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        plume_width = float(request.form['plume_width'])
        plume_height = float(request.form['plume_height'])
        distance = float(request.form['distance'])

        # Розрахунок кутів розбіжності
        angle = calculate_divergence_angles((plume_width, plume_height), distance)

        return render_template('result.html', angle=angle)

    return render_template('index.html')


def calculate_divergence_angles(plume_size, distance):

    area = plume_size[0] * plume_size[1]
    angle = 2 * math.atan(area / (2*distance))

    return angle


if __name__ == '__main__':
    app.run(debug=True)
