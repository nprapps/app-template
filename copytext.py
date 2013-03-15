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
    _row = []
    _index = 0

    def __init__(self, data, index):
        self._row = data
        self._index = index

    def __getattr__(self, name):
        if name not in self._row:
            return 'COPY ERROR: row `%i` has no column %s' % (self._index, name)

        return Markup(self._row[name])

    def __getitem__(self, i):
        return self._row[i]

    def __iter__(self):
        return iter(self._row)

    def __len__(self):
        return len(self._row)

class Sheet(object):
    """
    Wrap copy text, for a single worksheet, for error handling.
    """
    _sheet = []
    _name = None

    def __init__(self, data, name=None):
        self._sheet = data
        self._name = name

    def __getitem__(self, i):
        if i > len(self._sheet):
            return 'COPY ERROR: Row %i not in sheet' % i
        return self._sheet[i]

    def __getattr__(self, name):
        if not self._sheet:
            return 'COPY ERROR: sheet `%s`' % self._name

        if 'key' not in self._sheet[0]:
            return 'COPY ERROR: sheet `%s` has no "key" column' % self._name

        for row in self._sheet:
            if row['key'] == name:
                return Markup(row['value'])

        return 'COPY ERROR: `%s`' % name

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

    def __getattr__(self, name):
        try:
            return self._copy[name]
        except KeyError:
            return Sheet({}, name=name)

    def load(self):
        """
        Parses the downloaded .xls file and writes it as JSON.
        """
        try:
            book = xlrd.open_workbook(COPY_XLS)
        except IOError:
            raise CopyException('"%s" does not exist. Have you run "fab update_copy"?' % COPY_XLS)
        for sheet in book.sheets():
            column_names = sheet.row_values(0)
            rows = []
            for n in range(1, sheet.nrows):
                # Sheet takes array of rows
                rows.append(Row(dict(zip(column_names, sheet.row_values(n))), n))

            self._copy[sheet.name] = Sheet(rows, name=sheet.name)

