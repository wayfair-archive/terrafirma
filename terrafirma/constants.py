SUPPORTED_CHECKS = ('google_compute_firewall', 'google_compute_instance', 'google_storage_bucket_acl')
SUPPORTED_DYNAMIC_CHECKS = {'google_compute_firewall': ('cidr_functions', 'util_functions'),
                            'google_compute_instance': ('cidr_functions', 'naming_conventions')
                            }
SEVERITY_LEVELS = {"INFO": 0,
                   "WARN": 2,
                   "FATAL": 3}
