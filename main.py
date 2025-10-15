#!/usr/bin/env python3
"""
AI Life Simulator - Main Entry Point

An agent-based simulation where virtual humans make decisions and evolve their habits
using generative behavior modeling.
"""

import argparse
import sys
import time
from simulation import SimulationEngine
from visualization import run_visualization, MatplotlibAnalyzer

def main():
    parser = argparse.ArgumentParser(description='AI Life Simulator')
    parser.add_argument('--agents', type=int, default=10, help='Number of virtual humans (default: 10)')
    parser.add_argument('--time', type=float, help='Max simulation time (default: unlimited)')
    parser.add_argument('--speed', type=float, default=1.0, help='Simulation speed multiplier (default: 1.0)')
    parser.add_argument('--no-viz', action='store_true', help='Run without visualization')
    parser.add_argument('--web', action='store_true', help='Run web interface instead')
    parser.add_argument('--analyze', action='store_true', help='Run analysis on existing log data')
    
    args = parser.parse_args()
    
    if args.web:
        print("Starting web interface...")
        print("Open http://localhost:5000 in your browser")
        from web_app import app, socketio
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
        return
    
    if args.analyze:
        print("Loading simulation for analysis...")
        simulation = SimulationEngine(num_agents=1)  # Minimal simulation for analysis
        simulation.load_log_data('simulation_log.json')
        
        analyzer = MatplotlibAnalyzer(simulation)
        
        print("\nGenerating analysis plots...")
        analyzer.plot_agent_satisfaction_over_time()
        analyzer.plot_action_distribution()
        analyzer.plot_social_network()
        
        print("\n" + analyzer.generate_report())
        return
    
    # Create simulation
    print(f"Initializing AI Life Simulator with {args.agents} virtual humans...")
    simulation = SimulationEngine(num_agents=args.agents)
    simulation.set_speed(args.speed)
    
    # Add event callbacks for console output
    def on_agent_action(data):
        if data.get('ai_suggested'):
            print(f"🤖 AI suggested: {data['agent']} -> {data['action']}")
    
    def on_social_interaction(data):
        print(f"💬 Social: {data['agent1']} & {data['agent2']} at {data['location']}")
    
    def on_pattern_discovered(data):
        print(f"🧠 Discovered {data['new_patterns']} new behavior patterns (total: {data['total_patterns']})")
    
    simulation.add_event_callback('agent_action', on_agent_action)
    simulation.add_event_callback('social_interaction', on_social_interaction)
    simulation.add_event_callback('pattern_discovered', on_pattern_discovered)
    
    # Start visualization if requested
    viz_thread = None
    if not args.no_viz:
        try:
            print("Starting visualization...")
            viz_thread, visualizer = run_visualization(simulation)
            print("Visualization started! Use mouse and keyboard to interact.")
            print("Controls: Click=Select agent, C=Toggle connections, N=Toggle needs, Space=Pause, Esc=Deselect")
        except Exception as e:
            print(f"Could not start visualization: {e}")
            print("Running in console mode...")
    
    # Run simulation
    try:
        print(f"\nStarting simulation (speed: {args.speed}x)...")
        if args.time:
            print(f"Will run for {args.time} simulation time units")
        print("Press Ctrl+C to stop\n")
        
        simulation.run(max_time=args.time)
        
    except KeyboardInterrupt:
        print("\nStopping simulation...")
        simulation.stop()
    
    # Wait for visualization to close
    if viz_thread and viz_thread.is_alive():
        print("Close the visualization window to exit completely.")
        viz_thread.join()
    
    # Generate final report
    print("\n" + "="*50)
    print("SIMULATION COMPLETE")
    print("="*50)
    
    analyzer = MatplotlibAnalyzer(simulation)
    print(analyzer.generate_report())
    
    # Ask if user wants to see plots
    if simulation.log_data:
        try:
            response = input("\nGenerate analysis plots? (y/n): ").lower().strip()
            if response == 'y':
                print("Generating plots...")
                analyzer.plot_agent_satisfaction_over_time()
                analyzer.plot_action_distribution()
                analyzer.plot_social_network()
        except (EOFError, KeyboardInterrupt):
            pass
    
    print("\nThank you for using AI Life Simulator!")

if __name__ == "__main__":
    main()
