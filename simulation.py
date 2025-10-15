import time
import random
import numpy as np
from typing import Dict, List, Optional, Callable, Tuple
import threading
import json
from datetime import datetime

from agent import VirtualHuman, ActionType
from environment import SimulationEnvironment, LocationType
from behavior_model import GenerativeBehaviorModel
from metrics import EvaluationMetrics

class SimulationEngine:
    """Main simulation engine that orchestrates the AI life simulation"""
    
    def __init__(self, num_agents: int = 10, world_size: Tuple[int, int] = (100, 100)):
        self.num_agents = num_agents
        self.world_size = world_size
        
        # Core components
        self.environment = SimulationEnvironment(world_size[0], world_size[1])
        self.behavior_model = GenerativeBehaviorModel()
        self.agents = []
        
        # PRD: Evaluation metrics system
        self.metrics = EvaluationMetrics()
        
        # Simulation state
        self.running = False
        self.paused = False
        self.simulation_speed = 1.0
        self.time_step = 0.1  # Time step in simulation time units
        self.real_time_factor = 1.0  # 1.0 = real time, 10.0 = 10x speed
        
        # Statistics and monitoring
        self.stats = {
            'total_time': 0.0,
            'total_actions': 0,
            'agent_satisfaction': [],
            'pattern_discoveries': 0,
            'social_interactions': 0
        }
        
        # PRD: Performance tracking
        self.step_start_time = 0.0
        
        # Event callbacks
        self.event_callbacks = {
            'agent_action': [],
            'pattern_discovered': [],
            'social_interaction': [],
            'simulation_update': []
        }
        
        # Data logging
        self.log_data = []
        self.log_interval = 10  # Log every 10 time steps
        self.last_log_time = 0
        
        # Initialize agents
        self._create_agents()
        
        # Load existing patterns if available
        self.behavior_model.load_patterns('behavior_patterns.json')
    
    def _create_agents(self):
        """Create initial population of virtual humans"""
        self.agents = []
        
        # Generate diverse names
        first_names = ["Alex", "Sam", "Jordan", "Casey", "Riley", "Avery", "Quinn", "Blake", 
                      "Taylor", "Morgan", "Sage", "River", "Phoenix", "Rowan", "Skylar"]
        
        for i in range(self.num_agents):
            name = f"{random.choice(first_names)}_{i+1}"
            agent = VirtualHuman(i, name)
            
            # Assign random starting location
            home_locations = [name for name, loc in self.environment.locations.items() 
                            if loc.location_type == LocationType.HOME]
            if home_locations:
                start_location = random.choice(home_locations)
                self.environment.move_agent_to_location(i, start_location)
                agent.position = self.environment.locations[start_location].position
            
            self.agents.append(agent)
    
    def add_event_callback(self, event_type: str, callback: Callable):
        """Add callback for simulation events"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    def trigger_event(self, event_type: str, data: Dict):
        """Trigger event callbacks"""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in event callback: {e}")
    
    def update_agent_locations(self):
        """Update agent locations based on their actions"""
        for agent in self.agents:
            current_location = None
            
            # Find agent's current location
            for loc_name, location in self.environment.locations.items():
                if agent.id in location.current_occupants:
                    current_location = loc_name
                    break
            
            # Determine if agent should move based on action
            target_location = None
            
            if agent.current_action == ActionType.EAT:
                # Look for restaurant
                target_location = self.environment.find_suitable_location(
                    agent.id, LocationType.RESTAURANT, agent.position)
            
            elif agent.current_action == ActionType.WORK:
                # Look for workplace
                target_location = self.environment.find_suitable_location(
                    agent.id, LocationType.WORKPLACE, agent.position)
            
            elif agent.current_action == ActionType.SLEEP:
                # Look for home
                target_location = self.environment.find_suitable_location(
                    agent.id, LocationType.HOME, agent.position)
            
            elif agent.current_action == ActionType.SOCIALIZE:
                # Look for social area
                target_location = self.environment.find_suitable_location(
                    agent.id, LocationType.SOCIAL_AREA, agent.position)
            
            # Move agent if needed
            if target_location and target_location.name != current_location:
                success = self.environment.move_agent_to_location(
                    agent.id, target_location.name, current_location)
                if success:
                    agent.position = target_location.position
    
    def process_social_interactions(self):
        """Process social interactions between agents at same locations"""
        for location in self.environment.locations.values():
            if len(location.current_occupants) > 1:
                # Agents at same location can interact
                for i, agent1_id in enumerate(location.current_occupants):
                    for agent2_id in location.current_occupants[i+1:]:
                        agent1 = self.agents[agent1_id]
                        agent2 = self.agents[agent2_id]
                        
                        # Check if agents want to socialize
                        if (agent1.current_action == ActionType.SOCIALIZE or 
                            agent2.current_action == ActionType.SOCIALIZE):
                            
                            # Calculate interaction probability based on personality
                            interaction_prob = (
                                (agent1.personality.extraversion + agent2.personality.extraversion) / 2 *
                                (agent1.personality.agreeableness + agent2.personality.agreeableness) / 2
                            )
                            
                            if random.random() < interaction_prob * 0.3:  # Base 30% chance
                                # Social interaction occurs
                                self.environment.create_social_connection(agent1_id, agent2_id, 0.05)
                                
                                # Both agents get social satisfaction
                                agent1.needs['social'].satisfy(0.1)
                                agent2.needs['social'].satisfy(0.1)
                                
                                self.stats['social_interactions'] += 1
                                
                                # Trigger event
                                self.trigger_event('social_interaction', {
                                    'agent1': agent1.name,
                                    'agent2': agent2.name,
                                    'location': location.name,
                                    'time': self.stats['total_time']
                                })
    
    def apply_behavior_model_suggestions(self):
        """Apply AI behavior model suggestions to agents"""
        for agent in self.agents:
            # Get suggestion from behavior model
            suggested_action = self.behavior_model.suggest_action(agent)
            
            if suggested_action:
                # Override agent's natural decision with AI suggestion
                old_action = agent.current_action
                agent.current_action = suggested_action
                agent.action_duration = random.uniform(1.0, 3.0)
                
                # Perform the action
                success = self.perform_action(suggested_action, self.time_step)
                agent.total_actions += 1
                agent.action_history.append(suggested_action)
                
                # PRD: Record action in metrics
                reward = agent.memory[-1]['reward'] if agent.memory else 0.0
                self.metrics.record_agent_action(agent, suggested_action, success, reward)
                
                # Update behavior model with outcome
                self.behavior_model.update_pattern_effectiveness(agent, suggested_action, success)
                
                # Log AI intervention
                if old_action != suggested_action:
                    self.trigger_event('agent_action', {
                        'agent': agent.name,
                        'action': suggested_action.value,
                        'ai_suggested': True,
                        'success': success,
                        'time': self.stats['total_time']
                    })
    
    def update_simulation_statistics(self):
        """Update simulation statistics"""
        # Calculate average satisfaction
        if self.agents:
            satisfactions = []
            for agent in self.agents:
                satisfaction = sum(need.value for need in agent.needs.values()) / len(agent.needs)
                satisfactions.append(satisfaction)
            
            self.stats['agent_satisfaction'] = satisfactions
            avg_satisfaction = np.mean(satisfactions)
            self.environment.global_stats['avg_happiness'] = avg_satisfaction
        
        # Count total actions
        total_actions = sum(agent.total_actions for agent in self.agents)
        self.stats['total_actions'] = total_actions
        
        # Update behavior model statistics
        pattern_stats = self.behavior_model.get_pattern_statistics()
        self.stats['pattern_discoveries'] = pattern_stats.get('total_patterns', 0)
    
    def log_simulation_data(self):
        """Log simulation data for analysis"""
        if self.stats['total_time'] - self.last_log_time >= self.log_interval:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'simulation_time': self.stats['total_time'],
                'environment_state': self.environment.get_environment_state(),
                'agent_states': [agent.get_status() for agent in self.agents],
                'behavior_patterns': self.behavior_model.get_pattern_statistics(),
                'simulation_stats': self.stats.copy()
            }
            
            self.log_data.append(log_entry)
            self.last_log_time = self.stats['total_time']
            
            # Keep only recent log entries to manage memory
            if len(self.log_data) > 1000:
                self.log_data = self.log_data[-500:]
    
    def step(self):
        """Execute one simulation step"""
        if self.paused:
            return
        
        # PRD: Track computational efficiency
        self.step_start_time = time.time()
        
        # Update environment
        self.environment.update(self.time_step)
        
        # Update all agents
        for agent in self.agents:
            old_action_count = agent.total_actions
            agent.update(self.time_step)
            
            # Check if agent performed a new action
            if agent.total_actions > old_action_count and agent.memory:
                # Record action in metrics
                last_memory = agent.memory[-1]
                self.metrics.record_agent_action(
                    agent, 
                    last_memory['action'], 
                    last_memory['success'], 
                    last_memory['reward']
                )
            
            # Trigger agent action event
            self.trigger_event('agent_action', {
                'agent': agent.name,
                'action': agent.current_action.value,
                'ai_suggested': False,
                'time': self.stats['total_time']
            })
        
        # Update agent locations based on actions
        self.update_agent_locations()
        
        # Process social interactions
        self.process_social_interactions()
        
        # Apply AI behavior model suggestions
        self.apply_behavior_model_suggestions()
        
        # Evolve agent behaviors
        for agent in self.agents:
            if random.random() < 0.1:  # 10% chance per step
                agent.evolve_behavior()
        
        # Discover and evolve behavior patterns
        if int(self.stats['total_time']) % 50 == 0:  # Every 50 time units
            old_pattern_count = len(self.behavior_model.patterns)
            self.behavior_model.discover_patterns(self.agents)
            new_pattern_count = len(self.behavior_model.patterns)
            
            if new_pattern_count > old_pattern_count:
                self.trigger_event('pattern_discovered', {
                    'new_patterns': new_pattern_count - old_pattern_count,
                    'total_patterns': new_pattern_count,
                    'time': self.stats['total_time']
                })
        
        if int(self.stats['total_time']) % 100 == 0:  # Every 100 time units
            self.behavior_model.evolve_patterns()
        
        # Update statistics
        self.update_simulation_statistics()
        
        # Log data
        self.log_simulation_data()
        
        # Update time
        self.stats['total_time'] += self.time_step
        
        # PRD: Update evaluation metrics
        frame_time = time.time() - self.step_start_time
        if int(self.stats['total_time']) % 10 == 0:  # Every 10 time units
            metrics_snapshot = self.metrics.update_metrics(self, frame_time)
        
        # Trigger simulation update event
        self.trigger_event('simulation_update', {
            'time': self.stats['total_time'],
            'stats': self.stats.copy()
        })
    
    def run(self, max_time: Optional[float] = None):
        """Run the simulation"""
        self.running = True
        start_time = time.time()
        
        print(f"Starting AI Life Simulation with {self.num_agents} agents...")
        
        try:
            while self.running:
                if not self.paused:
                    self.step()
                    
                    # Check if max time reached
                    if max_time and self.stats['total_time'] >= max_time:
                        break
                
                # Control simulation speed
                if self.real_time_factor > 0:
                    time.sleep(self.time_step / self.real_time_factor)
                
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user")
        
        finally:
            self.running = False
            
            # Save behavior patterns
            self.behavior_model.save_patterns('behavior_patterns.json')
            
            # Save simulation log
            self.save_log_data('simulation_log.json')
            
            # PRD: Save metrics and generate report
            self.metrics.export_metrics_csv('simulation_metrics.csv')
            print("\n" + self.metrics.generate_report())
            
            elapsed_time = time.time() - start_time
            print(f"\nSimulation completed:")
            print(f"  Real time: {elapsed_time:.2f} seconds")
            print(f"  Simulation time: {self.stats['total_time']:.2f} units")
            print(f"  Total actions: {self.stats['total_actions']}")
            print(f"  Social interactions: {self.stats['social_interactions']}")
            print(f"  Behavior patterns discovered: {self.stats['pattern_discoveries']}")
    
    def pause(self):
        """Pause the simulation"""
        self.paused = True
    
    def resume(self):
        """Resume the simulation"""
        self.paused = False
    
    def stop(self):
        """Stop the simulation"""
        self.running = False
    
    def set_speed(self, speed_factor: float):
        """Set simulation speed (1.0 = real time, higher = faster)"""
        self.real_time_factor = max(0.1, speed_factor)
    
    def get_agent_by_id(self, agent_id: int) -> Optional[VirtualHuman]:
        """Get agent by ID"""
        if 0 <= agent_id < len(self.agents):
            return self.agents[agent_id]
        return None
    
    def get_agent_by_name(self, name: str) -> Optional[VirtualHuman]:
        """Get agent by name"""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
    
    def get_simulation_state(self) -> Dict:
        """Get complete simulation state"""
        return {
            'running': self.running,
            'paused': self.paused,
            'time': self.stats['total_time'],
            'agents': [agent.get_status() for agent in self.agents],
            'environment': self.environment.get_environment_state(),
            'behavior_model': self.behavior_model.get_pattern_statistics(),
            'statistics': self.stats.copy(),
            'prd_metrics': self.metrics.get_metrics_summary()
        }
    
    def save_log_data(self, filename: str):
        """Save simulation log data to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.log_data, f, indent=2)
            print(f"Simulation log saved to {filename}")
        except Exception as e:
            print(f"Error saving log data: {e}")
    
    def load_log_data(self, filename: str):
        """Load simulation log data from file"""
        try:
            with open(filename, 'r') as f:
                self.log_data = json.load(f)
            print(f"Simulation log loaded from {filename}")
        except FileNotFoundError:
            print(f"Log file {filename} not found")
        except Exception as e:
            print(f"Error loading log data: {e}")

# Utility function to run simulation in separate thread
def run_simulation_async(simulation: SimulationEngine, max_time: Optional[float] = None):
    """Run simulation in a separate thread"""
    thread = threading.Thread(target=simulation.run, args=(max_time,))
    thread.daemon = True
    thread.start()
    return thread
