"""
AI Pathfinding and survival solver using BFS and flood-fill space safety heuristics.
"""
from collections import deque
from src.constants import GRID_WIDTH, GRID_HEIGHT

class AISolver:
    """Computes intelligent moves for the snake using BFS and trap prevention."""

    MOVES = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    @classmethod
    def get_next_move(cls, snake_body, food_pos, current_dx, current_dy, grid_w=GRID_WIDTH, grid_h=GRID_HEIGHT):
        """
        Calculates the best next move (dx, dy).
        Tries safe shortest path to food first; falls back to largest space exploration.
        """
        if not snake_body:
            return (current_dx, current_dy)

        head = snake_body[-1]
        tail = snake_body[0]

        # 1. Find shortest path to food
        path_to_food = cls._bfs_path(head, food_pos, snake_body, grid_w, grid_h, ignore_tail=True)
        
        if path_to_food:
            next_step = path_to_food[0]
            simulated_head = [head[0] + next_step[0], head[1] + next_step[1]]
            
            # Check if taking this step leaves enough open space (flood fill >= length)
            simulated_body = snake_body[1:] + [simulated_head]
            free_space = cls._count_reachable_tiles(simulated_head, simulated_body, grid_w, grid_h)
            
            # If space is safe or snake can reach its tail, take the path
            if free_space >= len(snake_body) or cls._bfs_path(simulated_head, tail, simulated_body, grid_w, grid_h):
                return next_step

        # 2. Fallback: Path towards tail to stall and survive
        path_to_tail = cls._bfs_path(head, tail, snake_body, grid_w, grid_h, ignore_tail=True)
        if path_to_tail:
            return path_to_tail[0]

        # 3. Last Resort: Pick neighbor with the largest open flood-fill area
        best_move = None
        max_area = -1

        for dx, dy in cls.MOVES:
            # Cannot reverse 180 degrees directly
            if (dx == -current_dx and dy == -current_dy):
                continue
            
            nx, ny = head[0] + dx, head[1] + dy
            if 0 <= nx < grid_w and 0 <= ny < grid_h and [nx, ny] not in snake_body:
                area = cls._count_reachable_tiles([nx, ny], snake_body, grid_w, grid_h)
                if area > max_area:
                    max_area = area
                    best_move = (dx, dy)

        return best_move if best_move else (current_dx, current_dy)

    @classmethod
    def should_boost(cls, snake_body, food_pos, current_dx, current_dy, grid_w=GRID_WIDTH, grid_h=GRID_HEIGHT):
        """
        Determines whether it is safe for the AI to activate speed boost.
        Returns True if the path to food is open and safe with ample free space.
        """
        if not snake_body:
            return False
        head = snake_body[-1]
        path = cls._bfs_path(head, food_pos, snake_body, grid_w, grid_h, ignore_tail=True)
        if path and len(path) >= 2:
            free_space = cls._count_reachable_tiles(head, snake_body, grid_w, grid_h)
            if free_space >= max(20, len(snake_body) * 2):
                return True
        return False

    @classmethod
    def _bfs_path(cls, start, goal, obstacles, grid_w, grid_h, ignore_tail=False):
        """Standard BFS shortest path between start and goal avoiding obstacles."""
        obstacle_set = set(tuple(p) for p in obstacles)
        if ignore_tail and obstacles:
            obstacle_set.discard(tuple(obstacles[0]))

        queue = deque([(start[0], start[1], [])])
        visited = set([(start[0], start[1])])

        while queue:
            cx, cy, path = queue.popleft()

            if (cx, cy) == (goal[0], goal[1]):
                return path

            for dx, dy in cls.MOVES:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < grid_w and 0 <= ny < grid_h:
                    if (nx, ny) not in visited and ((nx, ny) not in obstacle_set or (nx, ny) == tuple(goal)):
                        visited.add((nx, ny))
                        queue.append((nx, ny, path + [(dx, dy)]))

        return None

    @classmethod
    def _count_reachable_tiles(cls, start, obstacles, grid_w, grid_h, max_depth=120):
        """Counts how many tiles are accessible from a starting position (flood fill)."""
        obstacle_set = set(tuple(p) for p in obstacles)
        queue = deque([(start[0], start[1])])
        visited = set([(start[0], start[1])])
        count = 0

        while queue and count < max_depth:
            cx, cy = queue.popleft()
            count += 1

            for dx, dy in cls.MOVES:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < grid_w and 0 <= ny < grid_h:
                    if (nx, ny) not in visited and (nx, ny) not in obstacle_set:
                        visited.add((nx, ny))
                        queue.append((nx, ny))

        return count
