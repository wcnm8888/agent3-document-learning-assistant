class DocumentIngestionError(RuntimeError):
    """文档摄入阶段的可定位错误。"""


class DocumentNotFoundError(DocumentIngestionError):
    pass


class DocumentExtractionError(DocumentIngestionError):
    pass


class EmptyChunkError(DocumentIngestionError):
    pass


class EmbeddingServiceError(DocumentIngestionError):
    pass


class EmbeddingApiError(EmbeddingServiceError):
    """Embedding API 返回或连接失败，保留可定位的服务端信息。"""


class EmbeddingDimensionMismatch(DocumentIngestionError):
    pass


class RetrievalError(DocumentIngestionError):
    pass


class DeepSeekApiError(DocumentIngestionError):
    pass


class AnswerValidationError(DocumentIngestionError):
    pass


class QdrantUnavailableError(DocumentIngestionError):
    pass


class VectorDimensionMismatch(DocumentIngestionError):
    pass


class MetadataIntegrityError(DocumentIngestionError):
    pass


class LearningError(DocumentIngestionError):
    """学习闭环数据和业务规则错误。"""


class DatabaseError(LearningError):
    pass


class SessionNotFoundError(LearningError):
    pass


class NoteNotFoundError(LearningError):
    pass


class NoteValidationError(LearningError):
    pass
