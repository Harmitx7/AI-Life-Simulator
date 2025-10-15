#!/usr/bin/env python3
"""
System test to verify all components work together
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        from agent import VirtualHuman, ActionType
        from environment import SimulationEnvironment, LocationType
        from behavior_model import GenerativeBehaviorModel
        from simulation import SimulationEngine
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_agent_creation():
    """Test agent creation and basic functionality"""
    try:
        from agent import VirtualHuman
        agent = VirtualHuman(0, "TestAgent")
        
        # Test basic properties
        assert hasattr(agent, 'needs')
        assert hasattr(agent, 'personality')
        assert hasattr(agent, 'habits')
        
        # Test decision making
        action = agent.decide_action()
        assert action is not None
        
        # Test action performance
        success = agent.perform_action(action, 0.1)
        assert isinstance(success, bool)
        
        print("✅ Agent creation and basic functionality work")
        return True
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def test_environment():
    """Test environment functionality"""
    try:
        from environment import SimulationEnvironment
        env = SimulationEnvironment(100, 100)
        
        # Test basic properties
        assert len(env.locations) > 0
        assert hasattr(env, 'environmental_factors')
        
        # Test updates
        env.update(0.1)
        
        print("✅ Environment functionality works")
        return True
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def test_behavior_model():
    """Test behavior model functionality"""
    try:
        from behavior_model import GenerativeBehaviorModel
        from agent import VirtualHuman
        
        model = GenerativeBehaviorModel()
        agents = [VirtualHuman(i, f"Agent{i}") for i in range(3)]
        
        # Test pattern discovery
        model.discover_patterns(agents)
        
        # Test suggestion
        suggestion = model.suggest_action(agents[0])
        # suggestion can be None (exploration) or an ActionType
        
        print("✅ Behavior model functionality works")
        return True
    except Exception as e:
        print(f"❌ Behavior model test failed: {e}")
        return False

def test_simulation():
    """Test full simulation functionality"""
    try:
        from simulation import SimulationEngine
        
        sim = SimulationEngine(num_agents=3)
        
        # Test basic properties
        assert len(sim.agents) == 3
        assert sim.environment is not None
        assert sim.behavior_model is not None
        
        # Test single step
        sim.step()
        
        # Test state retrieval
        state = sim.get_simulation_state()
        assert 'agents' in state
        assert 'environment' in state
        
        print("✅ Full simulation functionality works")
        return True
    except Exception as e:
        print(f"❌ Simulation test failed: {e}")
        return False

def run_all_tests():
    """Run all system tests"""
    print("🧪 Running AI Life Simulator System Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_agent_creation,
        test_environment,
        test_behavior_model,
        test_simulation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python demo.py' for a quick demo")
        print("2. Run 'python main.py' for full simulation")
        print("3. Run 'python main.py --web' for web interface")
    else:
        print("❌ Some tests failed. Check dependencies and code.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
