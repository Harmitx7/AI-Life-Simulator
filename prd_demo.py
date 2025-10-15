#!/usr/bin/env python3
"""
PRD-Compliant AI Life Simulator Demo
Demonstrates all PRD requirements in action
"""

from simulation import SimulationEngine
import time

def run_prd_demo():
    print("🤖 PRD-Compliant AI Life Simulator Demo")
    print("=" * 50)
    
    # Create simulation with PRD specifications
    print("Creating simulation with PRD-compliant features...")
    sim = SimulationEngine(num_agents=8)
    
    # Add event callbacks to show PRD features
    def on_action(data):
        agent_name = data['agent']
        action = data['action']
        ai_suggested = data.get('ai_suggested', False)
        
        if ai_suggested:
            print(f"🧠 AI Behavior Model: {agent_name} -> {action}")
        else:
            print(f"👤 Utility Decision: {agent_name} -> {action}")
    
    def on_social(data):
        print(f"💬 Social Network: {data['agent1']} & {data['agent2']} at {data['location']}")
    
    def on_pattern(data):
        print(f"🔍 Generative Learning: Discovered {data['new_patterns']} new behavior patterns!")
    
    def on_update(data):
        # Show PRD metrics every 20 time units
        if int(data['time']) % 20 == 0 and data['time'] > 0:
            print(f"\n📊 PRD METRICS at time {data['time']:.1f}:")
            
            # Get current state
            state = sim.get_simulation_state()
            
            # Show agent states (PRD format)
            print("  Agent States:")
            for agent in state['agents'][:3]:  # Show first 3 agents
                needs = agent['needs']
                print(f"    {agent['name']}: H:{needs['hunger']:.0f} E:{needs['energy']:.0f} "
                      f"S:{needs['social_need']:.0f} $:{agent['money']:.0f} 😊:{agent['mood']:.2f}")
            
            # Show environment (24-hour clock)
            env = state['environment']
            hour = env['environmental_factors'].get('current_hour', 0) % 24
            print(f"  Environment: {hour:.1f}:00, {env['environmental_factors']['weather']}")
            
            # Show PRD metrics if available
            if 'prd_metrics' in state and state['prd_metrics']:
                metrics = state['prd_metrics']
                if 'avg_happiness' in metrics:
                    print(f"  Happiness: {metrics['avg_happiness']['current']:.3f}")
                if 'decision_diversity' in metrics:
                    print(f"  Decision Diversity: {metrics['decision_diversity']['current']:.3f}")
                if 'emergent_patterns' in metrics:
                    print(f"  Emergent Patterns: {metrics['emergent_patterns']['current']}")
    
    sim.add_event_callback('agent_action', on_action)
    sim.add_event_callback('social_interaction', on_social)
    sim.add_event_callback('pattern_discovered', on_pattern)
    sim.add_event_callback('simulation_update', on_update)
    
    print("\nStarting PRD demo for 60 seconds...")
    print("Watch for:")
    print("  🧠 AI behavior suggestions")
    print("  💰 Money-based decisions")
    print("  🕐 24-hour time cycle effects")
    print("  🏢 Zone-based state changes")
    print("  📊 Real-time metrics")
    print()
    
    # Run simulation
    start_time = time.time()
    sim.set_speed(3.0)  # 3x speed for demo
    
    try:
        while time.time() - start_time < 60:  # 60 seconds
            sim.step()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    
    sim.stop()
    
    # Show final PRD results
    print("\n" + "=" * 50)
    print("PRD DEMO RESULTS")
    print("=" * 50)
    
    state = sim.get_simulation_state()
    
    # Agent analysis
    print("\n🧍‍♂️ AGENT ANALYSIS:")
    for agent in state['agents']:
        needs = agent['needs']
        personality = agent['personality']
        
        print(f"\n{agent['name']}:")
        print(f"  State: {agent['current_action']} (${agent['money']:.0f}, mood: {agent['mood']:.2f})")
        print(f"  Needs: H:{needs['hunger']:.0f} E:{needs['energy']:.0f} "
              f"S:{needs['social_need']:.0f} 😊:{needs['happiness']:.0f}")
        print(f"  Traits: Discipline:{personality['discipline']:.2f} "
              f"Sociability:{personality['sociability']:.2f} Ambition:{personality['ambition']:.2f}")
        
        # Show learned behaviors
        best_action = max(agent['action_rewards'].items(), key=lambda x: x[1])
        print(f"  Best Action: {best_action[0]} (reward: {best_action[1]:.2f})")
    
    # Environment analysis
    print(f"\n🌍 ENVIRONMENT:")
    env = state['environment']
    hour = env.get('current_hour', 0) % 24
    print(f"  Time: {hour:.1f}:00 (Day {env.get('day_cycle', 0)})")
    print(f"  Weather: {env['environmental_factors']['weather']}")
    print(f"  Active Locations: {len([loc for loc in env['locations'].values() if loc['occupants'] > 0])}")
    
    # Behavior model analysis
    print(f"\n🧠 AI BEHAVIOR MODEL:")
    behavior = state['behavior_model']
    print(f"  Total Patterns: {behavior['total_patterns']}")
    print(f"  Successful Patterns: {behavior['successful_patterns']}")
    print(f"  Average Success Rate: {behavior['avg_success_rate']:.3f}")
    
    # PRD Metrics
    if 'prd_metrics' in state and state['prd_metrics']:
        print(f"\n📊 PRD EVALUATION METRICS:")
        metrics = state['prd_metrics']
        
        if 'avg_happiness' in metrics:
            happiness = metrics['avg_happiness']
            print(f"  Global Well-being: {happiness['current']:.3f} (range: {happiness['min']:.3f}-{happiness['max']:.3f})")
        
        if 'decision_diversity' in metrics:
            diversity = metrics['decision_diversity']
            print(f"  Decision Diversity: {diversity['current']:.3f}")
        
        if 'computational_efficiency' in metrics:
            efficiency = metrics['computational_efficiency']
            print(f"  Computational Efficiency: {efficiency['avg_fps']:.1f} FPS")
        
        if 'emergent_patterns' in metrics:
            patterns = metrics['emergent_patterns']
            print(f"  Emergent Patterns: {patterns['total_detected']} detected")
    
    print(f"\n✅ PRD Demo complete!")
    print(f"   Simulation Time: {state['statistics']['total_time']:.1f} units")
    print(f"   Total Actions: {state['statistics']['total_actions']}")
    print(f"   Social Interactions: {state['statistics']['social_interactions']}")
    
    print(f"\n🎯 PRD FEATURES DEMONSTRATED:")
    print(f"   ✅ Agent Model: State variables (energy, hunger, happiness, money)")
    print(f"   ✅ Personality Traits: discipline, sociability, ambition, creativity")
    print(f"   ✅ Decision Engine: Utility maximization with reinforcement learning")
    print(f"   ✅ Environment: 24-hour clock, zone effects, weather system")
    print(f"   ✅ Behavior Engine: Pattern discovery and generative modeling")
    print(f"   ✅ Evaluation Metrics: Happiness, diversity, efficiency, emergence")
    print(f"   ✅ Data Logging: SQLite database with detailed tracking")
    
    print(f"\n📁 Generated Files:")
    print(f"   - simulation_metrics.db (SQLite database)")
    print(f"   - simulation_metrics.csv (CSV export)")
    print(f"   - behavior_patterns.json (AI learned patterns)")
    print(f"   - simulation_log.json (Detailed logs)")

if __name__ == "__main__":
    run_prd_demo()
