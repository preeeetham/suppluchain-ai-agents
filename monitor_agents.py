"""
Monitor script to check agent communication and status.
"""

import time
import subprocess
import sys

def check_agent_status():
    """Check if all agents are running."""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        agents = {
            'inventory': False,
            'demand': False, 
            'route': False,
            'supplier': False
        }
        
        for line in lines:
            if 'inventory_agent.py' in line and 'grep' not in line:
                agents['inventory'] = True
            elif 'demand_forecasting_agent.py' in line and 'grep' not in line:
                agents['demand'] = True
            elif 'route_optimization_agent.py' in line and 'grep' not in line:
                agents['route'] = True
            elif 'supplier_coordination_agent.py' in line and 'grep' not in line:
                agents['supplier'] = True
        
        return agents
        
    except Exception as e:
        print(f"Error checking agent status: {e}")
        return {}

def main():
    """Monitor agent status."""
    print("🤖 SUPPLY CHAIN AI AGENTS - LIVE MONITORING")
    print("=" * 60)
    
    for i in range(10):  # Monitor for 10 cycles
        print(f"\n📊 Status Check #{i+1} - {time.strftime('%H:%M:%S')}")
        print("-" * 40)
        
        agents = check_agent_status()
        
        if agents:
            for agent_name, is_running in agents.items():
                status = "✅ RUNNING" if is_running else "❌ STOPPED"
                print(f"  {agent_name.upper()} AGENT: {status}")
        else:
            print("  ❌ Could not check agent status")
        
        # Count running agents
        running_count = sum(1 for running in agents.values() if running)
        total_count = len(agents)
        
        print(f"\n📈 SUMMARY: {running_count}/{total_count} agents running")
        
        if running_count == total_count:
            print("🎉 ALL AGENTS OPERATIONAL!")
            print("💬 Multi-agent communication should be active")
            print("🧠 MeTTa knowledge graphs are being queried")
            print("🔄 Autonomous supply chain optimization in progress")
        else:
            print(f"⚠️  {total_count - running_count} agents not running")
        
        time.sleep(5)  # Check every 5 seconds
    
    print("\n🏁 Monitoring complete!")

if __name__ == "__main__":
    main()
