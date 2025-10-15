from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import threading
import time
from simulation import SimulationEngine, run_simulation_async

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai_life_simulator_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global simulation instance
simulation = None
simulation_thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_simulation', methods=['POST'])
def start_simulation():
    global simulation, simulation_thread
    
    data = request.get_json()
    num_agents = data.get('num_agents', 10)
    
    if simulation and simulation.running:
        return jsonify({'error': 'Simulation already running'}), 400
    
    # Create new simulation
    simulation = SimulationEngine(num_agents=num_agents)
    
    # Add event callbacks for real-time updates
    simulation.add_event_callback('simulation_update', emit_simulation_update)
    simulation.add_event_callback('agent_action', emit_agent_action)
    simulation.add_event_callback('social_interaction', emit_social_interaction)
    
    # Start simulation in background thread
    simulation_thread = run_simulation_async(simulation)
    
    return jsonify({'status': 'started', 'num_agents': num_agents})

@app.route('/api/stop_simulation', methods=['POST'])
def stop_simulation():
    global simulation
    
    if simulation:
        simulation.stop()
        return jsonify({'status': 'stopped'})
    
    return jsonify({'error': 'No simulation running'}), 400

@app.route('/api/pause_simulation', methods=['POST'])
def pause_simulation():
    global simulation
    
    if simulation:
        if simulation.paused:
            simulation.resume()
            return jsonify({'status': 'resumed'})
        else:
            simulation.pause()
            return jsonify({'status': 'paused'})
    
    return jsonify({'error': 'No simulation running'}), 400

@app.route('/api/simulation_state')
def get_simulation_state():
    global simulation
    
    if simulation:
        return jsonify(simulation.get_simulation_state())
    
    return jsonify({'error': 'No simulation running'}), 400

def emit_simulation_update(data):
    socketio.emit('simulation_update', data)

def emit_agent_action(data):
    socketio.emit('agent_action', data)

def emit_social_interaction(data):
    socketio.emit('social_interaction', data)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    if simulation:
        emit('simulation_state', simulation.get_simulation_state())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
