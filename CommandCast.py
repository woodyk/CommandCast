#!/usr/bin/env python3
#
# CommandCast.py
# Author: Wadih Khairallah

import subprocess
import os
import time
from PIL import Image, ImageDraw, ImageFont
import shutil
import argparse  # Added for command-line argument parsing

# Terminal configurations (for TikTok/Google Shorts video format)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FONT_SIZE = 20
LINE_HEIGHT = FONT_SIZE + 10  # Adjust line height
FONT_COLOR = (255, 255, 255)  # White color for command and output
BACKGROUND_COLOR = (0, 0, 0)  # Black terminal background

HEADER_PADDING = 200  # Padding at the top of the frame (header size)
HEADER_BUFFER = 20    # Vertical space between header and terminal content

FOOTER_MARGIN = 400  # Space reserved at the bottom of the video for overlays (footer size)
FOOTER_BUFFER = 20    # Vertical space between terminal content and footer

CONTENT_START_Y = HEADER_PADDING + HEADER_BUFFER  # Starting Y position for terminal content
CONTENT_END_Y = VIDEO_HEIGHT - FOOTER_MARGIN - FOOTER_BUFFER  # Ending Y position for terminal content

VISIBLE_HEIGHT = CONTENT_END_Y - CONTENT_START_Y  # Total available height for terminal content
VISIBLE_LINES = VISIBLE_HEIGHT // LINE_HEIGHT  # Maximum visible lines

# Configurable Prompt
PROMPT_TEXT = "user@localhost$ "  # Default prompt
PROMPT_COLOR = (0, 255, 0)  # Green color for the prompt

# Configurable header and footer background colors
HEADER_BG_COLOR = (50, 50, 50)  # Dark grey for header
FOOTER_BG_COLOR = (50, 50, 50)  # Dark grey for footer

# Configurable header and footer text
HEADER_TEXT = "ByAnAdmin Command Shorts"
FOOTER_TEXT = "Powered by CommandCast"

# Configurable header and footer text font sizes
HEADER_FONT_SIZE = 36 
FOOTER_FONT_SIZE = 20 

# Configurable output delay (in seconds)
OUTPUT_DELAY = 1  # Amount of time to wait before rendering output after typing the command

# Configurable pre-simulation delay (in seconds)
PRE_SIMULATION_DELAY = 2  # Amount of time to wait at the beginning of the video before starting the simulation

# Frame rate for the video
FRAME_RATE = 10  # Frames per second for the video

# Using Courier New as the font, pre-installed on most systems
FONT_NAME = "Courier New"

# Ensure frames directory exists
FRAMES_DIR = "frames"

# Function to ensure the frames directory is empty
def clear_frames_directory():
    """Clear all files in the frames directory and ensure it exists."""
    if os.path.exists(FRAMES_DIR):
        # Remove all files in the frames directory
        shutil.rmtree(FRAMES_DIR)
    # Re-create the frames directory
    os.makedirs(FRAMES_DIR)

# Function to simulate typing in the terminal and capture the frames
def simulate_typing(draw, img, command, pos, font, frame_idx, delay=0.05):
    """Simulate typing the command after the prompt is fully rendered."""
    x, y = pos
    for char in command:
        # Use getbbox() to get character width
        bbox = font.getbbox(char)
        char_width = bbox[2] - bbox[0]  # Width is the difference between right and left bounds
        draw.text((x, y), char, font=font, fill=FONT_COLOR)
        x += char_width  # Move cursor to the right for the next character

        # Save the current state as a frame
        frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
        img.save(frame_path)
        frame_idx += 1

        # Simulate typing delay
        time.sleep(delay)

    return frame_idx

# Function to render the prompt and command separately
def render_prompt_and_command(draw, img, prompt, prompt_color, command, pos, font, frame_idx, delay=0.05):
    """Render the prompt in one color, and type the command in another."""
    x, y = pos
    # Render the prompt (not typed, in prompt color)
    draw.text((x, y), prompt, font=font, fill=prompt_color)
    prompt_width = font.getbbox(prompt)[2]  # Get the width of the prompt

    # Save the frame with the fully rendered prompt
    frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
    img.save(frame_path)
    frame_idx += 1

    # Simulate typing the command in default font color
    frame_idx = simulate_typing(draw, img, command, (x + prompt_width, y), font, frame_idx, delay)

    return frame_idx

