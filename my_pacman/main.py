import pygame
import sys
import time
from typing import Dict, Any
from my_pacman.maze import Maze
from my_pacman.entities import Pacman, Ghost

class PacmanGame:
    def __init__(self, width: int = 800, height: int = 600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pacman")
        
        self.cell_size = 30
        self.maze = Maze()
        self.pacman = Pacman(1, 1)
        self.ghost = Ghost(self.maze.width-2, self.maze.height-2)
        
        self.game_over = False
        self.game_won = False
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        
        # Colors
        self.colors = {
        "background": (0, 0, 0),
        "wall": (0, 0, 255),
        "pellet": (255, 255, 255),
        "pacman": (255, 255, 0),
        "ghost": (255, 0, 0),
        "text": (255, 255, 255)
        }
        self.ghost_ai = PacmanBot(self.ghost, self.maze)  # 创建AI控制器
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 只在按键按下时设置方向（非持续检测）
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.pacman.set_direction((0, -1))
                elif event.key == pygame.K_s:
                    self.pacman.set_direction((0, 1))
                elif event.key == pygame.K_a:
                    self.pacman.set_direction((-1, 0))
                elif event.key == pygame.K_d:
                    self.pacman.set_direction((1, 0))
                elif event.key == pygame.K_r:
                    if self.game_over or self.game_won:
                        self.__init__()
    
    def update(self):
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        if not self.game_over and not self.game_won:
            self.pacman.update(self.maze, dt)
            self.ghost_ai.update(self.pacman)
            self.ghost.update(self.maze, dt)
            
            # 简化后的碰撞检测
            if self.pacman.get_position() == self.ghost.get_position():
                self.pacman.lives -= 1
                if self.pacman.lives <= 0:
                    self.game_over = True
                else:
                    self.pacman.respawn(1, 1)
            
            if self.maze.is_empty():
                self.game_won = True
    
    def draw(self):
        self.screen.fill(self.colors["background"])
        
        # Draw maze
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                rect = pygame.Rect(
                    x * self.cell_size, 
                    y * self.cell_size, 
                    self.cell_size, 
                    self.cell_size
                )
                
                if self.maze.is_wall(x, y):
                    pygame.draw.rect(self.screen, self.colors["wall"], rect)
        
        # Draw pellets
        for x, y in self.maze.pellets:
            center = (
                x * self.cell_size + self.cell_size // 2,
                y * self.cell_size + self.cell_size // 2
            )
            pygame.draw.circle(self.screen, self.colors["pellet"], center, 3)
        
        # Draw power pellets
        for x, y in self.maze.power_pellets:
            center = (
                x * self.cell_size + self.cell_size // 2,
                y * self.cell_size + self.cell_size // 2
            )
            pygame.draw.circle(self.screen, self.colors["power_pellet"], center, 6)
        
        # Draw pacman
        pacman_rect = pygame.Rect(
            self.pacman.x * self.cell_size,
            self.pacman.y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        pygame.draw.arc(
            self.screen, self.colors["pacman"],
            pacman_rect,
            0.2, 5.8,  # Mouth angle
            self.cell_size // 2
        )
        
        # Draw ghost
        ghost_color = self.colors["ghost"]
        ghost_rect = pygame.Rect(
            self.ghost.x * self.cell_size,
            self.ghost.y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        pygame.draw.rect(self.screen, self.colors["ghost"], ghost_rect, border_radius=self.cell_size//3)
        
        # Draw score and lives
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.pacman.score}", True, self.colors["text"])
        lives_text = font.render(f"Lives: {self.pacman.lives}", True, self.colors["text"])
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        
        # Draw game over or win message
        if self.game_over:
            font = pygame.font.SysFont(None, 72)
            text = font.render("GAME OVER", True, self.colors["text"])
            text_rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
            self.screen.blit(text, text_rect)
            
            restart_font = pygame.font.SysFont(None, 36)
            restart_text = restart_font.render("Press R to restart", True, self.colors["text"])
            restart_rect = restart_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        if self.game_won:
            font = pygame.font.SysFont(None, 72)
            text = font.render("YOU WIN!", True, self.colors["text"])
            text_rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
            self.screen.blit(text, text_rect)
            
            restart_font = pygame.font.SysFont(None, 36)
            restart_text = restart_font.render("Press R to restart", True, self.colors["text"])
            restart_rect = restart_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

class PacmanBot:
    """基于贪心算法的幽灵AI控制器"""
    def __init__(self, ghost, maze):
        self.ghost = ghost
        self.maze = maze
        self.last_direction = (0, 0)
    
    def update(self, pacman):
        # 获取当前位置
        gx, gy = self.ghost.get_position()
        px, py = pacman.get_position()
        
        # 获取所有可能的移动方向
        possible_moves = self.maze.get_valid_moves(gx, gy)
        
        if not possible_moves:
            self.ghost.set_direction((0, 0))
            return
        
        # 贪心算法：选择使曼哈顿距离最小的方向
        best_dir = None
        min_distance = float('inf')
        
        for dx, dy in possible_moves:
            new_x, new_y = gx + dx, gy + dy
            distance = abs(new_x - px) + abs(new_y - py)
            
            # 避免立即掉头（除非是唯一选择）
            if (-dx, -dy) == self.last_direction and len(possible_moves) > 1:
                distance += 2  # 给掉头方向增加惩罚
            
            if distance < min_distance:
                min_distance = distance
                best_dir = (dx, dy)
        
        if best_dir:
            self.ghost.set_direction(best_dir)
            self.last_direction = best_dir