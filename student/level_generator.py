"""TODO: build a canonical level using the injected terrain generator."""
from src.api import LevelDefinition, LevelSpecification, TerrainGeneratorContract, Position, CharacterDefinition, EnemyDefinition, ArtifactDefinition, PatrolDefinition, TerrainGenerationSpec, TerrainTopology # type: ignore
import random

class LevelGenerator:
    """Use the supplied TerrainGeneratorContract; do not instantiate a replacement."""

    def __init__(self, terrain_generator: TerrainGeneratorContract) -> None:
        #raise NotImplementedError("TODO LevelGenerator: retain injected generator and implement generate_level")
        self.terrain_generator = terrain_generator

    def generate_level(self, specification: LevelSpecification, seed: int) -> LevelDefinition:
        # Preserve specification identities and seed; choose valid opposite endpoints.
        #raise NotImplementedError("TODO LevelGenerator.generate_level")    
        for attempt in range(specification.max_attempts):
            terrain = self.terrain_generator.generate_terrain(specification.terrain_spec,seed + attempt)
            level_id = specification.level_id
            profile_id = specification.profile_id
            charac = CharacterDefinition(specification.agent_id)
            rng = random.Random(seed + attempt)
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

            if not start or not exit:
                continue

            queue = [(start, 0)]
            visited = [start]
            route_moves = None
            parents = {}

            direction = [(-1,0),(+1, 0),(0, -1),(0, +1)]

            while queue:
                current, move = queue.pop(0)
                if current == exit:
                    route_moves = move
                    break
                for dir in direction:
                    newPosition = Position(current.row + dir[0], current.column + dir[1])
                    if terrain.is_traversable(newPosition) and newPosition not in visited:
                        visited.append(newPosition)
                        queue.append((newPosition, move + 1))
                        parents[newPosition] = current

            if route_moves is None:
                continue

            if not specification.min_route_moves <= route_moves <= specification.max_route_moves:
                continue

            branchCount = 0

            for i in range(terrain.rows):
                for j in range(terrain.columns):
                    pos = Position(i,j)
                    if terrain.is_traversable(pos):
                        nighbor = 0
                        for dir in direction:
                            newpos = Position(i + dir[0], j + dir[1])
                            if terrain.is_traversable(newpos):
                                nighbor += 1
                        if nighbor >= 3:
                            branchCount+= 1

            if not specification.min_branch_tiles <= branchCount:
                continue
            
            deadEnd = 0

            for i in range(terrain.rows):
                for j in range(terrain.columns):
                    pos = Position(i,j)
                    if terrain.is_traversable(pos):
                        nighbor = 0
                        for dir in direction:
                            newpos = Position(i + dir[0], j + dir[1])
                            if terrain.is_traversable(newpos):
                                nighbor += 1
                        if nighbor == 1:
                            deadEnd += 1

            if not deadEnd <= specification.max_dead_end_tiles:
                continue

            shortest_route = [exit]
            current = exit

            while current != start:
                current = parents[current]
                shortest_route.append(current)

            shortest_route.reverse()

            if specification.require_alternate_path:
                alternate_found = False

                for i in range(len(shortest_route) - 1):
                    blocked_edge = (shortest_route[i], shortest_route[i + 1])

                    queue = [start]
                    visited = [start]

                    while queue:
                        current = queue.pop(0)

                        if current == exit:
                            alternate_found = True
                            break

                        for dir in direction:
                            newPosition = Position(
                                current.row + dir[0],
                                current.column + dir[1]
                            )

                            if (current, newPosition) == blocked_edge or (newPosition, current) == blocked_edge:
                                continue

                            if terrain.is_traversable(newPosition) and newPosition not in visited:
                                visited.append(newPosition)
                                queue.append(newPosition)

                    if alternate_found:
                        break

                if not alternate_found:
                    continue
            turns = 0
            lastDirect = None

            for i in range(len(shortest_route) - 1):
                current = shortest_route[i]
                next_position = shortest_route[i + 1]

                direction = (next_position.row - current.row, next_position.column - current.column)
                if not lastDirect:
                    lastDirect = direction
                    continue
                else:
                    if lastDirect != direction:
                        turns += 1
                    lastDirect = direction
            if not turns <= specification.max_turns:
                continue

            open_tiles = 0
            for i in range(terrain.rows):
                for j in range(terrain.columns):
                    position = Position(i, j)
                    if terrain.is_traversable(position):
                        if (position == start or position == exit) and not specification.allow_entities_on_endpoints:
                            continue
                        else:
                            open_tiles +=1
            if open_tiles == 0:
                continue


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

            # for en in enemies:
            #     for i in range(4):
            #         count = 0
            #         x = en.position.row
            #         y = en.position.column
            #         position1 = None
            #         position2 = None
            #         position3 = None

            #         if i == 0:
            #             if (terrain.is_traversable(Position(x, y - 1))
            #                 and all(a.position != Position(x, y - 1) for a in artifacts)
            #                 and all(e.position != Position(x, y - 1) for e in enemies)):
            #                 position1 = Position(x, y - 1)
            #                 count += 1

            #             if (terrain.is_traversable(Position(x + 1, y - 1))
            #                 and all(a.position != Position(x + 1, y - 1) for a in artifacts)
            #                 and all(e.position != Position(x + 1, y - 1) for e in enemies)):
            #                 position2 = Position(x + 1, y - 1)
            #                 count += 1

            #             if (terrain.is_traversable(Position(x + 1, y))
            #                 and all(a.position != Position(x + 1, y) for a in artifacts)
            #                 and all(e.position != Position(x + 1, y) for e in enemies)):
            #                 position3 = Position(x + 1, y)
            #                 count += 1

            #         elif i == 1:
            #             if (terrain.is_traversable(Position(x + 1, y))
            #                 and all(a.position != Position(x + 1, y) for a in artifacts)
            #                 and all(e.position != Position(x + 1, y) for e in enemies)):
            #                 position1 = Position(x + 1, y)
            #                 count += 1

            #             if (terrain.is_traversable(Position(x + 1, y + 1))
            #                 and all(a.position != Position(x + 1, y + 1) for a in artifacts)
            #                 and all(e.position != Position(x + 1, y + 1) for e in enemies)):
            #                 position2 = Position(x + 1, y + 1)
            #                 count += 1

            #             if (terrain.is_traversable(Position(x, y + 1))
            #                 and all(a.position != Position(x, y + 1) for a in artifacts)
            #                 and all(e.position != Position(x, y + 1) for e in enemies)):
            #                 position3 = Position(x, y + 1)
            #                 count += 1

            #         elif i == 2:
            #             if (terrain.is_traversable(Position(x, y + 1))
            #                 and all(a.position != Position(x, y + 1) for a in artifacts)
            #                 and all(e.position != Position(x, y + 1) for e in enemies)):
            #                 position1 = Position(x, y + 1)
            #                 count += 1

            #             if (terrain.is_traversable(Position(x - 1, y + 1))
            #                 and all(a.position != Position(x - 1, y + 1) for a in artifacts)
            #                 and all(e.position != Position(x - 1, y + 1) for e in enemies)):
            #                 position2 = Position(x - 1, y + 1)
            #                 count += 1

            #             if (terrain.is_traversable(Position(x - 1, y))
            #                 and all(a.position != Position(x - 1, y) for a in artifacts)
            #                 and all(e.position != Position(x - 1, y) for e in enemies)):
            #                 position3 = Position(x - 1, y)
            #                 count += 1

            #         else:
            #             if (terrain.is_traversable(Position(x - 1, y))
            #                 and all(a.position != Position(x - 1, y) for a in artifacts)
            #                 and all(e.position != Position(x - 1, y) for e in enemies)):
            #                 position1 = Position(x - 1, y)
            #                 count += 1

            #             if (terrain.is_traversable(Position(x - 1, y - 1))
            #                 and all(a.position != Position(x - 1, y - 1) for a in artifacts)
            #                 and all(e.position != Position(x - 1, y - 1) for e in enemies)):
            #                 position2 = Position(x - 1, y - 1)
            #                 count += 1

            #             if (terrain.is_traversable(Position(x, y - 1))
            #                 and all(a.position != Position(x, y - 1) for a in artifacts)
            #                 and all(e.position != Position(x, y - 1) for e in enemies)):
            #                 position3 = Position(x, y - 1)
            #                 count += 1

            #         if count == 3:
            #             enemy = PatrolDefinition(
            #                 enemy_id=en.enemy_id,
            #                 positions=(position1, position2, position3),
            #                 initial_phase=0
            #             )
            #             patrols.append(enemy)
            #             break


            return LevelDefinition(
                level_id=level_id,
                profile_id=profile_id,
                seed=seed,
                terrain=terrain,
                start=start,
                exit=exit,
                character=charac,
                artifacts=tuple(artifacts),
                enemies=tuple(enemies),
                patrols=tuple(patrols)
            )

        raise RuntimeError("Unable to generate a valid level within the maximum attempts.")

