#!/usr/bin/env python3
"""
main_cli_interactive.py

A command-line interface for the Gmail Rule-Based Email Processor.
This script interactively prompts the user for:
  - PostgreSQL configuration (user, password, db name, table name)
  - Path to the OAuth credentials JSON file
  - Email retrieval method and value
  - Interactive rule creation (conditions and actions)
  - Match policy (All/Any)
Then it fetches emails and applies the rules to stored emails.

It uses the core modules:
  - app_config.py
  - mail_service.py
  - pg_handler.py
  - rule_processor.py
"""

import sys
import os
import json
import getpass

import app_config
from pg_handler import init_database_if_missing, init_pg_table
from rule_processor import fetch_and_save_emails, apply_email_rules

def configure():
    print("=== Configuration ===")
    db_user = input("Enter PostgreSQL Username: ").strip()
    db_password = getpass.getpass("Enter PostgreSQL Password: ")
    db_name = input("Enter Database Name: ").strip()
    table_name = input("Enter Table Name: ").strip()
    oauth_file = input("Enter path to OAuth credentials JSON file: ").strip()
    
    # Update global configuration
    app_config.DATABASE_SETTINGS.clear()
    app_config.DATABASE_SETTINGS.update({
        "host": "localhost",
        "user": db_user,
        "password": db_password,
        "database": db_name,
        "table": table_name
    })
    
    if not os.path.exists(oauth_file):
        print(f"Error: OAuth credentials file '{oauth_file}' not found.")
        sys.exit(1)
    app_config.OAUTH_FILE = oauth_file
    
    print("\nConfiguration updated.")
    # Initialize database and table
    print(init_database_if_missing(app_config.DATABASE_SETTINGS))
    print(init_pg_table())

def fetch_emails_cli():
    print("\n=== Fetch Emails ===")
    print("Select retrieval method:")
    print("  1) Fetch by number of messages")
    print("  2) Fetch by timeframe (e.g., emails newer than a certain number of days/months)")
    method = input("Enter 1 or 2: ").strip()
    
    if method == "1":
        count = input("Enter the number of emails to fetch: ").strip()
        msg_param = count if count.isdigit() else "10"
    elif method == "2":
        timeframe_value = input("Enter timeframe value (number): ").strip()
        timeframe_unit = input("Enter timeframe unit ('days' or 'months'): ").strip().lower()
        if timeframe_unit not in ["days", "months"]:
            print("Invalid unit, defaulting to 'days'.")
            timeframe_unit = "days"
        msg_param = f"newer_than:{timeframe_value}{timeframe_unit[0]}"
    else:
        print("Invalid selection. Defaulting to fetching 10 messages.")
        msg_param = "10"
    
    result = fetch_and_save_emails(msg_param)
    print("\nFetch Emails Result:")
    print(result)

def create_rules_interactively():
    print("\n=== Rule Creation ===")
    conditions = []
    actions = []
    
    # Get conditions
    try:
        num_conditions = int(input("How many conditions do you want to add? "))
    except ValueError:
        num_conditions = 0
    for i in range(num_conditions):
        print(f"\nCondition #{i+1}:")
        field = input("  Enter field (From, To, Subject, Received Date/Time, Message): ").strip()
        # Validate field
        if field not in ["From", "To", "Subject", "Received Date/Time", "Message"]:
            print("  Invalid field. Defaulting to 'From'.")
            field = "From"
        # Choose predicate based on field type
        if field == "Received Date/Time":
            print("  Choose predicate: (1) less than, (2) greater than")
            pred_choice = input("  Enter 1 or 2: ").strip()
            predicate = "less than" if pred_choice == "1" else "greater than"
        else:
            print("  Choose predicate: (1) contains, (2) does not contain, (3) equals, (4) does not equal")
            pred_choice = input("  Enter 1, 2, 3, or 4: ").strip()
            predicate = {
                "1": "contains",
                "2": "does not contain",
                "3": "equals",
                "4": "does not equal"
            }.get(pred_choice, "contains")
        value = input("  Enter value to compare: ").strip()
        unit = ""
        if field == "Received Date/Time":
            unit = input("  Enter unit ('days' or 'months'): ").strip().lower()
            if unit not in ["days", "months"]:
                print("  Invalid unit, defaulting to 'days'.")
                unit = "days"
        condition = {"field": field, "predicate": predicate, "value": value}
        if field == "Received Date/Time":
            condition["unit"] = unit
        conditions.append(condition)
    
    # Get actions
    try:
        num_actions = int(input("\nHow many actions do you want to add? "))
    except ValueError:
        num_actions = 0
    for i in range(num_actions):
        print(f"\nAction #{i+1}:")
        print("  Choose action:")
        print("    1) Mark as Read")
        print("    2) Mark as Unread")
        print("    3) Move Message")
        print("    4) Star")
        print("    5) Unstar")
        print("    6) Archive")
        print("    7) Trash")
        action_choice = input("  Enter number (1-7): ").strip()
        action_map = {
            "1": "mark as read",
            "2": "mark as unread",
            "3": "move message",
            "4": "star",
            "5": "unstar",
            "6": "archive",
            "7": "trash"
        }
        action = action_map.get(action_choice, "mark as read")
        action_dict = {"action": action}
        if action == "move message":
            dest = input("  Enter destination (Inbox, Forum, Updates, Promotions): ").strip()
            if dest.lower() not in ["inbox", "forum", "updates", "promotions"]:
                print("  Invalid destination. Defaulting to 'inbox'.")
                dest = "inbox"
            action_dict["destination"] = dest.lower()
        actions.append(action_dict)
    
    # Get match policy
    match_policy = input("\nEnter match policy ('All' or 'Any'): ").strip()
    if match_policy.lower() not in ["all", "any"]:
        print("Invalid match policy. Defaulting to 'All'.")
        match_policy = "All"
    
    ruleset = {"match_policy": match_policy, "rules": conditions, "actions": actions}
    return ruleset

def save_rules_cli(ruleset):
    """Save ruleset to the JSON file."""
    with open(app_config.EMAIL_RULES_FILE, "w") as f:
        json.dump(ruleset, f, indent=4)
    print("\nRules saved to file.")

def apply_rules_cli():
    print("\n=== Apply Rules ===")
    choice = input("Do you want to apply rules to the stored emails? (y/n): ").strip().lower()
    if choice == "y":
        result = apply_email_rules()
        print("\nApply Rules Result:")
        print(result)
    else:
        print("Rules were not applied.")

def main():
    print("Gmail Rule-Based Email Processor (CLI Version)")
    print("-----------------------------------------------\n")
    # Configuration
    configure()
    
    # Fetch Emails
    fetch_emails_cli()
    
    # Rule Creation
    create_choice = input("\nDo you want to create rules interactively? (y/n): ").strip().lower()
    if create_choice == "y":
        ruleset = create_rules_interactively()
        print("\nFinal Ruleset:")
        print(json.dumps(ruleset, indent=4))
        save_rules_cli(ruleset)
    else:
        print("Skipping rule creation. Using existing rules if available.")
    
    # Apply Rules
    apply_rules_cli()
    print("\nDone.")

if __name__ == "__main__":
    main()
