import random
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import time

class ActionType(Enum):
    EAT = "eat"
    WORK = "work"
    SLEEP = "sleep"
    SOCIALIZE = "socialize"
    IDLE = "idle"

@dataclass
class Need:
    value: float  # 0.0 to 100.0 (changed to match PRD)
    decay_rate: float
    satisfaction_threshold: float = 30.0
    
    def update(self, dt: float):
        """Decay the need over time"""
        self.value = max(0.0, self.value - self.decay_rate * dt)
    
    def satisfy(self, amount: float):
        """Satisfy the need by a certain amount"""
        self.value = min(100.0, self.value + amount)
    
    def is_critical(self) -> bool:
        return self.value > self.satisfaction_threshold  # Higher values = more need

@dataclass
class PersonalityTrait:
    # PRD specified traits
    discipline: float = 0.5  # Maps to conscientiousness
    sociability: float = 0.5  # Maps to extraversion
    ambition: float = 0.5
    creativity: float = 0.5
    # Keep original Big Five for compatibility
    openness: float = 0.5
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5

class Habit:
    def __init__(self, action: ActionType, strength: float = 0.1, time_preference: float = 0.5):
        self.action = action
        self.strength = strength  # 0.0 to 1.0
        self.time_preference = time_preference  # 0.0 (morning) to 1.0 (night)
        self.success_count = 0
        self.total_attempts = 0
    
    def reinforce(self, success: bool):
        """Reinforce or weaken the habit based on outcome"""
        self.total_attempts += 1
        if success:
            self.success_count += 1
            self.strength = min(1.0, self.strength + 0.01)
        else:
            self.strength = max(0.0, self.strength - 0.005)
    
    def get_success_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.5
        return self.success_count / self.total_attempts

