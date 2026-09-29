from pydantic import BaseModel


class BaseService:
    def _update(self, model: BaseModel, data: BaseModel) -> BaseModel:
        return model.model_copy(update=data.model_dump(exclude_unset=True))
