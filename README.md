# HappyFoxAssessment
 This is my official project submission for HappyFox Internship.
# Gmail Rule-Based Email Processor
==============================


Overview
--------


The Gmail Rule-Based Email Processor is designed to help you automate your inbox by fetching emails from Gmail,
storing them in a PostgreSQL database, and applying user-defined rules. These rules can automatically mark emails
as read/unread, move, star, unstar, archive, or trash them.


Table of Contents
-----------------


* [Overview](#overview)
* [Features](#features)
* [Project Structure](#project-structure)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)
* [Rule Editor Details](#rule-editor-details)
* [Design Decisions](#design-decisions)
* [Screenshots](#screenshots)



Overview
--------


The Gmail Rule-Based Email Processor integrates with the Gmail API to fetch emails, store them in a PostgreSQL
database, and process them based on user-defined rules. The rules can automatically mark emails as read/unread,
move, star, unstar, archive, or trash them.


Key highlights:


* Streamlit UI for easy configuration and operation
* Gmail API with OAuth 2.0 for secure email retrieval
* PostgreSQL database for storing and retrieving email data
* Dynamic Rule Engine for automated email actions


Features
--------


### Secure Gmail Authentication


Uses OAuth 2.0 to connect to your Gmail account without exposing passwords.


### Flexible Rule Definition


* Conditions: From, To, Subject, Received Date/Time, Message body
* Predicates for text (contains, does not contain, equals, does not equal) and dates (less than, greater than for
days or months)
* Value: The text or number for comparison


### Actions


* Mark as Read/Unread
* Move Message (Inbox, Forum, Updates, Promotions)
* Star/Unstar
* Archive (remove INBOX label)
* Trash (moves email to Trash)


Project Structure
-----------------


The project is structured into four main modules:

* `app_config.py`: Global settings (SCOPES, OAUTH_FILE, DATABASE_SETTINGS, etc.)
* `mail_service.py`: Handles Gmail API logic.
* `pg_handler.py`: Handles database creation, insertion, and retrieval.
* `rule_processor.py`: Loads rules, evaluates emails, and executes actions.
* `streamlit_app.py`: Provides a clean, web-based UI.


Prerequisites
-------------


* Python 3.10+
* Gmail account with OAuth 2.0 credentials
* PostgreSQL database


Installation
------------


1. Clone the repository: `git clone https://github.com/ramya-git812/HappyFoxAssessment.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `streamlit run streamlit_app.py`


Configuration
-------------


1. Enter your Gmail credentials and select the database configuration.
2. Choose the retrieval method (Number of Messages or Timeframe).
3. Save the configuration to initialize the database and table.


Usage
-----


1. Fetch emails from Gmail using the chosen method.
2. Load existing rules or create new ones using the Rule Editor.
3. Apply rules to stored emails in real-time.


Rule Editor Details
------------------


### Conditions


* Field: From, To, Subject, Received Date/Time, Message
* Predicate (for text): contains, does not contain, equals, does not equal
* Predicate (for date): less than, greater than (with "days" or "months")
* Value: The text or number for comparison


### Actions


* Mark as Read/Unread
* Move Message (Inbox, Forum, Updates, Promotions)
* Star/Unstar
* Archive (remove INBOX label)
* Trash (moves email to Trash)


Design Decisions
-----------------


The project follows modular code and OAuth 2.0 security best practices.


* Modular Code: Each module handles a specific task, making it easy to maintain and extend.
* OAuth 2.0 Security: Users upload their Gmail credentials file; the system never exposes raw credentials in code.


Screenshots 
-----------------------



