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

    # Initialize Chassis (using mock infrastructure for local testing)
    chassis = BaseAgentChassis(config, mock_infrastructure=True)

    # Register the JetpackWiz Agent
    register_jetpack_wiz_agent(chassis)

    # Run the local server
    chassis.run_local(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
