# Terrafirma: The Terraform Security Linter

Terrafirma runs on Terraform plans which have been converted to JSON with [tf2json](https://github.com/philips/tfjson). Below is a basic example.

## Usage:

Save your Terraform plan to a file and then convert it to JSON and pipe it to terrafirma:

``` 
$ terraform plan -out=my_plan
$ tfjson my_plan | python terrafirma
```

### Original Hashicorp Language plan:

```
provider "google" {
  region      = "us-east1"
  project     = "my-project"
}

resource "google_compute_firewall" "default" {
  name    = "example_fw_rule"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["443", "22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["test-node"]
}
```
This is converted into a binary file with terraform plan -out, and from there flattened into JSON with tf2json:
```
{
    "allow.#": "1", 
    "allow.9999999.ports.#": "2", 
    "allow.9999999.ports.0": "443", 
    "allow.9999999.ports.1": "22", 
    "allow.9999999.protocol": "tcp", 
    "destination_ranges.#": "", 
    "destroy": false, 
    "destroy_tainted": false, 
    "id": "", 
    "name": "example_fw_rule", 
    "network": "default", 
    "priority": "1000", 
    "project": "", 
    "self_link": "", 
    "source_ranges.#": "1", 
    "source_ranges.888888": "0.0.0.0/0", 
    "target_tags.#": "1", 
    "target_tags.8888888": "test-node"
}
```
Now Terrafirma is able to run checks, based on the YAML policies that are defined:

### With policies:
google_compute_firewall.yaml:
```
google_compute_firewall:
  - issue: FW_1
    name: Source range open to Internet
    fields:
      source_ranges:
        - 0.0.0.0/0
    level: WARN

  - issue: FW_2
    name: SSH Open
    fields:
      allow.ports:
       - "22"
      allow.protocol:
        - tcp
    level: INFO

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

### The output produced is:

```
---
ISSUE FW_1
- Source range open to Internet
- SEVERITY WARN
- RESOURCE example_fw_rule.google_compute_firewall
---
ISSUE FW_2
- SSH Open
- SEVERITY INFO
- RESOURCE example_fw_rule.google_compute_firewall
---
ISSUE FW_3
- Overly permissive rule, slash 8
- SEVERITY WARN
- RESOURCE example_fw_rule.google_compute_firewall
---
ISSUE MI_1
- SSH open to the Internet
- SEVERITY FATAL
- RESOURCE example_fw_rule.meta_policy
---
```

The program exits with an exit code corrosponding with the highest severity finding:


```
Exit code 0: No issues OR informational only
Exit code 1: Error
Exit code 2: Highest issue level is WARN
Exit code 3: Highest issue level is FATAL
```
