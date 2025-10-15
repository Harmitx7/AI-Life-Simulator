import pygame
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from typing import Dict, List, Tuple, Optional
import threading
import time
from datetime import datetime

from simulation import SimulationEngine
from agent import ActionType
from environment import LocationType, Weather

class PygameVisualizer:
    """Real-time visualization using Pygame"""
    
    def __init__(self, simulation: SimulationEngine, width: int = 1200, height: int = 800):
        self.simulation = simulation
        self.width = width
        self.height = height
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AI Life Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Colors
        self.colors = {
            'background': (240, 240, 240),
            'agent': (50, 150, 200),
            'location_home': (100, 200, 100),
            'location_work': (200, 150, 100),
            'location_restaurant': (200, 100, 100),
            'location_social': (150, 100, 200),
            'location_park': (100, 200, 150),
            'text': (50, 50, 50),
            'ui_background': (220, 220, 220),
            'ui_border': (150, 150, 150)
        }
        
        # Action colors
        self.action_colors = {
            ActionType.EAT: (255, 100, 100),
            ActionType.WORK: (100, 100, 255),
            ActionType.SLEEP: (100, 255, 100),
            ActionType.SOCIALIZE: (255, 255, 100),
            ActionType.IDLE: (150, 150, 150)
        }
        
        # Layout
        self.world_rect = pygame.Rect(10, 10, 600, 600)
        self.info_rect = pygame.Rect(630, 10, 560, 780)
        
        # Visualization state
        self.selected_agent = None
        self.show_connections = True
        self.show_needs = True
        self.running = True
        
        # Scale factors
        self.scale_x = self.world_rect.width / simulation.world_size[0]
        self.scale_y = self.world_rect.height / simulation.world_size[1]
    
    def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        x = int(world_pos[0] * self.scale_x + self.world_rect.x)
        y = int(world_pos[1] * self.scale_y + self.world_rect.y)
        return (x, y)
    
    def draw_locations(self):
        """Draw all locations in the world"""
        for location in self.simulation.environment.locations.values():
            screen_pos = self.world_to_screen(location.position)
            
            # Choose color based on location type
            if location.location_type == LocationType.HOME:
                color = self.colors['location_home']
            elif location.location_type == LocationType.WORKPLACE:
                color = self.colors['location_work']
            elif location.location_type == LocationType.RESTAURANT:
                color = self.colors['location_restaurant']
            elif location.location_type == LocationType.SOCIAL_AREA:
                color = self.colors['location_social']
            else:
                color = self.colors['location_park']
            
            # Draw location as rectangle
            size = max(20, min(50, location.capacity // 2))
            rect = pygame.Rect(screen_pos[0] - size//2, screen_pos[1] - size//2, size, size)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.colors['ui_border'], rect, 2)
            
            # Draw occupancy indicator
            if location.current_occupants:
                occupancy_ratio = len(location.current_occupants) / location.capacity
                indicator_height = int(size * occupancy_ratio)
                indicator_rect = pygame.Rect(
                    screen_pos[0] - size//2, 
                    screen_pos[1] + size//2 - indicator_height,
                    4, indicator_height
                )
                pygame.draw.rect(self.screen, (255, 0, 0), indicator_rect)
            
            # Draw location name
            text = self.small_font.render(location.name[:8], True, self.colors['text'])
            text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] + size//2 + 15))
            self.screen.blit(text, text_rect)
    
    def draw_agents(self):
        """Draw all agents"""
        for agent in self.simulation.agents:
            screen_pos = self.world_to_screen(agent.position)
            
            # Agent color based on current action
            color = self.action_colors.get(agent.current_action, self.colors['agent'])
            
            # Draw agent as circle
            radius = 8 if agent != self.selected_agent else 12
            pygame.draw.circle(self.screen, color, screen_pos, radius)
            pygame.draw.circle(self.screen, (0, 0, 0), screen_pos, radius, 2)
            
            # Draw agent name
            if agent == self.selected_agent or radius > 8:
                text = self.small_font.render(agent.name, True, self.colors['text'])
                text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - 20))
                self.screen.blit(text, text_rect)
            
            # Draw needs bars if enabled
            if self.show_needs:
                self.draw_agent_needs(agent, screen_pos)
    
    def draw_agent_needs(self, agent, screen_pos: Tuple[int, int]):
        """Draw agent's needs as small bars"""
        needs = ['hunger', 'energy', 'social', 'work_satisfaction']
        bar_width = 20
        bar_height = 3
        
        for i, need_name in enumerate(needs):
            need_value = agent.needs[need_name].value
            bar_x = screen_pos[0] - bar_width // 2
            bar_y = screen_pos[1] + 15 + i * (bar_height + 1)
            
            # Background bar
            bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            pygame.draw.rect(self.screen, (100, 100, 100), bg_rect)
            
            # Need level bar
            need_width = int(bar_width * need_value)
            if need_width > 0:
                need_rect = pygame.Rect(bar_x, bar_y, need_width, bar_height)
                color = (255, 0, 0) if need_value < 0.3 else (255, 255, 0) if need_value < 0.7 else (0, 255, 0)
                pygame.draw.rect(self.screen, color, need_rect)
    
    def draw_social_connections(self):
        """Draw social connections between agents"""
        if not self.show_connections:
            return
        
        for agent1_id, connections in self.simulation.environment.social_network.items():
            if agent1_id >= len(self.simulation.agents):
                continue
                
            agent1 = self.simulation.agents[agent1_id]
            pos1 = self.world_to_screen(agent1.position)
            
            for agent2_id, strength in connections.items():
                if agent2_id >= len(self.simulation.agents) or strength < 0.1:
                    continue
                
                agent2 = self.simulation.agents[agent2_id]
                pos2 = self.world_to_screen(agent2.position)
                
                # Draw connection line
                alpha = int(255 * min(strength, 1.0))
                color = (100, 100, 255, alpha)
                
                # Create surface for alpha blending
                line_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.line(line_surface, color, pos1, pos2, 2)
                self.screen.blit(line_surface, (0, 0))
    
    def draw_info_panel(self):
        """Draw information panel"""
        # Clear info area
        pygame.draw.rect(self.screen, self.colors['ui_background'], self.info_rect)
        pygame.draw.rect(self.screen, self.colors['ui_border'], self.info_rect, 2)
        
        y_offset = 20
        
        # Simulation info
        sim_time = f"Time: {self.simulation.stats['total_time']:.1f}"
        day_cycle = f"Day: {self.simulation.environment.day_cycle}"
        time_of_day = f"Time of Day: {self.simulation.environment.get_time_of_day():.2f}"
        
        for text in [sim_time, day_cycle, time_of_day]:
            surface = self.font.render(text, True, self.colors['text'])
            self.screen.blit(surface, (self.info_rect.x + 10, self.info_rect.y + y_offset))
            y_offset += 25
        
        y_offset += 10
        
        # Environment info
        env_state = self.simulation.environment.get_environment_state()
        env_info = [
            f"Weather: {env_state['environmental_factors']['weather']}",
            f"Temperature: {env_state['environmental_factors']['temperature']:.2f}",
            f"Crowding: {env_state['environmental_factors']['crowding']:.2f}",
            f"Active Events: {env_state['active_events']}"
        ]
        
        for text in env_info:
            surface = self.small_font.render(text, True, self.colors['text'])
            self.screen.blit(surface, (self.info_rect.x + 10, self.info_rect.y + y_offset))
            y_offset += 20
        
        y_offset += 15
        
        # Statistics
        stats_info = [
            f"Total Actions: {self.simulation.stats['total_actions']}",
            f"Social Interactions: {self.simulation.stats['social_interactions']}",
            f"Behavior Patterns: {self.simulation.stats['pattern_discoveries']}"
        ]
        
        for text in stats_info:
            surface = self.small_font.render(text, True, self.colors['text'])
            self.screen.blit(surface, (self.info_rect.x + 10, self.info_rect.y + y_offset))
            y_offset += 20
        
        y_offset += 15
        
        # Selected agent info
        if self.selected_agent:
            self.draw_selected_agent_info(y_offset)
        else:
            # Agent list
            surface = self.font.render("Agents (click to select):", True, self.colors['text'])
            self.screen.blit(surface, (self.info_rect.x + 10, self.info_rect.y + y_offset))
            y_offset += 30
            
            for i, agent in enumerate(self.simulation.agents[:15]):  # Show first 15 agents
                action_color = self.action_colors.get(agent.current_action, self.colors['text'])
                text = f"{agent.name}: {agent.current_action.value}"
                surface = self.small_font.render(text, True, action_color)
                self.screen.blit(surface, (self.info_rect.x + 20, self.info_rect.y + y_offset))
                y_offset += 18
    
    def draw_selected_agent_info(self, y_offset: int):
        """Draw detailed info for selected agent"""
        agent = self.selected_agent
        
        # Agent name and action
        surface = self.font.render(f"Selected: {agent.name}", True, self.colors['text'])
        self.screen.blit(surface, (self.info_rect.x + 10, self.info_rect.y + y_offset))
        y_offset += 25
        
        action_color = self.action_colors.get(agent.current_action, self.colors['text'])
        surface = self.small_font.render(f"Action: {agent.current_action.value}", True, action_color)
        self.screen.blit(surface, (self.info_rect.x + 10, self.info_rect.y + y_offset))
        y_offset += 20
        
        # Needs
        surface = self.small_font.render("Needs:", True, self.colors['text'])
        self.screen.blit(surface, (self.info_rect.x + 10, self.info_rect.y + y_offset))
        y_offset += 20
        
        for need_name, need in agent.needs.items():
            color = (255, 0, 0) if need.value < 0.3 else (255, 255, 0) if need.value < 0.7 else (0, 255, 0)
            text = f"  {need_name}: {need.value:.2f}"
            surface = self.small_font.render(text, True, color)
            self.screen.blit(surface, (self.info_rect.x + 10, self.info_rect.y + y_offset))
            y_offset += 18
        
        y_offset += 10
        
        # Personality
        surface = self.small_font.render("Personality:", True, self.colors['text'])
        self.screen.blit(surface, (self.info_rect.x + 10, self.info_rect.y + y_offset))
        y_offset += 20
        
        personality_traits = [
            f"  Openness: {agent.personality.openness:.2f}",
            f"  Conscientiousness: {agent.personality.conscientiousness:.2f}",
            f"  Extraversion: {agent.personality.extraversion:.2f}",
            f"  Agreeableness: {agent.personality.agreeableness:.2f}",
            f"  Neuroticism: {agent.personality.neuroticism:.2f}"
        ]
        
        for text in personality_traits:
            surface = self.small_font.render(text, True, self.colors['text'])
            self.screen.blit(surface, (self.info_rect.x + 10, self.info_rect.y + y_offset))
            y_offset += 16
        
        y_offset += 10
        
        # Habits
        surface = self.small_font.render("Habits:", True, self.colors['text'])
        self.screen.blit(surface, (self.info_rect.x + 10, self.info_rect.y + y_offset))
        y_offset += 20
        
        for action, habit in agent.habits.items():
            text = f"  {action.value}: {habit.strength:.2f}"
            surface = self.small_font.render(text, True, self.colors['text'])
            self.screen.blit(surface, (self.info_rect.x + 10, self.info_rect.y + y_offset))
            y_offset += 16
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click"""
        if self.world_rect.collidepoint(pos):
            # Click in world area - select agent
            world_pos = (
                (pos[0] - self.world_rect.x) / self.scale_x,
                (pos[1] - self.world_rect.y) / self.scale_y
            )
            
            # Find closest agent
            closest_agent = None
            min_distance = float('inf')
            
            for agent in self.simulation.agents:
                dx = agent.position[0] - world_pos[0]
                dy = agent.position[1] - world_pos[1]
                distance = np.sqrt(dx*dx + dy*dy)
                
                if distance < min_distance and distance < 5:  # Within 5 units
                    min_distance = distance
                    closest_agent = agent
            
            self.selected_agent = closest_agent
    
    def run(self):
        """Run the visualization"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.show_connections = not self.show_connections
                    elif event.key == pygame.K_n:
                        self.show_needs = not self.show_needs
                    elif event.key == pygame.K_SPACE:
                        if self.simulation.paused:
                            self.simulation.resume()
                        else:
                            self.simulation.pause()
                    elif event.key == pygame.K_ESCAPE:
                        self.selected_agent = None
            
            # Clear screen
            self.screen.fill(self.colors['background'])
            
            # Draw world border
            pygame.draw.rect(self.screen, self.colors['ui_border'], self.world_rect, 2)
            
            # Draw simulation elements
            self.draw_locations()
            self.draw_social_connections()
            self.draw_agents()
            self.draw_info_panel()
            
            # Draw controls
            controls = [
                "Controls:",
                "Click: Select agent",
                "C: Toggle connections",
                "N: Toggle needs",
                "Space: Pause/Resume",
                "Esc: Deselect"
            ]
            
            for i, text in enumerate(controls):
                color = self.colors['text'] if i > 0 else (0, 0, 0)
                surface = self.small_font.render(text, True, color)
                self.screen.blit(surface, (10, self.height - 120 + i * 18))
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()

