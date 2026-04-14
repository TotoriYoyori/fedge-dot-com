class Helper:
    @staticmethod
    def help(module: str) -> str:
        """
        Entry point for internal development guidelines.

        Args:
            module (str): The module to get help for
                          (e.g., 'dependencies', 'schemas', 'models').

        Returns:
            str: Documentation string for the requested module.
        """

        if module == "dependencies":
            return Helper._dependencies_help()

        return f"No documentation available for module: {module}"

    @staticmethod
    def _dependencies_help() -> str:
        """
        Dependency Writing Guidelines

        Dependencies are reusable logic blocks used with FastAPI's Depends().
        They handle validation, authentication, and pre-processing before
        reaching route handlers.

        ----------------------------
        🔹 Naming Conventions
        ----------------------------

        1. valid_<entity>
           - Purpose: Validate and return a database ORM object
           - Return: ORM model (e.g., User)
           - Raises: Exception if validation fails

           Example:
               async def valid_access_token(...) -> User

        2. <entity>_exists
           - Purpose: Check existence of a resource
           - Return: bool (True/False)
           - Raises: Exception if already exists (for create flows)

           Example:
               async def username_already_exists(...) -> bool

        ----------------------------
        🔹 Design Principles
        ----------------------------

        - Keep dependencies focused on a single responsibility
        - Always raise domain-specific exceptions (avoid generic Exception)
        - Do NOT return None for failure cases — raise instead
        - Prefer async functions when interacting with database or I/O
        - Use Annotated + Depends for clarity and type safety

        ----------------------------
        🔹 Structure Pattern
        ----------------------------

        Typical dependency structure:

            async def dependency_name(
                input_data: Schema,
                db: Annotated[AsyncSession, Depends(get_db)]
            ) -> ReturnType:

                # 1. Fetch / validate
                entity = await Service.get_one_by(...)

                # 2. Validate condition
                if not entity:
                    raise SomeException

                # 3. Return result
                return entity

        ----------------------------
        🔹 When to Use Dependencies
        ----------------------------

        Use dependencies for:
        - Authentication (tokens, sessions)
        - Authorization (permissions, roles)
        - Validation (existence, uniqueness)
        - Shared request preprocessing

        Avoid using them for:
        - Complex business logic (keep that in services)
        - Heavy data transformations

        ----------------------------
        🔹 Notes
        ----------------------------

        - Dependencies should be composable and reusable
        - Keep them lightweight and predictable
        - Naming consistency is critical for readability

        """
