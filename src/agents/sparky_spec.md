# Agent Spec: Hello Chassis (Reference Agent)

*Note: This is the official "Hello World" reference agent for the platform. It is designed to prove that Redis queues, Postgres state, and LLM structured outputs are functioning correctly.*

## 1. Identity & Config
*   **Name:** `hello_chassis`
*   **Model:** `gemini-2.5-flash` *(Optional - Using Flash for instant, cheap responses)*
*   **Skills to Load:** *(Blank - No complex skills needed)*

## 2. Triggers & Routing
*   **Queue Name:** `hello_jobs`
*   **Priority:** *(Blank - Defaults to standard async execution)*

## 3. The Contracts (Pydantic Models)
*   **Incoming Payload (`HelloRequest`):** 
    *   `developer_name` (str): The name of the developer testing the system.
    *   `current_mood` (str): How they are feeling about the architecture today.
*   **State Model (`HelloState`):** 
    *   `interaction_count` (int): Defaults to 0. Tracks how many times this specific user has pinged Sparky.
*   **Final Output (`HelloResponse`):** 
    *   `greeting_message` (str): A cute, personalized welcome message.
    *   `affirmation` (str): A generated affirmation based on their mood.
    *   `total_interactions` (int): The updated count from the database.

## 4. Prompts (`prompts/system_prompt.jinja`)
*   **Core Directive:** "You are Sparky, the highly enthusiastic mascot of the BaseAgentChassis platform. Your job is to welcome developers, acknowledge their current mood, and provide a technical affirmation using the `get_affirmation` tool. Keep it short, cute, and slightly nerdy."
*   **Template Variables:** `{{ developer_name }}`, `{{ current_mood }}`

## 5. Custom Tools (`tools.py`)
*   `get_affirmation(mood: str) -> str`: A simple deterministic Python function that returns a hardcoded, nerdy affirmation based on whether the mood is positive, negative, or stressed (e.g., "May your Docker containers always start on the first try!").

## 6. Testing & Evaluation
*   *Safe Default:* Use `pytest` to test the `get_affirmation` tool. Use `chassis.run_local(mock_infrastructure=True)` to chat with Sparky in the terminal.