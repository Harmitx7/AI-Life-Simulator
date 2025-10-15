import numpy as np
import random
from typing import Dict, List, Tuple, Optional
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from agent import ActionType, VirtualHuman
import json

class BehaviorPattern:
    """Represents a learned behavior pattern"""
    def __init__(self, pattern_id: str, conditions: Dict, actions: List[ActionType], 
                 success_rate: float = 0.5, usage_count: int = 0):
        self.pattern_id = pattern_id
        self.conditions = conditions  # Environmental/internal conditions
        self.actions = actions  # Sequence of actions
        self.success_rate = success_rate
        self.usage_count = usage_count
        self.last_used = 0
        self.effectiveness_history = []
    
    def matches_conditions(self, agent_state: Dict, threshold: float = 0.8) -> bool:
        """Check if current state matches this pattern's conditions"""
        matches = 0
        total = 0
        
        for condition, expected_value in self.conditions.items():
            if condition in agent_state:
                current_value = agent_state[condition]
                if isinstance(expected_value, (int, float)):
                    # Numerical comparison with tolerance
                    if abs(current_value - expected_value) < 0.2:
                        matches += 1
                elif current_value == expected_value:
                    matches += 1
                total += 1
        
        return (matches / total) >= threshold if total > 0 else False
    
    def update_effectiveness(self, success: bool):
        """Update pattern effectiveness based on outcome"""
        self.usage_count += 1
        self.effectiveness_history.append(success)
        
        # Keep only recent history
        if len(self.effectiveness_history) > 20:
            self.effectiveness_history.pop(0)
        
        # Update success rate
        if self.effectiveness_history:
            self.success_rate = sum(self.effectiveness_history) / len(self.effectiveness_history)

