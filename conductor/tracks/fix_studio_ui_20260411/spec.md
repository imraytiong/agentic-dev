# Specification: Agent Studio UI Fix

## Overview
Upgrade the `GET /studio` placeholder in `src/universal_core/chassis.py` to a fully functional, modern, dark-mode chat interface using Tailwind CSS and Vanilla JS.

## Core Requirements
1. **Styling:** Use Tailwind CSS via CDN. Design a slick, dark-mode-first chat interface.
2. **Layout:** Include a scrollable message history, text input area, submit button, and a file upload button (paperclip icon).
3. **Functionality (Vanilla JS):**
    - Render user messages on the right and agent messages on the left.
    - Show a loading indicator while awaiting responses.
    - Parse basic markdown (specifically links `[Text](url)`) for outbound file downloads.
    - Handle text submission and file uploads (`multipart/form-data`).
4. **Backend Sync Route:** Create a `POST /chat` route in `chassis.py` to act as the backend handler for the Studio UI. This route should process the incoming form data, trigger the agent (by publishing to the relevant queue, or directly executing if running in a sync local mock), and return the agent's response.