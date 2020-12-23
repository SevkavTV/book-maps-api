from os import error
from flask import Flask, request, jsonify, make_response, Response
from flask_cors import CORS
from database import DatabaseConfig, Database
import pandas as pd


# initialize Flask
app = Flask(__name__)
CORS(app)
db = Database(DatabaseConfig)


@app.route('/api/get_all_entries', methods=['GET'])
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
        all_books = []
        for book in db.data[cols].values:
            book_dict = {property: value for property,
                         value in zip(cols, book)}
            all_books.append(book_dict)

        return make_response(jsonify(all_books), 200)


@app.route('/api/get_book_by_param', methods=['GET'])
def get_book_by_param():
    request_data = request.json

    if 'param' not in request_data.keys():
        err = 'No parameter in request'
        return make_response(jsonify(error=err), 400)
    else:
        param = request_data['param']


if __name__ == '__main__':
    app.run()
