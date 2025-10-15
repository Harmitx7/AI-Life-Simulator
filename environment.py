import random
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import time

class LocationType(Enum):
    HOME = "home"
    WORKPLACE = "workplace"
    RESTAURANT = "restaurant"
    SOCIAL_AREA = "social_area"
    PARK = "park"

@dataclass
class Location:
    name: str
    location_type: LocationType
    position: Tuple[float, float]
    capacity: int
    current_occupants: List[int]  # Agent IDs
    amenities: List[str]
    comfort_level: float = 0.5
    
    def can_accommodate(self, agent_id: int) -> bool:
        return len(self.current_occupants) < self.capacity
    
    def add_occupant(self, agent_id: int):
        if self.can_accommodate(agent_id) and agent_id not in self.current_occupants:
            self.current_occupants.append(agent_id)
    
    def remove_occupant(self, agent_id: int):
        if agent_id in self.current_occupants:
            self.current_occupants.remove(agent_id)

class Weather(Enum):
    SUNNY = "sunny"
    RAINY = "rainy"
    CLOUDY = "cloudy"
    STORMY = "stormy"

@dataclass
class EnvironmentalFactors:
    weather: Weather
    temperature: float  # 0.0 (cold) to 1.0 (hot)
    noise_level: float  # 0.0 (quiet) to 1.0 (loud)
    crowding: float     # 0.0 (empty) to 1.0 (crowded)
    
    def get_comfort_modifier(self) -> float:
        """Calculate comfort modifier based on environmental factors"""
        comfort = 0.5
        
        # Weather effects
        if self.weather == Weather.SUNNY:
            comfort += 0.1
        elif self.weather == Weather.STORMY:
            comfort -= 0.2
        elif self.weather == Weather.RAINY:
            comfort -= 0.1
        
        # Temperature effects (optimal around 0.5)
        temp_deviation = abs(self.temperature - 0.5)
        comfort -= temp_deviation * 0.3
        
        # Noise and crowding effects
        comfort -= self.noise_level * 0.2
        comfort -= self.crowding * 0.15
        
        return max(0.0, min(1.0, comfort))

