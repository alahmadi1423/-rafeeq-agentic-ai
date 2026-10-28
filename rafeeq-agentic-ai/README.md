# Rafeeq — Agentic AI Municipal Assistant

An educational prototype for a fictional municipal services assistant.

## Current features

- Local synthetic policy lookup
- Application validation
- Draft preparation
- Human approval checkpoint
- Automated tests
- Demo mode without an API key

## Data notice

All policies and example applicant information are synthetic.
They are not official Saudi municipal regulations.

## Requirements

Python 3.11 or a compatible version, and pip.

## Run in Google Colab

Open the notebook in this repository and run the cells in order.

## Run locally

Create a virtual environment and install pytest:

    python -m pip install pytest

From the project root, run:

    python -m pytest -v

## Security

No API key is required for the current demo.

Never commit .env files or real API keys.
Live model integration will be configured separately through
environment variables or a deployment secrets manager.

## Project status

Initial prototype. Live LLM integration, MCP, advanced retrieval,
evaluation, and the production API are planned next stages.
