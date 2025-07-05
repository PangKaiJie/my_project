"""
贪吃蛇环境
实现gym风格接口
"""

import numpy as np
import os
import time
from typing import Dict, List, Tuple, Any, Optional
from games.base_env import BaseEnv
from games.snake.snake_game import SnakeGame


class SnakeEnv(BaseEnv):
    """贪吃蛇环境"""
    
    def __init__(self, board_size=20, **kwargs):
        self.board_size = board_size
        self.game = SnakeGame(board_size)
        super().__init__(self.game)

    def _setup_spaces(self):
        """设置观察空间和动作空间"""
        self.observation_space = None
        self.action_space = None

    def _get_observation(self):
        """获取观察"""
        return self.game.board.copy()

    def _get_action_mask(self):
        """获取动作掩码"""
        # 贪吃蛇所有方向都可能有效，但要避免直接掉头
        return np.ones(4, dtype=bool)  # [up, down, left, right]

    def get_valid_actions(self):
        """获取有效动作"""
        return self.game.get_valid_actions()

    def is_terminal(self):
        """检查游戏是否结束"""
        return self.game.is_terminal()

    def get_winner(self):
        """获取获胜者"""
        return self.game.get_winner()

    def render(self, mode='human'):
        """渲染环境"""
        if mode == 'human':
            self.game.render()
        return self.game.board.copy()

    def get_board_state(self):
        """获取棋盘状态"""
        return self.game.board.copy()

    def get_snake_positions(self) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """获取蛇的位置"""
        state = self.game.get_state()
        return state['snake1'], state['snake2']
    
    def get_food_positions(self) -> List[Tuple[int, int]]:
        """获取食物位置"""
        state = self.game.get_state()
        return state['foods']
    
    def is_valid_move(self, action: Tuple[int, int]) -> bool:
        """检查移动是否有效"""
        return action in self.game.get_valid_actions()
    
    def get_game_info(self) -> Dict[str, Any]:
        """获取游戏信息"""
        info = self.game.get_game_info()
        info.update({
            'board_size': self.board_size,
            'initial_length': self.game.initial_length,
            'food_count': self.game.food_count,
            'snake1_length': len(self.game.snake1),
            'snake2_length': len(self.game.snake2),
            'alive1': self.game.alive1,
            'alive2': self.game.alive2
        })
        return info
    
    def clone(self):
        """克隆环境"""
        cloned_game = self.game.clone()
        cloned_env = SnakeEnv(self.board_size)
        cloned_env.game = cloned_game
        return cloned_env 
    
    def render(self, mode='human'):
        if mode != 'human':
            return
        
        # 获取游戏状态
        state = self.game.get_state()
        snake1 = state['snake1']  # 玩家1的蛇
        snake2 = state['snake2']  # 玩家2的蛇
        foods = state['foods']
        board_size = self.board_size
        
        # 打印游戏信息
        print(f"=== 贪吃蛇 (棋盘大小: {board_size}x{board_size}) ===")
        print(f"玩家蛇长度: {len(snake1)} | AI蛇长度: {len(snake2)} | 食物数量: {len(foods)}")
        print("控制: [W]上 [S]下 [A]左 [D]右")
        
        # 绘制顶部边界
        print("+" + "-" * (board_size * 2) + "+")
        
        # 绘制游戏区域
        for y in range(board_size):
            row = "|"
            for x in range(board_size):
                pos = (y, x)
                if pos == snake1[0]:  # 玩家蛇头
                    row += "●"  # 实心圆代表玩家蛇头
                elif pos in snake1[1:]:  # 玩家蛇身
                    row += "○"  # 空心圆代表玩家蛇身
                elif pos == snake2[0]:  # AI蛇头
                    row += "▲"  # 三角形代表AI蛇头
                elif pos in snake2[1:]:  # AI蛇身
                    row += "△"  # 空心三角形代表AI蛇身
                elif pos in foods:  # 食物
                    row += "★"
                else:  # 空地
                    row += " "
                row += " "  # 添加间距
            row += "|"
            print(row)
        
        # 绘制底部边界
        print("+" + "-" * (board_size * 2) + "+")
        
        # 游戏结束提示
        if not state['alive1'] or not state['alive2'] or self.game.is_terminal():
            print("\n游戏结束！按任意键退出...")
            input()
            raise KeyboardInterrupt