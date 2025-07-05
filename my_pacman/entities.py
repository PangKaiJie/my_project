from typing import Tuple, List
import numpy as np

class Entity:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.direction = (0, 0)
        self.speed = 1.0
        self.next_direction = (0, 0)
    
    def update_position(self, maze, dt: float):
        # 尝试改变方向
        new_x = self.x + self.next_direction[0] * self.speed * dt
        new_y = self.y + self.next_direction[1] * self.speed * dt
        
        if not maze.is_wall(int(new_x), int(new_y)):
            self.direction = self.next_direction
        else:
            self.next_direction = self.direction
            
        # 按当前方向移动
        new_x = self.x + self.direction[0] * self.speed * dt
        new_y = self.y + self.direction[1] * self.speed * dt
        
        if not maze.is_wall(int(new_x), int(new_y)):
            self.x = new_x
            self.y = new_y
        else:
            # 如果撞墙，对齐到网格
            self.x = round(self.x)
            self.y = round(self.y)
    
    def set_direction(self, direction: Tuple[int, int]):
        self.next_direction = direction
    
    def get_position(self) -> Tuple[int, int]:
        return (int(round(self.x)), int(round(self.y)))

class Pacman(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.speed = 2.0
        self.lives = 3
        self.score = 0
        self.direction = (1, 0)  # 初始向右移动
    
    def update(self, maze, dt: float):
        super().update_position(maze, dt)
        
        # 检查是否吃到豆子
        x, y = self.get_position()
        pellet_type = maze.eat_pellet(x, y)
        
        if pellet_type == 1:  
            self.score += 10
    
    def respawn(self, x: int, y: int):
        self.x = x
        self.y = y
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.powered_up = False
        self.power_time = 0.0

class Ghost(Entity):
    def __init__(self, x: int, y: int, color: str = "red"):
        super().__init__(x, y)
        self.speed = 1.8
        self.color = color
    
    def update(self, maze, dt: float, pacman=None):
        super().update_position(maze, dt)
    