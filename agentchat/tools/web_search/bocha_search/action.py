import json
from typing import Optional

import requests
from langchain.tools import tool

from agentchat.settings import app_settings


BOCHA_SEARCH_URL = "https://api.bocha.cn/v1/web-search"


@tool("web_search", parse_docstring=True)
def bocha_search(query: str, summary: bool = True, count: Optional[int] = 5):
    """
    使用博思接口进行联网搜索。

    Args:
        query: 搜索关键词。
        summary: 是否返回摘要。
        count: 期望返回的结果数量上限。

    Returns:
        str: 汇总的搜索结果列表。
    """
    return _bocha_search(query, summary, count)


def _bocha_search(query: str, summary: bool = True, count: Optional[int] = 5) -> str:
    api_key = app_settings.tools.bocha.get("api_key")
    if not api_key:
        return "未配置博思搜索的 API Key。"

    payload = {"query": query, "summary": summary, "count": count or 5}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(BOCHA_SEARCH_URL, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as err:
        return f"调用博思搜索失败: {err}"

    results = data.get("data", {}).get("webPages", {}).get("value") or []
    if not results:
        return "未找到相关内容。"

    lines = []
    max_items = count or len(results)
    for item in results[:max_items]:
        title = item.get("name") or "未命名结果"
        url = item.get("url") or ""
        snippet = item.get("snippet") or ""
        lines.append(f"{title}\n{url}\n{snippet}")

    return "\n\n".join(lines)
