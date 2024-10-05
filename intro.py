#!/usr/bin/env python3
#
# intro.py

import pygame
import random
import math
import os
import subprocess
import shutil

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 1280
FPS = 60  # Frames per second

# Configurable duration in seconds (default is 5 seconds, can be increased)
DURATION = 8  # Adjust this value to dynamically change the length of the video
TOTAL_FRAMES = DURATION * FPS

# Colors (in hex, converted to RGB)
BACKGROUND_COLOR = (5, 5, 5)  # Almost black background
PARTICLE_COLOR = (0, 255, 128)  # Neon green particles
LINE_COLOR = (255, 255, 255)  # Cyan for lines
TITLE_COLOR = (0, 255, 0)  # Clean, white title color for contrast
TERMINAL_COLOR = (0, 0, 0)  # Terminal background color (solid black)
TYPING_COLOR = (0, 255, 128)  # Typing text color (customizable)
OUTPUT_COLOR = (0, 255, 128)  # Command output color (customizable)

# Configurable title and command
title_text = "Command Line Tutorials"
typing_text = "figlet welcome"
command_output = '''
              _
__      _____| | ___ ___  _ __ ___   ___
\ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \\
 \ V  V /  __/ | (_| (_) | | | | | |  __/
  \_/\_/ \___|_|\___\___/|_| |_| |_|\___|

'''

# Fonts
font_title = pygame.font.SysFont('Courier New', 60, bold=True)  # Bold title font
font_terminal = pygame.font.SysFont('Courier New', 12)  # Smaller font for prompt, typing, and output

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Terminal Data Network Animation")

# Particle class
class Particle:
    def __init__(self):
        self.radius = random.randint(2, 4)  # Smaller, denser particles
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed_x = random.uniform(-4, 4)  # Faster movement
        self.speed_y = random.uniform(-4, 4)  # Faster movement
        self.glow_intensity = random.uniform(0.5, 1)  # Random glow intensity

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Boundary conditions to make particles "bounce"
        if self.x <= 0 or self.x >= SCREEN_WIDTH:
            self.speed_x *= -1
        if self.y <= 0 or self.y >= SCREEN_HEIGHT:
            self.speed_y *= -1

    def draw(self, surface):
        color = (int(PARTICLE_COLOR[0] * self.glow_intensity),
                 int(PARTICLE_COLOR[1] * self.glow_intensity),
                 int(PARTICLE_COLOR[2] * self.glow_intensity))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)

# Function to draw lines between particles
def draw_lines(particles, surface, max_distance):
    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            dist = math.sqrt((particles[i].x - particles[j].x) ** 2 + (particles[i].y - particles[j].y) ** 2)
            if dist < max_distance:
                # Dynamic flicker effect by randomizing opacity
                opacity = random.randint(50, 255)
                line_color = (LINE_COLOR[0], LINE_COLOR[1], LINE_COLOR[2], opacity)
                pygame.draw.line(surface, line_color, (particles[i].x, particles[i].y),
                                 (particles[j].x, particles[j].y), 1)

# Create directory to save frames
frame_dir = "animation_frames"
if not os.path.exists(frame_dir):
    os.makedirs(frame_dir)

# Create a list of particles (even more particles for higher density)
particles = [Particle() for _ in range(300)]

# Dynamic timing based on total video duration
title_fade_duration = int(TOTAL_FRAMES * 0.10)  # Title fade-in over 10% of total duration
terminal_fade_duration = int(TOTAL_FRAMES * 0.10)  # Terminal background fade-in over 10%
command_typing_duration = int(TOTAL_FRAMES * 0.30)  # Command typing takes 30% of total duration
output_display_duration = int(TOTAL_FRAMES * 0.50)  # Remaining 50% for fast command output

# Utility function to wrap text and center it
def wrap_text(text, font, max_width):
    """Wrap text to fit within a given width and center each line."""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        test_width, _ = font.size(test_line)
        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())  # Add the last line
    return lines

# Center text
def center_text(text_lines, font, screen_width):
    """Calculate x position to center each line horizontally."""
    positions = []
    for line in text_lines:
        text_width, _ = font.size(line)
        x_pos = (screen_width - text_width) // 2
        positions.append(x_pos)
    return positions

# Fade-in effect for text
def fade_in_text(surface, text_lines, font, pos, positions, color, alpha):
    """Render wrapped text line by line with fade-in effect and center justification."""
    for i, line in enumerate(text_lines):
        text_surface = font.render(line, True, color)
        text_surface.set_alpha(alpha)  # Set transparency level
        line_height = font.get_height()
        line_pos = (positions[i], pos[1] + i * line_height)  # Adjust for line spacing
        surface.blit(text_surface, line_pos)

