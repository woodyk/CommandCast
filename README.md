# CommandCast

**Author:** Wadih Khairallah

CommandCast is a Python application that generates animated videos simulating a terminal session. It reads a list of Linux commands from a file, executes them, captures their output, and creates a video where the commands are typed out in a terminal-like interface, along with their outputs. The video includes customizable headers and footers, making it ideal for creating engaging content for platforms like TikTok or Instagram Reels.

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Optional Arguments](#optional-arguments)
- [Configuration](#configuration)
- [Examples](#examples)
- [Notes](#notes)
- [License](#license)

## Features

- Simulates typing of terminal commands with adjustable typing speed.
- Executes actual Linux commands and captures their outputs.
- Renders a terminal interface with customizable header and footer.
- Supports scrolling when output exceeds the visible area.
- Generates video output suitable for social media platforms.
- Configurable font sizes, colors, and other visual aspects.

## Requirements

- Python 3.x
- Pillow library for image manipulation.
- FFmpeg for compiling frames into a video.
- A TrueType font installed on your system (default is "Courier New").

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/CommandCast.git
cd CommandCast
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt 
```

3. Install FFmpeg:

- Ubuntu/Debian:

  ```bash
  sudo apt-get install ffmpeg
  ```

- macOS (using Homebrew):

  ```bash
  brew install ffmpeg
  ```

- Windows: Download FFmpeg from the official website and follow the installation instructions.

## Usage

### Basic Usage

The script `CommandCast.py` reads commands from a file and generates a video simulating the terminal session.

```bash
python CommandCast.py commands.txt
```

Replace `commands.txt` with the path to your plain text file containing Linux commands, one command per line.

### Optional Arguments

- Specify Output Video Filename:

  ```bash
  python CommandCast.py commands.txt -o output_video.mp4
  ```

  The default output filename is `command_video.mp4`.

- Adjust Typing Delay:

  ```bash
  python CommandCast.py commands.txt -d 0.1
  ```

  Adjusts the typing delay to 0.1 seconds per character. The default is 0.05 seconds.

- View Help Message:

  ```bash
  python CommandCast.py -h
  ```

  Displays usage information and available arguments.

## Configuration

You can customize various aspects of the video by editing the configuration variables at the top of the `CommandCast.py` script.

### Terminal Appearance

- **Terminal Dimensions:**

  ```python
  VIDEO_WIDTH = 1080
  VIDEO_HEIGHT = 1920
  ```

- **Font Settings:**

  ```python
  FONT_NAME = "Courier New"
  FONT_SIZE = 20
  LINE_HEIGHT = FONT_SIZE + 10
  ```

- **Colors:**

  ```python
  FONT_COLOR = (255, 255, 255)       # Command and output text color
  BACKGROUND_COLOR = (0, 0, 0)       # Terminal background color
  PROMPT_COLOR = (0, 255, 0)         # Prompt text color
  HEADER_BG_COLOR = (50, 50, 50)     # Header background color
  FOOTER_BG_COLOR = (50, 50, 50)     # Footer background color
  ```

- **Prompt Text:**

  ```python
  PROMPT_TEXT = "user@localhost$ "
  ```

### Header and Footer

- **Text Content:**

  ```python
  HEADER_TEXT = "ByAnAdmin Command Shorts"
  FOOTER_TEXT = "Powered by CommandCast"
  ```

- **Font Sizes:**

  ```python
  HEADER_FONT_SIZE = 36
  FOOTER_FONT_SIZE = 20
  ```

### Delays and Timing

- **Typing Delay:**

  ```python
  DEFAULT_TYPING_DELAY = 0.05  # Default typing delay per character
  ```

- **Output Delay:**

  ```python
  OUTPUT_DELAY = 1  # Delay before command output appears
  ```

- **Pre-Simulation Delay:**

  ```python
  PRE_SIMULATION_DELAY = 2  # Delay before typing starts
  ```

### Frame Rate

```python
FRAME_RATE = 10  # Frames per second for the video
```

## Examples

**Example `commands.txt` File:**

```bash
echo "Hello, World!"
ls -la
pwd
```

**Running the Script:**

```bash
python CommandCast.py commands.txt -o my_terminal_video.mp4 -d 0.1
```

This command will generate a video named `my_terminal_video.mp4` with a typing delay of 0.1 seconds per character.

## Notes

- **Dependencies:** Ensure all dependencies are installed and accessible:
  - Pillow library (pip install Pillow)
  - FFmpeg (installed and added to system PATH)
- **Font Availability:** The default font is "Courier New". If this font is not available on your system, change the `FONT_NAME` variable to a font that exists.
- **Permissions:** Ensure you have the necessary permissions to read the commands file and write the output video file.
- **Platform Compatibility:** The script should work on Windows, macOS, and Linux, provided that the dependencies are correctly installed.
- **Error Handling:** The script assumes that the commands in the `commands.txt` file are valid Linux commands. Invalid commands may result in errors or unexpected outputs.
- **Performance:** Rendering frames and compiling the video may take some time, depending on the length of the commands and outputs.

## License

**Disclaimer:** Use this application responsibly. Executing arbitrary commands can be dangerous. Ensure that the commands in your `commands.txt` file are safe and do not harm your system.
