import os
import sys
import six
import yaml
from importlib import import_module
from terrafirma.policy_issue import Issue
from terrafirma.constants import SUPPORTED_DYNAMIC_CHECKS


def is_issue_in_list(issue_list, issue_name):
    for item in issue_list:
        if item.name == issue_name:
            return True

    return False


def load_policy(name):
    policy_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "policy/{}.yaml".format(name)
    )
    handle = open(policy_path)
    policy = yaml.load(handle)
    return policy


def key_filter(key):
    """
    Returns a cleaned key name

    Key names retrieved via tfjson include Terraform state numbers, as well as indices.  The keys also
    may include hash marks.  This function removes both for comparison to policy YAML files.

    Args:
      key (str): a key string

    Returns:
      str: a cleaned key string or the Issue
     """
    cleaned_key = ""
    split_key = key.split('.')
    for item in split_key:
        if not item.isdigit():
            cleaned_key = cleaned_key + "{}.".format(item)

    return cleaned_key[:-1].replace("#", "")


def locate_resource(resource, index, issue, check_type):
    """
    Locate a particular element in a resource based on the value in a check

    First this function iterates through the issue looking for the elements in the 'field' key.  It creates
    a list of these fields.

    The function then iterates through our resource, attempting to match the fields from our YAML policy (converted
    into a dict) to the resource.  Once it finds a match it increments the matched_fields counter and sets the
    last_matched_key.  If the check is dynamic, we dont actually want to match the value of the field, we want to do a
    comparison of it's value with our function, so check_type is used to branch.

    Args:
      resource (dict): A dict representing the resource we're checking
      index (str): A string which will vary between fields or checks depending if we're in a meta policy or not.
      issue (dict): A dict representation of our issue. NOT an Issue.
      check_type (str): Either "dynamic" or not. Dynamic checks don't want to match exact values

    Returns:
      int: A counter for detecting multiple matched fields.
      str: A string representing a key in a JSON object where we matched last. Useful for printing context later

    """

    matched_fields = []
    fields = []

    for field in issue[index]:
        fields.append(field)

    for key in resource:
        key_filtered = key_filter(key)
        if key_filtered in fields:
            if check_type == "dynamic":
                matched_fields.append(key)
            if resource[key] == str(issue[index][key_filter(key)][0]):
                matched_fields.append(key)

    if check_type == "dynamic":
        return matched_fields, matched_fields[-1] if matched_fields else None

    return len(matched_fields), matched_fields[-1] if matched_fields else None


def meta_policy_check(issues):
    """Checks for meta issues: Combinations of other issues

    This function takes a list of issues of type Issues and loads 'meta_policy'.  This policy contains
    combinations of issues which will raise the associated meta_issue.

    First it iterates through meta_issues in the meta_policy, and iterates through the check in each issue.
    these checks are appended to a list and then run through a check: if the issue in question is in the list of
    checks it is flagged

    Args:
      issues (list): A list of non-meta issues.

    Returns:
      set: A set of opened meta_issues.
    """

    policy_type = "meta_policy"
    policy = load_policy(policy_type)

    meta_issues = []
    check_list = []

    for meta_issue in policy[policy_type]:
        matched_checks = 0
        matched_resource = None
        for check in meta_issue['checks']:
            check_list.append(check)

        for check in check_list:
            if is_issue_in_list(issues, check):
                matched_checks = matched_checks + 1
                matched_resource = check

        if matched_checks == len(meta_issue['checks']):
            meta_issues.append(Issue(
                meta_issue['issue'], meta_issue['level'], matched_resource, meta_issue['name'], policy_type))

        return set(meta_issues)


def dynamic_policy_check(policy_type, resource, issue, resource_index):
    """
    Runs through dynamic (functional) policy checks.

    Dynamic checks defined in our policy file include a function name, a test, a field and a value.
    For example, in a static check 0.0.0.0/0 is analyzed a string, where as with a function we can analyze it as an
    ip address object.

    Creates a new issue based on the results of function name retrieved from the YAML file.

    Args:
      policy_type (str): A string representing what type of policy.  Used when opening an issue
      resource (dict): A dict object representing our resource
      issue (dict): An JSON-serialized Issue against which we are checking

    Returns:
      Issue: An issue we have opened

    """

    opened_issue = None

    for dyn_func in SUPPORTED_DYNAMIC_CHECKS[policy_type]:
        package_name = "terrafirma.{}".format(dyn_func)
        mod = import_module(package_name)
        if hasattr(mod, issue['function']):
            policy_check_function = getattr(mod, issue['function'])

    index = "fields"

    matched_fields, last_matched_key = locate_resource(
        resource, index, issue, 'dynamic')
    # a little py2/py3 compatibility voodoo here
    # see https://stackoverflow.com/questions/17431638/get-typeerror-dict-values-object-does-not-support-indexing-when-using-python
    if matched_fields:
        expected_value = list(six.viewvalues(issue['fields']))[0][0]
        val = policy_check_function(
            issue['test'], resource, last_matched_key, expected_value)
        if val:
            opened_issue = Issue(
                issue['issue'], issue['level'], resource_index,
                issue['name'], policy_type, last_matched_key
            )

    return opened_issue


def static_policy_check(issue, resource, policy_type, resource_index):
    """ The static policy check function

    Wrapper for locate_resource and a sanity check to handle multiple matches.

    Args:
      issue (dict): A JSON-serialized Issue
      resource (dict): A dict representing our resource to check
      policy_type (str): A string with our policy_type, used when opening resources

    Returns:
      Issue: An opened issues.

    """
    index = "fields"
    opened_issue = None

    matched_fields, last_matched_key = locate_resource(
        resource, index, issue, 'static')

    if matched_fields == len(issue[index]):
        opened_issue = Issue(
            issue['issue'], issue['level'], resource_index, issue['name'], policy_type, last_matched_key
        )

    return opened_issue


def read_stdin():
    data = ""
    for line in sys.stdin:
        data = data + line
    return data


def enum_policy(policy_type, resource, resource_index):
    """ Loads and enumerates through a policy file

    Loads the policy, enumerates through, calls static and dynamic checks.

    Args:
      policy_type (str): A string represented what type of policy.
      resource (dict): A dict object representing our resource

    Calls:
      static_policy_check(): For type: static issues
      dynamic_policy_check(): For type: dynamic issues

    Returns:
      list of type Issue: A list of our opened issues

    """

    opened_issues = []
    opened_issue = None

    policy = load_policy(policy_type)

    for issue in policy[policy_type]:
        if issue['checktype'] == "static":
            opened_issue = static_policy_check(
                issue, resource, policy_type, resource_index)
        elif issue['checktype'] == "dynamic":
            opened_issue = dynamic_policy_check(
                policy_type, resource, issue, resource_index)
        if opened_issue:
            opened_issues.append(opened_issue)

    return opened_issues
