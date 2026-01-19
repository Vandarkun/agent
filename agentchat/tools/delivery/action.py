import json
from typing import Optional
from datetime import datetime

import requests
from langchain.tools import tool
from loguru import logger

from agentchat.prompts.tool import DELIVERY_PROMPT
from agentchat.settings import app_settings


@tool(parse_docstring=True)
def get_delivery_info(delivery_number: str, mobile: Optional[str] = None):
    """
    根据用户提供的快递号码查询快递物流信息。

    Args:
        delivery_number (str): 用户提供的快递号码。
        mobile (Optional[str]): 收件人手机号后四位（有的快递公司校验需要）。

    Returns:
        str: 查询到的快递信息。
    """
    return _get_delivery(delivery_number, mobile)


def _get_delivery(delivery_number: str, mobile: Optional[str] = None) -> str:
    """调用阿里云快递查询接口，返回简要轨迹。"""
    endpoint = app_settings.tools.delivery.get("endpoint")
    appcode = app_settings.tools.delivery.get("api_key")
    if not endpoint or not appcode:
        return "未配置快递查询接口或AppCode。"

    params = {
        "expressNo": delivery_number,
        "mobile": mobile or "",
    }
    headers = {"Authorization": f"APPCODE {appcode}"}

    try:
        resp = requests.get(endpoint, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
    except Exception as err:
        logger.error(f"delivery request failed: {err}")
        return "查询快递信息失败，请稍后再试。"

    try:
        data = resp.json()
    except Exception:
        return resp.text

    # 解析常见字段（兼容返回示例）
    track_items = []
    company = None
    if isinstance(data, dict):
        payload = data.get("data", {}) if isinstance(data.get("data"), dict) else data
        company = (
            payload.get("typename")
            or payload.get("logisticsCompanyName")
            or payload.get("company")
            or payload.get("name")
        )
        items = (
            payload.get("logisticsTraceDetailList")
            or payload.get("list")
            or payload.get("trace")
            or payload.get("result", [])
        )
        if isinstance(items, list):
            for it in items:
                if not isinstance(it, dict):
                    continue
                ts = it.get("timeDesc")
                if not ts and it.get("time"):
                    try:
                        ts = datetime.fromtimestamp(it["time"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        ts = str(it.get("time"))
                status = it.get("desc") or it.get("status") or it.get("remark") or it.get("info")
                if ts or status:
                    track_items.append(f"{ts or ''} {status or ''}".strip())

    if not track_items and isinstance(data, dict):
        # fallback: dump raw json
        return json.dumps(data, ensure_ascii=False)

    track_items.reverse()
    company_display = company or "快递公司未知"
    return DELIVERY_PROMPT.format(company_display, delivery_number, track_items)
