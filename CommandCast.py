#!/usr/bin/env python3
#
# CommandCast.py
# Author: Wadih Khairallah

import subprocess
import os
import math
from PIL import Image, ImageDraw, ImageFont
import shutil
import argparse
import unicodedata
import re
import pexpect
import sys

# Function to convert hex color codes to RGB tuples
def hex_to_rgb(hex_color):
    """Convert a hex color code to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    # Expand shorthand hex codes, e.g., 'fff' to 'ffffff'
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Terminal configurations (for TikTok/Google Shorts video format)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Configurable font sizes
FONT_SIZE = 24
COMMENT_FONT_SIZE = 28  # Font size for comments

# Adjust line height based on font sizes
LINE_HEIGHT = FONT_SIZE + 10
COMMENT_LINE_HEIGHT = COMMENT_FONT_SIZE + 10

# Configurable colors (using hex codes)
FONT_COLOR_HEX = "#FFFFFF"  # White color for command and output
BACKGROUND_COLOR_HEX = "#000000"  # Black terminal background
PROMPT_COLOR_HEX = "#00FF00"  # Green color for the prompt

# Convert hex colors to RGB tuples
FONT_COLOR = hex_to_rgb(FONT_COLOR_HEX)
BACKGROUND_COLOR = hex_to_rgb(BACKGROUND_COLOR_HEX)
PROMPT_COLOR = hex_to_rgb(PROMPT_COLOR_HEX)

# Configurable Prompt
PROMPT_TEXT = "user@localhost$ "  # Default prompt

# Configurable header and footer background colors (using hex codes)
HEADER_BG_COLOR_HEX = "#323232"  # Dark grey for header
FOOTER_BG_COLOR_HEX = "#323232"  # Dark grey for footer

# Convert header and footer background colors to RGB
HEADER_BG_COLOR = hex_to_rgb(HEADER_BG_COLOR_HEX)
FOOTER_BG_COLOR = hex_to_rgb(FOOTER_BG_COLOR_HEX)

# Configurable header and footer text
HEADER_TEXT = "Command Line Shorts"
FOOTER_TEXT = "Powered by CommandCast"

# Configurable header and footer text font sizes
HEADER_FONT_SIZE = 36
FOOTER_FONT_SIZE = 24

# Configurable pre-simulation delay (in seconds)
PRE_SIMULATION_DELAY = 2  # Amount of time to wait at the beginning of the video before starting the simulation

# Frame rate for the video (you can change this value)
FRAME_RATE = 10  # Frames per second for the video

# Font settings
DEFAULT_FONT_NAMES = ["Courier New", "Courier", "Liberation Mono", "Nimbus Mono L", "FreeMono", "DejaVu Sans Mono"]

def get_available_font(font_names):
    """Return the first available font from the list."""
    for font_name in font_names:
        try:
            font = ImageFont.truetype(font_name, FONT_SIZE)
            return font_name
        except IOError:
            continue
    print("Error: None of the specified fonts are available.")
    sys.exit(1)

FONT_NAME = get_available_font(DEFAULT_FONT_NAMES)

# Ensure frames directory exists
FRAMES_DIR = "frames"

# Configurable comment card settings
COMMENT_CARD_BG_COLOR_HEX = "#00008B"  # Dark blue background for comment cards
COMMENT_TEXT_COLOR_HEX = "#FFFFFF"     # White text color for comments

# Convert comment card colors to RGB
COMMENT_CARD_BG_COLOR = hex_to_rgb(COMMENT_CARD_BG_COLOR_HEX)
COMMENT_TEXT_COLOR = hex_to_rgb(COMMENT_TEXT_COLOR_HEX)

# Terminal layout configurations
HEADER_PADDING = 200  # Padding at the top of the frame (header size)
HEADER_BUFFER = 20    # Vertical space between header and terminal content

FOOTER_MARGIN = 400  # Space reserved at the bottom of the video for overlays (footer size)
FOOTER_BUFFER = 20    # Vertical space between terminal content and footer

CONTENT_START_Y = HEADER_PADDING + HEADER_BUFFER  # Starting Y position for terminal content
CONTENT_END_Y = VIDEO_HEIGHT - FOOTER_MARGIN - FOOTER_BUFFER  # Ending Y position for terminal content

VISIBLE_HEIGHT = CONTENT_END_Y - CONTENT_START_Y  # Total available height for terminal content

# Typing speed configurations
# We will map typing speed (0 to 10) to characters per second (CPS)
MAX_CPS = 100     # Increased maximum CPS for faster typing at typing speed 10
MIN_CPS = 1       # Minimum characters per second at typing speed 0

def calculate_cps(typing_speed):
    """Calculate characters per second based on typing speed (0 to 10)."""
    # Ensure typing_speed is within 0 to 10
    typing_speed = max(0, min(typing_speed, 10))
    # Linear mapping from typing_speed to CPS
    cps = MIN_CPS + ((MAX_CPS - MIN_CPS) * (typing_speed / 10))
    return cps

# Function to handle word-wrapping for long text inside the comment card
def wrap_text_in_card(text, font, max_width):
    """Wrap text to fit inside a card, respecting the card's width."""
    lines = []
    words = text.split()
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        line_width = font.getbbox(test_line)[2] - font.getbbox(test_line)[0]

        if line_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines

