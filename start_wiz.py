import logging
import os
import yaml
from src.universal_core.chassis import BaseAgentChassis
from src.agents.jetpack_wiz.agent import register_jetpack_wiz_agent

logging.basicConfig(level=logging.INFO)

config_path = os.path.join(os.path.dirname(__file__), "src", "agents", "jetpack_wiz", "config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Preload tools and prompt for the UI
import inspect
from src.agents.jetpack_wiz.tools import run_git_command, resolve_module_path, ensure_repo_and_index, read_module_file
config.setdefault("agent", {})["tools"] = [
    {"name": "run_git_command", "description": (inspect.getdoc(run_git_command) or "").split("\n")[0], "source": inspect.getsource(run_git_command)},
    {"name": "resolve_module_path", "description": (inspect.getdoc(resolve_module_path) or "").split("\n")[0], "source": inspect.getsource(resolve_module_path)},
    {"name": "ensure_repo_and_index", "description": (inspect.getdoc(ensure_repo_and_index) or "").split("\n")[0], "source": inspect.getsource(ensure_repo_and_index)},
    {"name": "read_module_file", "description": (inspect.getdoc(read_module_file) or "").split("\n")[0], "source": inspect.getsource(read_module_file)}
]

prompt_path = os.path.join(os.path.dirname(__file__), "src", "agents", "jetpack_wiz", "prompts", "system_prompt.jinja")
if os.path.exists(prompt_path):
    with open(prompt_path, "r") as f:
        config.setdefault("agent", {})["system_prompt"] = f.read()

enable_studio = os.getenv("ENABLE_STUDIO", "false").lower() in ("true", "1", "yes")
chassis = BaseAgentChassis(config, enable_studio=enable_studio)

# Register the agent functions
register_jetpack_wiz_agent(chassis)

if __name__ == "__main__":
    chassis.run_local()
