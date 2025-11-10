from cvzone.HandTrackingModule import HandDetector
import cv2


# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 15

# Grid settings
GRID_SIZE = 20  # Size of each grid cell in pixels
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE   # 40 cells
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE  # 30 cells

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Hand detection settings
DETECTION_CONFIDENCE = 0.8
MAX_HANDS = 1
DIRECTION_THRESHOLD = 30  # Pixels to move before direction change

# Snake settings
INITIAL_LENGTH = 3
SNAKE_SPEED = 1  # Grid cells per frame

class HandController:
    def __init__(self):
        self.detector = HandDetector(
            detectionCon=DETECTION_CONFIDENCE,
            maxHands=MAX_HANDS
        )
        self.prev_position = None
        self.current_direction = None
        
    def get_direction_from_finger(self, img):
        """
        Tracks index finger and converts position change to direction.
        Returns: 'UP', 'DOWN', 'LEFT', 'RIGHT', or None
        """
        hands, img = self.detector.findHands(img, draw=True)
        
        if not hands:
            return None, img
            
        # Get index finger tip (landmark 8)
        hand = hands[0]
        lmList = hand['lmList']
        index_finger_tip = lmList[8][0:2]  # [x, y]
        
        # First time initialization
        if self.prev_position is None:
            self.prev_position = index_finger_tip
            return self.current_direction, img
        
        # Calculate movement delta
        dx = index_finger_tip[0] - self.prev_position[0]
        dy = index_finger_tip[1] - self.prev_position[1]
        
        # Determine direction based on largest movement
        if abs(dx) > DIRECTION_THRESHOLD or abs(dy) > DIRECTION_THRESHOLD:
            if abs(dx) > abs(dy):
                # Horizontal movement dominates
                direction = 'RIGHT' if dx > 0 else 'LEFT'
            else:
                # Vertical movement dominates
                direction = 'DOWN' if dy > 0 else 'UP'
            
            self.current_direction = direction
            self.prev_position = index_finger_tip
            
        return self.current_direction, img

import pygame
from collections import deque

class Snake:
    def __init__(self, grid_width, grid_height, grid_size):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid_size = grid_size
        
        # Snake body as list of grid coordinates
        start_x = grid_width // 2
        start_y = grid_height // 2
        self.body = deque([
            [start_x, start_y],
            [start_x - 1, start_y],
            [start_x - 2, start_y]
        ])
        
        self.direction = 'RIGHT'
        self.grow_pending = False
        
    def change_direction(self, new_direction):
        """
        Change direction with validation to prevent 180° turns.
        """
        opposites = {
            'UP': 'DOWN', 'DOWN': 'UP',
            'LEFT': 'RIGHT', 'RIGHT': 'LEFT'
        }
        
        # Don't allow reversing
        if opposites[new_direction] != self.direction:
            self.direction = new_direction
    
    def move(self):
        """
        Move snake one grid cell in current direction.
        Returns: True if move successful, False if collision
        """
        head = list(self.body[0])
        
        # Calculate new head position
        if self.direction == 'UP':
            head[1] -= 1
        elif self.direction == 'DOWN':
            head[1] += 1
        elif self.direction == 'LEFT':
            head[0] -= 1
        elif self.direction == 'RIGHT':
            head[0] += 1
        
        # Boundary wrapping (teleportation)
        head[0] = head[0] % self.grid_width
        head[1] = head[1] % self.grid_height
        
        # Check self-collision (excluding neck to prevent false positive)
        if head in list(self.body)[1:]:
            return False
        
        # Add new head
        self.body.appendleft(head)
        
        # Remove tail (unless growing)
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False
            
        return True
    
    def grow(self):
        """Mark snake to grow on next move."""
        self.grow_pending = True
    
    def check_food_collision(self, food_pos):
        """Check if head overlaps food."""
        return list(self.body[0]) == food_pos
    
    def draw(self, surface):
        """Draw snake on pygame surface."""
        for i, segment in enumerate(self.body):
            x = segment[0] * self.grid_size
            y = segment[1] * self.grid_size
            
            # Head in different color
            color = RED if i == 0 else GREEN
            pygame.draw.rect(
                surface,
                color,
                (x, y, self.grid_size - 2, self.grid_size - 2)
            )


import random
import pygame

class Food:
    def __init__(self, grid_width, grid_height, grid_size):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid_size = grid_size
        self.position = [0, 0]
        self.spawn()
    
    def spawn(self, snake_body=None):
        """
        Spawn food at random position not occupied by snake.
        """
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            
            # Ensure food doesn't spawn on snake
            if snake_body is None or [x, y] not in snake_body:
                self.position = [x, y]
                break
    
    def draw(self, surface):
        """Draw food as circle."""
        x = self.position[0] * self.grid_size + self.grid_size // 2
        y = self.position[1] * self.grid_size + self.grid_size // 2
        pygame.draw.circle(surface, BLUE, (x, y), self.grid_size // 2 - 2)


import pygame
import cv2

def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Finger-Controlled Snake")
    clock = pygame.time.Clock()
    
    # Initialize game objects
    snake = Snake(GRID_WIDTH, GRID_HEIGHT, GRID_SIZE)
    food = Food(GRID_WIDTH, GRID_HEIGHT, GRID_SIZE)
    hand_controller = HandController()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # Width
    cap.set(4, 480)  # Height
    
    score = 0
    game_over = False
    camera_active = True
    
    # Main game loop
    running = True
    while running:
        clock.tick(FPS)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Keyboard controls (fallback)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction('UP')
                elif event.key == pygame.K_DOWN:
                    snake.change_direction('DOWN')
                elif event.key == pygame.K_LEFT:
                    snake.change_direction('LEFT')
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction('RIGHT')
                elif event.key == pygame.K_r and game_over:
                    # Restart game
                    snake = Snake(GRID_WIDTH, GRID_HEIGHT, GRID_SIZE)
                    food = Food(GRID_WIDTH, GRID_HEIGHT, GRID_SIZE)
                    score = 0
                    game_over = False
                elif event.key == pygame.K_c:
                    # Toggle camera
                    camera_active = not camera_active
        
        if not game_over:
            # Get camera input if active
            if camera_active:
                success, img = cap.read()
                if success:
                    img = cv2.flip(img, 1)  # Mirror image
                    direction, img = hand_controller.get_direction_from_finger(img)
                    
                    if direction:
                        snake.change_direction(direction)
                    
                    # Show camera feed in small window
                    cv2.imshow("Hand Tracking", img)
                    cv2.waitKey(1)
            
            # Move snake
            if not snake.move():
                game_over = True
            
            # Check food collision
            if snake.check_food_collision(food.position):
                snake.grow()
                score += 10
                food.spawn(list(snake.body))
        
        # Drawing
        screen.fill(BLACK)
        
        # Draw grid (optional)
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (0, y), (SCREEN_WIDTH, y))
        
        # Draw game objects
        snake.draw(screen)
        food.draw(screen)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw game over screen
        if game_over:
            game_over_font = pygame.font.Font(None, 72)
            game_over_text = game_over_font.render('GAME OVER', True, RED)
            restart_text = font.render('Press R to Restart', True, WHITE)
            screen.blit(game_over_text, 
                       (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 
                        SCREEN_HEIGHT//2 - 50))
            screen.blit(restart_text,
                       (SCREEN_WIDTH//2 - restart_text.get_width()//2,
                        SCREEN_HEIGHT//2 + 30))
        
        pygame.display.flip()
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()
