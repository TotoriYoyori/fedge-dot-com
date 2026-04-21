from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.alias_generators import to_camel


class CustomBaseModel(BaseModel):
    """
    Project-wide base model for all schemas with common configuration:
    - Camel case alias generator for JSON compatibility.
    - Allows populating fields by their original Python names.
    """

    model_config = SettingsConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class DomainSettings(BaseSettings):
    """
    Common configurations for domain-specific settings, such as reading from common environmental variables.
    """
    ENVIRONMENT: str = "local"
    TEMPLATES_DIR: str = ""
    STATIC_DIR: str = ""
    DEFAULT_TEMPLATE_NAME: str = "index.html"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    def model_post_init(self, __context):
        """
        Settings inheriting from DomainSettings will automatically resolve their directory. Keep in mind
        this does mean each domain MUST contain a /static and /template directory.
        """
        import sys
        module = sys.modules[self.__class__.__module__]
        domain_path = Path(module.__file__).resolve().parent

        object.__setattr__(self, "TEMPLATES_DIR", str(domain_path / "templates"))
        object.__setattr__(self, "STATIC_DIR", str(domain_path / "static"))