# Function to ensure the frames directory is empty
def clear_frames_directory():
    """Clear all files in the frames directory and ensure it exists."""
    if os.path.exists(FRAMES_DIR):
        # Remove all files in the frames directory
        shutil.rmtree(FRAMES_DIR)
    # Re-create the frames directory
    os.makedirs(FRAMES_DIR)

# Function to simulate typing in the terminal and capture the frames
def simulate_typing(draw, img, text, pos, font, frame_idx, cps, fill_color=FONT_COLOR):
    """Simulate typing the text by generating frames character by character."""
    x, y = pos
    total_chars = len(text)
    time_per_char = 1.0 / cps  # seconds per character
    frame_duration = 1.0 / FRAME_RATE  # seconds per frame

    accumulated_time = 0.0
    char_index = 0

    while char_index < total_chars:
        # Save the current state as a frame
        frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
        img.save(frame_path)
        frame_idx += 1

        # Increment accumulated time
        accumulated_time += frame_duration

        # Render as many characters as needed based on accumulated time
        while accumulated_time >= time_per_char and char_index < total_chars:
            # Render the next character
            char = text[char_index]
            bbox = font.getbbox(char)
            char_width = bbox[2] - bbox[0]
            draw.text((x, y), char, font=font, fill=fill_color)
            x += char_width
            char_index += 1
            accumulated_time -= time_per_char  # Subtract the time per character

    return frame_idx

# Function to render the prompt and command separately, with word wrapping for long commands
def render_prompt_and_command(draw, img, prompt, prompt_color, command, pos, font, frame_idx, cps):
    """Render the prompt in one color, and type the command in another, with word wrapping."""
    x, y = pos
    # Render the prompt (not typed, in prompt color)
    draw.text((x, y), prompt, font=font, fill=prompt_color)
    prompt_width = font.getbbox(prompt)[2]  # Get the width of the prompt

    # Define the maximum width for the command text (the available space after the prompt)
    max_width = VIDEO_WIDTH - 100  # Adjust this as needed for margins

    # Calculate the remaining width for the command after the prompt is rendered
    remaining_width = max_width - prompt_width

    # Split and wrap the command text
    command_lines = wrap_text_in_card(command, font, remaining_width)

    # Save the frame with the fully rendered prompt
    frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
    img.save(frame_path)
    frame_idx += 1

    # Start typing the command, wrapping lines if necessary
    for idx, line in enumerate(command_lines):
        if idx == 0:
            # First line: render it next to the prompt
            line_x = x + prompt_width
        else:
            # Subsequent lines: move to the start of the new line
            y += LINE_HEIGHT
            line_x = 50  # Align new lines to the start of the screen margin

        # Simulate typing the command line
        frame_idx = simulate_typing(draw, img, line, (line_x, y), font, frame_idx, cps)

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
    draw.text((header_text_x, header_text_y), HEADER_TEXT, font=header_font, fill=FONT_COLOR)
    draw.text((footer_text_x, footer_text_y), FOOTER_TEXT, font=footer_font, fill=FONT_COLOR)

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
def generate_output_delay_frames(draw, img, frame_idx, output_delay):
    """Generate static frames to account for the output delay."""
    # Calculate how many frames are needed for the output delay
    total_frames = int(output_delay * FRAME_RATE)

    print(f"Generating {total_frames} output delay frames for {output_delay} seconds delay...")

    for _ in range(total_frames):
        # Save each frame
        frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
        img.save(frame_path)
        frame_idx += 1

    return frame_idx

