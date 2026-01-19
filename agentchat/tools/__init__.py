from agentchat.tools.send_email.action import send_email
from agentchat.tools.web_search.bocha_search.action import bocha_search
from agentchat.tools.arxiv.action import get_arxiv
from agentchat.tools.get_weather.action import get_weather
from agentchat.tools.delivery.action import get_delivery_info


AgentTools = [
    send_email,
    bocha_search,
    get_weather,
    get_arxiv,
    get_delivery_info,
]


AgentToolsWithName = {
    "send_email": send_email,
    "bocha_search": bocha_search,
    "web_search": bocha_search,
    "get_arxiv": get_arxiv,
    "get_weather": get_weather,
    "get_delivery_info": get_delivery_info,
}

WorkSpacePlugins = AgentToolsWithName

LingSeekPlugins = AgentToolsWithName

WeChatTools = {
    "bocha_search": bocha_search,
    "get_arxiv": get_arxiv,
    "get_weather": get_weather,
}
