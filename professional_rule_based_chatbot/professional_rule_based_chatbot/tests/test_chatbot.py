import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chatbot import RuleBasedAssistant


class ChatbotTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "faq.json"
        data = {
            "assistant_name": "Test Bot",
            "suggested_topics": ["orders"],
            "business_hours": {"schedule": {}},
            "intents": [
                {"name": "order_status", "patterns": ["track my order", "order status"],
                 "response": "Please provide your order ID."}
            ]
        }
        self.path.write_text(json.dumps(data), encoding="utf-8")
        self.bot = RuleBasedAssistant(self.path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_greeting(self):
        response, should_exit = self.bot.respond("hello")
        self.assertIn("Test Bot", response)
        self.assertFalse(should_exit)

    def test_intent_match(self):
        response, should_exit = self.bot.respond("Can you track my order?")
        self.assertIn("order ID", response)
        self.assertFalse(should_exit)

    def test_exit(self):
        response, should_exit = self.bot.respond("quit")
        self.assertTrue(should_exit)
        self.assertIn("goodbye", response.lower())

    def test_empty_message(self):
        response, _ = self.bot.respond("   ")
        self.assertIn("didn't receive", response)


if __name__ == "__main__":
    unittest.main()
