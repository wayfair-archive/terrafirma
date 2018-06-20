import json

from terrafirma.checks import meta_policy_check, read_stdin, enum_policy
from terrafirma.constants import SUPPORTED_CHECKS


def main():
    tf_plan = json.loads(read_stdin())
    issues = []
    highest_issue_level = 0

    for resource in tf_plan:
        for check in SUPPORTED_CHECKS:
            if resource.startswith(check):
                issues += enum_policy(check, tf_plan[resource], resource)

    for issue in issues:
        print(issue.get_issue_description(tf_plan))
        if(issue.severity_level > highest_issue_level):
            highest_issue_level = issue.severity_level

    meta_issues = meta_policy_check(issues)

    for meta_issue in meta_issues:
        print(meta_issue.get_issue_description(tf_plan))
        if(meta_issue.severity_level > highest_issue_level):
            highest_issue_level = meta_issue.severity_level

    raise SystemExit(highest_issue_level)
