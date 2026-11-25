"""TODO: generate canonical terrain deterministically from specification and seed."""
import random
from src.api import Terrain, TerrainGenerationSpec, TerrainTopology

def chooseD(rows, columns, tile, rng):
    directions = []

    if columns >= tile:
        directions.append("horizontal")

    if rows >= tile:
        directions.append("vertical")

    if not directions:
        raise ValueError("Segment cannot fit in the terrain.")

    return rng.choice(directions)

class TerrainGenerator:
    """Keep state local; identical inputs must also agree across fresh instances."""

    def __init__(self) -> None:
        #raise NotImplementedError("TODO TerrainGenerator: implement constructor and generate_terrain")
        pass

    def generate_terrain(self, specification: TerrainGenerationSpec, seed: int) -> Terrain:
        # This workbench accepts only its documented public introductory family.
        #raise NotImplementedError("TODO TerrainGenerator.generate_terrain")
        row = specification.rows
        columns = specification.columns
        maxTiles = specification.max_open_tiles
        minTiles = specification.min_open_tiles
        rng = random.Random(seed)
        tiles = rng.randint(minTiles,maxTiles)

        grid = []
        for i in range(row):
            line = []
            for j in range(columns):
                line.append("#")
            grid.append(line)



        if specification.topology == TerrainTopology.STRAIGHT_PATH:
            direction = chooseD(row,columns,tiles,rng)

            if direction == "horizontal":
                starting_tile = rng.randint(1, row) - 1
                for i in range(tiles):
                    grid[starting_tile][i] = "."

                    
            elif direction == "vertical":
                starting_tile = rng.randint(1, columns) - 1
                for i in range(tiles):
                    grid[i][starting_tile]= "."

            else:
                raise ValueError("No valid straight path can fit in the terrain.")

            terr = []

            for i in grid:
                terr.append(''.join(i))

            return Terrain(tuple(terr))

        elif specification.topology == TerrainTopology.BENT_PATH:

            for attempt in range(specification.max_attempts):
                rng = random.Random(seed + attempt)
                grid = []
                for i in range(row):
                    line = []
                    for j in range(columns):
                        line.append("#")
                    grid.append(line)

                if tiles < 2:
                    raise ValueError("Bent path requires at least 2 open tiles.")

                if tiles <= 3:
                    turns = 1
                else:
                    turns = rng.randint(1, 2)

                if turns == 1:
                    segment1 = rng.randint(1, tiles - 1)
                    segment2 = tiles - segment1

                else:
                    segment1 = rng.randint(1, tiles - 3)
                    segment2 = rng.randint(2, tiles - segment1 - 1)
                    segment3 = tiles - (segment1 + segment2)

                # Check which first directions can fit both segments
                directions = []

                if columns >= segment1 and row >= segment2 + 1:
                    directions.append("horizontal")

                if row >= segment1 and columns >= segment2 + 1:
                    directions.append("vertical")

                if not directions:
                    continue

                direction = rng.choice(directions)

                if direction == "horizontal":

                    ch = rng.randint(1, 2)

                    if ch == 1:
                        starting_row = rng.randint(1, row - segment2) - 1
                    else:
                        starting_row = rng.randint(segment2 + 1, row) - 1

                    starting_column = rng.randint(1, columns - segment1 + 1) - 1

                    # Place segment1
                    for i in range(segment1):
                        grid[starting_row][starting_column + i] = "."

                    # Place segment2
                    if ch == 1:
                        for j in range(segment2):
                            grid[starting_row + j + 1][starting_column + segment1 - 1] = "."

                        third_row = starting_row + segment2

                    else:
                        for j in range(segment2):
                            grid[starting_row - j - 1][starting_column + segment1 - 1] = "."

                        third_row = starting_row - segment2

                    # Two-turn path: check segment3
                    if turns == 2:

                        third_column = starting_column + segment1 - 1

                        right_space = columns - third_column - 1
                        left_space = third_column

                        if right_space >= segment3 and left_space >= segment3:
                            ch2 = rng.randint(1, 2)

                            if ch2 == 1:
                                for x in range(segment3):
                                    grid[third_row][third_column + x + 1] = "."
                            else:
                                for x in range(segment3):
                                    grid[third_row][third_column - x - 1] = "."

                        elif right_space >= segment3:
                            for x in range(segment3):
                                grid[third_row][third_column + x + 1] = "."

                        elif left_space >= segment3:
                            for x in range(segment3):
                                grid[third_row][third_column - x - 1] = "."

                        else:
                            # Segment3 cannot fit; try another attempt
                            continue

                else:

                    ch = rng.randint(1, 2)

                    if ch == 1:
                        starting_column = rng.randint(1, columns - segment2) - 1
                    else:
                        starting_column = rng.randint(segment2 + 1, columns) - 1

                    starting_row = rng.randint(1, row - segment1 + 1) - 1

                    # Place segment1
                    for i in range(segment1):
                        grid[starting_row + i][starting_column] = "."

                    # Place segment2
                    if ch == 1:
                        for j in range(segment2):
                            grid[starting_row + segment1 - 1][starting_column + j + 1] = "."

                        third_column = starting_column + segment2

                    else:
                        for j in range(segment2):
                            grid[starting_row + segment1 - 1][starting_column - j - 1] = "."

                        third_column = starting_column - segment2

                    # Two-turn path: check segment3
                    if turns == 2:

                        third_row = starting_row + segment1 - 1

                        down_space = row - third_row - 1
                        up_space = third_row

                        if down_space >= segment3 and up_space >= segment3:
                            ch2 = rng.randint(1, 2)

                            if ch2 == 1:
                                for x in range(segment3):
                                    grid[third_row + x + 1][third_column] = "."
                            else:
                                for x in range(segment3):
                                    grid[third_row - x - 1][third_column] = "."

                        elif down_space >= segment3:
                            for x in range(segment3):
                                grid[third_row + x + 1][third_column] = "."

                        elif up_space >= segment3:
                            for x in range(segment3):
                                grid[third_row - x - 1][third_column] = "."

                        else:
                            # Segment3 cannot fit; try another attempt
                            continue

                terr = []

                for i in grid:
                    terr.append("".join(i))

                return Terrain(tuple(terr))

            raise ValueError("Unable to generate a valid bent path within the allowed attempts.")

        elif specification.topology == TerrainTopology.BRANCHING_TREE:
            for attempt in range(specification.max_attempts):
                rng = random.Random(seed + attempt)

                grid = []
                for i in range(row):
                    line = []
                    for j in range(columns):
                        line.append("#")
                    grid.append(line)
                tile_copy = tiles
                if row >= columns:
                    direction = "vertical"
                else:
                    direction = "horizontal"

                if direction == "vertical":
                    starting_row = rng.choice([0, row - 1])
                    starting_column = rng.randint(2, columns - 1) - 1

                    main = rng.randint(3, row)
                    tile_copy -= main

                    side1 = rng.randint(1, starting_column)
                    side2 = rng.randint(1, columns - starting_column - 1)
                    tile_copy -= (side1 + side2)

                    while tile_copy < 0:
                        if side1 > side2:
                            side1 -= 1
                            tile_copy += 1
                        elif side2 > side1:
                            side2 -= 1
                            tile_copy += 1
                        else:
                            main -= 1
                            tile_copy += 1

                    used = side1 + side2 + main
                    additional = 0
                    while used < minTiles:
                        if side1 < starting_column:
                            side1 += 1
                            used += 1
                        elif side2 < columns - starting_column - 1:
                            side2 += 1
                            used += 1
                        else:
                            if main < row:
                                main += 1
                                used += 1
                            else:
                                additional = minTiles - used
                                break
                    used += additional
                    if used < minTiles:
                        continue

                    intpoint = rng.randint(2, main - 1) - 1

                    if starting_row == 0:
                        branch_row = starting_row + intpoint

                        for i in range(main):
                            grid[starting_row + i][starting_column] = "."
                    else:
                        branch_row = starting_row - intpoint

                        for i in range(main):
                            grid[starting_row - i][starting_column] = "."

                    for j in range(side1):
                        grid[branch_row][starting_column - 1 - j] = "."

                    for x in range(side2):
                        grid[branch_row][starting_column + 1 + x] = "."

                    if additional:
                        if side1 >= side2:
                            r = branch_row
                            c = starting_column - side1
                            up = branch_row
                            down = row - branch_row - 1
                            if up >= down:
                                try:
                                    for y in range(additional):
                                        grid[r- y-1][c] = "."
                                        additional-=1
                                except:
                                    try:
                                        for i in range(additional):
                                            grid[r +i+1][c] = "."
                                            additional -=1
                                    except:
                                        try:
                                            c = starting_column + side2
                                            for y in range(additional):
                                                grid[r+ y+1][c] = "."
                                                additional-=1
                                        except:
                                            for i in range(additional):
                                                grid[r -i-1][c] = "."
                                                additional -=1

                            else:
                                try:
                                    for i in range(additional):
                                        grid[r +i+1][c] = "."
                                        additional -=1
                                except:
                                    try:
                                        for y in range(additional):
                                            grid[r- y-1][c] = "."
                                            additional-=1
                                    except:
                                        try:
                                            c = starting_column + side2
                                            for y in range(additional):
                                                grid[r+ y+1][c] = "."
                                                additional-=1
                                        except:
                                            for i in range(additional):
                                                grid[r -i-1][c] = "."
                                                additional -=1
                        else:
                            r= branch_row
                            c = starting_column + side2
                            up = branch_row
                            down = row - branch_row - 1

                            if up < down:
                                try:
                                    for y in range(additional):
                                        grid[r+ y+1][c] = "."
                                        additional-=1
                                except:
                                    try:
                                        for i in range(additional):
                                            grid[r -i-1][c] = "."
                                            additional -=1
                                    except:
                                        try:
                                            c = starting_column - side1
                                            for y in range(additional):
                                                grid[r- y-1][c] = "."
                                                additional-=1
                                        except:
                                            for i in range(additional):
                                                grid[r +i+1][c] = "."
                                                additional -=1


                else:
                    starting_column = rng.choice([0, columns - 1])
                    starting_row = rng.randint(2, row - 1) - 1

                    main = rng.randint(3, columns)
                    tile_copy -= main

                    side1 = rng.randint(1, starting_row)

                    side2 = rng.randint(1, row - starting_row - 1)

                    tile_copy -= (side1 + side2)
                    additional = 0
                    while tile_copy < 0:
                        if side1 > side2:
                            side1 -= 1
                            tile_copy += 1
                        elif side2 > side1:
                            side2 -= 1
                            tile_copy += 1
                        else:
                            if main<columns :
                                main +=1
                                tile_copy += 1
                            else:
                                additional += 1

                    used = side1 + side2 + main

                    while used < minTiles:
                        if side1 < starting_row:
                            side1 += 1
                            used += 1
                        elif side2 < row - starting_row - 1:
                            side2 += 1
                            used += 1
                        else:
                            if main < columns:
                                main += 1
                                used += 1
                            else:
                                additional = minTiles - used
                                break

                    used += additional
                    if used < minTiles:
                        continue

                    intpoint = rng.randint(2, main - 1) - 1

                    if starting_column == 0:
                        branch_column = starting_column + intpoint

                        for i in range(main):
                            grid[starting_row][starting_column + i] = "."
                    else:
                        branch_column = starting_column - intpoint

                        for i in range(main):
                            grid[starting_row][starting_column - i] = "."

                    for j in range(side1):
                        grid[starting_row - 1 - j][branch_column] = "."

                    for x in range(side2):
                        grid[starting_row + 1 + x][branch_column] = "."

                    if additional:
                        if side1 >= side2:
                            r = starting_row - side1
                            c = branch_column
                            left = branch_column
                            right = columns - branch_column - 1

                            if left >= right:
                                try:
                                    for y in range(additional):
                                        grid[r][c - y - 1] = "."
                                        additional -= 1
                                except:
                                    try:
                                        for i in range(additional):
                                            grid[r][c + i + 1] = "."
                                            additional -= 1
                                    except:
                                        try:
                                            r = starting_row + side2
                                            for y in range(additional):
                                                grid[r][c + y + 1] = "."
                                                additional -= 1
                                        except:
                                            for i in range(additional):
                                                grid[r][c - i - 1] = "."
                                                additional -= 1
                            else:
                                try:
                                    for i in range(additional):
                                        grid[r][c + i + 1] = "."
                                        additional -= 1
                                except:
                                    try:
                                        for y in range(additional):
                                            grid[r][c - y - 1] = "."
                                            additional -= 1
                                    except:
                                        try:
                                            r = starting_row + side2
                                            for y in range(additional):
                                                grid[r][c + y + 1] = "."
                                                additional -= 1
                                        except:
                                            for i in range(additional):
                                                grid[r][c - i - 1] = "."
                                                additional -= 1



                        else:
                            r = starting_row + side2
                            c = branch_column
                            left = branch_column
                            right = columns - branch_column - 1

                            if left < right:
                                try:
                                    for y in range(additional):
                                        grid[r][c + y + 1] = "."
                                        additional -= 1
                                except:
                                    try:
                                        for i in range(additional):
                                            grid[r][c - i - 1] = "."
                                            additional -= 1
                                    except:
                                        try:
                                            r = starting_row - side1
                                            for y in range(additional):
                                                grid[r][c - y - 1] = "."
                                                additional -= 1
                                        except:
                                            for i in range(additional):
                                                grid[r][c + i + 1] = "."
                                                additional -= 1

                terr = []
                for i in grid:
                    terr.append("".join(i))

                return Terrain(tuple(terr))

            raise ValueError("Unable to generate a valid branching path within the allowed attempts.")

        
        elif specification.topology == TerrainTopology.GENERAL:
            grid = []
            for i in range(row):
                line = []
                for j in range(columns):
                    line.append("#")
                grid.append(line)

            tile_copy = tiles

            top = 0
            bottom = row - 1
            left = 0
            right = columns - 1

            while tile_copy > 0 and top <= bottom and left <= right:

                # Move downward
                for i in range(top, bottom + 1):
                    if grid[i][left] == "#" and tile_copy > 0:
                        grid[i][left] = "."
                        tile_copy -= 1

                left += 1

                # Move right
                for j in range(left, right + 1):
                    if grid[bottom][j] == "#" and tile_copy > 0:
                        grid[bottom][j] = "."
                        tile_copy -= 1

                bottom -= 1

                # Move upward
                for i in range(bottom, top - 1, -1):
                    if grid[i][right] == "#" and tile_copy > 0:
                        grid[i][right] = "."
                        tile_copy -= 1

                right -= 1

                # Move left
                for j in range(right, left - 1, -1):
                    if grid[top][j] == "#" and tile_copy > 0:
                        grid[top][j] = "."
                        tile_copy -= 1

                top += 1

            terr = []
            for i in grid:
                terr.append("".join(i))

            print(terr)

            return Terrain(tuple(terr))

specification = TerrainGenerationSpec(
    rows=2,
    columns=5,
    min_open_tiles=6,
    max_open_tiles=6,
    topology=TerrainTopology.GENERAL,
    max_attempts=3
)

generator = TerrainGenerator()
terrain = generator.generate_terrain(specification, seed=11)

print(terrain.terrain_rows)