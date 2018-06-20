import operator

function_dict = {"GE": operator.ge,
                 "LE": operator.le,
                 "EQ": operator.eq
                 }


def range_comparison(test, resource, key, value):
    if "-" in resource[key]:
        port_range = abs(eval(resource[key]))
    else:
        port_range = 1

    if function_dict[test](port_range, value):
        return True
    else:
        return False
