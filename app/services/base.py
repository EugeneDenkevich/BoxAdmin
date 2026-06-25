from pydantic import BaseModel


class BaseService:
    def _update_by_data(self, source: BaseModel, data: BaseModel) -> BaseModel:
        return source.model_copy(update=data.model_dump(exclude_unset=True))
