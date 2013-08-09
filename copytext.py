#!/usr/bin/env python

from flask import Markup
import xlrd

COPY_XLS = 'data/copy.xls'

class CopyException(Exception):
    pass

class Row(object):
    """
    Wraps a row of copy for error handling.
    """
    _sheet = None
    _row = {} 
    _index = 0

    def __init__(self, sheet, data, index):
        self._sheet = sheet
        self._row = data
        self._index = index

    def __getitem__(self, i):
        """
        Allow dict-style item access by index (column id), or by column name.
        """
        if isinstance(i, int):
            return self._row[i]
        else:
            return self.__getattr__(i)

    def __getattr__(self, name):
        """
        Allow object-style property access by column name.
        """
        if name in self.__dict__:
            return self.__dict__[name]

        if not self._row:
            return 'COPY.%s.%i (row does not exist)' % (self._sheet.name, self._index)

        if name not in self._row:
            return 'COPY.%s.%i.%s [column does not exist]' % (self._sheet.name, self._index, name)

        return Markup(self._row[name])

    def __iter__(self):
        return iter(self._row)

    def __len__(self):
        return len(self._row)

class Sheet(object):
    """
    Wrap copy text, for a single worksheet, for error handling.
    """
    name = None
    _sheet = []
    _columns = []

    def __init__(self, name, data, columns):
        self.name = name
        self._sheet = [Row(self, row, i) for i, row in enumerate(data)]
        self._columns = columns

    def __getitem__(self, i):
        """
        Allow dict-style item access by index (row id), or by row name ("key" column).
        """
        if isinstance(i, int):
            if i > len(self._sheet):
                return Row(self, {}, i)

            return self._sheet[i]
        else:
            return self.__getattr__(i)

    def __getattr__(self, name):
        """
        Allow object-style property access by row name ("key" column).
        """
        if name in self.__dict__:
            return self.__dict__[name]

        if not self._sheet and not self._columns:
            return 'COPY.%s.%s [sheet does not exist]' % (self.name, name)

        if 'key' not in self._columns:
            return 'COPY.%s.%s [no key column]' % (self.name, name)

        for row in self._sheet:
            if row['key'] == name:
                return Markup(row['value'])

        return 'COPY.%s.%s [key does not exist]' % (self.name, name)

    def __iter__(self):
        return iter(self._sheet)

    def __len__(self):
        return len(self._sheet)

class Copy(object):
    """
    Wraps copy text, for multiple worksheets, for error handling.
    """
    _copy = {}

    def __init__(self):
        self.load()

    def __getitem__(self, name):
        """
        Allow dict-style item access by sheet name.
        """
        return self.__getattr__(name)

    def __getattr__(self, name):
        """
        Allow object-style property access by sheet name.
        """
        if name in self.__dict__:
            return self.__dict__[name]

        try:
            return self._copy[name]
        except KeyError:
            return Sheet(name, {}, [])

    def load(self):
        """
        Parses the downloaded .xls file and writes it as JSON.
        """
        try:
            book = xlrd.open_workbook(COPY_XLS)
        except IOError:
            raise CopyException('"%s" does not exist. Have you run "fab update_copy"?' % COPY_XLS)

        for sheet in book.sheets():
            columns = sheet.row_values(0)
            rows = []

            for n in range(1, sheet.nrows):
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
                    obj[name][row['key']] = row._row['value']
            else:
                obj[name] = []
                
                for row in sheet:
                    obj[name].append(row._row)
            
        return json.dumps(obj)
