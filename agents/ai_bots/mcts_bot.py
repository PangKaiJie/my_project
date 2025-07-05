"""
MCTS Bot
使用蒙特卡洛树搜索算法
"""

import time
import random
import math
from typing import Dict, List, Tuple, Any, Optional
from agents.base_agent import BaseAgent
import config
import copy


class MCTSNode:
    """MCTS节点"""
    
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.untried_actions = self._get_untried_actions()
    
    def _get_untried_actions(self):
        """获取未尝试的动作"""
        if hasattr(self.state, 'get_valid_actions'):
            return self.state.get_valid_actions()
        return []
    
    def is_fully_expanded(self):
        """检查是否完全展开"""
        return len(self.untried_actions) == 0
    
    def is_terminal(self):
        """检查是否为终止节点"""
        if hasattr(self.state, 'is_terminal'):
            return self.state.is_terminal()
        return False
    
    def get_winner(self):
        """获取获胜者"""
        if hasattr(self.state, 'get_winner'):
            return self.state.get_winner()
        return None
    
    def clone_state(self):
        """克隆状态"""
        if hasattr(self.state, 'clone'):
            return self.state.clone()
        return self.state


class MCTSBot(BaseAgent):
    """MCTS Bot"""
    
    def __init__(self, name: str = "MCTSBot", player_id: int = 1, 
             simulation_count: int = 100, exploration_weight: float = 1.414):
        super().__init__(name, player_id)
        self.simulation_count = simulation_count
        self.exploration_weight = exploration_weight  # 初始化探索权重
        
        # 从配置获取参数
        ai_config = config.AI_CONFIGS.get('mcts', {})
        self.simulation_count = ai_config.get('simulation_count', simulation_count)
        self.timeout = ai_config.get('timeout', 10)
        self.exploration_weight = ai_config.get('exploration_weight', exploration_weight)  # 允许配置覆盖
        
    def get_action(self, observation: Any, env: Any) -> Any:
        """完整的MCTS流程"""
        root = MCTSNode(env.game.clone())
        
        for _ in range(self.simulation_count):
            node = root
            # 1. 选择
            while not node.is_terminal() and node.is_fully_expanded():
                node = self._select_child(node)
            
            # 2. 扩展
            if not node.is_terminal() and not node.is_fully_expanded():
                node = self._expand(node)
            
            # 3. 模拟
            result = self.simulate(node.clone_state())
            
            # 4. 回传
            self._backpropagate(node, result)
        
        # 选择访问次数最多的动作
        best_action = max(root.children, key=lambda x: x.visits).action
        return best_action
    
    def simulate(self, game, first_action=None):
        """改进的随机模拟策略"""
        if first_action is not None:
            game.step(first_action)
        
        while not game.is_terminal():
            valid_actions = game.get_valid_actions()
            if not valid_actions:
                break
            
            # 启发式：优先选择靠近已有棋子的位置（示例）
            if random.random() < 0.7:  # 70%概率使用启发式
                action = self._heuristic_action(game, valid_actions)
            else:
                action = random.choice(valid_actions)
            game.step(action)
        
        winner = game.get_winner()
        if winner == self.player_id:
            return 1
        elif winner is not None:
            return -1
        else:
            return 0

    def _heuristic_action(self, game, valid_actions):
        """启发式动作选择（示例：优先选择靠近对手棋子的位置）"""
        # 实现可根据具体游戏调整
        return random.choice(valid_actions)
    
    def reset(self):
        """重置MCTS Bot"""
        super().reset()
    
    def get_info(self) -> Dict[str, Any]:
        """获取MCTS Bot信息"""
        info = super().get_info()
        info.update({
            'type': 'MCTS',
            'description': '使用蒙特卡洛树搜索的Bot',
            'strategy': f'MCTS with {self.simulation_count} simulations',
            'timeout': self.timeout
        })
        return info 
    
    def _select_child(self, node:MCTSNode) -> MCTSNode:
        "使用UCB1选择最佳子节点"
        best_child = None
        best_score = -float('inf')

        for child in node.children:
            if child.visits == 0:
                return child # 优先选择未访问的节点
            # 添加node.visits非零检查
            if node.visits == 0:
                return child  # 父节点未访问过，直接返回子节点
            
            # UCB1公式: score = (value / visits) + C * sqrt(ln(parent_visits) / visits)
            exploitation = child.value / child.visits
            exploration = math.sqrt(2 * math.log(node.visits) / child.visits)
            score = exploitation + self.exploration_weight * exploration
            
            if score > best_score:
                best_score = score
                best_child = child
        
        return best_child if best_child is not None else random.choice(node.children)
    
    def _expand(self, node: MCTSNode) -> MCTSNode:
        """扩展节点：从未尝试的动作中选择一个并创建子节点"""
        if not node.untried_actions:
            return node  # 无未尝试动作，直接返回
        
        action = node.untried_actions.pop()
        new_state = node.clone_state()
        new_state.step(action)  # 执行动作
        child_node = MCTSNode(new_state, parent=node, action=action)
        node.children.append(child_node)
        return child_node
    
    def _backpropagate(self, node: MCTSNode, result: float):
        """反向传播模拟结果"""
        while node is not None:
            node.visits += 1
            node.value += result if node.parent is None or node.parent.state.current_player == self.player_id else -result
            node = node.parent