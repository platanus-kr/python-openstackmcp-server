# file: openstack_mcp.py

import os
import logging
from typing import Any
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# .env 로딩
load_dotenv()

# FastMCP 인스턴스 초기화
mcp = FastMCP("openstack")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("openstack_mcp")

# Keystone/Nova 환경 변수
OS_AUTH_URL = os.getenv("OS_AUTH_URL")
OS_USERNAME = os.getenv("OS_USERNAME")
OS_PASSWORD = os.getenv("OS_PASSWORD")
OS_PROJECT_NAME = os.getenv("OS_PROJECT_NAME")
OS_USER_DOMAIN_ID = os.getenv("OS_USER_DOMAIN_ID")
OS_PROJECT_DOMAIN_ID = os.getenv("OS_PROJECT_DOMAIN_ID")
NOVA_ENDPOINT = os.getenv("NOVA_ENDPOINT")


async def get_token_and_project_id() -> tuple[str, str]:
    url = f"{OS_AUTH_URL}/v3/auth/tokens"
    logger.info(f"🔑 Keystone 인증 시도: {url}")

    headers = {"Content-Type": "application/json"}
    data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": OS_USERNAME,
                        "domain": {"id": OS_USER_DOMAIN_ID},
                        "password": OS_PASSWORD,
                    }
                },
            },
            "scope": {
                "project": {
                    "name": OS_PROJECT_NAME,
                    "domain": {"id": OS_PROJECT_DOMAIN_ID}
                }
            },
        }
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=data, headers=headers, timeout=10.0)
        resp.raise_for_status()

        token = resp.headers.get("X-Subject-Token")
        json_data = resp.json()
        project_id = json_data["token"]["project"]["id"]

        logger.info(f"✅ Keystone 인증 성공. Token: {token[:10]}..., Project ID: {project_id}")
        return token, project_id


@mcp.tool()
async def list_instances() -> str:
    """OpenStack 프로젝트에서 인스턴스 목록을 조회합니다."""
    try:
        token, _ = await get_token_and_project_id()
    except Exception as e:
        logger.error(f"❌ 인증 실패: {e}")
        return f"[인증 실패] {e}"

    url = f"{NOVA_ENDPOINT}/servers/detail"
    headers = {"X-Auth-Token": token}
    logger.info(f"🛰️ 인스턴스 목록 요청: {url}")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            servers = data.get("servers", [])
            logger.info(f"✅ 인스턴스 조회 성공. 총 {len(servers)}개")
        except Exception as e:
            logger.error(f"❌ 인스턴스 조회 실패: {e}")
            return f"[인스턴스 조회 실패] {e}"

    if not servers:
        return "프로젝트에 실행 중인 인스턴스가 없습니다."

    result = []
    for s in servers:
        image_info = s.get("image")
        if isinstance(image_info, dict):
            image_id = image_info.get("id", "N/A")
        elif isinstance(image_info, str):
            image_id = image_info
        else:
            image_id = "N/A"

        result.append(
            f"""Name: {s['name']}
ID: {s['id']}
Status: {s['status']}
Flavor: {s['flavor']['id']}
Image: {image_id}
---"""
        )

    return "\n".join(result)


if __name__ == "__main__":
    logger.info("🚀 FastMCP 서버 실행 시작 (transport=stdio)")
    mcp.run(transport="stdio")  # 또는 "http"