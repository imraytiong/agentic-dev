import logging
import json
import asyncio
import os
import time
import subprocess
from typing import Literal
from pydantic import BaseModel
from src.universal_core.chassis import BaseAgentChassis
from src.universal_core.interfaces import AgentContext
from src.agents.jetpack_wiz.models import (
    JetpackWizRequest, 
    JetpackWizResponse, 
    JetpackWizState, 
    PendingInterrupt
)
from src.agents.jetpack_wiz.tools import (
    run_git_command, 
    resolve_module_path, 
    ensure_repo_and_index, 
    read_module_file
)

logger = logging.getLogger(__name__)

CAPABILITIES_MSG = """I am the JetpackWiz Agent. I can help you navigate and analyze the massive AndroidX repository! 

Here is what I can do:
1. **Module Discovery**: Ask me about any component (e.g., 'Tell me about Room') and I will find the exact repository path using deep semantic search.
2. **Git Analysis**: I can look up commit history, file changes, and specific diffs for any module.
3. **API Surface Review**: I can read `current.txt` files to explain the public API surface and signatures of a library.
4. **Version History**: I can list the latest 5 released versions of a module using git tags.
5. **API Change Analysis**: I can compare the `current.txt` API files between two versions to tell you exactly what public signatures changed.
6. **Context Management**: I handle the heavy lifting of cloning and indexing the repo so you don't have to!

Which module would you like to start with?"""