# Function to render header and footer background
def render_header_footer(draw):
    """Render header and footer areas with their respective background colors and text."""
    # Draw header background
    draw.rectangle([(0, 0), (VIDEO_WIDTH, HEADER_PADDING)], fill=HEADER_BG_COLOR)
    # Draw footer background
    draw.rectangle([(0, VIDEO_HEIGHT - FOOTER_MARGIN), (VIDEO_WIDTH, VIDEO_HEIGHT)], fill=FOOTER_BG_COLOR)

    # Load fonts for header and footer text
    header_font = ImageFont.truetype(FONT_NAME, HEADER_FONT_SIZE)
    footer_font = ImageFont.truetype(FONT_NAME, FOOTER_FONT_SIZE)

    # Calculate positions for header and footer text
    header_text_bbox = draw.textbbox((0, 0), HEADER_TEXT, font=header_font)
    header_text_width = header_text_bbox[2] - header_text_bbox[0]
    header_text_height = header_text_bbox[3] - header_text_bbox[1]

    footer_text_bbox = draw.textbbox((0, 0), FOOTER_TEXT, font=footer_font)
    footer_text_width = footer_text_bbox[2] - footer_text_bbox[0]
    footer_text_height = footer_text_bbox[3] - footer_text_bbox[1]

    # Center the text horizontally
    header_text_x = (VIDEO_WIDTH - header_text_width) // 2
    footer_text_x = (VIDEO_WIDTH - footer_text_width) // 2

    # Vertical positions for header and footer text
    header_text_y = (HEADER_PADDING - header_text_height) // 2
    footer_text_y = VIDEO_HEIGHT - FOOTER_MARGIN + (FOOTER_MARGIN - footer_text_height) // 2

    # Draw header and footer text
    draw.text((header_text_x, header_text_y), HEADER_TEXT, font=header_font, fill=(255, 255, 255))
    draw.text((footer_text_x, footer_text_y), FOOTER_TEXT, font=footer_font, fill=(255, 255, 255))

# Function to generate frames for the pre-simulation delay
def generate_pre_simulation_frames(draw, img, frame_idx):
    """Generate static frames to account for the pre-simulation delay."""
    # Calculate how many frames are needed for the pre-simulation delay
    total_frames = int(PRE_SIMULATION_DELAY * FRAME_RATE)

    print(f"Generating {total_frames} pre-simulation frames for {PRE_SIMULATION_DELAY} seconds delay...")

    for _ in range(total_frames):
        # Save each frame
        frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
        img.save(frame_path)
        frame_idx += 1

    return frame_idx

# Function to generate frames for the output delay
def generate_output_delay_frames(draw, img, frame_idx):
    """Generate static frames to account for the output delay."""
    # Calculate how many frames are needed for the output delay
    total_frames = int(OUTPUT_DELAY * FRAME_RATE)

    print(f"Generating {total_frames} output delay frames for {OUTPUT_DELAY} seconds delay...")

    for _ in range(total_frames):
        # Save each frame
        frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
        img.save(frame_path)
        frame_idx += 1

    return frame_idx

# Function to handle scrolling in the terminal, considering header and footer
def scroll_terminal(draw, visible_lines, font, frame_idx):
    """Handle scrolling behavior by moving text up when the terminal window overflows."""
    # Create a new blank image
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    # Render the header and footer background
    render_header_footer(draw)

    # Redraw the visible lines
    y_offset = CONTENT_START_Y
    for line_segments in visible_lines:
        x_offset = 50  # Start position for each line
        for text, color in line_segments:
            draw.text((x_offset, y_offset), text, font=font, fill=color)
            text_width = font.getbbox(text)[2] - font.getbbox(text)[0]
            x_offset += text_width
        y_offset += LINE_HEIGHT

    # Save the scrolled frame
    frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
    img.save(frame_path)
    return img, draw, frame_idx + 1

# Helper function to add lines with scroll check
def add_line(visible_lines, new_line_segments, font, img, draw, frame_idx):
    """Add a new line (composed of text segments with colors) to visible_lines and handle scrolling if necessary."""
    # Before adding the line, check if we need to scroll
    if len(visible_lines) >= VISIBLE_LINES:
        # Remove the oldest line
        visible_lines.pop(0)
        # Scroll the terminal before rendering the new line
        img, draw, frame_idx = scroll_terminal(draw, visible_lines, font, frame_idx)
    visible_lines.append(new_line_segments)
    return img, draw, frame_idx

