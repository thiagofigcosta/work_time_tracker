import sys

has_raw_input = True
try:
    raw_input
except NameError:
    has_raw_input = False
if sys.version_info[0] == 2 and has_raw_input:
    input = raw_input


def input_string(not_none=True):
    while True:
        str_input = str(input())
        if str_input.strip() == '':
            str_input = None
        if not not_none or str_input is not None:
            return str_input


def input_number(is_float=False, greater_or_eq=0, lower_or_eq=None):
    out = 0
    converted = False
    while not converted:
        try:
            if is_float:
                out = float(input())
            else:
                out = int(input())
            if (lower_or_eq is None or out <= lower_or_eq) and (greater_or_eq is None or out >= greater_or_eq):
                converted = True
            else:
                print('ERROR. Out of boundaries [{},{}], type again: '.format(greater_or_eq, lower_or_eq))
        except ValueError:
            if not is_float:
                print('ERROR. Not an integer, type again: ')
            else:
                print('ERROR. Not a float number, type again: ')
    return out


def input_numeric_list(is_float=False, greater_or_eq=0, lower_or_eq=None):
    out = ''
    not_converted = True
    while not_converted:
        try:
            out = input()
            out_test = out.split(',')
            for test in out_test:
                if is_float:
                    test = float(test)
                else:
                    test = int(test)
                if (lower_or_eq is None or test <= lower_or_eq) and (greater_or_eq is None or test >= greater_or_eq):
                    not_converted = False
                else:
                    print('ERROR. Out of boundaries [{},{}], type again: '.format(greater_or_eq, lower_or_eq))
                    not_converted = True
                    break
        except ValueError:
            if not is_float:
                print('ERROR. Not an integer, type again: ')
            else:
                print('ERROR. Not a float number, type again: ')
    return out


def input_boolean():
    while True:
        try:
            out = input()
            if out.lower() in ('true', '1', 't', 'y', 'yes', 'sim', 'verdade'):
                return True
            elif out.lower() in ('false', '0', 'f', 'n', 'no', 'nao', 'não', 'mentira'):
                return False
            else:
                raise ValueError()
        except:
            print('ERROR. Not a boolean, type again: ')
