#!/usr/bin/env python3

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys, os

# Append the parent directory so our modules can be imported.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import functions from our updated project modules
import mail_service
import rule_processor

# ----------------------- Unit Tests for Mail Service -----------------------
class TestMailService(unittest.TestCase):
    def test_convert_date_string_valid(self):
        # Test with a proper email date header.
        date_str = "Tue, 15 Nov 2022 12:45:26 +0000"
        dt = mail_service.convert_date_string(date_str)
        self.assertIsInstance(dt, datetime)
        self.assertEqual(dt.strftime('%Y-%m-%d'), '2022-11-15')
    
    def test_convert_date_string_invalid(self):
        # When the date string is invalid, expect None.
        date_str = "Invalid Date String"
        dt = mail_service.convert_date_string(date_str)
        self.assertIsNone(dt)

# ----------------------- Unit Tests for Rule Processor -----------------------
class TestRuleProcessorUnit(unittest.TestCase):
    def test_check_condition_contains(self):
        # Check if the 'contains' condition works for text.
        condition = {"predicate": "contains", "value": "test"}
        self.assertTrue(rule_processor.check_condition("This is a test email", condition))
        self.assertFalse(rule_processor.check_condition("No match here", condition))
    
    def test_check_condition_date_less_than(self):
        # Test the date condition: email received less than 7 days ago.
        condition = {"predicate": "less than", "value": "7", "unit": "days"}
        email_date = datetime.now() - timedelta(days=5)
        self.assertTrue(rule_processor.check_condition(email_date, condition))
    
    def test_check_condition_date_greater_than(self):
        # Test the date condition: email received more than 7 days ago.
        condition = {"predicate": "greater than", "value": "7", "unit": "days"}
        email_date = datetime.now() - timedelta(days=10)
        self.assertTrue(rule_processor.check_condition(email_date, condition))
    
    def test_evaluate_email_rules_all(self):
        # Test evaluating an email when ALL conditions must match.
        email = {
            "from": "example@example.com",
            "subject": "Test Email",
            "received_date": datetime.now() - timedelta(days=3),
            "message": "This is a test email."
        }
        ruleset = {
            "match_policy": "All",
            "rules": [
                {"field": "From", "predicate": "contains", "value": "example"},
                {"field": "Subject", "predicate": "contains", "value": "Test"}
            ]
        }
        self.assertTrue(rule_processor.evaluate_email_rules(email, ruleset))
    
    def test_evaluate_email_rules_any(self):
        # Test evaluating an email when ANY condition is enough to match.
        email = {
            "from": "user@domain.com",
            "subject": "Another Email",
            "received_date": datetime.now() - timedelta(days=1),
            "message": "No test content here."
        }
        ruleset = {
            "match_policy": "Any",
            "rules": [
                {"field": "From", "predicate": "contains", "value": "example"},
                {"field": "Subject", "predicate": "contains", "value": "Email"}
            ]
        }
        # Since the subject contains "Email", at least one condition is met.
        self.assertTrue(rule_processor.evaluate_email_rules(email, ruleset))

# ----------------------- Integration Tests -----------------------
class TestIntegration(unittest.TestCase):
    @patch('mail_service.authorize_email_service')
    @patch('mail_service.fetch_emails')
    @patch('mail_service.retrieve_email')
    @patch('pg_handler.insert_email_pg')
    def test_fetch_and_save_emails_integration(self, mock_insert_email, mock_retrieve_email, mock_fetch_emails, mock_authorize):
        # Setup mocks to simulate Gmail API responses.
        fake_service = MagicMock()
        mock_authorize.return_value = fake_service
        
        # Simulate fetch_emails returning one fake message.
        fake_message = {"id": "12345"}
        mock_fetch_emails.return_value = [fake_message]
        
        # Simulate retrieve_email returning fake email details.
        fake_email_data = {
            "email_id": "12345",
            "from": "test@example.com",
            "to": "user@example.com",
            "subject": "Integration Test",
            "received_date": datetime.now(),
            "message": "This is a test message."
        }
        mock_retrieve_email.return_value = fake_email_data
        
        # Simulate a successful insert into the database.
        mock_insert_email.return_value = "Stored email 12345"
        
        # Call the function to fetch and save emails.
        from rule_processor import fetch_and_save_emails
        result = fetch_and_save_emails("1")
        self.assertIn("Stored email 12345", result)
    
    @patch('rule_processor.authorize_email_service')
    @patch('rule_processor.get_emails_pg')
    @patch('rule_processor.execute_email_actions')
    def test_apply_email_rules_integration(self, mock_execute_actions, mock_get_emails, mock_authorize):
        # Setup mocks to simulate the rules processing flow.
        fake_service = MagicMock()
        mock_authorize.return_value = fake_service
        
        # Simulate fetching one fake email from the database.
        fake_email = {
            "email_id": "67890",
            "from": "rule@example.com",
            "subject": "Rule Test",
            "received_date": datetime.now() - timedelta(days=2),
            "message": "Apply rule."
        }
        mock_get_emails.return_value = [fake_email]
        
        # Create a fake ruleset.
        fake_ruleset = {
            "match_policy": "All",
            "rules": [
                {"field": "From", "predicate": "contains", "value": "rule"}
            ],
            "actions": [{"action": "mark as read"}]
        }
        
        # Patch load_email_rules to return our fake ruleset.
        with patch('rule_processor.load_email_rules', return_value=fake_ruleset):
            # Simulate execute_email_actions returning a success message.
            mock_execute_actions.return_value = "Email 67890 marked as read."
            result = rule_processor.apply_email_rules()
            self.assertIn("Email 67890", result)
            self.assertIn("marked as read", result)

if __name__ == "__main__":
    unittest.main()
