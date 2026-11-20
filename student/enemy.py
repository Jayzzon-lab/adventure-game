"""TODO: implement initial enemy data; introductory gameplay has no enemies."""
from src.api import EnemyDefinition, Position # type: ignore


class Enemy:
    """Expose read-only identity, position, and nonnegative encounter penalty."""

    def __init__(self, enemy_id: str, position: Position, encounter_penalty: int) -> None:
        #raise NotImplementedError("TODO Enemy: implement constructor and properties")
        
        definition = EnemyDefinition(enemy_id.strip(),position, encounter_penalty)
        self._enemy_id = definition.enemy_id
        self._position = definition.position
        self._encounter_penalty = definition.encounter_penalty
    @property
    def enemy_id(self) -> str:
        #raise NotImplementedError("TODO Enemy.enemy_id")
        
        return self._enemy_id

    @property
    def position(self) -> Position:
        #raise NotImplementedError("TODO Enemy.position")
        
        return self._position

    @property
    def encounter_penalty(self) -> int:
        #raise NotImplementedError("TODO Enemy.encounter_penalty")
        
        return self._encounter_penalty