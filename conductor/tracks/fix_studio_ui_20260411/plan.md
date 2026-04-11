# Implementation Plan: Agent Studio UI Fix

## Layer 1: The Chat Handler API
- [x] Task: Implement a `POST /chat` route in `chassis.py` to handle the Studio UI's sync requests and interface with the agent.

## Layer 2: The HTML/CSS Structure
- [x] Task: Update the `GET /studio` endpoint in `chassis.py` to serve a full HTML document.
- [x] Task: Implement the Tailwind CSS layout (dark mode, scrollable history, input area, file upload).

## Layer 3: Client-Side Logic
- [x] Task: Implement Vanilla JS logic for message rendering, loading states, and markdown link parsing.
- [x] Task: Implement the JS `fetch` logic for submitting text and `multipart/form-data` to the `/chat` API.

## Layer 4: Verification
- [x] Task: Verify the UI loads and functions correctly via `pytest` or local execution.