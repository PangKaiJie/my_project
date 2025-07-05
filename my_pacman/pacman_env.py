import pygame
import gym
from gym import spaces
import numpy as np
from .main import PacmanGame

class PacmanEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        super(PacmanEnv, self).__init__()
        self.game = PacmanGame()
        self.action_space = spaces.Discrete(4)  # Up, Down, Left, Right
        self.observation_space = spaces.Box(
            low=0, high=255,
            shape=(self.game.screen.get_height(), self.game.screen.get_width(), 3),
            dtype=np.uint8
        )
    
    def step(self, action):
        # Map action to direction
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        self.game.pacman.set_direction(directions[action])
        
        # Update game state
        self.game.update()
        
        # Get observation
        obs = self._get_obs()
        
        # Calculate reward
        reward = self.game.pacman.score
        
        # Check if episode is done
        done = self.game.game_over or self.game.game_won
        
        # Additional info
        info = {
            'lives': self.game.pacman.lives,
            'powered_up': self.game.pacman.powered_up
        }
        
        return obs, reward, done, info
    
    def reset(self):
        self.game.__init__()
        return self._get_obs()
    
    def render(self, mode='human'):
        self.game.draw()
        if mode == 'human':
            pygame.display.flip()
    
    def close(self):
        pygame.quit()
    
    def _get_obs(self):
        # Return the current screen as observation
        return pygame.surfarray.array3d(self.game.screen)