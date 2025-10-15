# AI Life Simulator - Usage Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Demo (30 seconds)
```bash
python demo.py
```

### 3. Run Full Simulation with Visualization
```bash
python main.py
```

### 4. Run Web Interface
```bash
python main.py --web
```
Then open http://localhost:5000 in your browser

## 🎮 Running Modes

### Console Mode (Basic)
```bash
python main.py --no-viz --agents 15 --time 100
```

### With Pygame Visualization
```bash
python main.py --agents 10 --speed 2.0
```
- **Click**: Select agent to see details
- **C**: Toggle social connections display
- **N**: Toggle needs bars
- **Space**: Pause/Resume simulation
- **Esc**: Deselect agent

### Web Dashboard
```bash
python main.py --web
```
Features:
- Real-time agent monitoring
- Interactive charts
- Environment status
- Control simulation remotely

### Analysis Mode
```bash
python main.py --analyze
```
Generates plots from previous simulation data

## 🤖 What You'll See

### Virtual Humans
Each agent has:
- **Unique personality** (Big Five traits)
- **Basic needs**: hunger, energy, social, work satisfaction
- **Learned habits** that evolve over time
- **Decision-making** based on current state

### Actions
- **🍽️ Eat**: Satisfies hunger
- **💼 Work**: Increases work satisfaction, uses energy
- **😴 Sleep**: Restores energy
- **👥 Socialize**: Fulfills social needs
- **⏸️ Idle**: Default state

### AI Behavior Evolution
- **Pattern Discovery**: AI learns common behavior sequences
- **Habit Formation**: Successful actions become stronger habits
- **Generative Modeling**: New behaviors emerge from learned patterns
- **Social Learning**: Agents influence each other through interactions

### Environment
- **Dynamic weather** affects comfort and decisions
- **Multiple locations**: homes, workplaces, restaurants, social areas
- **Resource availability** changes over time
- **Random events** create variety

## 📊 Key Features

### 1. Autonomous Decision Making
Agents choose actions based on:
- Current needs (hunger, energy, etc.)
- Personality traits
- Learned habits
- Environmental factors
- Social influences

### 2. Generative Behavior Modeling
- **Machine Learning**: Discovers patterns in agent behavior
- **Evolution**: Successful patterns are reinforced
- **Mutation**: Variations of successful patterns are created
- **Adaptation**: Behaviors adapt to changing conditions

### 3. Social Dynamics
- **Relationship Building**: Agents form social connections
- **Influence**: Social agents affect each other's decisions
- **Group Behaviors**: Emergent social patterns

### 4. Rich Environment
- **Multiple Locations**: Each with different purposes and capacities
- **Weather System**: Affects agent comfort and decisions
- **Events**: Random occurrences that change the world
- **Resource Management**: Limited availability creates competition

## 🔧 Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --agents N        Number of virtual humans (default: 10)
  --time T          Max simulation time (default: unlimited)
  --speed S         Speed multiplier (default: 1.0)
  --no-viz          Run without Pygame visualization
  --web             Start web interface
  --analyze         Analyze existing log data
```

## 📈 Understanding the Output

### Console Messages
- `👤 Agent: action` - Natural agent decision
- `🧠 AI: Agent -> action` - AI-suggested behavior
- `💬 Agent1 & Agent2 socializing!` - Social interaction
- `🔍 Discovered N new behavior patterns!` - AI learning

### Visualization Colors
- **Red**: Eating
- **Blue**: Working  
- **Green**: Sleeping
- **Yellow**: Socializing
- **Gray**: Idle

### Need Bars (Visualization)
- **Red**: Critical need (< 30%)
- **Yellow**: Moderate need (30-70%)
- **Green**: Satisfied need (> 70%)

## 🧠 AI Learning Process

1. **Data Collection**: Agents perform actions and record outcomes
2. **Pattern Recognition**: AI identifies common behavior sequences
3. **Clustering**: Similar situations are grouped together
4. **Pattern Creation**: Successful sequences become behavioral patterns
5. **Suggestion**: AI suggests actions based on learned patterns
6. **Feedback**: Success/failure updates pattern effectiveness
7. **Evolution**: Patterns mutate and evolve over time

## 📁 Generated Files

- `behavior_patterns.json`: Learned AI behavior patterns
- `simulation_log.json`: Detailed simulation data for analysis
- Console output shows real-time activity

## 🎯 Experiment Ideas

1. **Personality Effects**: Run with different agent counts to see how personality diversity affects outcomes
2. **Speed Testing**: Use `--speed 10` to see long-term behavior evolution
3. **Social Dynamics**: Watch how agents with high extraversion create social hubs
4. **Habit Formation**: Observe how repeated successful actions become stronger habits
5. **Environmental Impact**: Notice how weather and events affect agent decisions

## 🐛 Troubleshooting

### Missing Dependencies
```bash
pip install numpy matplotlib pygame pandas scikit-learn flask flask-socketio
```

### Pygame Issues (Windows)
If visualization doesn't work, use:
```bash
python main.py --no-viz
```

### Web Interface Not Loading
Check that port 5000 is available:
```bash
python main.py --web
# Then visit http://localhost:5000
```

## 🎉 Have Fun!

This simulator demonstrates emergent AI behavior, social dynamics, and machine learning in action. Watch as your virtual humans develop unique personalities, form relationships, and evolve their behaviors over time!
