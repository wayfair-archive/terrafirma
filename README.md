# Terrafirma

Terrafirma is a Terraform static analysis tool designed for detecting security misconfigurations.  Inspired by projects such as [bandit](https://github.com/openstack/bandit) and [SecurityMonkey](https://github.com/Netflix/security_monkey) it is designed for use in a continous integration/deployment environment.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Terrafirma requires [tfjson](https://github.com/philips/tfjson).  Terraform does not support JSON output (see [PR:3170](https://github.com/hashicorp/terraform/pull/3170)). 

```
go get github.com/philips/tfjson
```

### Installing

build and install terrafirma as well as it's requirements. One way is to use wheels and virtualenv:

```
virtualenv -p python3 virtualenv
source virtualenv/bin/activate
pip install -r requirements.txt
python setup.py build bdist_wheel
pip install terrafirma --find-links=dist
```

You can determine if it was installed correctly by running the checks in the next section.

### Testing

to check that terrafirma is installed and functioning correctly you can execute the included tests:

```
python setup.py test
```

### Usage
*   See [Basic Usage](docs/basic_usage.md) for examples of how to use Terrafirma
*   See [Writing Checks](docs/writing_checks.md) for help understanding the check types and implementing new checks
*   See [Tests](docs/tests.md) for running terrafirma unit tests to ensure it's functioning correctly.
