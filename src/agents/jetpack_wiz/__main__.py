import yaml
import os
import asyncio
from src.universal_core.chassis import BaseAgentChassis
from src.agents.jetpack_wiz.agent import register_jetpack_wiz_agent

def main():
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Preload tools and prompt for the UI
    from src.agents.jetpack_wiz.tools import run_git_command, resolve_module_path, ensure_repo_and_index, read_module_file
    config.setdefault("agent", {})["tools"] = [
        run_git_command, resolve_module_path, ensure_repo_and_index, read_module_file
    ]
    
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.jinja")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r") as f:
            config.setdefault("agent", {})["system_prompt"] = f.read()

    # Initialize Chassis (using mock infrastructure for local testing)
    enable_studio = os.getenv("ENABLE_STUDIO", "false").lower() in ("true", "1", "yes")
    chassis = BaseAgentChassis(config, mock_infrastructure=True, enable_studio=enable_studio)

    # Register the JetpackWiz Agent
    register_jetpack_wiz_agent(chassis)

    # Run the local server
    chassis.run_local(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
