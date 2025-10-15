#!/usr/bin/env python3
"""
PRD Evaluation Metrics System
Tracks and analyzes simulation performance according to PRD requirements
"""

import numpy as np
import sqlite3
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from agent import VirtualHuman, ActionType

@dataclass
class MetricSnapshot:
    timestamp: float
    simulation_time: float
    avg_happiness: float
    decision_diversity: float
    computational_efficiency: float
    emergent_patterns: int
    agent_count: int

class EvaluationMetrics:
    """PRD-compliant evaluation metrics system"""
    
    def __init__(self, db_path: str = "simulation_metrics.db"):
        self.db_path = db_path
        self.snapshots = []
        self.init_database()
        
        # Metrics tracking
        self.start_time = datetime.now()
        self.frame_times = []
        self.decision_history = []
        
    def init_database(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                simulation_time REAL,
                avg_happiness REAL,
                decision_diversity REAL,
                computational_efficiency REAL,
                emergent_patterns INTEGER,
                agent_count INTEGER,
                raw_data TEXT
            )
        ''')
        
        # Create agent actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                agent_id INTEGER,
                agent_name TEXT,
                action TEXT,
                success BOOLEAN,
                reward REAL,
                needs_state TEXT,
                money REAL,
                mood REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def calculate_avg_happiness(self, agents: List[VirtualHuman]) -> float:
        """PRD Metric 1: Average happiness over time (global well-being)"""
        if not agents:
            return 0.0
        
        happiness_values = []
        for agent in agents:
            # Calculate happiness from needs (PRD format: 0-100)
            happiness = agent.needs['happiness'].value
            # Factor in other needs for overall well-being
            energy_factor = agent.needs['energy'].value / 100.0
            hunger_factor = (100 - agent.needs['hunger'].value) / 100.0
            social_factor = (100 - agent.needs['social_need'].value) / 100.0
            
            overall_happiness = (happiness + energy_factor * 20 + hunger_factor * 15 + social_factor * 10) / 100.0
            happiness_values.append(overall_happiness)
        
        return np.mean(happiness_values)
    
    def calculate_decision_diversity(self, agents: List[VirtualHuman]) -> float:
        """PRD Metric 2: Diversity of decisions across agents"""
        if not agents:
            return 0.0
        
        # Count action distribution
        action_counts = {action: 0 for action in ActionType}
        total_actions = 0
        
        for agent in agents:
            for action in agent.action_history[-10:]:  # Last 10 actions
                action_counts[action] += 1
                total_actions += 1
        
        if total_actions == 0:
            return 0.0
        
        # Calculate Shannon entropy for diversity
        probabilities = [count / total_actions for count in action_counts.values() if count > 0]
        if len(probabilities) <= 1:
            return 0.0
        
        entropy = -sum(p * np.log2(p) for p in probabilities)
        max_entropy = np.log2(len(ActionType))
        
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def calculate_computational_efficiency(self, frame_time: float) -> float:
        """PRD Metric 3: Computational efficiency (FPS, iteration time)"""
        self.frame_times.append(frame_time)
        
        # Keep only recent frame times
        if len(self.frame_times) > 100:
            self.frame_times = self.frame_times[-50:]
        
        if not self.frame_times:
            return 0.0
        
        avg_frame_time = np.mean(self.frame_times)
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
        
        # Normalize to 0-1 scale (60 FPS = 1.0, 1 FPS = 0.0)
        return min(1.0, fps / 60.0)
    
    def detect_emergent_patterns(self, agents: List[VirtualHuman]) -> int:
        """PRD Metric 4: Emergence of complex behavior patterns"""
        patterns_detected = 0
        
        for agent in agents:
            if len(agent.memory) < 20:
                continue
            
            # Look for repeated action sequences
            recent_actions = [m['action'] for m in agent.memory[-20:]]
            
            # Check for 3-action patterns
            for i in range(len(recent_actions) - 5):
                pattern = recent_actions[i:i+3]
                
                # Count occurrences of this pattern
                occurrences = 0
                for j in range(i+3, len(recent_actions) - 2):
                    if recent_actions[j:j+3] == pattern:
                        occurrences += 1
                
                # If pattern repeats 2+ times, it's emergent
                if occurrences >= 2:
                    patterns_detected += 1
                    break  # One pattern per agent max
        
        return patterns_detected
    
    def record_agent_action(self, agent: VirtualHuman, action: ActionType, success: bool, reward: float):
        """Record individual agent action for detailed analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agent_actions 
            (timestamp, agent_id, agent_name, action, success, reward, needs_state, money, mood)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().timestamp(),
            agent.id,
            agent.name,
            action.value,
            success,
            reward,
            json.dumps({k: v.value for k, v in agent.needs.items()}),
            agent.money,
            agent.mood
        ))
        
        conn.commit()
        conn.close()
    
    def update_metrics(self, simulation, frame_time: float):
        """Update all metrics and store snapshot"""
        agents = simulation.agents
        
        # Calculate all metrics
        avg_happiness = self.calculate_avg_happiness(agents)
        decision_diversity = self.calculate_decision_diversity(agents)
        computational_efficiency = self.calculate_computational_efficiency(frame_time)
        emergent_patterns = self.detect_emergent_patterns(agents)
        
        # Create snapshot
        snapshot = MetricSnapshot(
            timestamp=datetime.now().timestamp(),
            simulation_time=simulation.stats['total_time'],
            avg_happiness=avg_happiness,
            decision_diversity=decision_diversity,
            computational_efficiency=computational_efficiency,
            emergent_patterns=emergent_patterns,
            agent_count=len(agents)
        )
        
        self.snapshots.append(snapshot)
        
        # Store in database
        self.store_snapshot(snapshot, simulation)
        
        return snapshot
    
    def store_snapshot(self, snapshot: MetricSnapshot, simulation):
        """Store metrics snapshot in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Prepare raw data
        raw_data = {
            'agents': [agent.get_status() for agent in simulation.agents],
            'environment': simulation.environment.get_environment_state(),
            'behavior_patterns': simulation.behavior_model.get_pattern_statistics()
        }
        
        cursor.execute('''
            INSERT INTO metrics 
            (timestamp, simulation_time, avg_happiness, decision_diversity, 
             computational_efficiency, emergent_patterns, agent_count, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            snapshot.timestamp,
            snapshot.simulation_time,
            snapshot.avg_happiness,
            snapshot.decision_diversity,
            snapshot.computational_efficiency,
            snapshot.emergent_patterns,
            snapshot.agent_count,
            json.dumps(raw_data)
        ))
        
        conn.commit()
        conn.close()
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of all metrics"""
        if not self.snapshots:
            return {}
        
        recent_snapshots = self.snapshots[-10:]  # Last 10 snapshots
        
        return {
            'avg_happiness': {
                'current': recent_snapshots[-1].avg_happiness,
                'trend': np.mean([s.avg_happiness for s in recent_snapshots]),
                'min': min(s.avg_happiness for s in self.snapshots),
                'max': max(s.avg_happiness for s in self.snapshots)
            },
            'decision_diversity': {
                'current': recent_snapshots[-1].decision_diversity,
                'trend': np.mean([s.decision_diversity for s in recent_snapshots]),
                'min': min(s.decision_diversity for s in self.snapshots),
                'max': max(s.decision_diversity for s in self.snapshots)
            },
            'computational_efficiency': {
                'current': recent_snapshots[-1].computational_efficiency,
                'trend': np.mean([s.computational_efficiency for s in recent_snapshots]),
                'avg_fps': 1.0 / np.mean(self.frame_times) if self.frame_times else 0.0
            },
            'emergent_patterns': {
                'current': recent_snapshots[-1].emergent_patterns,
                'total_detected': sum(s.emergent_patterns for s in self.snapshots),
                'peak': max(s.emergent_patterns for s in self.snapshots)
            },
            'simulation_health': {
                'uptime': (datetime.now() - self.start_time).total_seconds(),
                'total_snapshots': len(self.snapshots),
                'agent_count': recent_snapshots[-1].agent_count
            }
        }
    
    def export_metrics_csv(self, filename: str):
        """Export metrics to CSV for analysis"""
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'simulation_time', 'avg_happiness', 
                         'decision_diversity', 'computational_efficiency', 
                         'emergent_patterns', 'agent_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for snapshot in self.snapshots:
                writer.writerow({
                    'timestamp': snapshot.timestamp,
                    'simulation_time': snapshot.simulation_time,
                    'avg_happiness': snapshot.avg_happiness,
                    'decision_diversity': snapshot.decision_diversity,
                    'computational_efficiency': snapshot.computational_efficiency,
                    'emergent_patterns': snapshot.emergent_patterns,
                    'agent_count': snapshot.agent_count
                })
    
    def generate_report(self) -> str:
        """Generate comprehensive metrics report"""
        if not self.snapshots:
            return "No metrics data available."
        
        summary = self.get_metrics_summary()
        
        report = []
        report.append("=== PRD EVALUATION METRICS REPORT ===\n")
        
        # Happiness metrics
        happiness = summary['avg_happiness']
        report.append(f"📊 AVERAGE HAPPINESS (Global Well-being)")
        report.append(f"  Current: {happiness['current']:.3f}")
        report.append(f"  Trend: {happiness['trend']:.3f}")
        report.append(f"  Range: {happiness['min']:.3f} - {happiness['max']:.3f}")
        
        # Diversity metrics
        diversity = summary['decision_diversity']
        report.append(f"\n🎯 DECISION DIVERSITY")
        report.append(f"  Current: {diversity['current']:.3f}")
        report.append(f"  Trend: {diversity['trend']:.3f}")
        report.append(f"  Range: {diversity['min']:.3f} - {diversity['max']:.3f}")
        
        # Efficiency metrics
        efficiency = summary['computational_efficiency']
        report.append(f"\n⚡ COMPUTATIONAL EFFICIENCY")
        report.append(f"  Current: {efficiency['current']:.3f}")
        report.append(f"  Average FPS: {efficiency['avg_fps']:.1f}")
        report.append(f"  Trend: {efficiency['trend']:.3f}")
        
        # Pattern emergence
        patterns = summary['emergent_patterns']
        report.append(f"\n🧠 EMERGENT BEHAVIOR PATTERNS")
        report.append(f"  Current: {patterns['current']}")
        report.append(f"  Total Detected: {patterns['total_detected']}")
        report.append(f"  Peak: {patterns['peak']}")
        
        # System health
        health = summary['simulation_health']
        report.append(f"\n💻 SIMULATION HEALTH")
        report.append(f"  Uptime: {health['uptime']:.1f} seconds")
        report.append(f"  Snapshots: {health['total_snapshots']}")
        report.append(f"  Active Agents: {health['agent_count']}")
        
        # Performance assessment
        report.append(f"\n🎯 PERFORMANCE ASSESSMENT")
        
        # Overall score (0-100)
        happiness_score = happiness['trend'] * 25
        diversity_score = diversity['trend'] * 25
        efficiency_score = efficiency['trend'] * 25
        pattern_score = min(25, patterns['total_detected'] * 2)
        
        overall_score = happiness_score + diversity_score + efficiency_score + pattern_score
        
        report.append(f"  Happiness Score: {happiness_score:.1f}/25")
        report.append(f"  Diversity Score: {diversity_score:.1f}/25")
        report.append(f"  Efficiency Score: {efficiency_score:.1f}/25")
        report.append(f"  Pattern Score: {pattern_score:.1f}/25")
        report.append(f"  OVERALL SCORE: {overall_score:.1f}/100")
        
        if overall_score >= 80:
            report.append("  🏆 EXCELLENT - Simulation performing exceptionally well!")
        elif overall_score >= 60:
            report.append("  ✅ GOOD - Simulation meeting most objectives")
        elif overall_score >= 40:
            report.append("  ⚠️ FAIR - Some areas need improvement")
        else:
            report.append("  ❌ POOR - Significant issues detected")
        
        return "\n".join(report)
