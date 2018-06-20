def instance_name_check(test, resource, key, value):
    if test == "ISBAD":
        if resource[key].startswith(value):
            return True
        else:
            return False
    else:
        return False
