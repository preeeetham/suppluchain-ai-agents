#!/usr/bin/env python3
"""
Startup script for the complete Supply Chain AI Agents system
Runs both the backend API server and frontend development server
"""

import asyncio
import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

class FullStackRunner:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_backend(self):
        """Start the FastAPI backend server"""
        print("🚀 Starting backend API server...")
        try:
            # Start the API server
            backend_process = subprocess.Popen([
                sys.executable, "api_server.py"
            ], cwd=os.getcwd())
            
            self.processes.append(backend_process)
            print("✅ Backend API server started on http://localhost:8000")
            return backend_process
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return None
    
    def start_frontend(self):
        """Start the Next.js frontend development server"""
        print("🚀 Starting frontend development server...")
        try:
            frontend_dir = Path("frontend")
            if not frontend_dir.exists():
                print("❌ Frontend directory not found!")
                return None
            
            # Install dependencies if needed
            if not (frontend_dir / "node_modules").exists():
                print("📦 Installing frontend dependencies...")
                subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            
            # Start the Next.js dev server
            frontend_process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=frontend_dir)
            
            self.processes.append(frontend_process)
            print("✅ Frontend development server started on http://localhost:3000")
            return frontend_process
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return None
    
    def start_agents(self):
        """Start the AI agents in the background"""
        print("🤖 Starting AI agents...")
        try:
            # Start inventory agent
            inventory_process = subprocess.Popen([
                sys.executable, "agents/inventory_agent.py"
            ], cwd=os.getcwd())
            self.processes.append(inventory_process)
            
            # Start demand forecasting agent
            demand_process = subprocess.Popen([
                sys.executable, "agents/demand_forecasting_agent.py"
            ], cwd=os.getcwd())
            self.processes.append(demand_process)
            
            # Start route optimization agent
            route_process = subprocess.Popen([
                sys.executable, "agents/route_optimization_agent.py"
            ], cwd=os.getcwd())
            self.processes.append(route_process)
            
            # Start supplier coordination agent
            supplier_process = subprocess.Popen([
                sys.executable, "agents/supplier_coordination_agent.py"
            ], cwd=os.getcwd())
            self.processes.append(supplier_process)
            
            print("✅ All AI agents started")
            return True
        except Exception as e:
            print(f"❌ Error starting agents: {e}")
            return False
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down all services...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up all running processes"""
        for process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Warning: Error stopping process: {e}")
        
        print("✅ All services stopped")
    
    def run(self):
        """Run the complete full-stack system"""
        print("🌟 Starting Supply Chain AI Agents Full-Stack System")
        print("=" * 60)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Start AI agents first
            if not self.start_agents():
                print("❌ Failed to start AI agents")
                return
            
            # Wait a moment for agents to initialize
            time.sleep(2)
            
            # Start backend API server
            backend_process = self.start_backend()
            if not backend_process:
                print("❌ Failed to start backend")
                return
            
            # Wait for backend to start
            time.sleep(3)
            
            # Start frontend development server
            frontend_process = self.start_frontend()
            if not frontend_process:
                print("❌ Failed to start frontend")
                return
            
            print("\n🎉 All services started successfully!")
            print("=" * 60)
            print("📊 Dashboard: http://localhost:3000")
            print("🔌 API Server: http://localhost:8000")
            print("📚 API Docs: http://localhost:8000/docs")
            print("🤖 AI Agents: Running in background")
            print("=" * 60)
            print("Press Ctrl+C to stop all services")
            
            # Keep the main process alive
            while self.running:
                time.sleep(1)
                
                # Check if any process has died
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        print(f"⚠️  Process {i} has stopped unexpectedly")
                        self.running = False
                        break
            
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        except Exception as e:
            print(f"❌ Error running system: {e}")
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    runner = FullStackRunner()
    runner.run()

if __name__ == "__main__":
    main()
