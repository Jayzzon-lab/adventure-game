"""TODO: generate canonical terrain deterministically from specification and seed."""
import random
from src.api import Terrain, TerrainGenerationSpec # type: ignore


class TerrainGenerator:
    """Keep state local; identical inputs must also agree across fresh instances."""

    def __init__(self) -> None:
        #raise NotImplementedError("TODO TerrainGenerator: implement constructor and generate_terrain")
        pass

    def generate_terrain(self, specification: TerrainGenerationSpec, seed: int) -> Terrain:
        # This workbench accepts only its documented public introductory family.
        #raise NotImplementedError("TODO TerrainGenerator.generate_terrain")
        rng = random.Random(seed)
        for attempts in range(specification.max_attempts):
            terrain_rows = ()
            for i in range(specification.rows):
                row = ""
                for j in range(specification.columns):
                    tile = rng.choice(["#", "."])
                    row += tile
                terrain_rows += (row,)
            count = 0
            for x in terrain_rows:
                for y in x:
                    if y == ".":
                        count += 1
                    else:
                        continue
            if specification.min_open_tiles <= count <= specification.max_open_tiles:
                return Terrain(terrain_rows)
        raise ValueError("Unable to generate valid terrain within maximum attempts.")