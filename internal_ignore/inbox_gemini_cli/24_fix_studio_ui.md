# Payload: Fix the Agent Studio UI

**ATTENTION GEMINI CLI:**
The Universal Core is functioning, but the `GET /studio` route in `src/universal_core/chassis.py` is currently just returning a placeholder stub (`"Embedded chat interface goes here."`). 

We need a functional, "wow-factor" UI for the hackathon developers!

Please update `src/universal_core/chassis.py` to serve a complete, functional HTML page for the `/studio` route. 

**Requirements for the HTML/JS:**
1. Use Tailwind CSS via CDN (`<script src="https://cdn.tailwindcss.com"></script>`) for a slick, modern dark-mode chat interface.
2. Include a scrollable message history container.
3. Include an input area with a text field, a submit button, and a file upload button (a paperclip icon 📎).
4. Write vanilla JavaScript within the HTML to handle the chat logic:
   - Display user messages on the right, agent messages on the left.
   - Send the text (and optionally the attached file) to the backend. (If you need to add a simple `POST /chat` route to `chassis.py` to handle this sync UI traffic and route it to the active consumer, please do so).
   - Display a loading indicator while waiting for the agent.
   - Render markdown links (like `[Download](/download/123)`) properly so outbound files are clickable.

Please implement this full UI, commit the changes, push the branch, and drop a message in `inbox_scribe/` when complete!