"""智能文档问答助手的文档摄入核心。"""

from .config import Settings
from .ingestion import DocumentIngestionService

__all__ = ["DocumentIngestionService", "Settings"]
