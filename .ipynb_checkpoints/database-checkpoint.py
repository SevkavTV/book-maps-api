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
        book_info = {}

        return df.iloc[df['ISBN'] == ISBN]


db = Database(DatabaseConfig)
print(db.get_book_info('9780930326258'))
