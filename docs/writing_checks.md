# Writing checks

Checks are divided into three types:
* Static checks - validate matching fields
* Meta checks - Create issues out of multiple checks
* Dynamic checks - Call python functions on plan resources to determine check success or failure

## Static checks

Given the JSON input from our plan:

```
    "source_ranges.1080289494": "0.0.0.0/0", 
```

We can check for this value using the following YAML:

google_compute_firewall.yaml:
```
google_compute_firewall:
  - issue: FW_1
    name: Source range open to Internet
    fields:
      source_ranges:
        - 0.0.0.0/0
    level: WARN
```

This provides basic matching of the string `0.0.0.0/0` and outputs a `WARN` message.

```
---
ISSUE FW_1
- Source range open to Internet
- SEVERITY WARN
- RESOURCE example_fw_rule.google_compute_firewall
---
```

## Meta Checks

Meta checks run on issues created by static and dynamic checks.  In this case, the terraform plan produces two issues:
 * FW_1 (source range open to the Internet)
 * FW_2 (SSH open) 

```
    "source_ranges.1080289494": "0.0.0.0/0",
    "allow.805075243.ports.#": "2",
    "allow.805075243.ports.1": "22",
    "allow.805075243.protocol": "tcp",
```

The meta policy below creates a new issue from the combination of these issues: MI_1 which is higher severity than either issue alone.
Currently meta checks only support an `AND` operator.

meta_policy.yaml

```
meta_policy:
  -  issue: MI_1
     name: SSH open to the Internet
     checks:
       - FW_1
       - FW_2
     logic: AND
     level: FATAL

```

### Example Output:

```
ISSUE MI_1
- SSH open to the Internet
- SEVERITY FATAL
- RESOURCE example_fw_rule.meta_policy

```

## Dynamic checks

Sometimes we need to do more testing than simple string testing. This is when dynamic checks can be used for more advanced validation.

Given the terraform plan 
```
"source_ranges.1080289494": "0.0.0.0/0",
```
our static check will simply do a string comparison.  But what if the entry was 10.0.0.0/8?

First define a python function for testing. In this case we may want to lump multiple CIDR checks together so we have:

```
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
```

Currently, all dynamic checks require these four arguments, and require a `True` or `False` return.

We then modify `constants.py` to indicate we would like to use our dynamic check for firewalls and instances.  `SUPPORTED_CHECKS` indicates resource types we can run checks against, and `SUPPORTED_DYNAMIC_CHECKS` indicate the functions to use while performing dynamic checks on those resources.

```
SUPPORTED_CHECKS = ('google_compute_firewall', 'google_compute_instance')
SUPPORTED_DYNAMIC_CHECKS = {'google_compute_firewall': ('cidr_functions',),
                            'google_compute_instance': ('cidr_functions', 'naming_conventions')
                            }
```

and at this point, we can use our check in our YAML policy:

```
  - issue: FW_3
    checktype: dynamic
    name: Overly permissive rule, slash 8
    function: cidr_comparison
    test: GE
    fields:
      source_ranges:
         - "8"
    level: WARN
```

Terrafirma will look in the namespace for a function defined in the YAML, and pass it specified arguments. A `False` return value opens an issue.

```
ISSUE FW_3
- Overly permissive rule, slash 8
- SEVERITY WARN
- RESOURCE example_fw_rule.google_compute_firewall
```
