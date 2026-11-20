"""TODO: build a canonical level using the injected terrain generator."""
from src.api import LevelDefinition, LevelSpecification, TerrainGeneratorContract # type: ignore


class LevelGenerator:
    """Use the supplied TerrainGeneratorContract; do not instantiate a replacement."""

    def __init__(self, terrain_generator: TerrainGeneratorContract) -> None:
        #raise NotImplementedError("TODO LevelGenerator: retain injected generator and implement generate_level")
        
    def generate_level(self, specification: LevelSpecification, seed: int) -> LevelDefinition:
        # Preserve specification identities and seed; choose valid opposite endpoints.
        #raise NotImplementedError("TODO LevelGenerator.generate_level")

        return LevelDefinition(level_id, profile_id,seed, terrain, start, exit, charac , artifact, enemies, patrols)
        