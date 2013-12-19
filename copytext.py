#!/usr/bin/env python

from flask import Markup
import xlrd

class CopyException(Exception):
    pass

class Error(object):
    """
    An error object that can mimic the structure of the COPY data, whether the error happens at the Copy, Sheet or Row level. Will print the error whenever it gets repr'ed. 
    """
    _error = ''

    def __init__(self, error):
        self._error = error

    def __getitem__(self, i):
        return self
    
    def __iter__(self):
        return iter([self])

    def __len__(self):
        return 1

    def __repr__(self):
        return self._error

class Row(object):
    """
    Wraps a row of copy for error handling.
    """
    _sheet = None
    _row = []
    _columns = []
    _index = 0

    def __init__(self, sheet, row, columns, index):
        self._sheet = sheet
        self._row = row
        self._columns = columns
        self._index = index

    def __getitem__(self, i):
        """
        Allow dict-style item access by index (column id), or by column name.
        """
        if isinstance(i, int):
            if i >= len(self._row):
                return Error('COPY.%s.%i.%i [column index outside range]' % (self._sheet.name, self._index, i))

            return Markup(self._row[i])

        if i not in self._columns:
            return Error('COPY.%s.%i.%s [column does not exist in sheet]' % (self._sheet.name, self._index, i))

        return Markup(self._row[self._columns.index(i)])

    def __iter__(self):
        return iter(self._row)

    def __len__(self):
        return len(self._row)

    def __repr__(self):
        if 'value' in self._columns:
            return Markup(self._row[self._columns.index('value')])

        return Error('COPY.%s.%s [no value column in sheet]' % (self._sheet.name, self._row[self._columns.index('key')])) 

class Sheet(object):
    """
    Wrap copy text, for a single worksheet, for error handling.
    """
    name = None
    _sheet = []
    _columns = []

    def __init__(self, name, data, columns):
        self.name = name
        self._sheet = [Row(self, [row[c] for c in columns], columns, i) for i, row in enumerate(data)]
        self._columns = columns

    def __getitem__(self, i):
        """
        Allow dict-style item access by index (row id), or by row name ("key" column).
        """
        if isinstance(i, int):
            if i >= len(self._sheet):
                return Error('COPY.%s.%i [row index outside range]' % (self.name, i))

            return self._sheet[i]

        if 'key' not in self._columns:
            return Error('COPY.%s.%s [no key column in sheet]' % (self.name, i))

        for row in self._sheet:
            if row['key'] == i:
                return row 

        return Error('COPY.%s.%s [key does not exist in sheet]' % (self.name, i))

    def __iter__(self):
        return iter(self._sheet)

    def __len__(self):
        return len(self._sheet)

class Copy(object):
    """
    Wraps copy text, for multiple worksheets, for error handling.
    """
    _filename = ''
    _copy = {}

    def __init__(self, filename='data/copy.xls'):
        self._filename = filename
        self.load()

    def __getitem__(self, name):
        """
        Allow dict-style item access by sheet name.
        """
        if name not in self._copy:
            return Error('COPY.%s [sheet does not exist]' % name)

        return self._copy[name]

    def load(self):
        """
        Parses the downloaded .xls file and writes it as JSON.
        """
        try:
            book = xlrd.open_workbook(self._filename)
        except IOError:
            raise CopyException('"%s" does not exist. Have you run "fab update_copy"?' % self._filename)

        for sheet in book.sheets():
            columns = sheet.row_values(0)
            rows = []

            for n in range(0, sheet.nrows):
                # Sheet takes array of rows
                rows.append(dict(zip(columns, sheet.row_values(n))))

            self._copy[sheet.name] = Sheet(sheet.name, rows, columns)

    def json(self):
        """
        Serialize the copy as JSON.
        """
        import json

        obj = {}    
    
        for name, sheet in self._copy.items():
            if 'key' in sheet._columns:
                obj[name] = {}

                for row in sheet:
                    obj[name][row['key']] = row['value']
            else:
                obj[name] = []
                
                for row in sheet:
                    obj[name].append(row._row)
            
        return json.dumps(obj)
