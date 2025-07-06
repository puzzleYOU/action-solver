from abc import ABC

import pydantic


class BaseModel(pydantic.BaseModel):
    class Key(ABC):
        pass