# Function to render the command and output in a terminal-like format, generating frames for each
def render_terminal_frames(commands, font_name, frame_idx=0, delay=0.05):
    """Generate frames that simulate typing and displaying the output of commands."""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    # Render the header and footer background
    render_header_footer(draw)

    font = ImageFont.truetype(font_name, FONT_SIZE)
    visible_lines = []  # Keep track of visible lines (screen buffer)

    # Generate pre-simulation frames
    frame_idx = generate_pre_simulation_frames(draw, img, frame_idx)

    for command, output in commands:
        print(f"Running command: {command}")

        # Get the y position for the prompt
        y_position = CONTENT_START_Y + len(visible_lines) * LINE_HEIGHT

        # Check if y_position is within CONTENT_END_Y
        if y_position + LINE_HEIGHT > CONTENT_END_Y:
            # Need to scroll before adding new line
            img, draw, frame_idx = scroll_terminal(draw, visible_lines, font, frame_idx)

        # Render the prompt and type the command
        frame_idx = render_prompt_and_command(draw, img, PROMPT_TEXT, PROMPT_COLOR, command, (50, y_position), font, frame_idx, delay)

        # Combine the prompt and command into one line with their respective colors
        line_segments = [(PROMPT_TEXT, PROMPT_COLOR), (command, FONT_COLOR)]

        # Add the combined line to visible_lines
        img, draw, frame_idx = add_line(visible_lines, line_segments, font, img, draw, frame_idx)

        # Generate frames for the output delay (OUTPUT_DELAY)
        frame_idx = generate_output_delay_frames(draw, img, frame_idx)

        # Process output line by line
        for line in output.splitlines():
            print(f"Output: {line}")

            # Get the y position for the output line
            y_position = CONTENT_START_Y + len(visible_lines) * LINE_HEIGHT

            # Check if y_position is within CONTENT_END_Y
            if y_position + LINE_HEIGHT > CONTENT_END_Y:
                # Need to scroll before adding new line
                img, draw, frame_idx = scroll_terminal(draw, visible_lines, font, frame_idx)

            # Draw the line
            draw.text((50, y_position), line, font=font, fill=FONT_COLOR)

            # Add output line to visible_lines
            img, draw, frame_idx = add_line(visible_lines, [(line, FONT_COLOR)], font, img, draw, frame_idx)

            # Save the current state as a frame
            frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
            img.save(frame_path)
            frame_idx += 1

    return frame_idx

# Function to run a Linux command and capture its output
def run_command(command):
    """Run the given Linux command and capture its output."""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout + result.stderr

# Function to generate a video using ffmpeg from the frames
def create_video_from_frames(output_file, frame_rate=10):
    """Use ffmpeg to generate a video from the rendered frames."""
    ffmpeg_command = [
        "ffmpeg",
        "-y",  # Overwrite output file
        "-framerate", str(frame_rate),  # Frame rate
        "-i", os.path.join(FRAMES_DIR, "frame_%d.png"),  # Input frames
        "-c:v", "libx264",  # Video codec
        "-pix_fmt", "yuv420p",  # Pixel format for compatibility
        output_file  # Output video file
    ]

    # Execute the ffmpeg command to generate the video
    subprocess.run(ffmpeg_command)

# Function to generate a single video for all commands in a file
def generate_video_from_commands(commands_file, output_file="command_video.mp4", delay=0.05):
    """Generate a single video for all commands listed in the given file."""

    # Clear the frames directory before starting
    clear_frames_directory()

    # Read commands from the specified file
    with open(commands_file, 'r') as file:
        commands = [cmd.strip() for cmd in file.readlines() if cmd.strip()]

    # Gather commands and their outputs
    command_outputs = [(cmd, run_command(cmd)) for cmd in commands]

    # Generate frames for typing and output display
    print(f"Generating frames for all commands in {commands_file}")
    frame_count = render_terminal_frames(command_outputs, FONT_NAME, delay=delay)

    # Compile the frames into a video
    print(f"Compiling {frame_count} frames into a video...")
    create_video_from_frames(output_file)

    # Cleanup frames if needed
    shutil.rmtree(FRAMES_DIR)

# Main execution
if __name__ == "__main__":
    import argparse  # Import argparse for command-line argument parsing

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate a video from terminal commands.')
    parser.add_argument('commands_file', metavar='commands_file', type=str,
                        help='File containing Linux commands to run')
    parser.add_argument('-o', '--output', dest='output_file', default='command_video.mp4',
                        help='Output video file name (default: command_video.mp4)')
    parser.add_argument('-d', '--delay', dest='typing_delay', type=float, default=0.05,
                        help='Typing delay in seconds (default: 0.05)')

    args = parser.parse_args()

    commands_file = args.commands_file
    output_file = args.output_file
    delay = args.typing_delay

    # Generate a single video for all commands
    generate_video_from_commands(commands_file, output_file=output_file, delay=delay)

