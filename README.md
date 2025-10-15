# AI Life Simulator

An agent-based simulation where virtual humans make decisions (eat, work, sleep, socialize) and evolve their habits using generative behavior modeling.

## Features

- **Virtual Human Agents**: Each agent has unique personality traits, needs, and habits
- **Decision Making**: Agents autonomously decide between eating, working, sleeping, and socializing
- **Habit Evolution**: Behaviors adapt over time based on experiences and outcomes
- **Generative Modeling**: AI-driven behavior patterns that emerge naturally
- **Real-time Visualization**: Watch agents live their virtual lives
- **Web Interface**: Interactive dashboard to monitor and control the simulation

## Installation

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the simulation:
```bash
python main.py
```

### Run with web interface:
```bash
python web_app.py
```

## Architecture

- `agent.py` - Virtual human agent implementation
- `simulation.py` - Main simulation engine
- `behavior_model.py` - Generative behavior modeling
- `environment.py` - World state and environment
- `visualization.py` - Real-time visualization
- `web_app.py` - Web interface
- `main.py` - Entry point

## Agent Behaviors

Each agent has:
- **Basic Needs**: Hunger, energy, social, work satisfaction
- **Personality Traits**: Introversion/extroversion, conscientiousness, etc.
- **Habits**: Learned patterns that influence decision-making
- **Memory**: Past experiences that shape future choices
