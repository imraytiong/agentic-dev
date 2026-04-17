import asyncio
from src.agents.jetpack_wiz.tools import read_module_file
import os

async def main():
    repo = "/tmp/androidx-live-test"
    path = "compose/ui/ui/api/current.txt"
    print(f"Does it exist? {os.path.exists(os.path.join(repo, path))}")
    content = await read_module_file(path, repo)
    print(f"Content length: {len(content)}")
    print(content[:100])

asyncio.run(main())
