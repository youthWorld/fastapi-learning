from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from schemas.favorites import NewsItemBase


class AddHistoryDTO(BaseModel):
    """
    添加浏览历史DTO
    """

    news_id: int = Field(alias="newsId", description="新闻ID")


class HistoryNewsItemResponse(NewsItemBase):
    """
    浏览历史新闻响应模型
    """

    view_time: datetime = Field(description="浏览时间")


class HistoryListResponse(BaseModel):
    """
    浏览历史列表响应模型
    """

    list: list[HistoryNewsItemResponse]
    total: int = Field(description="浏览历史总数")
    has_more: bool = Field(alias="hasMore", description="是否有更多数据")

    model_config = ConfigDict(
        populate_by_name=True,
    )
