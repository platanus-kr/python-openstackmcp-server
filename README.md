# python-openstackmcp-server (prototype)

> OpenStack API를 이용해 서버 목록을 조회하는 간단한 MCP Server

- python 3.11
- FastMCP

## run as local

**`.env` setup**

> sample `.env`

```bash
OS_AUTH_URL=http://8.8.8.8:5000/identity
OS_USERNAME=admin
OS_PASSWORD=openstack_admin_password
OS_PROJECT_NAME=admin
OS_USER_DOMAIN_ID=default
OS_PROJECT_DOMAIN_ID=default
NOVA_ENDPOINT=http://8.8.8.8:9999/compute/v2.1
```

**install dependency**

```bash
uv venv
source .venv/bin/activate
uv add "mcp[cli]" httpx
```
**Start MCP Server**

```bash
uv run my_first_os_mcp.py
```

**MCP client configuration**

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/PARENT",
        "run",
        "my_first_os_mcp.py"
      ]
    }
  }
}
```

**sample; retrieve instances count**

![sample](https://private-user-images.githubusercontent.com/6806008/461592358-6dcdf1b7-b535-4a38-8993-8cb2a8298996.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0Njk4NjAsIm5iZiI6MTc1MTQ2OTU2MCwicGF0aCI6Ii82ODA2MDA4LzQ2MTU5MjM1OC02ZGNkZjFiNy1iNTM1LTRhMzgtODk5My04Y2IyYTgyOTg5OTYucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MDcwMiUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTA3MDJUMTUxOTIwWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MTAzMmM4Zjk5MWI3MWZkZmY1ODQ1Y2M4YTUwZGQ3MGI0YjNkZWYyNzI1MmY3MWMwM2QwZTE2MmU5MmNkZjQ4NiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.RgU7B_Pidhc8cpO76ao5SDwwyp61Fb5VURO0gRwAU7Q)