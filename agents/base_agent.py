"""
智能体基类
定义所有智能体的基本接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
import time

class BaseAgent(ABC):
    """智能体基类"""
    def __init__(self, name="Agent", player_id=1):
        self.name = name
        self.player_id = player_id
        self.total_moves = 0
        self.total_time = 0.0

    @abstractmethod
    def get_action(self, observation, env):
        pass

    def reset(self):
        """重置智能体统计"""
        self.total_moves = 0
        self.total_time = 0.0
    
    def update_stats(self, result: str, move_time: float = 0):
        """更新比赛结果统计
        Args:
            result: 'win', 'lose' 或 'draw'
            move_time: 该步用时(秒)
        """
        self.total_moves += 1
        self.total_time += move_time
        
        if not hasattr(self, 'wins'):
            self.wins = 0
            self.losses = 0
            self.draws = 0
            
        if result == 'win':
            self.wins += 1
        elif result == 'lose':
            self.losses += 1
        elif result == 'draw':
            self.draws += 1
    
    def get_info(self):
        """获取智能体信息"""
        return {
            'name': self.name,
            'player_id': self.player_id,
            'type': self.__class__.__name__,
            'description': f'{self.__class__.__name__} 智能体',
            'total_moves': self.total_moves,
            'total_time': self.total_time,
            'avg_time_per_move': self.total_time / max(1, self.total_moves),
            'avg_time_per_move': self.total_time / max(1, self.total_moves),
            'wins': getattr(self, 'wins', 0),
            'losses': getattr(self, 'losses', 0),
            'draws': getattr(self, 'draws', 0)
        }

    # ... 保持原有实现 ... 