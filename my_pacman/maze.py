import numpy as np
from typing import Tuple, List

class Maze:
    def __init__(self, width: int = 20, height: int = 15):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)
        self.pellets = set()
        self.power_pellets = set()
        self._generate_maze()
        
    def _generate_maze(self):
        # 创建墙壁
        self.grid[0, :] = 1
        self.grid[-1, :] = 1
        self.grid[:, 0] = 1
        self.grid[:, -1] = 1
        
        # 添加一些内部墙壁
        for i in range(2, self.height-2, 3):
            for j in range(2, self.width-2, 4):
                self.grid[i, j] = 1
                
        # 只添加普通豆子
        for i in range(1, self.height-1):
            for j in range(1, self.width-1):
                if self.grid[i, j] == 0 and (i % 2 != 0 or j % 3 != 0):
                    self.pellets.add((j, i))  # (x, y)
    
    def is_wall(self, x: int, y: int) -> bool:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x] == 1
        return True
    
    def get_valid_moves(self, x: int, y: int) -> List[Tuple[int, int]]:
        moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if not self.is_wall(new_x, new_y):
                moves.append((dx, dy))
        return moves
    
    def eat_pellet(self, x: int, y: int) -> int:
        """Returns: 1 for pellet, 2 for power pellet, 0 for nothing"""
        pos = (x, y)
        if pos in self.pellets:
            self.pellets.remove(pos)
            return 1
        elif pos in self.power_pellets:
            self.power_pellets.remove(pos)
            return 2
        return 0
    
    def is_empty(self) -> bool:
        return len(self.pellets) == 0 and len(self.power_pellets) == 0
    
    def get_pellet_positions(self) -> List[Tuple[int, int]]:
        return list(self.pellets) + list(self.power_pellets)