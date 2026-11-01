#!/usr/bin/env python3
"""
Professional Rule-Based Interactive Terminal Assistant
Python 3.9+ | Standard library only
Run: python chatbot.py
"""
from __future__ import annotations

import json
import re
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
FAQ_PATH = ROOT / "data" / "faq.json"

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
BLUE = "\033[94m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"


def color(text: str, shade: str, enabled: bool = True) -> str:
    return f"{shade}{text}{RESET}" if enabled else text


def terminal_width() -> int:
    try:
        return max(60, min(100, __import__("shutil").get_terminal_size((80, 24)).columns))
    except OSError:
        return 80


def wrap(text: str, indent: int = 0) -> str:
    width = max(40, terminal_width() - indent - 2)
    return textwrap.fill(text, width=width, subsequent_indent=" " * indent)


@dataclass
class Match:
    intent: str
    score: float
    response: str
    source: str = "knowledge base"


class RuleBasedAssistant:
    """Intent matcher and response engine backed by editable JSON knowledge."""

    EXIT_WORDS = {"bye", "exit", "quit", "goodbye", "close"}
    GREETING_WORDS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
    THANKS_WORDS = {"thanks", "thank you", "thx", "appreciate it"}

    def __init__(self, faq_path: Path = FAQ_PATH, threshold: float = 0.34):
        self.faq_path = faq_path
        self.threshold = threshold
        self.knowledge = self._load_knowledge()
        self.turn_count = 0
        self.last_intent: str | None = None
        self.user_name: str | None = None

    def _load_knowledge(self) -> dict[str, Any]:
        try:
            with self.faq_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict) or "intents" not in data:
                raise ValueError("FAQ file must contain an 'intents' list.")
            return data
        except FileNotFoundError:
            raise RuntimeError(f"Knowledge file not found: {self.faq_path}")
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid JSON in {self.faq_path}: {exc}") from exc

    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^\w\s@.+'-]", " ", text)
        return re.sub(r"\s+", " ", text)

    @staticmethod
    def _phrase_present(phrase: str, text: str) -> bool:
        phrase = RuleBasedAssistant.normalize(phrase)
        return bool(re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text))

    def _score_intent(self, user_text: str, intent: dict[str, Any]) -> float:
        normalized = self.normalize(user_text)
        phrases = intent.get("patterns", [])
        if not phrases:
            return 0.0
        best = 0.0
        words = set(normalized.split())
        for phrase in phrases:
            p = self.normalize(phrase)
            if not p:
                continue
            if self._phrase_present(p, normalized):
                score = 1.0 if p == normalized else min(0.98, 0.72 + 0.04 * len(p.split()))
            else:
                p_words = set(p.split())
                overlap = len(words & p_words) / max(1, len(p_words))
                # Small penalty for very short/common matches.
                score = overlap * (0.72 if len(p_words) <= 1 else 0.88)
            best = max(best, score)
        return best

    def detect_intents(self, user_text: str) -> list[Match]:
        matches: list[Match] = []
        for intent in self.knowledge["intents"]:
            score = self._score_intent(user_text, intent)
            if score >= self.threshold:
                matches.append(Match(
                    intent=intent["name"],
                    score=score,
                    response=intent["response"],
                    source=intent.get("category", "knowledge base"),
                ))
        return sorted(matches, key=lambda item: item.score, reverse=True)

    def business_hours_response(self) -> str:
        config = self.knowledge.get("business_hours", {})
        now = datetime.now()
        day = now.strftime("%A").lower()
        today = config.get("schedule", {}).get(day)
        if not today or today.get("closed", False):
            return f"We are currently closed today. {config.get('closed_message', 'Please contact us during business hours.')}"
        opening = datetime.strptime(today["open"], "%H:%M").time()
        closing = datetime.strptime(today["close"], "%H:%M").time()
        current = now.time()
        status = "open" if opening <= current < closing else "closed"
        return (
            f"Our business is **{status}** right now. Today's hours are "
            f"{opening.strftime('%I:%M %p').lstrip('0')}–{closing.strftime('%I:%M %p').lstrip('0')}."
        )

    def respond(self, user_text: str) -> tuple[str, bool]:
        """Return (response, should_exit). Supports multiple intents in one message."""
        raw = user_text.strip()
        normalized = self.normalize(raw)
        if not normalized:
            return "I didn't receive a message. Please type a question or choose a suggested topic.", False

        if normalized in self.EXIT_WORDS:
            return "Thank you for chatting with us. Goodbye, and have a great day!", True

        if normalized in self.GREETING_WORDS or any(
            normalized.startswith(g + " ") for g in self.GREETING_WORDS
        ):
            name = f", {self.user_name}" if self.user_name else ""
            return (
                f"Hello{name}! I'm {self.knowledge.get('assistant_name', 'Support Assistant')}. "
                "I can help with business hours, products, orders, returns, payments, and account questions. "
                "What would you like to know?"
            ), False

        if normalized in self.THANKS_WORDS:
            return "You're very welcome! Is there anything else I can help you with?", False

        if normalized in {"help", "menu", "what can you do", "options"}:
            topics = self.knowledge.get("suggested_topics", [])
            return "Here are some things I can help with:\n" + "\n".join(f"  • {topic}" for topic in topics), False

        if "business hours" in normalized or "opening hours" in normalized or "are you open" in normalized:
            self.last_intent = "business_hours"
            return self.business_hours_response(), False

        matches = self.detect_intents(raw)
        if matches:
            # Return up to two genuinely distinct intent answers for multi-intent queries.
            selected = [matches[0]]
            if len(matches) > 1 and matches[1].score >= max(self.threshold, matches[0].score * 0.72):
                selected.append(matches[1])
            self.last_intent = selected[0].intent
            if len(selected) == 1:
                return selected[0].response, False
            return "\n\n".join(
                f"**{m.intent.replace('_', ' ').title()}**\n{m.response}" for m in selected
            ), False

        return (
            "I'm sorry, I couldn't confidently match that question to my support topics. "
            "Could you rephrase it or type **help** to see what I can answer? "
            "If this needs a person, please contact support@example.com."
        ), False


