#!/usr/bin/env python3
"""
Quick demo of the AI Life Simulator
"""

from simulation import SimulationEngine
import time

def run_demo():
    print("🤖 AI Life Simulator Demo")
    print("=" * 40)
    
    # Create a small simulation
    print("Creating simulation with 5 virtual humans...")
    sim = SimulationEngine(num_agents=5)
    
    # Add some event callbacks for demo
    def on_action(data):
        if data.get('ai_suggested'):
            print(f"🧠 AI: {data['agent']} -> {data['action']}")
        else:
            print(f"👤 {data['agent']}: {data['action']}")
    
    def on_social(data):
        print(f"💬 {data['agent1']} & {data['agent2']} socializing!")
    
    def on_pattern(data):
        print(f"🔍 Discovered {data['new_patterns']} new behavior patterns!")
    
    sim.add_event_callback('agent_action', on_action)
    sim.add_event_callback('social_interaction', on_social)
    sim.add_event_callback('pattern_discovered', on_pattern)
    
    print("\nStarting simulation for 30 seconds...")
    print("Watch the virtual humans make decisions!\n")
    
    # Run for a short time
    start_time = time.time()
    sim.set_speed(5.0)  # 5x speed
    
    try:
        while time.time() - start_time < 30:
            sim.step()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    
    sim.stop()
    
    # Show results
    print("\n" + "=" * 40)
    print("DEMO RESULTS")
    print("=" * 40)
    
    state = sim.get_simulation_state()
    print(f"Simulation time: {state['statistics']['total_time']:.1f}")
    print(f"Total actions: {state['statistics']['total_actions']}")
    print(f"Social interactions: {state['statistics']['social_interactions']}")
    print(f"Behavior patterns: {state['statistics']['pattern_discoveries']}")
    
    print("\nAgent Status:")
    for agent in state['agents']:
        satisfaction = sum(agent['needs'].values()) / len(agent['needs'])
        print(f"  {agent['name']}: {agent['current_action']} (satisfaction: {satisfaction:.2f})")
    
    print(f"\nEnvironment: {state['environment']['environmental_factors']['weather']}")
    print(f"Active locations: {len([loc for loc in state['environment']['locations'].values() if loc['occupants'] > 0])}")
    
    print("\n🎉 Demo complete! Run 'python main.py' for the full experience.")

if __name__ == "__main__":
    run_demo()