def register_jetpack_wiz_agent(chassis: BaseAgentChassis):
    
    @chassis.consume_task(queue_name="jetpack_wiz_jobs", payload_model=JetpackWizRequest)
    async def process_wiz_request(payload: JetpackWizRequest, context: AgentContext) -> JetpackWizResponse:
        logger.info(f"Processing JetpackWiz Request: {payload.query}")
        
        # 1. Load State
        state_key = f"jetpack_wiz_state_{context.session_id}"
        if chassis.state_store:
            try:
                state = await chassis.state_store.load_state(state_key, JetpackWizState)
            except Exception:
                state = JetpackWizState()
        else:
            state = JetpackWizState()
            
        repo_path = chassis.config.get("agent", {}).get("repo_path", "/tmp/androidx-main")
        
        # 1.5 System Initialization (Background Clone & Index)
        repo_exists = os.path.exists(os.path.join(repo_path, ".git"))
        
        if state.is_cloning or (repo_exists and state.is_indexing):
            ping_phrases = ["is it done", "status", "check", "hello", "ping", "how is it going", "how's it going", "what's up", "hi", "what can you do", "help"]
            is_ping = any(phrase in payload.query.lower() for phrase in ping_phrases)

            if not is_ping:
                state.pending_queries.append(payload.query)
                if chassis.state_store:
                    await chassis.state_store.save_state(state_key, state)
            
            elapsed = 0
            if state.clone_start_time:
                elapsed = time.time() - state.clone_start_time
            
            if state.is_cloning:
                size_stat = "0 MB"
                if os.path.exists(repo_path):
                    try:
                        out = subprocess.check_output(["du", "-sh", repo_path], text=True)
                        size_stat = out.split()[0]
                    except Exception:
                        pass
                message = f"Still working on it - so far I've downloaded {size_stat}. Sorry it's taking a while. I'll let you know when I'm done!"
            else:
                message = "The download is complete! I'm just indexing the directory structure so I can search it quickly. Almost done!"
            
            if not is_ping:
                message = f"I've added '{payload.query}' to my list. " + message

            if elapsed > 60:
                message += f" (It has been running for {int(elapsed/60)} minutes. The AndroidX repo is massive, thank you for your patience!)"
                
            return JetpackWizResponse(message=message, is_interrupt=False)

        elif not repo_exists:
            state.is_cloning = True
            state.is_indexing = True
            state.clone_start_time = time.time()
            state.pending_queries.append(payload.query)
            
            if chassis.state_store:
                await chassis.state_store.save_state(state_key, state)
                
            async def background_init():
                try:
                    logger.info(f"Starting background initialization for {repo_path}")
                    await ensure_repo_and_index(repo_path, chassis.vector_store)
                    logger.info(f"Background initialization complete for {repo_path}")
                    
                    if chassis.state_store:
                        curr_state = await chassis.state_store.load_state(state_key, JetpackWizState)
                        curr_state.is_cloning = False
                        curr_state.is_indexing = False
                        curr_state.has_indexed = True
                        await chassis.state_store.save_state(state_key, curr_state)
                    
                    while True:
                        if chassis.state_store:
                            curr_state = await chassis.state_store.load_state(state_key, JetpackWizState)
                            if not curr_state.pending_queries:
                                break
                            current_query = curr_state.pending_queries.pop(0)
                            await chassis.state_store.save_state(state_key, curr_state)
                        else:
                            break

                        logger.info(f"Proactive Analysis: Searching for '{current_query}'")
                        candidates = await resolve_module_path(current_query, chassis.vector_store)
                        logger.info(f"Proactive Analysis Candidates: {candidates}")
                        focus_path = candidates[0]['path'] if candidates else "root"
                        
                        git_output = await run_git_command(["log", "-n", "3", "--stat", "--", focus_path], repo_path)
                        
                        summary_prompt = f"The user asked: '{current_query}'. I have finished downloading the AndroidX repo and analyzed the module '{focus_path}'. Here is the git history:\n{git_output}\n\nPlease provide a proactive summary for the user starting with 'I've finished the download and analysis for {current_query}!'"
                        
                        class FinalSummary(BaseModel):
                            summary: str
                        
                        final_decision = await chassis.ask_structured(summary_prompt, FinalSummary)
                        
                        if chassis.state_store:
                            curr_state = await chassis.state_store.load_state(state_key, JetpackWizState)
                            curr_state.pending_notifications.append(final_decision.summary)
                            await chassis.state_store.save_state(state_key, curr_state)
                        
                except Exception as e:
                    logger.error(f"Background initialization or proactive analysis failed: {e}")
                    if chassis.state_store:
                        curr_state = await chassis.state_store.load_state(state_key, JetpackWizState)
                        curr_state.is_cloning = False
                        curr_state.is_indexing = False
                        await chassis.state_store.save_state(state_key, curr_state)
                        
            asyncio.create_task(background_init())
            return JetpackWizResponse(message="Sorry, this is my first time downloading the AndroidX repository so it might take a minute! I'm cloning it in the background right now. I'll send you a message once it's complete.", is_interrupt=False)

        if repo_exists and not state.has_indexed:
            logger.info("Server restarted with existing repo. Re-indexing directory structure...")
            await ensure_repo_and_index(repo_path, chassis.vector_store)
            state.has_indexed = True
            if chassis.state_store:
                await chassis.state_store.save_state(state_key, state)
            logger.info("Re-indexing complete.")

        if state.pending_notifications:
            notification = "\n\n".join(state.pending_notifications)
            state.pending_notifications = []
            if chassis.state_store:
                await chassis.state_store.save_state(state_key, state)
            return JetpackWizResponse(message=f"I have an update from my background task:\n\n{notification}", is_interrupt=False)

        ping_phrases = ["is it done", "status", "check", "hello", "ping", "how is it going", "how's it going", "what's up", "hi", "what can you do", "help"]
        is_ping = any(phrase in payload.query.lower() for phrase in ping_phrases)
        if is_ping and not state.active_focus.module_path:
            return JetpackWizResponse(message=f"Hello! The repository is fully downloaded and I'm ready to go!\n\n{CAPABILITIES_MSG}", is_interrupt=False)

        if state.pending_interrupt:
            reply_text = payload.user_reply or payload.query
            selected_path = None
            reply_clean = reply_text.strip().lower()
            
            try:
                selection_idx = int(reply_clean) - 1
                if 0 <= selection_idx < len(state.pending_interrupt.options):
                    selected_path = state.pending_interrupt.options[selection_idx]
            except ValueError:
                pass
            
            if not selected_path:
                for option in state.pending_interrupt.options:
                    if reply_clean in option.lower():
                        selected_path = option
                        break
            
            if selected_path:
                state.active_focus.module_path = selected_path
                state.pending_interrupt = None
                state.command_history = []
                payload.query = f"Now that I've selected the module path {selected_path}, please continue analyzing."
                logger.info(f"🎯 FOCUS LOCKED: {state.active_focus.module_path}")

        reset_phrases = ["start over", "reset", "clear", "different module"]
        if any(phrase in payload.query.lower() for phrase in reset_phrases):
            state.active_focus.module_path = None
            state.command_history = []
            if chassis.state_store:
                await chassis.state_store.save_state(state_key, state)
            return JetpackWizResponse(message=f"Context cleared! {CAPABILITIES_MSG}", is_interrupt=False)

        if not state.active_focus.module_path:
            logger.info(f"🔍 REQUEST: Semantic Search for: '{payload.query}'")
            candidates = await resolve_module_path(payload.query, chassis.vector_store)
            logger.info(f"✅ RESPONSE: Found {len(candidates)} candidates.")
            
            if candidates:
                if len(candidates) > 1 and candidates[0]['score'] < 0.9:
                    options = [c['path'] for c in candidates]
                    state.pending_interrupt = PendingInterrupt(intent="disambiguate_path", options=options, original_request=payload.query)
                    if chassis.state_store:
                        await chassis.state_store.save_state(state_key, state)
                    
                    context_blocks = []
                    for opt in options:
                        readme_path = os.path.join(repo_path, opt, "README.md")
                        gradle_path = os.path.join(repo_path, opt, "build.gradle")
                        desc = ""
                        if os.path.exists(readme_path):
                            with open(readme_path, 'r') as f:
                                desc = f.read(500)
                        elif os.path.exists(gradle_path):
                            with open(gradle_path, 'r') as f:
                                desc = f.read(500)
                        context_blocks.append(f"Module: {opt}\nContext Snippet:\n{desc}\n")
                    context_str = "\n".join(context_blocks)

                    disambiguation_prompt = f"""
The user asked: '{payload.query}'
I found multiple ambiguous module paths in the repository.

Options and their file context snippets:
{context_str}

Please present these options to the user in a clean, numbered list (1., 2., 3., etc.).
For each option, use the context snippet provided to write a short, 1-sentence description of what that specific module does.

You must use the `summarize` action to output the final numbered list.
                    """
                    class DisambiguationDecision(BaseModel):
                        action: Literal["summarize"]
                        summary: str
                        
                    try:
                        decision = await chassis.ask_structured(disambiguation_prompt, DisambiguationDecision)
                        return JetpackWizResponse(message=decision.summary, is_interrupt=True)
                    except Exception as e:
                        logger.error(f"Disambiguation summary error: {e}")
                        msg = f"I found multiple modules matching your query. Please select one:\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
                        return JetpackWizResponse(message=msg, is_interrupt=True)
                else:
                    state.active_focus.module_path = candidates[0]['path']
                    logger.info(f"🎯 FOCUS LOCKED: {state.active_focus.module_path}")
            else:
                 return JetpackWizResponse(message="I could not find any modules matching your request. Could you be more specific?", is_interrupt=False)

        # 4. The Triage Loop
        system_prompt_base = f"""You are the JetpackWiz Agent. Current Focus: {state.active_focus.module_path}
        
        Strict Rules:
        1. Triage Loop: NEVER request a raw diff (-p) without first running --stat or --name-only.
        2. Scope: Do not read files outside the repository.
        3. API Analysis: If the user asks for "public APIs", "API surface", or to "list APIs", you MUST find the relevant `current.txt` files (using `run_git` with `ls-files` if needed) and then use `read_file` to actually read and list the classes and methods. Do not just list the filenames. When summarizing an API surface, ALWAYS format the output as a clean, bulleted list.
        4. Version Analysis: If the user asks for versions or latest releases, you MUST NOT guess. Follow this sequence:
           a. Use `read_file` on `{state.active_focus.module_path}/build.gradle` (or .kts) to find the artifact prefix (e.g. `androidx.room_room-runtime-`).
           b. Use `run_git` with `tag -l "prefix*" --sort=-v:refname` to list the actual tags.
           c. ONLY THEN summarize the top 5 results. If you don't run `git tag`, you are hallucinating.
        5. API Change Analysis: If the user asks "what has changed since the last version" or to "compare versions", you MUST NOT use `git diff` with git tags. AndroidX stores API versions as text files. Follow this sequence:
           a. Use `run_git` with `ls-files` on the module's `api/` directory to see all the versioned `.txt` files (e.g. `1.10.0-beta01.txt`).
           b. Use `read_file` on the two specific version files you want to compare.
           c. Summarize the differences into a human-readable explanation followed by a clean, orderly list of added, removed, or changed signatures.
        6. Focus: Answer the NEW User Query below. Do not get stuck retrying old failed commands.
        7. Git Syntax: ALWAYS use `--` to separate paths (e.g. `["log", "--", "path"]`).
        8. Failures: Do not apologize for tool failures. Fix and retry or summarize what you found.
        9. ACTION ENUM: Your "action" MUST be EXACTLY one of: "run_git", "read_file", or "summarize". 

        Command History: {json.dumps(state.command_history, indent=2)}
        NEW User Query: {payload.query}
        """
        
        class AgentDecision(BaseModel):
            action: Literal["run_git", "read_file", "summarize"]
            git_args: list[str] = []
            file_path: str = ""
            summary: str = ""
            
        try:
            conversation_history = ""
            for triage_step in range(3):
                current_prompt = f"{system_prompt_base}\n\nConversation History so far:\n{conversation_history}\n\nDecide next action:"
                decision = await chassis.ask_structured(current_prompt, AgentDecision)
                logger.info(f"🧠 TRIAGE STEP {triage_step}: Action={decision.action}")
                
                if decision.action == "run_git":
                    logger.info(f"🛠️ TOOL CALL [{triage_step}]: git {' '.join(decision.git_args)}")
                    state.command_history.append(f"git {' '.join(decision.git_args)}")
                    git_output = await run_git_command(decision.git_args, repo_path)
                    conversation_history += f"\n> git {' '.join(decision.git_args)}\nResult: {git_output[:1000]}\n"
                    
                elif decision.action == "read_file":
                    logger.info(f"📄 TOOL CALL [{triage_step}]: read_file {decision.file_path}")
                    file_content = await read_module_file(decision.file_path, repo_path)
                    conversation_history += f"\n> read_file {decision.file_path}\nResult: {file_content[:1000]}\n"
                    
                elif decision.action == "summarize":
                    if chassis.state_store: await chassis.state_store.save_state(state_key, state)
                    return JetpackWizResponse(message=decision.summary, is_interrupt=False)
                
                else:
                    break
            
            # If we exhaust triage steps, force a summary
            final_summary_prompt = f"""You are the JetpackWiz Agent.
            Your analysis steps are complete. Please provide a final response to the user's query: '{payload.query}' based on the facts found.

            History of your actions and findings:
            {conversation_history}

            You MUST output pure JSON matching this exact schema:
            {{
            "summary": "Your final detailed answer to the user"
            }}
            """
            class FinalSummary(BaseModel): summary: str
            final_obj = await chassis.ask_structured(final_summary_prompt, FinalSummary)
            if chassis.state_store: await chassis.state_store.save_state(state_key, state)
            return JetpackWizResponse(message=final_obj.summary, is_interrupt=False)
                
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return JetpackWizResponse(message=f"I encountered an error: {str(e)}", is_interrupt=False)
            
    return process_wiz_request