def render_header(assistant_name: str, use_color: bool = True) -> None:
    width = terminal_width()
    line = "═" * (width - 2)
    print(color("╔" + line + "╗", CYAN, use_color))
    title = f"  {assistant_name}  •  Rule-Based Support"
    print(color("║", CYAN, use_color) + color(title[:width-4].ljust(width-4), BOLD, use_color) + color("║", CYAN, use_color))
    print(color("╚" + line + "╝", CYAN, use_color))
    print(color("  Secure local session | Type 'help' for topics | Type 'exit' to quit\n", DIM, use_color))


def main() -> int:
    no_color = "--no-color" in sys.argv or not sys.stdout.isatty()
    try:
        assistant = RuleBasedAssistant()
    except RuntimeError as exc:
        print(color(f"Startup error: {exc}", RED, not no_color))
        return 1

    render_header(assistant.knowledge.get("assistant_name", "Support Assistant"), not no_color)
    print(color("Assistant:", GREEN, not no_color), wrap(
        "Hello! Welcome. I can answer common product and customer-support questions. How can I help?"
    ))
    while True:
        try:
            user_text = input(color("\nYou  › ", BLUE, not no_color)).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + color("Assistant:", GREEN, not no_color), "Session ended. Goodbye!")
            break

        response, should_exit = assistant.respond(user_text)
        print(color("\nAssistant:", GREEN, not no_color))
        for paragraph in response.split("\n"):
            print(wrap(paragraph, indent=2) if paragraph else "")
        assistant.turn_count += 1
        if should_exit:
            break
    print(color(f"\nSession summary: {assistant.turn_count} user message(s).", DIM, not no_color))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
