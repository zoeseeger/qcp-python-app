#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed

def read_file(file):
    with open(file, "r") as f:
        try:
            for line in f:
                yield line
        except UnicodeDecodeError:
            pass

def get_type(file):
    for line in read_file(file):
        if 'PSI4' in line:
            return 'psi4'
        elif 'GAMESS' in line:
            return 'gamess'
        # extend to lammps

def write_xyz(atoms, filename = None):
    """Writes an xyz file using a list of atoms in xyz format, with or without atomic numbers.
"""
    if filename is None:
        raise ValueError('write_xyz: Must give a path to the output file')
    else:
        with open(filename, "w") as file:
            file.write(str(len(atoms)) + '\n\n')
            for atom in atoms:
                parts = atom.split()
                if len(parts) > 4:
                    sym, *_, x, y, z = parts
                else:
                    sym, x, y, z = parts
                x, y, z = float(x), float(y), float(z)
                file.write(f"{sym:5s} {x:>15.10f} {y:15.10f} {z:15.10f} \n")

def get_files(directory, ext):
    """Accepts a tuple of file extensions, searches in all subdirectories of the directory given for relevant files. Returns a list of files with their relative path to the directory passed in.

    Usage:
        >>> for filepath in get_files('.', ("log", "out")):
        >>>     parse_file(filepath)
    """
    import os

    fileLst = []
    for path, dirs, files in os.walk(directory):
        for file in files:
            for e in ext:
                if file.endswith(e) and file != 'freq.out': # freq.out used for thermo calculations with the fortran code
                    fileLst.append(os.path.join(path, file))
    return fileLst

def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True

def sort_elements(lst):
    """
    Sort a list of atom dictionaries by atomic number. 
    Returns a list of tuples- [(symbol, atomic number), (symbol, atomic number), ...]

    TODO: Extend to giving back the objects- more useful than just for formatting of symbols
    """
    from chemData import pTable
    
    els = []
    elements = set([atom['sym'] for atom in lst])
    for i in elements:
        els.append((i, pTable[i][0])) # sym, atom number
    sorted_els = sorted(els, key = lambda val: val[1])
    return sorted_els

def write_csv_from_dict(data, return_name = False):
    """Write to file from dictionary"""

    import csv

    # convert to try/except

    done = False
    while not done:
        to_file = input('Print to csv? [Y/N] ')
        if to_file.lower() in ('y', 'n'):
            done = True
            if to_file.lower() == 'y':
                filename = check_user_input('Filename', lambda item: item.endswith('.csv'), "Please give a filename ending in '.csv'")
                with open(filename, "w", encoding = 'utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(data.keys())
                    content = zip(*[data[key] for key in data.keys()])
                    writer.writerows(content) 
                if return_name:
                    return filename
        else:   
            print("Please select 'Y' or 'N'")

def write_csv_from_nested(data,*,col_names = None, return_name = False):
    """
    Write to csv from nested data structure; list of tuples, list of lists. 
    
    NB: requires a list or tuple of column names passed to the `col_names` parameter
    """

    import csv

    if type(col_names) not in (list, tuple):
        raise AttributeError('Must pass in column names as a list or tuple of values')
    # convert to try/except
    done = False
    while not done:
        to_file = input('Print to csv? [Y/N] ')
        if to_file.lower() in ('y', 'n'):
            done = True
            if to_file.lower() == 'y':
                filename = check_user_input('Filename', lambda item: item.endswith('.csv'), "Please give a filename ending in '.csv'")
                with open(filename, "w", encoding = 'utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(col_names)       
                    writer.writerows(data)
                if return_name:
                    return filename
        else:   
            print("Please select 'Y' or 'N'")

def search_dict_recursively(d):
    ret = {}
    for k, v in d.items():
        if isinstance(v, dict):
            ret[k] = search_dict_recursively(v)
        else:
            ret[k] = v
    return ret


def check_user_input(user_input, condition, if_error):
    """
    Uses a try/except statement to create a scenario where the end user cannot give unexpected input. Give the condition referring to an item in a lambda expression i.e. lambda item: item.endswith('.csv'), or lambda item: item in range(...)

    Usage:
        >>> check_user_input('Filename of output', lambda item: item.endswith('.csv'), "Please print a name ending in '.csv'")
        # Produces:
        while not correct:
            try:
                item = input('Filename of output: ')
            except ValueError:
                print("Please enter a filename ending in '.csv'")
            if not filename.endswith('.csv'):
                print("Please enter a filename ending in '.csv'")
            else:
                correct = True
        return item
    """
    f = condition
    correct = False
    while not correct:
        try:
            item = input(user_input + ': ')
        except ValueError:
            print(if_error)
        if not f(item):
            print(if_error)
        else:
            correct = True
    return item

def sort_data(data):
    """ 
    Sorts the data into alphanumerical order
    """
    collapsed = [[k, v] for k, v in data.items()]
    sorted_data = sorted(collapsed, key = lambda kv: kv[0])
    sorted_dict  = {}
    for data in sorted_data:
        k, v = data
        sorted_dict[k] = v # as of py 3.6, dicts remain ordered- so no need to implement ordered dict
    return sorted_dict

def assign_molecules_from_dict_keys(data):
    """ 
    Assign a cation and anion to each path.
    """
    for key in data.keys():
        cation = ''
        anion = ''
        vals = key.split('/')
        for val in vals:
            # different names for the same anion
            if val == 'ch':
                val = 'choline'
            if val == 'ac':
                val = 'acetate'
            if val == 'h2po4':
                val = 'dhp' # in Molecules.Anions
            if val == 'mesylate':
                val = 'mes'
            if val in Molecule.Cations:
                cation = val
            elif val in Molecule.Anions:
                anion = val
        data[key]['cation'] = cation
        data[key]['anion'] = anion
    return data

def responsive_table(data, strings, min_width):
    """
    Returns a table that is reponsive in size to every column.
    Requires a dictionary to be passed in, with the keys referring to
    the headers of the table.
    Also pass in the number of each column that should be a string, starting
    from 1.

    Usage:
        >>> d = {'col1': [1,2,3,4],
                 'col2': ['One', 'Two', 'Three', 'Four']}
        >>> responsive_table(d, strings = [2])

    Can also give a minimum width, defaults to 13 spaces
        >>> responsive_table(d, strings = [2], min_width = 5)
    """
    num_cols = len(data.keys())
    content = zip(*[data[key] for key in data.keys()]) # dict values into list of lists
    # unknown number of arguments
    max_sizes = {}
    for k, v in data.items():
        max_sizes[k] = len(max([str(val) for val in v], key = len))

    # create the thing to pass into .format()- can't have brackets like zip gives
    formatting = []
    index = 0
    all_sizes = []
    if min_width is None:
        min_width = 13
    for val in zip(data.keys(), max_sizes.values()):
        entry, size = val
        if size < min_width or index + 1 not in strings:
            size = min_width
        # also check dict key length
        if len(entry) > size:
            size = len(entry)
        formatting += [entry, size]
        all_sizes.append(size)
        index += 1
    line_length = sum(all_sizes) + num_cols * 3 - 1 # spaces in header
    print('+' + '-' * line_length + '+')
    output_string = '|' + " {:^{}} |" * len(data.keys())
    print(output_string.format(*formatting))
    print('+' + '-' * line_length + '+')
    for line in content:
        formatting = []
        for val in zip(line, all_sizes):
            entry, size = val
            if isinstance(size, float):
                size = f'{size}.5f'
            formatting.append(entry)
            formatting.append(size)
        print(output_string.format(*formatting))
    print('+' + '-' * line_length + '+')
