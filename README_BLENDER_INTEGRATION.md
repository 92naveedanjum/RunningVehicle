# Blender + VSCode Integration Guide

## Setup Instructions

### 1. Find Your Blender Installation Path

First, locate your Blender executable. Common locations:

- `C:\Program Files\Blender Foundation\Blender 4.2\blender.exe`
- `C:\Program Files\Blender Foundation\Blender 3.6\blender.exe`
- `C:\Program Files\Blender Foundation\Blender\blender.exe`

### 2. Update the Tasks Configuration

Open `.vscode\tasks.json` and update the `command` path to match your Blender installation:

```json
"command": "& 'C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe'"
```

### 3. Running Your Script in Blender

#### Method 1: Using VSCode Tasks (Recommended)

1. Open your Python file (`Garden (1).py`)
2. Press `Ctrl+Shift+B` (Build command)
3. Select "Run in Blender"
4. Blender will open and execute your script automatically!

#### Method 2: Using the Command Palette

1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "Run in Blender"

#### Method 3: Using the Batch File

Double-click `run_in_blender.bat` to run the script.

## Available Tasks

### Run in Blender
Opens Blender GUI and runs your script. You'll see the 3D scene and can interact with it.

### Run in Blender (Background)
Runs Blender in headless mode (no GUI). Useful for batch processing or rendering.

## Tips

### Auto-Reload in Blender
If you want to keep Blender open and reload your script after making changes:

1. In Blender's Scripting tab, open your script
2. Make changes in VSCode
3. In Blender, press `Alt+P` to reload and run the script

### Debugging
To see print statements from your script:
- Run Blender from the command line or use the VSCode task
- Output will appear in the VSCode terminal

### Common Issues

**"Blender not found"**: Update the path in `tasks.json` to match your installation

**"Permission denied"**: Run VSCode as administrator

**Script doesn't run**: Make sure your script uses `if __name__ == "__main__":` block

## Example Workflow

1. Edit `Garden (1).py` in VSCode
2. Press `Ctrl+Shift+B`
3. Blender opens and shows your animated scene
4. Make changes in VSCode
5. Close Blender or switch focus
6. Press `Ctrl+Shift+B` again to see updates

## Advanced: Blender VSCode Extension

For even better integration, install the "Blender Development" extension:

1. In VSCode, press `Ctrl+Shift+X`
2. Search for "Blender Development"
3. Install the extension by Jacques Lucke
4. Configure it to point to your Blender executable
5. Use `Ctrl+Shift+P` → "Blender: Start" to launch Blender with live code sync
