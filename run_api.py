"""启动 FastAPI 服务。"""

import os

import uvicorn


def _get_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8080"))
    reload = _get_bool(os.getenv("RELOAD"), default=False)

    uvicorn.run("api.main:app", host=host, port=port, reload=reload)