# Function to handle scrolling in the terminal, considering header, footer, and comments
def scroll_terminal(draw, visible_items, font, comment_font, frame_idx):
    """Handle scrolling by moving text up when the terminal window overflows, including comment cards."""
    # Create a new blank image
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    # Render the header and footer background
    render_header_footer(draw)

    # Redraw the visible items starting from the beginning
    y_offset = CONTENT_START_Y
    for item in visible_items:
        if item['type'] == 'line':
            x_offset = 50  # Start position for each line
            for text, color in item['segments']:
                draw.text((x_offset, y_offset), text, font=font, fill=color)
                text_width = font.getbbox(text)[2] - font.getbbox(text)[0]
                x_offset += text_width
            y_offset += LINE_HEIGHT
        elif item['type'] == 'comment_card':
            x = 50
            card_width = item['card_width']
            card_height = item['card_height']
            padding = item['padding']
            card_color = item['card_color']
            radius = item['radius']
            # Draw rounded rectangle
            draw.rounded_rectangle(
                [(x, y_offset), (x + card_width, y_offset + card_height)],
                radius=radius, fill=card_color
            )
            # Draw the text lines inside the card
            y_text_offset = y_offset + padding
            for line_text, line_color in item['lines']:
                draw.text((x + padding, y_text_offset), line_text, font=comment_font, fill=line_color)
                y_text_offset += COMMENT_LINE_HEIGHT
            # Update y_offset
            y_offset += card_height  # Move y_offset down by the total height of the card
        else:
            pass  # Unknown item type
    # Save the scrolled frame
    frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
    img.save(frame_path)
    return img, draw, frame_idx + 1

# Function to render a comment with a fixed-width card and simulate typing
def render_comment(draw, img, comment_text, comment_font, frame_idx, cps):
    """Render a comment inside a fixed-width card, then simulate typing the text."""
    x = 50  # Left margin
    padding = 20  # Padding inside the card

    # Fixed card width (full width of the terminal content area)
    card_width = VIDEO_WIDTH - 2 * x

    # Beveled card background color
    card_color = COMMENT_CARD_BG_COLOR
    text_color = COMMENT_TEXT_COLOR
    radius = 15

    # Calculate maximum width for text inside the card
    max_text_width = card_width - 2 * padding

    # Word-wrap the comment text to fit within the card's width
    wrapped_lines = wrap_text_in_card(comment_text, comment_font, max_text_width)

    # If there are no wrapped lines, skip rendering the comment
    if not wrapped_lines:
        return frame_idx, None  # Return None for comment_item

    # Calculate the height of the comment card
    card_height = len(wrapped_lines) * COMMENT_LINE_HEIGHT + 2 * padding

    # Create the comment card item
    comment_item = {
        'type': 'comment_card',
        'lines': [(line, text_color) for line in wrapped_lines],
        'card_width': card_width,
        'card_height': card_height,
        'padding': padding,
        'card_color': card_color,
        'radius': radius
    }

    return frame_idx, comment_item

def sanitize_output(text):
    """Remove non-printable characters and ANSI escape codes, but preserve necessary formatting."""
    # Remove ANSI escape codes
    ansi_escape = re.compile(r'''
        \x1B  # ESC
        (?:   # 7-bit C1 Fe (except CSI)
            [@-Z\\-_]
        |     # or [ for CSI, followed by a control sequence
            \[
            [0-?]*  # Parameter bytes
            [ -/]*  # Intermediate bytes
            [@-~]   # Final byte
        )
    ''', re.VERBOSE)
    text = ansi_escape.sub('', text)
    # Remove control characters except for newline and tab
    text = ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C' or ch in ('\n', '\t'))
    return text