class SimulationEnvironment:
    """The world in which virtual humans live and interact"""
    
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.time_step = 0
        self.day_cycle = 0  # Days since simulation start
        
        # PRD: 24-hour clock system
        self.current_hour = 8.0  # Start at 8 AM
        self.hours_per_time_step = 0.1  # Each time step = 6 minutes
        
        # Environmental state
        self.environmental_factors = EnvironmentalFactors(
            weather=Weather.SUNNY,
            temperature=0.6,
            noise_level=0.3,
            crowding=0.2
        )
        
        # Locations in the world
        self.locations = {}
        self._create_default_locations()
        
        # Global resources and constraints
        self.resources = {
            'food_availability': 1.0,
            'job_availability': 0.8,
            'social_events': 0.6
        }
        
        # Social network - tracks relationships between agents
        self.social_network = {}
        
        # Event system
        self.active_events = []
        self.event_history = []
        
        # Statistics
        self.global_stats = {
            'total_interactions': 0,
            'avg_happiness': 0.5,
            'resource_consumption': 0.0
        }
    
    def _create_default_locations(self):
        """Create default locations in the environment"""
        locations_data = [
            ("Home District", LocationType.HOME, (20, 20), 50, ["bed", "kitchen", "bathroom"]),
            ("Office Complex", LocationType.WORKPLACE, (80, 30), 30, ["desk", "meeting_room", "coffee_machine"]),
            ("Central Restaurant", LocationType.RESTAURANT, (50, 50), 20, ["food", "seating", "kitchen"]),
            ("Community Center", LocationType.SOCIAL_AREA, (30, 70), 40, ["games", "events", "seating"]),
            ("City Park", LocationType.PARK, (70, 80), 100, ["benches", "playground", "nature"]),
            ("Cafe Corner", LocationType.RESTAURANT, (40, 30), 15, ["coffee", "wifi", "quiet"]),
            ("Sports Club", LocationType.SOCIAL_AREA, (60, 20), 25, ["gym", "courts", "lockers"]),
            ("Library", LocationType.SOCIAL_AREA, (25, 45), 35, ["books", "quiet", "study_areas"])
        ]
        
        for name, loc_type, pos, capacity, amenities in locations_data:
            location = Location(
                name=name,
                location_type=loc_type,
                position=pos,
                capacity=capacity,
                current_occupants=[],
                amenities=amenities,
                comfort_level=random.uniform(0.4, 0.9)
            )
            self.locations[name] = location
    
    def get_time_of_day(self) -> float:
        """Get current time as fraction of day (0.0 = midnight, 0.5 = noon)"""
        return (self.current_hour % 24) / 24.0
    
    def get_current_hour(self) -> float:
        """Get current hour (0-24)"""
        return self.current_hour % 24
    
    def is_work_hours(self) -> bool:
        """Check if it's work hours (9 AM to 5 PM)"""
        hour = self.get_current_hour()
        return 9 <= hour <= 17
    
    def is_sleep_time(self) -> bool:
        """Check if it's typical sleep time (10 PM to 6 AM)"""
        hour = self.get_current_hour()
        return hour >= 22 or hour <= 6
    
    def is_day_time(self) -> bool:
        """Check if it's daytime (6 AM to 8 PM)"""
        hour = self.get_current_hour()
        return 6 <= hour <= 20
    
    def update_environmental_factors(self):
        """Update environmental conditions"""
        # Weather changes
        if random.random() < 0.05:  # 5% chance per time step
            self.environmental_factors.weather = random.choice(list(Weather))
        
        # Temperature varies with time of day and weather
        time_of_day = self.get_time_of_day()
        base_temp = 0.3 + 0.4 * (1 + np.sin(2 * np.pi * time_of_day - np.pi/2)) / 2
        
        if self.environmental_factors.weather == Weather.SUNNY:
            base_temp += 0.1
        elif self.environmental_factors.weather == Weather.RAINY:
            base_temp -= 0.1
        elif self.environmental_factors.weather == Weather.STORMY:
            base_temp -= 0.2
        
        self.environmental_factors.temperature = max(0.0, min(1.0, base_temp))
        
        # Noise level varies with time and crowding
        hour = self.get_current_hour()
        if self.is_day_time():
            # Peak noise during work hours
            if self.is_work_hours():
                self.environmental_factors.noise_level = 0.4 + 0.5 * self.environmental_factors.crowding
            else:
                self.environmental_factors.noise_level = 0.3 + 0.4 * self.environmental_factors.crowding
        else:
            self.environmental_factors.noise_level = 0.1 + 0.2 * self.environmental_factors.crowding
        
        # Update crowding based on total occupancy
        total_occupants = sum(len(loc.current_occupants) for loc in self.locations.values())
        total_capacity = sum(loc.capacity for loc in self.locations.values())
        self.environmental_factors.crowding = total_occupants / total_capacity if total_capacity > 0 else 0
    
    def find_suitable_location(self, agent_id: int, preferred_type: LocationType, 
                             current_position: Tuple[float, float]) -> Optional[Location]:
        """Find a suitable location for an agent"""
        suitable_locations = [
            loc for loc in self.locations.values()
            if (loc.location_type == preferred_type and 
                loc.can_accommodate(agent_id))
        ]
        
        if not suitable_locations:
            return None
        
        # Choose closest available location
        def distance(loc):
            dx = loc.position[0] - current_position[0]
            dy = loc.position[1] - current_position[1]
            return np.sqrt(dx*dx + dy*dy)
        
        return min(suitable_locations, key=distance)
    
    def move_agent_to_location(self, agent_id: int, location_name: str, 
                             current_location: Optional[str] = None):
        """Move an agent to a new location"""
        # Remove from current location
        if current_location and current_location in self.locations:
            self.locations[current_location].remove_occupant(agent_id)
        
        # Add to new location
        if location_name in self.locations:
            self.locations[location_name].add_occupant(agent_id)
            return True
        
        return False
    
    def get_social_opportunities(self, agent_id: int, location_name: str) -> List[int]:
        """Get list of other agents at the same location for social interaction"""
        if location_name not in self.locations:
            return []
        
        location = self.locations[location_name]
        return [occupant for occupant in location.current_occupants if occupant != agent_id]
    
    def create_social_connection(self, agent1_id: int, agent2_id: int, strength: float = 0.1):
        """Create or strengthen social connection between two agents"""
        if agent1_id not in self.social_network:
            self.social_network[agent1_id] = {}
        if agent2_id not in self.social_network:
            self.social_network[agent2_id] = {}
        
        # Update connection strength
        current_strength1 = self.social_network[agent1_id].get(agent2_id, 0.0)
        current_strength2 = self.social_network[agent2_id].get(agent1_id, 0.0)
        
        self.social_network[agent1_id][agent2_id] = min(1.0, current_strength1 + strength)
        self.social_network[agent2_id][agent1_id] = min(1.0, current_strength2 + strength)
        
        self.global_stats['total_interactions'] += 1
    
    def get_social_connections(self, agent_id: int) -> Dict[int, float]:
        """Get all social connections for an agent"""
        return self.social_network.get(agent_id, {})
    
    def spawn_random_event(self):
        """Spawn random events that affect the environment"""
        if random.random() < 0.02:  # 2% chance per time step
            event_types = [
                "festival", "storm", "market_day", "construction", 
                "celebration", "maintenance", "concert"
            ]
            
            event = {
                'type': random.choice(event_types),
                'location': random.choice(list(self.locations.keys())),
                'duration': random.randint(3, 10),
                'effect': random.uniform(-0.3, 0.5),
                'start_time': self.time_step
            }
            
            self.active_events.append(event)
    
    def update_events(self):
        """Update active events and remove expired ones"""
        active_events = []
        
        for event in self.active_events:
            if self.time_step - event['start_time'] < event['duration']:
                active_events.append(event)
                
                # Apply event effects
                if event['location'] in self.locations:
                    location = self.locations[event['location']]
                    location.comfort_level = max(0.0, min(1.0, 
                        location.comfort_level + event['effect'] * 0.1))
            else:
                # Event ended, add to history
                self.event_history.append(event)
        
        self.active_events = active_events
    
    def update_resources(self):
        """Update global resource availability"""
        # Food availability varies with time and events
        base_food = 0.8 + 0.2 * np.sin(2 * np.pi * self.get_time_of_day())
        
        # Events can affect resources
        for event in self.active_events:
            if event['type'] == 'market_day':
                base_food += 0.2
            elif event['type'] == 'storm':
                base_food -= 0.3
        
        self.resources['food_availability'] = max(0.1, min(1.0, base_food))
        
        # Job availability is more stable but can be affected by events
        job_modifier = 0.0
        for event in self.active_events:
            if event['type'] == 'construction':
                job_modifier += 0.1
            elif event['type'] == 'storm':
                job_modifier -= 0.2
        
        self.resources['job_availability'] = max(0.1, min(1.0, 0.8 + job_modifier))
        
        # Social events availability
        social_base = 0.6
        if self.is_day_time():
            social_base += 0.2
        
        for event in self.active_events:
            if event['type'] in ['festival', 'celebration', 'concert']:
                social_base += 0.3
        
        self.resources['social_events'] = max(0.0, min(1.0, social_base))
    
    def get_zone_effects(self, location_name: str) -> Dict[str, float]:
        """PRD: Get zone-based effects on agent states"""
        if location_name not in self.locations:
            return {}
        
        location = self.locations[location_name]
        effects = {}
        
        # Zone effects based on PRD specification
        if location.location_type == LocationType.HOME:
            effects = {
                'energy_gain': 15.0,  # Rest at home
                'happiness_gain': 2.0,
                'money_cost': 0.0
            }
        elif location.location_type == LocationType.WORKPLACE:
            effects = {
                'money_gain': 12.0 + (3.0 if self.is_work_hours() else 1.0),
                'energy_loss': 10.0,
                'happiness_loss': 2.0,
                'hunger_gain': 5.0
            }
        elif location.location_type == LocationType.RESTAURANT:
            effects = {
                'hunger_reduction': 25.0,
                'happiness_gain': 5.0,
                'social_gain': 3.0,
                'money_cost': 8.0
            }
        elif location.location_type == LocationType.SOCIAL_AREA:
            effects = {
                'social_reduction': 20.0,
                'happiness_gain': 8.0,
                'money_cost': 4.0
            }
        elif location.location_type == LocationType.PARK:
            effects = {
                'happiness_gain': 6.0,
                'social_reduction': 5.0,
                'energy_gain': 3.0,
                'money_cost': 0.0
            }
        
        # Apply environmental modifiers
        comfort_mod = self.environmental_factors.get_comfort_modifier()
        for key, value in effects.items():
            if 'gain' in key or 'reduction' in key:
                effects[key] = value * comfort_mod
        
        return effects

    def calculate_location_attractiveness(self, location_name: str, agent_needs: Dict) -> float:
        """Calculate how attractive a location is for an agent based on their needs"""
        if location_name not in self.locations:
            return 0.0

        location = self.locations[location_name]
        attractiveness = location.comfort_level

        # PRD: Location type matches needs (using 0-100 scale)
        if location.location_type == LocationType.RESTAURANT and agent_needs.get('hunger', 0) > 70:
            attractiveness += 0.8
        elif location.location_type == LocationType.HOME and agent_needs.get('energy', 100) < 30:
            attractiveness += 0.7
        elif location.location_type == LocationType.WORKPLACE and self.is_work_hours():
            attractiveness += 0.6
        elif location.location_type == LocationType.SOCIAL_AREA and agent_needs.get('social_need', 0) > 60:
            attractiveness += 0.5

        # Environmental factors
        attractiveness *= self.environmental_factors.get_comfort_modifier()

        # Crowding penalty
        occupancy_ratio = len(location.current_occupants) / location.capacity
        attractiveness *= (1.0 - 0.3 * occupancy_ratio)

        # Active events at location
        for event in self.active_events:
            if event['location'] == location_name:
                attractiveness += event['effect']

        return max(0.0, attractiveness)
    
    def update(self, dt: float):
        """Update the environment state"""
        self.time_step += dt
        
        # Update 24-hour clock
        self.current_hour += self.hours_per_time_step * dt
        
        # Check for new day
        if int(self.current_hour) // 24 > self.day_cycle:
            self.day_cycle = int(self.current_hour) // 24
        
        # Update various systems
        self.update_environmental_factors()
        self.spawn_random_event()
        self.update_events()
        self.update_resources()
        
        # Decay social connections over time
        for agent_connections in self.social_network.values():
            for other_agent in agent_connections:
                agent_connections[other_agent] *= 0.999  # Slow decay
    
    def get_environment_state(self) -> Dict:
        """Get current environment state for monitoring"""
        return {
            'time_step': self.time_step,
            'day_cycle': self.day_cycle,
            'time_of_day': self.get_time_of_day(),
            'environmental_factors': {
                'weather': self.environmental_factors.weather.value,
                'temperature': self.environmental_factors.temperature,
                'noise_level': self.environmental_factors.noise_level,
                'crowding': self.environmental_factors.crowding,
                'comfort_modifier': self.environmental_factors.get_comfort_modifier()
            },
            'resources': self.resources.copy(),
            'active_events': len(self.active_events),
            'locations': {
                name: {
                    'type': loc.location_type.value,
                    'occupants': len(loc.current_occupants),
                    'capacity': loc.capacity,
                    'comfort': loc.comfort_level
                }
                for name, loc in self.locations.items()
            },
            'social_connections': len(self.social_network),
            'global_stats': self.global_stats.copy()
        }
