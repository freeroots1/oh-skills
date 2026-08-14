#!/usr/bin/env python3
"""Generate password hash for Hermes dashboard"""
from plugins.dashboard_auth.basic import hash_password
print(hash_password('hermes123'))
