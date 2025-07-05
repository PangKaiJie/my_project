from agents.base_agent import BaseAgent
import copy
import time

class MinimaxBot(BaseAgent):
    def __init__(self, name="MinimaxBot", player_id=1, max_depth=2):
        super().__init__(name, player_id)
        self.max_depth = max_depth
        self.time_limit = 60

    def evaluate(self, game):
        # 检查是否已胜利
        if game.get_winner() == self.player_id:
            return float('inf')
        elif game.get_winner() is not None:
            return float('-inf')
        
        #定义棋型权重
        weights = {
            "five":5,
            "live_four":4,
            "rush_four":3,
            "live_three":2,
            "live_two":1
        }

        score = 0
        board = game.board
        size = board.shape[0]

        for row in range(size):
            for col in range(size):
                if board[row, col] == self.player_id:
                    # 检查己方棋型
                    score += self._count_patterns(board, row, col, self.player_id, weights)
                elif board[row, col] != 0:
                    # 检查对方棋型
                    score -= self._count_patterns(board, row, col, 3-self.player_id, weights)
        
        return score
    
    def _count_patterns(self, board, row, col, player_id, weights):
        # 统计单个位置的棋型贡献
        directions = [(1, 0), (1, 1), (0, 1), (1, -1)]
        point_score = 0
        size = board.shape[0]

        for dx, dy in directions:
            count, open_ends = self._count_consecutive(board, row, col, dx, dy, player_id, size)
            
            if count >= 5:
                point_score += weights['five']
            elif count == 4 and open_ends >=1:
                point_score += weights['live_four']
            elif count == 4:
                point_score += weights['rush_four']
            elif count == 3 and open_ends >=2:
                point_score += weights['live_three']
            elif count == 2 and open_ends >=2:
                point_score += weights['live_two']
            
        return point_score
    
    def _count_consecutive(self, board, row, col, dx, dy, player_id, size):
        # 统计连续棋子和开放端点
        count = 1
        open_ends = 0

        #正向检测
        x, y = row + dx, col + dy
        while 0 <= x <size and 0 <= y < size and board[x, y] == player_id:
            count += 1
            x += dx
            y += dy
        if 0 <= x < size and 0 <= y < size and board[x, y] == 0:
            open_ends += 1
        
        #正向检测
        x, y = row - dx, col - dy
        while 0 <= x <size and 0 <= y < size and board[x, y] == player_id:
            count += 1
            x -= dx
            y -= dy
        if 0 <= x < size and 0 <= y < size and board[x, y] == 0:
            open_ends += 1

        return count, open_ends

    """
    def evaluate(self, game):
        # 极简评估函数：只检查胜负和棋子数量
        winner = game.get_winner()
        if winner == self.player_id:
            return float('inf')
        elif winner is not None:
            return float('-inf')
        
        # 仅计算己方棋子数量
        return (game.board == self.player_id).sum()
    """

    def get_action(self, observation, env):
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            return None

        start_time = time.time()    
        best_score = float('-inf')
        best_action = valid_actions[0]
        
        for action in valid_actions:
            # 超时检查
            if time.time() - start_time > self.time_limit:
                print("Time out! Return current best action.")
                break

            # 克隆游戏状态
            game_copy = env.game.clone()
            # 执行动作
            game_copy.step(action)
            # 计算分数
            score = self.minimax(game_copy, self.max_depth - 1, False)
            
            if score > best_score:
                best_score = score
                best_action = action
        print(f"Total time: {time.time() - start_time:.2f}s")        
        return best_action

    def minimax(self, game, depth, maximizing, alpha=float('-inf'), beta=float('inf'), start_time=None):
        # 初始化时间记录
        if start_time is None:
            start_time = time.time()
        # 超时检查
        if time.time() - start_time > self.time_limit:
            return 0  
        
        if depth == 0 or game.is_terminal():
            return self.evaluate(game)
        
        valid_actions = game.get_valid_actions()
        if not valid_actions:
            return 0
            
        if maximizing:
            max_score = float('-inf')
            for action in valid_actions:
                game_copy = game.clone()
                game_copy.step(action)
                score = self.minimax(game_copy, depth - 1, False, alpha, beta)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return max_score
        else:
            min_score = float('inf')
            for action in valid_actions:
                game_copy = game.clone()
                game_copy.step(action)
                score = self.minimax(game_copy, depth - 1, True, alpha, beta)
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return min_score 