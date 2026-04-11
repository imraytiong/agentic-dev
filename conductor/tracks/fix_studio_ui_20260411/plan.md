# Implementation Plan: Agent Studio UI Fix

## Layer 1: The Chat Handler API
- [ ] Task: Implement a `POST /chat` route in `chassis.py` to handle the Studio UI's sync requests and interface with the agent.

## Layer 2: The HTML/CSS Structure
- [ ] Task: Update the `GET /studio` endpoint in `chassis.py` to serve a full HTML document.
- [ ] Task: Implement the Tailwind CSS layout (dark mode, scrollable history, input area, file upload).

## Layer 3: Client-Side Logic
- [ ] Task: Implement Vanilla JS logic for message rendering, loading states, and markdown link parsing.
- [ ] Task: Implement the JS `fetch` logic for submitting text and `multipart/form-data` to the `/chat` API.

## Layer 4: Verification
- [ ] Task: Verify the UI loads and functions correctly via `pytest` or local execution.