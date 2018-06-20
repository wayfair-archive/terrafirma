import operator

import iptools

function_dict = {"GE": operator.ge,
                 "LE": operator.le,
                 "EQ": operator.eq
                 }


def cidr_comparison(test, resource, key, value):
    ip_range = iptools.IpRange(resource[key])
    host_bits = 32 - int(value)
    if function_dict[test](len(ip_range), 2**host_bits):
        return True
    else:
        return False
