from terrafirma.constants import SEVERITY_LEVELS


class Issue(object):

    def __init__(self, name, sev, resource_index, desc, issue_type, key="meta"):
        self.name = name
        self.severity = sev
        self.severity_level = SEVERITY_LEVELS[sev]
        self.resource_index = resource_index
        self.desc = desc
        self.issue_type = issue_type
        self.key = key
        self.reskey = self.resource_index + "." + self.key

    def get_issue_description(self, tf_plan):
        if self.issue_type != "meta_policy":
            return_string = "ISSUE: {}\n- DESCRIPTION: {}\n- SEVERITY: {}\n- RESOURCE: {}\n\n{}:\n{{\n {}: {}\n}}\n---".format(
                self.name, self.desc, self.severity, self.reskey, self.resource_index, self.key,
                (tf_plan[self.resource_index][self.key]))
        else:
            return_string = "ISSUE: {}\n- DESCRIPTON: {}\n- SEVERITY: {}\n- RESOURCE: {}\n---".format(
                self.name, self.desc, self.severity, self.reskey)
        return return_string
