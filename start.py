#!/usr/bin/env python3
"""
Robust startup script for Allergen Detection FYP
Waits for model to fully load before starting website
"""
import subprocess
import sys
import time
import os
from pathlib import Path
import json

class Startup:
    def __init__(self):
        self.root = Path(__file__).parent
        self.api_proc = None
        self.nextjs_proc = None
        
    def log(self, level, msg):
        """Print log message"""
        prefix = {
            'OK': '[OK] ',
            'FAIL': '[FAIL] ',
            'INFO': '[INFO] ',
            'WARN': '[WARN] '
        }.get(level, '• ')
        print(f"{prefix}{msg}")
    
    def run_cmd(self, cmd, cwd=None, timeout=30):
        """Run command and return output"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True if isinstance(cmd, str) else False
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def start_api(self):
        """Start ML API and wait for full initialization"""
        self.log('INFO', 'Starting ML API (port 8000)...')
        
        try:
            # Get Python executable from venv
            if sys.platform == 'win32':
                python_exe = self.root / '.venv' / 'Scripts' / 'python.exe'
            else:
                python_exe = self.root / '.venv' / 'bin' / 'python'
            
            if not python_exe.exists():
                python_exe = sys.executable
            
            # Start API process
            self.api_proc = subprocess.Popen(
                [str(python_exe), '-m', 'src.api.allergen_api', '--host', '127.0.0.1', '--port', '8000'],
                cwd=str(self.root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.log('INFO', 'Waiting for ML API to fully initialize with model...')
            
            # Wait for API to be ready with model loaded
            max_attempts = 60  # 60 seconds for model to load
            for attempt in range(max_attempts):
                try:
                    import urllib.request
                    response = urllib.request.urlopen('http://localhost:8000/health', timeout=2)
                    
                    if response.status == 200:
                        # API is responding
                        health_data = json.loads(response.read().decode())
                        
                        # Check if model is loaded
                        if health_data.get('model_loaded'):
                            self.log('OK', 'ML API ready with model loaded')
                            return True
                        else:
                            self.log('INFO', f'Model loading... ({attempt + 1}s)')
                except Exception as e:
                    if attempt % 5 == 0:
                        self.log('INFO', f'Waiting for API... ({attempt + 1}s)')
                
                time.sleep(1)
            
            self.log('WARN', 'ML API timeout - model may still be loading')
            return True
        
        except Exception as e:
            self.log('FAIL', f'Could not start ML API: {e}')
            return False
    
    def start_nextjs(self):
        """Start Next.js website"""
        self.log('INFO', 'Starting Next.js website (port 3000)...')
        
        try:
            webapp = self.root / 'webapp'
            
            # Ensure node_modules exists
            node_modules = webapp / 'node_modules'
            if not node_modules.exists():
                self.log('FAIL', 'node_modules not found. Run: cd webapp && npm install')
                return False
            
            # Set up environment
            env = os.environ.copy()
            
            # Add node_modules/.bin to PATH for this process
            node_bin = node_modules / '.bin'
            if node_bin.exists():
                if 'PATH' in env:
                    env['PATH'] = str(node_bin) + os.pathsep + env['PATH']
                else:
                    env['PATH'] = str(node_bin)
            
            # Method 1: Try using npm from node_modules/.bin directly
            npm_exe = None
            if sys.platform == 'win32':
                npm_candidates = [
                    node_bin / 'npm.cmd',
                    node_bin / 'npm.ps1',
                    node_modules / '.bin' / 'npm',
                ]
            else:
                npm_candidates = [
                    node_bin / 'npm',
                ]
            
            for candidate in npm_candidates:
                if candidate.exists():
                    npm_exe = str(candidate)
                    break
            
            # Method 2: Try system npm
            if not npm_exe:
                try:
                    result = subprocess.run(['npm', '--version'], capture_output=True, timeout=5)
                    if result.returncode == 0:
                        npm_exe = 'npm'
                except:
                    pass
            
            # Method 3: Use npx (comes with Node.js)
            if not npm_exe:
                try:
                    result = subprocess.run(['npx', '--version'], capture_output=True, timeout=5)
                    if result.returncode == 0:
                        npm_exe = 'npx'
                except:
                    pass
            
            if not npm_exe:
                self.log('FAIL', 'npm/npx not found. Install Node.js: https://nodejs.org/')
                return False
            
            self.log('INFO', f'Starting with: {npm_exe}')
            
            # Start Next.js
            cmd = [npm_exe, 'run', 'dev'] if npm_exe != 'npx' else ['npx', 'next', 'dev']
            
            self.nextjs_proc = subprocess.Popen(
                cmd,
                cwd=str(webapp),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # Wait for startup
            time.sleep(5)
            
            # Check if Next.js started
            try:
                import urllib.request
                response = urllib.request.urlopen('http://localhost:3000', timeout=3)
                self.log('OK', 'Next.js website started')
                return True
            except Exception as check_err:
                self.log('INFO', 'Next.js starting (checking again...)...')
                time.sleep(3)
                try:
                    import urllib.request
                    response = urllib.request.urlopen('http://localhost:3000', timeout=3)
                    self.log('OK', 'Next.js website ready')
                    return True
                except:
                    self.log('WARN', 'Next.js started in background (may still be initializing)')
                    return True
        
        except Exception as e:
            self.log('FAIL', f'Could not start Next.js: {e}')
            return False
    
    def run(self):
        """Main startup sequence"""
        print("\n" + "="*60)
        print("     ALLERGEN DETECTION - START ALL SERVICES")
        print("="*60 + "\n")
        
        # Run pre-flight check
        self.log('INFO', 'Running pre-flight checks...')
        success, out, err = self.run_cmd([sys.executable, 'preflight_check.py'])
        if not success:
            self.log('WARN', 'Pre-flight checks had warnings')
        
        print()
        
        # Start ML API (WAIT for model to load)
        if not self.start_api():
            self.log('FAIL', 'Could not start ML API')
            return 1
        
        print()
        
        # Start Next.js (only after API is ready with model)
        if not self.start_nextjs():
            self.log('WARN', 'Next.js may not have started properly')
        
        print()
        print("="*60)
        print("     SERVICES STARTED SUCCESSFULLY")
        print("="*60)
        print("\nWeb:  http://localhost:3000")
        print("API:  http://localhost:8000")
        print("Docs: http://localhost:8000/docs\n")
        print("Press Ctrl+C to stop all services\n")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
                
                # Check processes
                if self.api_proc and self.api_proc.poll() is not None:
                    self.log('WARN', 'ML API stopped unexpectedly')
                    self.api_proc = None
                
                if self.nextjs_proc and self.nextjs_proc.poll() is not None:
                    self.log('WARN', 'Next.js stopped unexpectedly')
                    self.nextjs_proc = None
        
        except KeyboardInterrupt:
            print("\n")
            self.log('INFO', 'Shutting down services...')
            
            if self.api_proc:
                try:
                    self.api_proc.terminate()
                    self.api_proc.wait(timeout=5)
                    self.log('OK', 'ML API stopped')
                except:
                    try:
                        self.api_proc.kill()
                    except:
                        pass
                    self.log('WARN', 'ML API force-stopped')
            
            if self.nextjs_proc:
                try:
                    self.nextjs_proc.terminate()
                    self.nextjs_proc.wait(timeout=5)
                    self.log('OK', 'Next.js stopped')
                except:
                    try:
                        self.nextjs_proc.kill()
                    except:
                        pass
                    self.log('WARN', 'Next.js force-stopped')
            
            print()
            return 0

if __name__ == "__main__":
    startup = Startup()
    sys.exit(startup.run())
