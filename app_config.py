#!/usr/bin/env python3

"""
app_config.py
Global settings for the project, used across modules.
"""

# Required Gmail API permissions
PERMISSIONS = ['https://www.googleapis.com/auth/gmail.modify']

# Populated at runtime with database credentials + table name
DATABASE_SETTINGS = {}

# Path to OAuth credentials JSON
OAUTH_FILE = "oauth_creds.json"

# File containing JSON rules for processing emails
EMAIL_RULES_FILE = "email_rules.json"
