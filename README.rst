=================================================================================
Email sandbox
=================================================================================

Demonstration of how to retrieve mail from one's inbox.

Usage
================================================================================

Create a file called ``local_settings.py`` and define ``USERNAME`` and
``PASSWORD``. For example::

    USERNAME = "alice@example.com"
    PASSWORD = "password"

Then, run the server via::

    make

Navigate to http://localhost:8000/ to browse your mailboxes. Follow the links to
view messages.
