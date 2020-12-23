from os import error, truncate
from flask import Flask, request, jsonify, make_response, Response
from flask_cors import CORS
from database import DatabaseConfig, Database
import pandas as pd


# initialize Flask
app = Flask(__name__)
CORS(app)
db = Database(DatabaseConfig)


@app.route('/api/get_all_entries', methods=['POST'])
def get_all_entries():
    request_data = request.json

    if 'column_names' not in request_data.keys():
        err = 'No column names key in request'
        return make_response(jsonify(error=err), 400)
    else:
        cols = request_data['column_names']

    not_found_columns = [col for col in cols if (col not in db.data.columns)]

    if len(not_found_columns) > 0:
        err = f"Columns {not_found_columns} are not in our database"
        return make_response(jsonify(error=err), 400)
    else:
        all_books = db.get_all_books(cols)

        return make_response(jsonify(all_books), 200)


@app.route('/api/get_entries_by_param', methods=['POST'])
def get_entries_by_param():
    request_data = request.json

    if 'param' not in request_data.keys():
        err = 'No parameter in request'
        return make_response(jsonify(error=err), 400)
    else:
        param = request_data['param']

    if isinstance(param, str):
        found_books = db.find_books_by_param(param)

        return make_response(jsonify(found_books), 200)
    else:
        err = "Param type is not string"
        return make_response(jsonify(error=err), 400)


@app.route('/api/get_book_info_by_ISBN', methods=['POST'])
def get_book_info_by_ISBN():
    request_data = request.json

    if 'ISBN' not in request_data.keys():
        err = 'No ISBN in request'
        return make_response(jsonify(error=err), 400)
    else:
        ISBN = request_data['ISBN']

    if isinstance(ISBN, str):
        book_info = db.get_book_info(ISBN)

        return make_response(jsonify(book_info), 200)
    else:
        err = "Param ISBN is not string"
        return make_response(jsonify(error=err), 400)


@app.route('/api/filter_books', methods=['POST'])
def filter_books():
    request_data = request.json

    if 'operator' not in request_data.keys():
        err = 'No operator in request, allowed values are AND/OR'
        return make_response(jsonify(error=err), 400)
    elif request_data['operator'] not in ['AND', 'OR']:
        err = 'No such operator is supported'
        return make_response(jsonify(error=err), 400)
    else:
        operator = request_data['operator']

    not_found_columns = [col for col in request_data.keys() if (
        col not in db.data.columns and col != 'operator')]

    if len(not_found_columns) > 0:
        err = f"Columns {not_found_columns} are not in our database"
        return make_response(jsonify(error=err), 400)
    else:
        filter_dict = {key: value for key,
                       value in request_data.items() if key in db.data.columns}
        filtered_books = db.filter_books(filter_dict, operator=operator)

        return make_response(jsonify(filtered_books), 200)


if __name__ == '__main__':
    app.run(debug=True)
