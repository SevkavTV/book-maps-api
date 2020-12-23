from numpy.core.numeric import True_
import pandas as pd


class DatabaseConfig:

    path_to_file = 'classification.csv'

    mode_to_extension = {'hdf': ('h5', 'hdf', 'hdf5'),
                         'pkl': ('pkl', 'pickle', 'pt'),
                         'csv': ('csv', 'tsv', 'txt'),
                         'excel': ('xlsx', 'xls', 'xml')}

    extension_to_mode = {ext: mode for mode,
                         exts in mode_to_extension.items() for ext in exts}

    drop_columns = ['Dewey classification', 'BL record ID', 'Archival Resource Key',
                    'Number within series', 'Provenance', 'Referenced in', 'Type of resource',
                    'BNB number', 'Archival Resource Key', 'Type of name', 'Edition',
                    'BL shelfmark']

    drop_nan_in_columns = [
        'Place of creation/publication', 'Country of publication', 'ISBN']


class Database:

    def __init__(self, config_object) -> None:
        self.config = config_object
        self.data = self.read_data()
        self.city_to_geo = Database.initiliaze_city_to_geo()
        self.data = self.preprocess(self.data)

    def read_data(self):
        '''
        Read data from 'classification.csv' file
        '''
        file_extension = self.config.path_to_file.split('.')[-1]

        if file_extension is None:
            raise Exception('File extension is None')

        elif file_extension not in self.config.extension_to_mode.keys():
            raise Exception('Not supported extension')

        else:
            mode = self.config.extension_to_mode[file_extension]

        if mode == 'csv':
            df = pd.read_csv(self.config.path_to_file)

        elif mode == 'pkl':
            df = pd.read_pickle(self.config.path_to_file)

        elif mode == 'hdf':
            df = pd.read_hdf(self.config.path_to_file)

        else:
            df = pd.read_excel(self.config.path_to_file)

        return df

    def preprocess(self, df):
        '''
        Preprocess the data (delete unused columns and books without location)
        '''
        df.drop(self.config.drop_columns, axis=1, inplace=True)
        df = df[~df[self.config.drop_nan_in_columns].isna().any(
            axis=1)]

        df['Place of creation/publication'] = df['Place of creation/publication'].apply(
            lambda x: x.split(';')[0].strip())
        df = df[df['Place of creation/publication']
                .apply(lambda x: x in self.city_to_geo)]

        df.reset_index(drop=True, inplace=True)

        return df

    def get_all_books(self, cols):
        '''
        Get all books as a list dictionaries with given cols.
        '''
        df = self.data
        all_books = []

        for book in df[cols].values:
            book_dict = {property: value for property,
                         value in zip(cols, book)}

            all_books.append(book_dict)

        for book in all_books:
            if 'Place of creation/publication' in book.keys():
                city = book['Place of creation/publication']
                coordinates = self.city_to_geo[city]

                book['Place of creation/publication'] = coordinates

        return all_books

    def find_books_by_param(self, param):
        '''
        Find all books which contains in their fields given parameter
        and return list with ISBNs of all these books.
        '''
        df = self.data
        found_books = set()

        for column in df:
            db = df[df[column].str.contains(param, na=False)]

            ISBN_list = db['ISBN'].tolist()

            for ISBN in ISBN_list:
                found_books.add(ISBN)

        return list(found_books)

    def get_book_info(self, ISBN):
        '''
        Find book by its ISBN and return dictionary with info about it.
        '''
        df = self.data

        book = df[df['ISBN'] == ISBN].iloc[0]

        book_dict = book.to_dict()

        if 'Place of creation/publication' in book_dict.keys():
            city = book_dict['Place of creation/publication']
            coordinates = self.city_to_geo[city]

            book_dict['Place of creation/publication'] = coordinates

        return book_dict

    def filter_books(self, filter_dict, operator='AND'):
        '''
        Filter books by given parametres.
        '''
        df = self.data

        filtered_books = set()

        for ii, (column, values) in enumerate(filter_dict.items()):
            books = df[df[column].apply(
                lambda val: val in values)]['ISBN'].tolist()
            if ii == 0:
                filtered_books = set(books)
            elif operator == 'AND':
                filtered_books = filtered_books.intersection(set(books))
            elif operator == 'OR':
                filtered_books = filtered_books.union(set(books))
            else:
                raise Exception('Unsupported operator')

        return list(filtered_books)

    @staticmethod
    def initiliaze_city_to_geo():
        '''
        Return latitude and longtitude of a given city.
        '''
        dict_city = {}

        with open('coordinates.txt', 'r', encoding="utf-8") as file:

            for line in file:
                item = line.split(':')
                lat, lng = item[1].split()
                dict_city[item[0]] = {"lat": float(lat), "lng": float(lng)}

        return dict_city


# code that generate list of all cities in database and write it to file 'cities.txt'

# db = Database(DatabaseConfig)
# df = db.data
# list_cities = df['Place of creation/publication'].tolist()
# with open('cities.txt', 'w', encoding="utf-8") as file:
#     for item in list_cities:
#         item = item.split(';')
#         for city in item:
#             file.write(city.strip() + '\n')