# Function to simulate typing effect
def type_text(surface, text, font, prompt, typed_chars, pos, color):
    display_text = prompt + text[:typed_chars]
    text_surface = font.render(display_text, True, color)
    surface.blit(text_surface, pos)

# Function to draw the terminal background with transparency
def draw_terminal_background(surface, alpha):
    terminal_surf = pygame.Surface((SCREEN_WIDTH - 100, 300), pygame.SRCALPHA)  # Terminal area
    terminal_surf.fill((0, 0, 0, alpha))  # Transparent black background
    surface.blit(terminal_surf, (50, 250))  # Position the terminal background

# Wrap title text based on screen width
wrapped_title = wrap_text(title_text, font_title, SCREEN_WIDTH - 100)
centered_positions = center_text(wrapped_title, font_title, SCREEN_WIDTH)
title_height = len(wrapped_title) * font_title.get_height()
title_pos = (0, 50)  # Only y-pos is needed since x-pos is calculated for each line

# Animation loop
running = True
frame_count = 0
title_alpha = 0  # For fade-in effect
terminal_alpha = 0  # For terminal background fade-in
typed_chars = 0  # For typing effect
command_output_lines = command_output.split('\n')
output_index = 0  # To track which line of command output to show
output_show = False  # Control when output should appear
command_pause_frames = FPS  # Pause for 1 second after command is fully typed

while running and frame_count < TOTAL_FRAMES:
    screen.fill(BACKGROUND_COLOR)

    # Update particles
    for particle in particles:
        particle.move()
        particle.draw(screen)

    # Draw lines between particles
    draw_lines(particles, screen, max_distance=100)

    # Title fade-in proportional to video length
    if frame_count < title_fade_duration:
        title_alpha = int(255 * (frame_count / title_fade_duration))  # Fade in over time
    else:
        title_alpha = 255  # Fully opaque after fade-in duration
    fade_in_text(screen, wrapped_title, font_title, title_pos, centered_positions, TITLE_COLOR, title_alpha)

    # Terminal background fade-in proportional to video length
    if frame_count > title_fade_duration and frame_count < title_fade_duration + terminal_fade_duration:
        terminal_alpha = int(200 * ((frame_count - title_fade_duration) / terminal_fade_duration))  # Fade in to transparency
    elif frame_count >= title_fade_duration + terminal_fade_duration:
        terminal_alpha = 200  # Set transparency for terminal
    if terminal_alpha > 0:
        draw_terminal_background(screen, terminal_alpha)

    # Command typing proportional to video length
    if frame_count > title_fade_duration + terminal_fade_duration:
        command_typing_frame_start = title_fade_duration + terminal_fade_duration
        typing_progress = (frame_count - command_typing_frame_start) / command_typing_duration
        if typing_progress <= 1:
            typed_chars = int(len(typing_text) * typing_progress)  # Progressively type out command
        else:
            typed_chars = len(typing_text)  # Ensure all characters are typed after the duration

        # Display typed command
        type_text(screen, typing_text, font_terminal, "user@linux:~$ ", typed_chars, (60, 270), TYPING_COLOR)

        # Display command output quickly after command typing is complete
        if typing_progress > 1:
            output_show = True

    # Show command output fast once the command is typed
    if output_show:
        for i, line in enumerate(command_output_lines[:output_index + 1]):
            fade_in_text(screen, [line], font_terminal, (60, 320 + i * 20), [60], OUTPUT_COLOR, 255)  # Adjust line height to remove extra spacing
        if output_index < len(command_output_lines) - 1:
            output_index += 1  # Display all lines quickly without delay

    # Save each frame
    pygame.image.save(screen, os.path.join(frame_dir, f"frame_{frame_count:04d}.png"))

    # Update the display
    pygame.display.flip()

    # Increment frame count
    frame_count += 1

    # Event handling (for quitting the program early)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Clean up and quit Pygame
pygame.quit()

# FFmpeg command to stitch the frames into a video
output_file = "intro.mp4"
ffmpeg_command = [
    "ffmpeg",
    "-r", "60",  # Frame rate
    "-f", "image2",
    "-s", "720x1280",  # Resolution
    "-i", os.path.join(frame_dir, "frame_%04d.png"),  # Input frames
    "-vcodec", "libx264",
    "-crf", "25",  # Quality setting
    "-pix_fmt", "yuv420p",
    output_file
]

print("Creating video with FFmpeg...")
subprocess.run(ffmpeg_command)

# Clean up the temporary frames after video creation
shutil.rmtree(frame_dir)
print("Temporary frames cleaned up, and video created:", output_file)