# Updated add_item function
def add_item(visible_items, new_item, font, comment_font, img, draw, frame_idx, total_visible_height):
    """Add a new item to visible_items and handle scrolling if necessary. Returns updated variables and y_position."""
    # Calculate the height of the new item
    if new_item['type'] == 'line':
        item_height = LINE_HEIGHT
    elif new_item['type'] == 'comment_card':
        item_height = new_item['card_height']
    else:
        item_height = LINE_HEIGHT  # default

    # Before adding the item, check if we need to scroll
    while total_visible_height + item_height > VISIBLE_HEIGHT:
        # Remove the oldest item
        oldest_item = visible_items.pop(0)
        # Subtract its height from total_visible_height
        if oldest_item['type'] == 'line':
            total_visible_height -= LINE_HEIGHT
        elif oldest_item['type'] == 'comment_card':
            total_visible_height -= oldest_item['card_height']
        else:
            total_visible_height -= LINE_HEIGHT  # default

        # Scroll the terminal before rendering the new item
        img, draw, frame_idx = scroll_terminal(draw, visible_items, font, comment_font, frame_idx)

    # Calculate y_position where the new item should be rendered
    y_position = CONTENT_START_Y + total_visible_height

    # Add the new item to visible_items
    visible_items.append(new_item)
    # Increase total_visible_height
    total_visible_height += item_height

    return img, draw, frame_idx, total_visible_height, y_position

