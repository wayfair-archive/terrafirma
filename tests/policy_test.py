import json

from terrafirma.checks import load_policy, static_policy_check, meta_policy_check, dynamic_policy_check, is_issue_in_list


def run_policy_function(filename, resource_type, check_type):

    with open(filename) as handle:
        resource = json.load(handle)

    issues = []

    for issue in load_policy(resource_type)[resource_type]:
        if check_type == "static" and issue['checktype'] != "dynamic":
            opened_issue = static_policy_check(
                issue, resource["{}.default".format(resource_type)], check_type, resource_type + ".default")
            if opened_issue:
                issues.append(opened_issue)
        elif check_type == "dynamic" and issue['checktype'] == "dynamic":
            opened_issue = dynamic_policy_check(
                resource_type, resource["{}.default".format(resource_type)], issue, resource_type + ".default")
            if opened_issue:
                issues.append(opened_issue)
    return issues


def test_bad_static_policy():
    issues = run_policy_function(
        "tests/plans/firewall/bad_firewall_plan.json", "google_compute_firewall", "static")

    assert is_issue_in_list(issues, "FW_1") is True and is_issue_in_list(
        issues, "FW_2") is True


def test_good_static_policy():
    issues = run_policy_function(
        "tests/plans/firewall/good_firewall_plan.json", "google_compute_firewall", "static")

    assert is_issue_in_list(issues, "FW_1") is False and is_issue_in_list(
        issues, "FW_2") is True


def test_meta_policy():
    issues = run_policy_function(
        "tests/plans/firewall/bad_firewall_plan.json", "google_compute_firewall", "static")

    meta_issues = meta_policy_check(issues)
    assert is_issue_in_list(meta_issues, "MI_1") is True


def test_bad_dynamic_policy():
    issues = run_policy_function(
        "tests/plans/firewall/bad_firewall_plan.json", "google_compute_firewall", "dynamic")

    assert is_issue_in_list(issues, "FW_3") is True


def test_good_dynamic_policy():
    issues = run_policy_function(
        "tests/plans/firewall/good_firewall_plan.json", "google_compute_firewall", "dynamic")

    assert is_issue_in_list(issues, "FW_3") is False


def test_issue_severity():
    issues = run_policy_function(
        "tests/plans/firewall/bad_firewall_plan.json", "google_compute_firewall", "dynamic")

    for issue in issues:
        if(issue.name == "FW_2"):
            assert(issue.severity_level == 0)
        if(issue.name == "FW_4"):
            assert(issue.severity_level == 2)
        if(issue.name == "MI_1"):
            assert(issue.severity_level == 3)
