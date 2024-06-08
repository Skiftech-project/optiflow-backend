import csv
import io

from flasgger import swag_from
from flask import Blueprint, jsonify, make_response, request

radiation_pattern_bp = Blueprint('radiation_pattern', __name__)


@radiation_pattern_bp.post('/uploadFile')
@swag_from('docs/RadiationPattern/upload_file.yml')
def upload_file():
    if not request.files:
        return jsonify({'message': 'No file uploaded'}), 400

    uploaded_file = request.files.get('input_data')

    if not uploaded_file:
        return jsonify({'error': 'No such file'}), 400

    try:
        return jsonify(processing_data(uploaded_file)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def processing_data(uploaded_file):
    available_length = [1, 2, 4]
    csv_data = uploaded_file.read().decode('utf-8')
    csv_reader = csv.reader(io.StringIO(csv_data))

    column_names = next(csv_reader)

    column_data = {column_name: [] for column_name in column_names}

    for row in csv_reader:
        for i, value in enumerate(row):
            column_name = column_names[i]

            try:
                if value == '':
                    pass
                else:
                    column_data[column_name].append(float(value))
            except ValueError:
                raise ValueError(
                    f"Invalid value '{value}' in column '{column_name}'")

    if len(column_data) in available_length:
        return process_column_lengths(column_data, len(column_data))
    else:
        raise ValueError(
            f"Invalid number of columns. Expected {available_length}, got {len(column_data)}")


def process_column_lengths(column_data, length):
    length_dict = {
        1: 'similar',
        2: 'partially_similar',
        4: 'different'
    }
    max_length = max(len(lst) for lst in column_data.values())
    min_number = min(min(lst) for lst in column_data.values())

    for column_name, values in column_data.items():
        if len(values) < max_length:
            while len(values) < max_length:
                values.append(min_number)

    data = [values for values in column_data.values()]

    return {
        'data': data,
        'model_type': length_dict.get(length, 'invalid')
    }