# Updated render_terminal_frames function
def render_terminal_frames(commands, font_name, frame_idx=0, typing_speed=5, output_delay=0):
    """Generate frames that simulate typing and displaying the output of commands."""
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    # Render the header and footer background
    render_header_footer(draw)

    # Load fonts
    font = ImageFont.truetype(font_name, FONT_SIZE)
    comment_font = ImageFont.truetype(font_name, COMMENT_FONT_SIZE)

    # Calculate characters per second based on typing_speed
    cps = calculate_cps(typing_speed)

    visible_items = []  # Keep track of visible items (screen buffer)
    total_visible_height = 0  # Initialize total visible height

    # Generate pre-simulation frames
    frame_idx = generate_pre_simulation_frames(draw, img, frame_idx)

    for command, output in commands:
        if command.startswith('#'):
            # This is a comment
            comment_text = command.lstrip('# ').strip()
            print(f"Displaying comment: {comment_text}")

            # Add blank line before the comment
            blank_line_item = {'type': 'line', 'segments': [("", FONT_COLOR)]}
            img, draw, frame_idx, total_visible_height, _ = add_item(
                visible_items, blank_line_item, font, comment_font, img, draw, frame_idx, total_visible_height
            )

            # Render the comment card
            frame_idx, comment_item = render_comment(draw, img, comment_text, comment_font, frame_idx, cps)

            if comment_item:
                # Add the comment card to visible_items and get y_position
                img, draw, frame_idx, total_visible_height, y_position = add_item(
                    visible_items, comment_item, font, comment_font, img, draw, frame_idx, total_visible_height
                )

                # Draw the comment card background
                draw.rounded_rectangle(
                    [(50, y_position), (50 + comment_item['card_width'], y_position + comment_item['card_height'])],
                    radius=comment_item['radius'], fill=comment_item['card_color']
                )

                # Save the frame with the full card
                frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
                img.save(frame_path)
                frame_idx += 1

                # Simulate typing inside the card
                y_offset = y_position + comment_item['padding']
                for line in comment_item['lines']:
                    line_text, line_color = line
                    frame_idx = simulate_typing(
                        draw, img, line_text, (50 + comment_item['padding'], y_offset),
                        comment_font, frame_idx, cps, fill_color=line_color
                    )
                    y_offset += COMMENT_LINE_HEIGHT

                # Generate output delay frames as per the configurable delay
                frame_idx = generate_output_delay_frames(draw, img, frame_idx, output_delay)

            # Add blank line after the comment
            img, draw, frame_idx, total_visible_height, _ = add_item(
                visible_items, blank_line_item, font, comment_font, img, draw, frame_idx, total_visible_height
            )

        # Check for clear or reset command
        elif command in ['clear', 'reset']:
            print(f"Executing command: {command}")

            # Handle the clear or reset command
            # Simulate typing of the command first
            # Create the line item with prompt and command
            line_item = {
                'type': 'line',
                'segments': [(PROMPT_TEXT, PROMPT_COLOR), (command, FONT_COLOR)]
            }

            # Add the line item using add_item
            img, draw, frame_idx, total_visible_height, y_position = add_item(
                visible_items, line_item, font, comment_font, img, draw, frame_idx, total_visible_height
            )

            # Render the prompt
            draw.text((50, y_position), PROMPT_TEXT, font=font, fill=PROMPT_COLOR)

            # Simulate typing of the command after the prompt
            x_offset = 50 + font.getbbox(PROMPT_TEXT)[2]
            frame_idx = simulate_typing(draw, img, command, (x_offset, y_position), font, frame_idx, cps)

            # Generate output delay frames as per the configurable delay
            frame_idx = generate_output_delay_frames(draw, img, frame_idx, output_delay)

            # Clear the visible items (this mimics clearing the terminal screen)
            visible_items.clear()
            total_visible_height = 0

            # Redraw the empty terminal between header and footer
            img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), BACKGROUND_COLOR)
            draw = ImageDraw.Draw(img)
            render_header_footer(draw)

            # Save the cleared terminal frame
            frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
            img.save(frame_path)
            frame_idx += 1

        else:
            # This is a normal command
            print(f"Running command: {command}")

            # Word-wrap the command text
            prompt_width = font.getbbox(PROMPT_TEXT)[2]
            max_width = VIDEO_WIDTH - 100  # Set a padding around the text area
            remaining_width = max_width - prompt_width

            # Split and wrap the command text
            command_lines = wrap_text_in_card(command, font, remaining_width)

            # Handle the first line
            first_line_command = command_lines[0] if command_lines else ''
            line_item = {
                'type': 'line',
                'segments': [(PROMPT_TEXT, PROMPT_COLOR), (first_line_command, FONT_COLOR)]
            }
            # Add the line item using add_item
            img, draw, frame_idx, total_visible_height, y_position = add_item(
                visible_items, line_item, font, comment_font, img, draw, frame_idx, total_visible_height
            )

            # Render the prompt
            draw.text((50, y_position), PROMPT_TEXT, font=font, fill=PROMPT_COLOR)

            # Simulate typing of the first line of command after the prompt
            x_offset = 50 + prompt_width
            frame_idx = simulate_typing(draw, img, first_line_command, (x_offset, y_position), font, frame_idx, cps)

            # Handle subsequent lines of the command
            for line in command_lines[1:]:
                # Create a line item for each subsequent line
                line_item = {
                    'type': 'line',
                    'segments': [(line, FONT_COLOR)]
                }
                # Add the line item using add_item
                img, draw, frame_idx, total_visible_height, y_position = add_item(
                    visible_items, line_item, font, comment_font, img, draw, frame_idx, total_visible_height
                )
                # Simulate typing of the line starting at x = 50
                frame_idx = simulate_typing(draw, img, line, (50, y_position), font, frame_idx, cps)

            # Generate output delay frames as per the configurable delay
            frame_idx = generate_output_delay_frames(draw, img, frame_idx, output_delay)

            # Sanitize the output before processing
            sanitized_output = sanitize_output(output)

            # Process output lines
            output_lines = sanitized_output.splitlines()
            if output_lines:
                for line in output_lines:
                    line = line.expandtabs()
                    print(f"Output: {line}")

                    # Create output line item
                    line_item = {
                        'type': 'line',
                        'segments': [(line, FONT_COLOR)]
                    }

                    # Add the output line item using add_item
                    img, draw, frame_idx, total_visible_height, y_position = add_item(
                        visible_items, line_item, font, comment_font, img, draw, frame_idx, total_visible_height
                    )

                    # Render the line
                    draw.text((50, y_position), line, font=font, fill=FONT_COLOR)

                    # Save the frame
                    frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
                    img.save(frame_path)
                    frame_idx += 1

            else:
                # If there is no output, save a frame to show the command execution
                frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx}.png")
                img.save(frame_path)
                frame_idx += 1

    return frame_idx

