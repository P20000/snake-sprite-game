"""
Snake entity handling segment movement, directional queue, collisions, and sprite rendering.
"""
from collections import deque
import pygame
from src.constants import TILE_SIZE, GRID_WIDTH, GRID_HEIGHT

class Snake:
    """Represents the player-controlled snake with smooth input buffering."""

    def __init__(self, start_x=None, start_y=None):
        if start_x is None:
            start_x = GRID_WIDTH // 2
        if start_y is None:
            start_y = GRID_HEIGHT // 2

        self.body = [[start_x - 2, start_y], [start_x - 1, start_y], [start_x, start_y]]
        self.dx = 1
        self.dy = 0
        self.input_queue = deque(maxlen=3)
        self.growth_pending = 0

    @property
    def head(self):
        """Returns the current head position [x, y]."""
        return self.body[-1]

    @property
    def length(self):
        """Returns the current number of body segments."""
        return len(self.body)

    def queue_direction(self, new_dx, new_dy):
        """
        Adds a new movement direction to the input buffer,
        preventing direct 180-degree reversals against the current/last-queued direction.
        """
        # Determine base direction to compare against
        last_dx, last_dy = self.input_queue[-1] if self.input_queue else (self.dx, self.dy)

        # Disallow reversing 180 degrees or duplicate identical commands
        if (new_dx == -last_dx and new_dy == -last_dy) or (new_dx == last_dx and new_dy == last_dy):
            return

        self.input_queue.append((new_dx, new_dy))

    def handle_key_event(self, key):
        """Handles WASD and Arrow keys."""
        if key in (pygame.K_w, pygame.K_UP):
            self.queue_direction(0, -1)
        elif key in (pygame.K_s, pygame.K_DOWN):
            self.queue_direction(0, 1)
        elif key in (pygame.K_a, pygame.K_LEFT):
            self.queue_direction(-1, 0)
        elif key in (pygame.K_d, pygame.K_RIGHT):
            self.queue_direction(1, 0)

    def grow(self, amount=1):
        """Increases the number of segments to grow upon moving."""
        self.growth_pending += amount

    def step(self, wrap_walls=False, grid_w=GRID_WIDTH, grid_h=GRID_HEIGHT):
        """
        Advances the snake one grid step.
        Returns (is_alive, head_position).
        """
        # Pop next direction from queue if available
        if self.input_queue:
            self.dx, self.dy = self.input_queue.popleft()

        new_x = self.body[-1][0] + self.dx
        new_y = self.body[-1][1] + self.dy

        # Handle wall wrapping / boundaries
        if wrap_walls:
            new_x %= grid_w
            new_y %= grid_h
        else:
            if not (0 <= new_x < grid_w and 0 <= new_y < grid_h):
                return False, [new_x, new_y]

        new_head = [new_x, new_y]

        # Check self-collision (excluding the tail if the snake is not growing this turn)
        collision_body = self.body if self.growth_pending > 0 else self.body[1:]
        if new_head in collision_body:
            return False, new_head

        self.body.append(new_head)

        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.body.pop(0)

        return True, new_head

    def draw(self, surface, sprites):
        """Renders the snake with rotation-aware head, corner, body, and tail sprites."""
        for i, pos in enumerate(self.body):
            sprite = None
            angle = 0

            if i == len(self.body) - 1:  # Head
                if len(self.body) > 1:
                    dir_vec = (self.body[i][0] - self.body[i - 1][0], self.body[i][1] - self.body[i - 1][1])
                else:
                    dir_vec = (self.dx, self.dy)

                if dir_vec == (0, -1):
                    sprite = sprites.get("head_up")
                elif dir_vec == (0, 1):
                    sprite = sprites.get("head_down")
                elif dir_vec == (-1, 0):
                    sprite = sprites.get("head_left")
                else:
                    sprite = sprites.get("head_right")

            elif i == 0:  # Tail
                if len(self.body) > 1:
                    dir_vec = (self.body[1][0] - self.body[0][0], self.body[1][1] - self.body[0][1])
                else:
                    dir_vec = (self.dx, self.dy)

                if dir_vec == (0, -1):
                    sprite = sprites.get("tail_up")
                elif dir_vec == (0, 1):
                    sprite = sprites.get("tail_down")
                elif dir_vec == (-1, 0):
                    sprite = sprites.get("tail_left")
                else:
                    sprite = sprites.get("tail_right")

            else:  # Body or Corner
                prev_p = self.body[i - 1]
                curr_p = self.body[i]
                next_p = self.body[i + 1]

                dx1, dy1 = curr_p[0] - prev_p[0], curr_p[1] - prev_p[1]
                dx2, dy2 = next_p[0] - curr_p[0], next_p[1] - curr_p[1]

                if dx1 == dx2 and dy1 == dy2:  # Straight
                    sprite = sprites.get("body_vertical") if dx1 == 0 else sprites.get("body_horizontal")
                else:  # Corner turn
                    sprite = sprites.get("corner")
                    if ((dx1, dy1) == (-1, 0) and (dx2, dy2) == (0, 1)) or \
                       ((dx1, dy1) == (0, -1) and (dx2, dy2) == (1, 0)):
                        angle = 0
                    elif ((dx1, dy1) == (0, 1) and (dx2, dy2) == (1, 0)) or \
                         ((dx1, dy1) == (-1, 0) and (dx2, dy2) == (0, -1)):
                        angle = 90
                    elif ((dx1, dy1) == (1, 0) and (dx2, dy2) == (0, -1)) or \
                         ((dx1, dy1) == (0, 1) and (dx2, dy2) == (-1, 0)):
                        angle = 180
                    elif ((dx1, dy1) == (0, -1) and (dx2, dy2) == (-1, 0)) or \
                         ((dx1, dy1) == (1, 0) and (dx2, dy2) == (0, 1)):
                        angle = 270

            if sprite:
                if angle != 0:
                    sprite = pygame.transform.rotate(sprite, angle)
                surface.blit(sprite, (pos[0] * TILE_SIZE, pos[1] * TILE_SIZE))
