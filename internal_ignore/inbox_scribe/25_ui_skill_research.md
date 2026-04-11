# UI Skill Research

Please paste any URLs, code snippets, or UI patterns you found on the internet below. 

Gemini Scribe will read these URLs and extract the best practices to upgrade the `frontend-ui-builder` skill.

**URLs:**
- [Paste URL 1 here]
- [Paste URL 2 here]

## Output from Gemini Web
This is some output from Gemini Web research:
To achieve that middle-ground predictability where application developers can actually trust an AI's output without hand-holding, you have to constrain the agent's playing field. When running autonomous agents in headless environments—like a Podman container on a dedicated host—heavy Node modules, complex state management, and browser automation introduce too much friction.

By combining spec-driven development (SDD) with lightweight, HTML-over-the-wire frameworks, you force the agent to build against a rigid blueprint using a highly restricted vocabulary. This drastically cuts down on hallucinations and produces clean, finished UIs.

Here is the expanded research covering lightweight open-source approaches and spec-driven agent skills.

### 1. Spec-Driven UI Development (The Blueprint)

Spec-driven development means the agent never guesses what the UI should do. It reads a declarative contract, builds the UI to satisfy that contract, and verifies it.

- **A2UI Protocol (Agent-to-UI):** This is a rapidly emerging standard specifically designed for AI agents. Instead of generating executable React or JavaScript, the agent generates declarative, framework-agnostic JSON blueprints of native components. The client renders these blueprints using its native design system.
    
    - _Why it's agent-friendly:_ It eliminates code hallucination entirely because the agent only dictates _data and structure_, not executable code.
        
    - _Sources:_ Look into the **Flutter GenUI SDK** or **CopilotKit / AG UI**, which are pioneering this protocol for multi-agent systems.
        
- **Behavior-Driven Development (BDD) via Gherkin:** Feed the agent `.feature` files written in Gherkin syntax (Given/When/Then).
    
    - _Why it's agent-friendly:_ LLMs are incredibly good at reading Markdown and Gherkin. In a multi-agent setup, this allows you to divide labor cleanly: the "brain" of your system can logically map out the user flow in a `.feature` file, while the "forge" generates the semantic HTML and tests required to make that specific feature pass.
        
    - _Sources:_ **Cucumber / Gherkin documentation**.
        

### 2. Lightweight, Modern Open-Source Stacks (The Anti-Bloat Approach)

If your agent must write actual web code (HTML/JS) rather than JSON payloads, modern React or Angular is often too complex and prone to state-management hallucinations. You want hyper-declarative, lightweight stacks.

- **HTMX + Tailwind CSS:** HTMX allows you to access AJAX, CSS Transitions, and WebSockets directly in HTML using attributes (like `hx-post` or `hx-get`).
    
    - _The Skill:_ Train the agent to use HTML as the single source of truth. Because HTMX eliminates the need for client-side JavaScript routing and state, the agent only has to worry about generating the correct server response and Tailwind utility classes.
        
    - _Sources:_ **[HTMX.org](https://htmx.org/)**.
        
- **Alpine.js for Micro-Interactions:** If you need client-side interactivity (like a dropdown or modal) without a build step, Alpine.js is perfect.
    
    - _The Skill:_ The agent injects minimal state directly into the HTML element (e.g., `<div x-data="{ open: false }">`). It prevents the agent from inventing disconnected, complex JavaScript files.
        
    - _Sources:_ **[Alpinejs.dev](https://alpinejs.dev/)**.
        
- **Web Components (Lit):** If you need reusable components, Lit (built by Google) provides a lightweight wrapper around standard Web Components.
    
    - _The Skill:_ The agent builds strictly encapsulated `<custom-elements>`, preventing CSS bleed and making unit testing in a headless DOM trivial.
        
    - _Sources:_ **[Lit.dev](https://lit.dev/)**.
        

### 3. Actionable Best Practices & Agent "Skills" Contexts

To integrate these concepts into your Gemini CLI, you should create specialized context files (skills) that define exact operating parameters. Here are two examples of skills you can feed your agent:

**Skill A: Spec-First Implementation**

> **Directive:** You are a Spec-Driven UI Generator. You do not design features; you satisfy contracts.
> 
> **Protocol:**
> 
> 1. Ingest the provided Gherkin `.feature` file or OpenAPI schema.
>     
> 2. Generate a DOM testing file (e.g., Vitest + Testing Library) that asserts every "Then" statement in the spec.
>     
> 3. Generate the minimal HTML/HTMX required to make the tests pass.
>     
> 4. Use `data-testid` attributes extensively to bind your HTML to your tests.
>     
>     **Constraint:** Never write code that does not directly map to a line in the provided spec.
>     

**Skill B: Hypermedia-Driven UI (HTMX + Alpine)**

> **Directive:** You build lightweight, server-rendered UIs.
> 
> **Protocol:**
> 
> 1. **Zero Client-Side Routing:** All state and data mutations must be handled via HTMX attributes (`hx-get`, `hx-post`, `hx-swap`).
>     
> 2. **Micro-State Only:** For transient UI state (tabs, toggles, modals), use inline Alpine.js (`x-data`). Do not create external `.js` files.
>     
> 3. **Styling:** Use Tailwind CSS exclusively.
>     
>     **Validation:** Ensure all interactive elements have proper `aria-` labels mapped to their Alpine `x-data` state.
>     

By leaning on A2UI, HTMX, and strict spec-driven boundaries, you ensure that the CLI agent operates as a precise fabricator rather than a speculative designer.

Which specific spec format—like OpenAPI for data or Gherkin for user behavior—feels like the best fit for your current workflow?

**Notes/Preferences:**
- (e.g., "I really like the loading spinner on URL 1" or "Check out how URL 2 handles markdown rendering")