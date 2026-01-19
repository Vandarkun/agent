"""测试接口路由。"""

from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["test"])


@router.get("")
async def test_endpoint():
    """测试接口。"""
    return {"status": "ok", "message": "test ok"}
