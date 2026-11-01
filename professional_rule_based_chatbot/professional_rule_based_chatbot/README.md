# Nova Support — Rule-Based Interactive Terminal Assistant

A polished, configurable Python terminal chatbot built with **Python 3.9+** and the standard library. It demonstrates multi-intent recognition, regex-based text normalization, a JSON knowledge base, contextual business-hours responses, graceful fallback handling, and clean exit commands.

## Features

- **Multi-intent recognition:** scores patterns and can return more than one relevant answer.
- **Natural input handling:** case normalization, whitespace cleanup, punctuation handling, and phrase boundaries.
- **Editable FAQ dataset:** business responses and supported intents live in `data/faq.json`.
- **Business-hours awareness:** checks the current weekday and local system time against the configured schedule.
- **Conversation flow:** greeting, help/menu, thanks, support intents, fallback, and exit states.
- **Terminal-friendly UI:** readable headings, wrapped output, optional ANSI colors, and keyboard interrupt handling.
- **Safe support guidance:** sample responses warn users not to share passwords, OTPs, UPI PINs, CVVs, or full card details.
- **Unit tests:** basic automated tests for greeting, intent matching, exit, and empty input.
- **No third-party packages required.**

## Requirements

- Python 3.9 or newer
- Windows, macOS, or Linux terminal

## Run

Open a terminal in this project folder:

```bash
python chatbot.py
```

Disable terminal colors:

```bash
python chatbot.py --no-color
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Try these messages

```text
hello
help
What are your business hours?
Can you track my order?
Tell me about product availability
How can I pay?
I forgot my password
I want to return an item
Thank you
bye
```

## Customize for your own business

Open `data/faq.json`:

1. Change `assistant_name`.
2. Replace `support@example.com` in sample responses with your real support contact.
3. Update the `business_hours.schedule` values using 24-hour `HH:MM` format.
4. Add or edit entries in `intents`.

Each intent has this structure:

```json
{
  "name": "warranty",
  "category": "products",
  "patterns": ["warranty period", "product guarantee", "is it under warranty"],
  "response": "The warranty depends on the product. Please share its model number."
}
```

Add several natural ways a customer might ask the same question to `patterns`. Keep patterns specific enough to avoid accidental matches. The matcher is deterministic and rule-based; it does not use a language model or learn automatically.

## Project structure

```text
professional_rule_based_chatbot/
├── chatbot.py
├── data/
│   └── faq.json
├── tests/
│   └── test_chatbot.py
├── README.md
└── .gitignore
```

## Design notes and limitations

- This is a **terminal application**, not a hosted web chatbot. The terminal adapts output width; a browser-based responsive interface would be a separate frontend.
- The current sample FAQ and email are placeholders. Replace them before demonstrating it as a real company's assistant.
- The system uses transparent pattern scoring, not AI/ML. Ambiguous questions may trigger a fallback or a less relevant match; expand and test patterns for your domain.
- Business hours use the computer's local timezone.
- No user data is sent to a server or stored between sessions.

## Suggested future enhancements

- Add a web UI with FastAPI/Flask and a responsive chat interface.
- Add admin-managed FAQs, chat transcript export, and analytics.
- Add multilingual FAQ sets and configurable confidence thresholds.
- Connect verified order lookup APIs only after implementing authentication and authorization.