# Updated run_commands_in_persistent_shell function
def run_commands_in_persistent_shell(commands, timeout=10):
    """Run the list of commands in a persistent shell and capture outputs after each command."""
    print("Starting persistent bash session...")
    # Start bash without loading .bashrc or .bash_profile
    bash = pexpect.spawn('/bin/bash', ['--noprofile', '--norc'], encoding='utf-8', echo=False)
    outputs = []
    unique_marker_end = 'COMMAND_OUTPUT_END_UNIQUE'
    
    # Set PS1 to empty to prevent bash from printing the prompt
    bash.sendline('unset PROMPT_COMMAND; PS1=""')
    # Disable command echo
    bash.setecho(False)
    # Disable history expansion
    bash.sendline('set +H')
    # Ensure the shell is ready
    bash.expect_exact('')  # Wait for the shell to be ready

    # Discard any initial output
    if bash.before:
        bash.before = ''
    if bash.buffer:
        bash.buffer = ''

    for command in commands:
        if command.startswith('#'):
            outputs.append('')
            continue
        print(f"Executing command: {command}")
        # Send the command and append an echo of the unique marker
        bash.sendline(f"{command}\necho {unique_marker_end}")
        # Read output until the unique marker is found
        output = ''
        try:
            bash.expect_exact(unique_marker_end, timeout=timeout)
            # Get the output before the marker
            output = bash.before.strip()
            # Remove any command echoes that might have slipped through
            output_lines = output.splitlines()
            # Remove any lines that match the command or are empty
            output_lines = [line for line in output_lines if line.strip() != command.strip() and line.strip()]
            # Reconstruct the output
            output = '\n'.join(output_lines)
        except pexpect.exceptions.TIMEOUT:
            print(f"Timeout while executing command: {command}")
            output = bash.before.strip()
        outputs.append(output)
    bash.close()
    return outputs

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
def generate_video_from_commands(commands_file, output_file="command_video.mp4", typing_speed=5, frame_rate=10, output_delay=0):
    """Generate a single video for all commands listed in the given file."""

    global FRAME_RATE, MAX_CPS
    FRAME_RATE = frame_rate
    # MAX_CPS remains at 100

    # Clear the frames directory before starting
    clear_frames_directory()

    # Read commands from the specified file
    with open(commands_file, 'r') as file:
        commands = [cmd.strip() for cmd in file.readlines() if cmd.strip()]

    # Run commands in a persistent shell and gather outputs
    command_outputs = list(zip(commands, run_commands_in_persistent_shell(commands)))

    # Generate frames for typing and output display
    print(f"Generating frames for all commands in {commands_file}")
    frame_count = render_terminal_frames(command_outputs, FONT_NAME, typing_speed=typing_speed, output_delay=output_delay)

    # Compile the frames into a video
    print(f"Compiling {frame_count} frames into a video...")
    create_video_from_frames(output_file, frame_rate=FRAME_RATE)

    # Cleanup frames if needed
    shutil.rmtree(FRAMES_DIR)

# Main execution
if __name__ == "__main__":
    import argparse  # Import argparse for command-line argument parsing

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate a video from terminal commands.')
    parser.add_argument('commands_file', metavar='commands_file', type=str,
                        help='File containing commands to run')
    parser.add_argument('-o', '--output', dest='output_file', default='command_video.mp4',
                        help='Output video file name (default: command_video.mp4)')
    parser.add_argument('-s', '--speed', dest='typing_speed', type=float, default=5,
                        help='Typing speed from 0 (slowest) to 10 (fastest), default is 5')
    parser.add_argument('-f', '--framerate', dest='frame_rate', type=int, default=10,
                        help='Frame rate of the output video, default is 10 FPS')
    parser.add_argument('-d', '--output-delay', dest='output_delay', type=float, default=2,
                        help='Delay in seconds before showing command output, default is 2')

    args = parser.parse_args()

    commands_file = args.commands_file
    output_file = args.output_file
    typing_speed = args.typing_speed
    frame_rate = args.frame_rate
    output_delay = args.output_delay

    # Generate a single video for all commands
    generate_video_from_commands(commands_file, output_file=output_file, typing_speed=typing_speed, frame_rate=frame_rate, output_delay=output_delay)

