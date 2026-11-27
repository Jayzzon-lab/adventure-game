"""TODO: build a canonical level using the injected terrain generator."""
from src.api import LevelDefinition, LevelSpecification, TerrainGeneratorContract, Position, CharacterDefinition, EnemyDefinition, ArtifactDefinition, PatrolDefinition # type: ignore
import random

class LevelGenerator:
    """Use the supplied TerrainGeneratorContract; do not instantiate a replacement."""

    def __init__(self, terrain_generator: TerrainGeneratorContract) -> None:
        #raise NotImplementedError("TODO LevelGenerator: retain injected generator and implement generate_level")
        self.terrain_generator = terrain_generator

# level_id: str
#     profile_id: str
#     seed: int
#     terrain: Terrain
#     start: Position
#     exit: Position
#     character: CharacterDefinition
#     artifacts: tuple[ArtifactDefinition, ...] = ()
#     enemies: tuple[EnemyDefinition, ...] = ()
#     patrols: tuple[PatrolDefinition, ...] = ()


# min_route_moves: int
# max_route_moves: int
# min_branch_tiles: int
# max_dead_end_tiles: int
# require_alternate_path: bool
# allow_entity_overlap: bool
# allow_entities_on_endpoints: bool
# max_turns: int
# max_attempts: int

    def generate_level(self, specification: LevelSpecification, seed: int) -> LevelDefinition:
        # Preserve specification identities and seed; choose valid opposite endpoints.
        #raise NotImplementedError("TODO LevelGenerator.generate_level")
        terrain = self.terrain_generator.generate_terrain(specification.terrain_spec,seed)
        level_id = specification.level_id
        profile_id = specification.profile_id
        charac = CharacterDefinition(specification.agent_id)
        rng = random.Random(seed)
        artifacts = []
        enemies = []
        patrols = []


        start = None
        exit = None

        for i in range(terrain.rows):
            for j in range(terrain.columns):
                position = Position(i, j)
                if terrain.is_traversable(position):
                    start = position
                    break
            if start:
                break

        for i in range(terrain.rows):
            for j in range(terrain.columns):
                position = Position(terrain.rows -1 - i, terrain.columns -1 - j)
                if terrain.is_traversable(position):
                    exit = position
                    if exit == start:
                        exit = None
                        continue
                    else:
                        break
            if exit:
                break

        open_tiles = 0
        for i in range(terrain.rows):
            for j in range(terrain.columns):
                position = Position(i, j)
                if terrain.is_traversable(position):
                    if (position == start or position == exit) and not specification.allow_entities_on_endpoints:
                        continue
                    else:
                        open_tiles +=1


        for i in range(specification.enemy_count):
            space = rng.randint(0,open_tiles-1)
            enemy_id = f"enemy_{i+1}"
            stopper = 0
            penalty = rng.randint(specification.enemy_penalty_min,specification.enemy_penalty_max)

            for h in range(terrain.rows):
                for j in range(terrain.columns):
                    position = Position(h, j)

                    if terrain.is_traversable(position):
                        if (position == start or position == exit) and not specification.allow_entities_on_endpoints:
                            continue

                        if space <= 0:
                            exist = 0

                            for x in artifacts:
                                if x.position == position:
                                    exist += 1

                            for x in enemies:
                                if x.position == position:
                                    exist += 1

                            if exist and not specification.allow_entity_overlap:
                                continue

                            

                            stopper += 1
                            
                        else:
                            space -= 1
                            continue

                    if stopper:
                        break

                if stopper:
                    break
            if stopper:
                enemy = EnemyDefinition(enemy_id,position,penalty)
                enemies.append(enemy)
        
        remain = specification.enemy_count - len(enemies)
        if remain:
            while remain > 0:
                added = 0
                enemy_id = f"enemy_{len(enemies) + 1}"
                penalty = rng.randint(specification.enemy_penalty_min,specification.enemy_penalty_max)
                for i in range(terrain.rows):
                    for j in range(terrain.columns):
                        position = Position(i, j)
                        if terrain.is_traversable(position):
                            if (position == start or position == exit) and not specification.allow_entities_on_endpoints:
                                continue
                            exist = 0
                            
                            for x in artifacts:
                                if x.position == position:
                                    exist += 1

                            for x in enemies:
                                if x.position == position:
                                    exist += 1

                            if exist and not specification.allow_entity_overlap:
                                continue
                            enemy = EnemyDefinition(enemy_id,position,penalty)
                            enemies.append(enemy)
                            remain -=1
                            added += 1
                        if added:
                            break
                    if added:
                        break
                if added == 0:
                    break


        for i in range(specification.artifact_count):
            space = rng.randint(0, open_tiles - 1)
            artifact_id = f"artifact_{i+1}"
            stopper = 0
            value = rng.randint(specification.artifact_value_min, specification.artifact_value_max)

            for h in range(terrain.rows):
                for j in range(terrain.columns):
                    position = Position(h, j)

                    if terrain.is_traversable(position):
                        if (position == start or position == exit) and not specification.allow_entities_on_endpoints:
                            continue


                        if space <= 0:
                            exist = 0

                            for x in artifacts:
                                if x.position == position:
                                    exist += 1

                            for x in enemies:
                                if x.position == position:
                                    exist += 1

                            if exist and not specification.allow_entity_overlap:
                                continue

                            
                            stopper += 1

                        else:
                            space -= 1
                            continue

                    if stopper:
                        break

                if stopper:
                    break

            if stopper:
                newartifact = ArtifactDefinition(artifact_id, position, value)
                artifacts.append(newartifact)


        remain = specification.artifact_count - len(artifacts)

        if remain:
            while remain > 0:
                added = 0
                artifact_id = f"artifact_{len(artifacts) + 1}"
                value = rng.randint(specification.artifact_value_min, specification.artifact_value_max)

                for i in range(terrain.rows):
                    for j in range(terrain.columns):
                        position = Position(i, j)

                        if terrain.is_traversable(position):
                            if (position == start or position == exit) and not specification.allow_entities_on_endpoints:
                                continue

                            exist = 0

                            for x in artifacts:
                                if x.position == position:
                                    exist += 1

                            for x in enemies:
                                if x.position == position:
                                    exist += 1

                            if exist and not specification.allow_entity_overlap:
                                continue

                            newartifact = ArtifactDefinition(artifact_id, position, value)
                            artifacts.append(newartifact)
                            remain -= 1
                            added += 1

                        if added:
                            break

                    if added:
                        break

                if added == 0:
                    break

        for en in enemies:
            for i in range(4):
                count = 0
                x = en.position.row
                y = en.position.column
                position1 = None
                position2 = None
                position3 = None

                if i == 0:
                    if terrain.is_traversable(Position(x , y - 1)):
                        position1 = Position(x , y - 1)
                        count +=1

                    if terrain.is_traversable(Position(x +1 , y -1)):
                        position2 = Position(x +1 , y -1)
                        count +=1

                    if terrain.is_traversable(Position(x +1 , y)):
                        position3 = Position(x +1 , y)
                        count +=1

                elif i == 1:
                    if terrain.is_traversable(Position(x +1 , y)):
                        position1 = Position(x +1 , y)
                        count +=1

                    if terrain.is_traversable(Position(x+1 , y+1)):
                        position2 = Position(x+1 , y+1)
                        count +=1

                    if terrain.is_traversable(Position(x , y +1)):
                        position3 = Position(x , y +1)
                        count +=1

                elif i == 2:
                    if terrain.is_traversable(Position(x , y+1)):
                        position1 = Position(x , y+1)
                        count +=1
                        
                    if terrain.is_traversable(Position(x-1 , y+1)):
                        position2 = Position(x-1 , y+1)
                        count +=1

                    if terrain.is_traversable(Position(x -1, y)):
                        position3 = Position(x -1, y)
                        count +=1
                        

                else:
                    if terrain.is_traversable(Position(x -1 , y)):
                        position1 = Position(x -1 , y)
                        count +=1

                    if terrain.is_traversable(Position(x -1, y -1)):
                        position2 = Position(x -1, y -1)
                        count +=1

                    if terrain.is_traversable(Position(x , y-1)):
                        position3 = Position(x , y-1)
                        count +=1
                        
                if count == 3:
                    enemy = PatrolDefinition(en.enemy_id, tuple([position1,position2,position3]), 0)
                    patrols.append(enemy)



        return LevelDefinition(level_id, profile_id,seed, terrain, start, exit, charac , tuple(artifacts), tuple(enemies), tuple(patrols))
        