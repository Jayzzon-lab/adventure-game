"""TODO: implement initial artifact data; introductory gameplay has no artifacts."""
from src.api import ArtifactDefinition, Position # type: ignore


class Artifact:
    """Expose read-only canonical identity, position, and nonnegative value."""

    def __init__(self, artifact_id: str, position: Position, value: int) -> None:
        #raise NotImplementedError("TODO Artifact: implement constructor and properties")
        
        definition = ArtifactDefinition(artifact_id.strip(), position, value)
        self._artifact_id = definition.artifact_id
        self._position = definition.position
        self._value = definition.value
        
    @property
    def artifact_id(self) -> str:
        # raise NotImplementedError("TODO Artifact.artifact_id")
        
        return self._artifact_id
    @property
    def position(self) -> Position:
        #raise NotImplementedError("TODO Artifact.position")
        
        return self._position
    @property
    def value(self) -> int:
        #raise NotImplementedError("TODO Artifact.value")
       
        return self._value