class VirtualHuman:
    def __init__(self, agent_id: int, name: str = None):
        self.id = agent_id
        self.name = name or f"Agent_{agent_id}"
        
        # Basic needs (PRD format: 0-100 scale)
        self.needs = {
            'hunger': Need(random.uniform(20, 50), 2.0),  # Increases over time
            'energy': Need(random.uniform(60, 90), 1.5),  # Decreases over time
            'happiness': Need(random.uniform(40, 70), 0.8),
            'social_need': Need(random.uniform(20, 50), 1.0)
        }
        
        # Additional PRD state variables
        self.money = random.uniform(100, 500)
        self.mood = random.uniform(0.3, 0.7)  # 0-1 scale
        
        # Personality traits (PRD + Big Five model)
        discipline = random.uniform(0.2, 0.8)
        sociability = random.uniform(0.2, 0.8)
        self.personality = PersonalityTrait(
            discipline=discipline,
            sociability=sociability,
            ambition=random.uniform(0.2, 0.8),
            creativity=random.uniform(0.2, 0.8),
            openness=random.uniform(0.2, 0.8),
            conscientiousness=discipline,  # Map discipline to conscientiousness
            extraversion=sociability,  # Map sociability to extraversion
            agreeableness=random.uniform(0.2, 0.8),
            neuroticism=random.uniform(0.2, 0.8)
        )
        
        # Habits - learned behaviors
        self.habits = {
            ActionType.EAT: Habit(ActionType.EAT, random.uniform(0.1, 0.3)),
            ActionType.WORK: Habit(ActionType.WORK, random.uniform(0.1, 0.3)),
            ActionType.SLEEP: Habit(ActionType.SLEEP, random.uniform(0.1, 0.3)),
            ActionType.SOCIALIZE: Habit(ActionType.SOCIALIZE, random.uniform(0.1, 0.3))
        }
        
        # Current state
        self.current_action = ActionType.IDLE
        self.action_duration = 0.0
        self.position = (random.uniform(0, 100), random.uniform(0, 100))
        self.energy_level = random.uniform(0.5, 1.0)
        
        # Memory and learning
        # PRD Decision weights for utility maximization
        self.decision_weights = {
            'need_urgency': 0.4,
            'habit_strength': 0.2,
            'personality': 0.2,
            'money_factor': 0.1,
            'mood_factor': 0.1
        }
        
        # Reinforcement learning parameters
        self.learning_rate = 0.1
        self.action_rewards = {action: 0.0 for action in ActionType}
        self.action_counts = {action: 0 for action in ActionType}
        
        # Memory and learning
        self.memory = []
        
        # Statistics
        self.total_actions = 0
        self.action_history = []
        self.satisfaction_history = []
    
    def update_needs(self, dt: float):
        """Update all needs based on time passage (PRD format)"""
        # Hunger increases over time
        self.needs['hunger'].value = min(100, self.needs['hunger'].value + self.needs['hunger'].decay_rate * dt)
        
        # Energy decreases over time (except when sleeping)
        if self.current_action != ActionType.SLEEP:
            self.needs['energy'].value = max(0, self.needs['energy'].value - self.needs['energy'].decay_rate * dt)
        
        # Social need increases over time
        self.needs['social_need'].value = min(100, self.needs['social_need'].value + self.needs['social_need'].decay_rate * dt)
        
        # Happiness decays slowly
        self.needs['happiness'].value = max(0, self.needs['happiness'].value - self.needs['happiness'].decay_rate * dt)
        
        # Update mood based on overall satisfaction
        overall_satisfaction = (100 - self.needs['hunger'].value + self.needs['energy'].value + 
                              100 - self.needs['social_need'].value + self.needs['happiness'].value) / 400
        self.mood = 0.7 * self.mood + 0.3 * overall_satisfaction
    
    def get_time_of_day(self) -> float:
        """Get current time as fraction of day (0.0 = midnight, 0.5 = noon)"""
        return (time.time() % 86400) / 86400
    
    def calculate_action_utility(self, action: ActionType) -> float:
        """PRD-compliant utility maximization for decision making"""
        utility = 0.0
        
        # Need-based utility (PRD format: higher need values = more urgent)
        if action == ActionType.EAT:
            utility += (self.needs['hunger'].value / 100.0) * 3.0  # Urgent when hungry
            utility -= self.money * 0.001  # Cost consideration
        elif action == ActionType.SLEEP:
            utility += ((100 - self.needs['energy'].value) / 100.0) * 2.5  # Urgent when tired
        elif action == ActionType.SOCIALIZE:
            utility += (self.needs['social_need'].value / 100.0) * self.personality.sociability * 2.0
            utility -= self.money * 0.0005  # Small cost for socializing
        elif action == ActionType.WORK:
            utility += self.personality.ambition * 1.5  # Ambitious agents work more
            utility += (1.0 if self.money < 200 else 0.5)  # Work more when poor
            utility -= ((100 - self.needs['energy'].value) / 100.0) * 0.5  # Less likely when tired
        
        # Habit influence (learned behavior)
        if action in self.habits:
            habit = self.habits[action]
            time_of_day = self.get_time_of_day()
            time_match = 1.0 - abs(time_of_day - habit.time_preference)
            utility += habit.strength * time_match * self.decision_weights['habit_strength'] * 5.0
        
        # Personality modifiers (PRD traits)
        if action == ActionType.SOCIALIZE:
            utility *= (0.3 + self.personality.sociability * 0.7)
        elif action == ActionType.WORK:
            utility *= (0.3 + self.personality.discipline * 0.7)
        elif action == ActionType.EAT:
            utility *= (0.5 + self.personality.discipline * 0.5)  # Disciplined eating
        
        # Mood influence
        utility *= (0.7 + self.mood * 0.6)
        
        # Reinforcement learning component
        if self.action_counts[action] > 0:
            avg_reward = self.action_rewards[action] / self.action_counts[action]
            utility += avg_reward * 0.5
        
        # Add controlled randomness
        utility += random.uniform(-0.3, 0.3)
        
        return max(0.0, utility)
    
    def decide_action(self) -> ActionType:
        """Decide what action to take based on current state"""
        # Calculate utilities for all possible actions
        action_utilities = {}
        for action in ActionType:
            if action != ActionType.IDLE:
                action_utilities[action] = self.calculate_action_utility(action)
        
        # Add idle as low-utility option
        action_utilities[ActionType.IDLE] = 0.1
        
        # Choose action based on utilities (softmax selection)
        actions = list(action_utilities.keys())
        utilities = list(action_utilities.values())
        
        # Convert to probabilities using softmax
        exp_utilities = np.exp(np.array(utilities) * 3.0)  # Temperature parameter
        probabilities = exp_utilities / np.sum(exp_utilities)
        
        # Select action
        chosen_action = np.random.choice(actions, p=probabilities)
        return chosen_action
    
    def perform_action(self, action: ActionType, dt: float) -> bool:
        """PRD-compliant action performance with rewards and costs"""
        success = True
        reward = 0.0
        cost = 0.0
        
        if action == ActionType.EAT:
            if self.needs['hunger'].value > 10 and self.money >= 5:
                # Reduce hunger, cost money, gain happiness
                hunger_reduction = min(30 * dt, self.needs['hunger'].value)
                self.needs['hunger'].value -= hunger_reduction
                self.needs['happiness'].value = min(100, self.needs['happiness'].value + 5 * dt)
                cost = 5 * dt
                self.money -= cost
                reward = hunger_reduction * 0.1
            else:
                success = False
        
        elif action == ActionType.SLEEP:
            if self.needs['energy'].value < 90:
                # Restore energy, reduce social need slightly
                energy_gain = min(40 * dt, 100 - self.needs['energy'].value)
                self.needs['energy'].value += energy_gain
                self.needs['social_need'].value = min(100, self.needs['social_need'].value + 2 * dt)
                reward = energy_gain * 0.05
            else:
                success = False
        
        elif action == ActionType.SOCIALIZE:
            if self.needs['social_need'].value > 5 and self.money >= 3:
                # Reduce social need, cost money, gain happiness
                social_reduction = min(25 * dt, self.needs['social_need'].value)
                self.needs['social_need'].value -= social_reduction
                self.needs['happiness'].value = min(100, self.needs['happiness'].value + 8 * dt)
                cost = 3 * dt
                self.money -= cost
                reward = social_reduction * 0.08 + self.personality.sociability * 0.1
            else:
                success = False
        
        elif action == ActionType.WORK:
            if self.needs['energy'].value > 20:
                # Earn money, reduce energy and happiness, increase hunger
                money_earned = (10 + self.personality.ambition * 5) * dt
                self.money += money_earned
                self.needs['energy'].value = max(0, self.needs['energy'].value - 15 * dt)
                self.needs['hunger'].value = min(100, self.needs['hunger'].value + 8 * dt)
                self.needs['happiness'].value = max(0, self.needs['happiness'].value - 3 * dt)
                reward = money_earned * 0.02 + self.personality.ambition * 0.1
            else:
                success = False
        
        # Update mood based on action success and happiness
        if success:
            self.mood = min(1.0, self.mood + 0.02)
        else:
            self.mood = max(0.0, self.mood - 0.05)
        
        # Reinforcement learning update
        self.action_counts[action] += 1
        if success:
            self.action_rewards[action] += reward
            # Adjust decision weights based on success
            if reward > 0.5:
                self.decision_weights['habit_strength'] = min(0.5, self.decision_weights['habit_strength'] + 0.01)
        else:
            self.action_rewards[action] -= 0.1
        
        # Update habit strength based on success
        if action in self.habits:
            self.habits[action].reinforce(success)
        
        # Record action in memory with PRD format
        self.memory.append({
            'action': action,
            'success': success,
            'reward': reward,
            'cost': cost,
            'timestamp': time.time(),
            'needs_state': {k: v.value for k, v in self.needs.items()},
            'money': self.money,
            'mood': self.mood
        })
        
        # Limit memory size
        if len(self.memory) > 100:
            self.memory.pop(0)
        
        return success
    
    def update(self, dt: float):
        """Update agent state"""
        # Update needs
        self.update_needs(dt)
        
        # Decide and perform action
        if self.action_duration <= 0:
            new_action = self.decide_action()
            self.current_action = new_action
            self.action_duration = random.uniform(1.0, 3.0)  # Action lasts 1-3 time units
            
            # Perform the action
            success = self.perform_action(new_action, dt)
            self.total_actions += 1
            self.action_history.append(new_action)
            
            # Calculate overall satisfaction
            satisfaction = sum(need.value for need in self.needs.values()) / len(self.needs)
            self.satisfaction_history.append(satisfaction)
        
        self.action_duration -= dt
    
    def get_status(self) -> Dict:
        """Get current status of the agent (PRD format)"""
        return {
            'id': self.id,
            'name': self.name,
            'current_action': self.current_action.value,
            'needs': {k: v.value for k, v in self.needs.items()},
            'money': self.money,
            'mood': self.mood,
            'personality': {
                'discipline': self.personality.discipline,
                'sociability': self.personality.sociability,
                'ambition': self.personality.ambition,
                'creativity': self.personality.creativity,
                # Keep original for compatibility
                'openness': self.personality.openness,
                'conscientiousness': self.personality.conscientiousness,
                'extraversion': self.personality.extraversion,
                'agreeableness': self.personality.agreeableness,
                'neuroticism': self.personality.neuroticism
            },
            'habits': {k.value: {'strength': v.strength, 'success_rate': v.get_success_rate()} 
                      for k, v in self.habits.items()},
            'position': self.position,
            'total_actions': self.total_actions,
            'avg_satisfaction': np.mean(self.satisfaction_history) if self.satisfaction_history else 50.0,
            'decision_weights': self.decision_weights.copy(),
            'action_rewards': {k.value: v for k, v in self.action_rewards.items()}
        }
    
    def evolve_behavior(self):
        """Evolve behavior patterns based on recent experiences"""
        if len(self.memory) < 10:
            return
        
        # Analyze recent performance
        recent_memory = self.memory[-20:]
        action_performance = {}
        
        for memory in recent_memory:
            action = memory['action']
            if action not in action_performance:
                action_performance[action] = {'successes': 0, 'attempts': 0, 'satisfaction': 0}
            
            action_performance[action]['attempts'] += 1
            if memory['success']:
                action_performance[action]['successes'] += 1
            action_performance[action]['satisfaction'] += memory['satisfaction_gain']
        
        # Adjust decision weights based on performance
        for action, perf in action_performance.items():
            if perf['attempts'] > 0:
                success_rate = perf['successes'] / perf['attempts']
                avg_satisfaction = perf['satisfaction'] / perf['attempts']
                
                # Adjust habit strength based on performance
                if action in self.habits:
                    if success_rate > 0.7 and avg_satisfaction > 0.1:
                        self.habits[action].strength = min(1.0, self.habits[action].strength + 0.02)
                    elif success_rate < 0.3 or avg_satisfaction < 0.05:
                        self.habits[action].strength = max(0.0, self.habits[action].strength - 0.01)