def run_visualization(simulation: SimulationEngine):
    """Run visualization in a separate thread"""
    visualizer = PygameVisualizer(simulation)
    
    def viz_thread():
        visualizer.run()
    
    thread = threading.Thread(target=viz_thread)
    thread.daemon = True
    thread.start()
    return thread, visualizer

class MatplotlibAnalyzer:
    """Analysis and plotting using Matplotlib"""
    
    def __init__(self, simulation: SimulationEngine):
        self.simulation = simulation
    
    def plot_agent_satisfaction_over_time(self, agent_ids: Optional[List[int]] = None):
        """Plot agent satisfaction over time"""
        if not self.simulation.log_data:
            print("No log data available")
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        times = []
        satisfactions = {}
        
        for log_entry in self.simulation.log_data:
            times.append(log_entry['simulation_time'])
            
            for agent_state in log_entry['agent_states']:
                agent_id = agent_state['id']
                if agent_ids is None or agent_id in agent_ids:
                    if agent_id not in satisfactions:
                        satisfactions[agent_id] = []
                    
                    # Calculate satisfaction from needs
                    needs = agent_state['needs']
                    avg_satisfaction = sum(needs.values()) / len(needs)
                    satisfactions[agent_id].append(avg_satisfaction)
        
        # Plot satisfaction curves
        for agent_id, satisfaction_data in satisfactions.items():
            if len(satisfaction_data) == len(times):
                agent_name = f"Agent {agent_id}"
                if agent_id < len(self.simulation.agents):
                    agent_name = self.simulation.agents[agent_id].name
                ax.plot(times, satisfaction_data, label=agent_name, alpha=0.7)
        
        ax.set_xlabel('Simulation Time')
        ax.set_ylabel('Average Satisfaction')
        ax.set_title('Agent Satisfaction Over Time')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_action_distribution(self):
        """Plot distribution of actions taken by agents"""
        action_counts = {action.value: 0 for action in ActionType}
        
        for agent in self.simulation.agents:
            for action in agent.action_history:
                action_counts[action.value] += 1
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        actions = list(action_counts.keys())
        counts = list(action_counts.values())
        colors = [self.get_action_color(ActionType(action)) for action in actions]
        
        bars = ax.bar(actions, counts, color=colors, alpha=0.7)
        ax.set_xlabel('Actions')
        ax.set_ylabel('Count')
        ax.set_title('Distribution of Actions Taken')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def get_action_color(self, action: ActionType) -> str:
        """Get matplotlib color for action"""
        color_map = {
            ActionType.EAT: 'red',
            ActionType.WORK: 'blue',
            ActionType.SLEEP: 'green',
            ActionType.SOCIALIZE: 'orange',
            ActionType.IDLE: 'gray'
        }
        return color_map.get(action, 'black')
    
    def plot_social_network(self):
        """Plot social network graph"""
        try:
            import networkx as nx
        except ImportError:
            print("NetworkX required for social network visualization")
            return
        
        G = nx.Graph()
        
        # Add nodes (agents)
        for agent in self.simulation.agents:
            G.add_node(agent.id, name=agent.name)
        
        # Add edges (social connections)
        for agent1_id, connections in self.simulation.environment.social_network.items():
            for agent2_id, strength in connections.items():
                if strength > 0.1:  # Only show significant connections
                    G.add_edge(agent1_id, agent2_id, weight=strength)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Draw nodes
        node_colors = [self.simulation.agents[node].personality.extraversion 
                      for node in G.nodes() if node < len(self.simulation.agents)]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              cmap='viridis', node_size=300, alpha=0.8)
        
        # Draw edges
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        nx.draw_networkx_edges(G, pos, width=[w*3 for w in weights], 
                              alpha=0.6, edge_color='gray')
        
        # Draw labels
        labels = {node: self.simulation.agents[node].name 
                 for node in G.nodes() if node < len(self.simulation.agents)}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        ax.set_title('Social Network (Node color = Extraversion)')
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def generate_report(self) -> str:
        """Generate a text report of simulation results"""
        if not self.simulation.agents:
            return "No agents in simulation"
        
        report = []
        report.append("=== AI Life Simulation Report ===\n")
        
        # Basic stats
        report.append(f"Simulation Time: {self.simulation.stats['total_time']:.2f}")
        report.append(f"Number of Agents: {len(self.simulation.agents)}")
        report.append(f"Total Actions: {self.simulation.stats['total_actions']}")
        report.append(f"Social Interactions: {self.simulation.stats['social_interactions']}")
        report.append(f"Behavior Patterns Discovered: {self.simulation.stats['pattern_discoveries']}\n")
        
        # Agent summary
        report.append("=== Agent Summary ===")
        for agent in self.simulation.agents:
            avg_satisfaction = np.mean(agent.satisfaction_history) if agent.satisfaction_history else 0.5
            most_common_action = max(agent.action_history, key=agent.action_history.count) if agent.action_history else ActionType.IDLE
            
            report.append(f"{agent.name}:")
            report.append(f"  Average Satisfaction: {avg_satisfaction:.3f}")
            report.append(f"  Most Common Action: {most_common_action.value}")
            report.append(f"  Total Actions: {agent.total_actions}")
            report.append("")
        
        # Environment summary
        env_state = self.simulation.environment.get_environment_state()
        report.append("=== Environment Summary ===")
        report.append(f"Current Weather: {env_state['environmental_factors']['weather']}")
        report.append(f"Average Crowding: {env_state['environmental_factors']['crowding']:.3f}")
        report.append(f"Active Events: {env_state['active_events']}")
        report.append(f"Social Connections: {env_state['social_connections']}")
        
        return "\n".join(report)
