"""Tests for MarkdownV2 escaping in start handler messages."""

import re

from bot.handlers.start import WELCOME_MESSAGE, HELP_MESSAGE


class TestWelcomeMessageMarkdownV2:
    def test_no_unescaped_exclamation(self):
        """The '!' character must be escaped in MarkdownV2."""
        assert not re.search(r"(?<!\\)!", WELCOME_MESSAGE), (
            "WELCOME_MESSAGE contains unescaped '!' characters"
        )

    def test_no_unescaped_dot(self):
        """The '.' character must be escaped in MarkdownV2."""
        assert not re.search(r"(?<!\\)\.", WELCOME_MESSAGE), (
            "WELCOME_MESSAGE contains unescaped '.' characters"
        )


class TestHelpMessageMarkdownV2:
    def test_no_unescaped_exclamation(self):
        assert not re.search(r"(?<!\\)!", HELP_MESSAGE), (
            "HELP_MESSAGE contains unescaped '!' characters"
        )

    def test_no_unescaped_dot(self):
        assert not re.search(r"(?<!\\)\.", HELP_MESSAGE), (
            "HELP_MESSAGE contains unescaped '.' characters"
        )
