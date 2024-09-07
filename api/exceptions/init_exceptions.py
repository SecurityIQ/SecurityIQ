class ClassUninitializedError(Exception):
    def __init__(self, class_name: str) -> None:
        super().__init__(f"{class_name} is not initialized")
