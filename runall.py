import os
import subprocess
import sys

root = os.path.dirname(os.path.abspath(__file__))

commands = [
    ("python client.py", os.path.join(root, "backend")),
    ("python closesource.py --headless", os.path.join(root, "backend")),
    ("npm start", os.path.join(root, "backend", "opencode-bridge")),
]

for cmd, cwd in commands:
    if sys.platform == "win32":
        subprocess.Popen(f'start cmd /k "{cmd}"', shell=True, cwd=cwd)
    elif sys.platform == "darwin":
        mac_cmd = cmd.replace("python ", "python3 ")
        apple_script = f'''
        tell application "Terminal"
            activate
            do script "cd {cwd} && {mac_cmd}"
        end tell
        '''
        subprocess.Popen(["osascript", "-e", apple_script])
    else:
        subprocess.Popen(cmd, shell=True, cwd=cwd)

print("Started gateway, engine, and OpenCode bridge.")
print("Run the UI separately: cd desktop && npm run tauri dev")
