import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
from hello_agents.protocols.mcp.client import MCPClient

async def test_mcp():
    print('Connecting to MCP server...')
    async with MCPClient(['amap-mcp-server'], env={'AMAP_MAPS_API_KEY': 'test'}) as client:
        print('Connected!')
        tools = await client.list_tools()
        print(f'Found {len(tools)} tools:')
        for t in tools:
            print(f"  - {t['name']}: {t['description'][:1000]}")

asyncio.run(test_mcp())