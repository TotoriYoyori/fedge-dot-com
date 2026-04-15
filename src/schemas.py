from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CustomBaseModel(BaseModel):
    """
    Project-wide base model with common configuration:
    - Camel case alias generator for JSON compatibility.
    - Allows populating fields by their original Python names.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