class GenerativeBehaviorModel:
    """AI system that generates and evolves behavior patterns"""
    
    def __init__(self):
        self.patterns = {}  # pattern_id -> BehaviorPattern
        self.pattern_counter = 0
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        self.min_pattern_usage = 5  # Minimum usage before pattern is considered established
        
        # Clustering for pattern discovery
        self.scaler = StandardScaler()
        self.clusterer = None
        self.state_history = []
        
    def extract_agent_state_vector(self, agent: VirtualHuman) -> np.ndarray:
        """Extract numerical features from agent state for pattern analysis"""
        features = []
        
        # Needs
        for need_name, need in agent.needs.items():
            features.append(need.value)
        
        # Personality traits
        features.extend([
            agent.personality.openness,
            agent.personality.conscientiousness,
            agent.personality.extraversion,
            agent.personality.agreeableness,
            agent.personality.neuroticism
        ])
        
        # Time of day
        features.append(agent.get_time_of_day())
        
        # Current action (one-hot encoded)
        for action_type in ActionType:
            features.append(1.0 if agent.current_action == action_type else 0.0)
        
        # Habit strengths
        for action_type in [ActionType.EAT, ActionType.WORK, ActionType.SLEEP, ActionType.SOCIALIZE]:
            if action_type in agent.habits:
                features.append(agent.habits[action_type].strength)
            else:
                features.append(0.0)
        
        return np.array(features)
    
    def discover_patterns(self, agents: List[VirtualHuman]):
        """Discover new behavior patterns from agent data"""
        if len(agents) < 3:
            return
        
        # Collect state vectors from all agents
        state_vectors = []
        agent_actions = []
        
        for agent in agents:
            if len(agent.memory) > 5:
                state_vector = self.extract_agent_state_vector(agent)
                state_vectors.append(state_vector)
                
                # Get recent action sequence
                recent_actions = [m['action'] for m in agent.memory[-3:]]
                agent_actions.append(recent_actions)
        
        if len(state_vectors) < 3:
            return
        
        # Normalize state vectors
        state_vectors = np.array(state_vectors)
        if hasattr(self.scaler, 'mean_'):
            normalized_states = self.scaler.transform(state_vectors)
        else:
            normalized_states = self.scaler.fit_transform(state_vectors)
        
        # Cluster similar states
        n_clusters = min(5, len(state_vectors) // 2)
        if n_clusters >= 2:
            self.clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = self.clusterer.fit_predict(normalized_states)
            
            # Create patterns from clusters
            for cluster_id in range(n_clusters):
                cluster_indices = np.where(cluster_labels == cluster_id)[0]
                if len(cluster_indices) >= 2:
                    self._create_pattern_from_cluster(
                        cluster_id, 
                        [state_vectors[i] for i in cluster_indices],
                        [agent_actions[i] for i in cluster_indices]
                    )
    
    def _create_pattern_from_cluster(self, cluster_id: int, states: List[np.ndarray], 
                                   action_sequences: List[List[ActionType]]):
        """Create a behavior pattern from a cluster of similar states"""
        # Calculate average state conditions
        avg_state = np.mean(states, axis=0)
        
        # Extract meaningful conditions (needs and personality)
        conditions = {
            'hunger': float(avg_state[0]),
            'energy': float(avg_state[1]),
            'happiness': float(avg_state[2]),
            'social_need': float(avg_state[3]),
            'time_of_day': float(avg_state[9])  # Assuming time_of_day is at index 9
        }
        
        # Find most common action sequence
        action_counter = {}
        for seq in action_sequences:
            seq_key = tuple(seq)
            action_counter[seq_key] = action_counter.get(seq_key, 0) + 1
        
        if action_counter:
            most_common_seq = max(action_counter.keys(), key=action_counter.get)
            pattern_id = f"pattern_{self.pattern_counter}_{cluster_id}"
            self.pattern_counter += 1
            
            # Create new pattern
            new_pattern = BehaviorPattern(
                pattern_id=pattern_id,
                conditions=conditions,
                actions=list(most_common_seq),
                success_rate=0.5,
                usage_count=0
            )
            
            self.patterns[pattern_id] = new_pattern
    
    def suggest_action(self, agent: VirtualHuman) -> Optional[ActionType]:
        """Suggest an action based on learned patterns"""
        if random.random() < self.exploration_rate:
            return None  # Let agent explore
        
        # Get current agent state
        agent_state = {
            'hunger': agent.needs['hunger'].value,
            'energy': agent.needs['energy'].value,
            'social_need': agent.needs['social_need'].value,
            'happiness': agent.needs['happiness'].value,
            'time_of_day': agent.get_time_of_day()
        }
        
        # Find matching patterns
        matching_patterns = []
        for pattern in self.patterns.values():
            if (pattern.matches_conditions(agent_state) and 
                pattern.usage_count >= self.min_pattern_usage and
                pattern.success_rate > 0.6):
                matching_patterns.append(pattern)
        
        if not matching_patterns:
            return None
        
        # Select best pattern based on success rate and recency
        best_pattern = max(matching_patterns, 
                          key=lambda p: p.success_rate * (1.0 + 0.1 * (100 - p.last_used)))
        
        # Return first action from pattern
        if best_pattern.actions:
            best_pattern.last_used = 0  # Reset recency
            return best_pattern.actions[0]
        
        return None
    
    def update_pattern_effectiveness(self, agent: VirtualHuman, suggested_action: ActionType, 
                                   success: bool):
        """Update pattern effectiveness based on action outcome"""
        agent_state = {
            'hunger': agent.needs['hunger'].value,
            'energy': agent.needs['energy'].value,
            'social_need': agent.needs['social_need'].value,
            'happiness': agent.needs['happiness'].value,
            'time_of_day': agent.get_time_of_day()
        }
        
        # Find patterns that suggested this action
        for pattern in self.patterns.values():
            if (pattern.matches_conditions(agent_state) and 
                pattern.actions and pattern.actions[0] == suggested_action):
                pattern.update_effectiveness(success)
                break
    
    def evolve_patterns(self):
        """Evolve and prune patterns based on performance"""
        patterns_to_remove = []
        
        for pattern_id, pattern in self.patterns.items():
            # Age all patterns
            pattern.last_used += 1
            
            # Remove ineffective patterns
            if (pattern.usage_count >= self.min_pattern_usage * 2 and 
                pattern.success_rate < 0.3):
                patterns_to_remove.append(pattern_id)
            
            # Remove unused old patterns
            elif pattern.last_used > 100 and pattern.usage_count < self.min_pattern_usage:
                patterns_to_remove.append(pattern_id)
        
        # Remove patterns
        for pattern_id in patterns_to_remove:
            del self.patterns[pattern_id]
        
        # Mutate successful patterns
        self._mutate_successful_patterns()
    
    def _mutate_successful_patterns(self):
        """Create variations of successful patterns"""
        successful_patterns = [p for p in self.patterns.values() 
                             if p.success_rate > 0.8 and p.usage_count >= self.min_pattern_usage]
        
        for pattern in successful_patterns[:3]:  # Limit mutations
            if random.random() < 0.1:  # 10% chance to mutate
                self._create_pattern_mutation(pattern)
    
    def _create_pattern_mutation(self, original_pattern: BehaviorPattern):
        """Create a mutated version of a successful pattern"""
        # Slightly modify conditions
        new_conditions = original_pattern.conditions.copy()
        for key, value in new_conditions.items():
            if isinstance(value, (int, float)):
                new_conditions[key] = value + random.uniform(-0.1, 0.1)
                new_conditions[key] = max(0.0, min(1.0, new_conditions[key]))
        
        # Slightly modify action sequence
        new_actions = original_pattern.actions.copy()
        if len(new_actions) > 1 and random.random() < 0.3:
            # Swap two actions
            i, j = random.sample(range(len(new_actions)), 2)
            new_actions[i], new_actions[j] = new_actions[j], new_actions[i]
        
        # Create mutated pattern
        mutation_id = f"mutation_{self.pattern_counter}_{original_pattern.pattern_id}"
        self.pattern_counter += 1
        
        mutated_pattern = BehaviorPattern(
            pattern_id=mutation_id,
            conditions=new_conditions,
            actions=new_actions,
            success_rate=original_pattern.success_rate * 0.9,  # Slightly lower initial success
            usage_count=0
        )
        
        self.patterns[mutation_id] = mutated_pattern
    
    def get_pattern_statistics(self) -> Dict:
        """Get statistics about learned patterns"""
        if not self.patterns:
            return {'total_patterns': 0}
        
        success_rates = [p.success_rate for p in self.patterns.values()]
        usage_counts = [p.usage_count for p in self.patterns.values()]
        
        return {
            'total_patterns': len(self.patterns),
            'avg_success_rate': np.mean(success_rates),
            'avg_usage_count': np.mean(usage_counts),
            'established_patterns': len([p for p in self.patterns.values() 
                                       if p.usage_count >= self.min_pattern_usage]),
            'successful_patterns': len([p for p in self.patterns.values() 
                                      if p.success_rate > 0.7])
        }
    
    def save_patterns(self, filename: str):
        """Save learned patterns to file"""
        pattern_data = {}
        for pattern_id, pattern in self.patterns.items():
            pattern_data[pattern_id] = {
                'conditions': pattern.conditions,
                'actions': [action.value for action in pattern.actions],
                'success_rate': pattern.success_rate,
                'usage_count': pattern.usage_count,
                'effectiveness_history': pattern.effectiveness_history
            }
        
        with open(filename, 'w') as f:
            json.dump(pattern_data, f, indent=2)
    
    def load_patterns(self, filename: str):
        """Load patterns from file"""
        try:
            with open(filename, 'r') as f:
                pattern_data = json.load(f)
            
            for pattern_id, data in pattern_data.items():
                actions = [ActionType(action_str) for action_str in data['actions']]
                pattern = BehaviorPattern(
                    pattern_id=pattern_id,
                    conditions=data['conditions'],
                    actions=actions,
                    success_rate=data['success_rate'],
                    usage_count=data['usage_count']
                )
                pattern.effectiveness_history = data.get('effectiveness_history', [])
                self.patterns[pattern_id] = pattern
                
        except FileNotFoundError:
            pass  # No existing patterns to load
