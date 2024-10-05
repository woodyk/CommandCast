#!/usr/bin/env python3
import subprocess
import json
import argparse
import threading
import queue
import sys

def execute_commands(filename):
    with open(filename, 'r') as f:
        # Read all lines, including comments starting with '#'
        lines = [line.rstrip('\n') for line in f if line.strip()]

    executed_commands = []

    # Initialize a queue to store output lines
    q = queue.Queue()

    def enqueue_output(pipe, q):
        for line in iter(pipe.readline, ''):
            q.put(line)
        pipe.close()

    # Start a bash subprocess
    process = subprocess.Popen(
        ['/bin/bash'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Start a thread to read stdout
    thread = threading.Thread(target=enqueue_output, args=(process.stdout, q))
    thread.daemon = True
    thread.start()

    for line in lines:
        if line.startswith('#'):
            # It's a comment for rendering in an HTML card, not a command
            comment = line[1:].strip()  # Strip the '#' and leading/trailing spaces
            executed_commands.append({
                'type': 'comment',
                'content': comment
            })
        else:
            # Treat this as a command
            start_marker = "__CMD_START__"
            end_marker = "__CMD_END__"

            # Send echo statements and the actual command
            process.stdin.write(f'echo {start_marker}\n')
            process.stdin.write(f'{line}\n')
            process.stdin.write(f'echo {end_marker}\n')
            process.stdin.flush()

            # Read output until end_marker is found
            command_output = []
            while True:
                try:
                    line_output = q.get(timeout=10)  # Timeout to prevent hanging
                except queue.Empty:
                    print("Error: Timeout while waiting for command output.", file=sys.stderr)
                    process.terminate()
                    sys.exit(1)

                line_output = line_output.rstrip('\n')
                if line_output == start_marker:
                    continue  # Ignore the start marker
                elif line_output == end_marker:
                    break  # End of command output
                else:
                    command_output.append(line_output)

            # Append the command and its output
            executed_commands.append({
                'type': 'command',
                'command': line,
                'output': '\n'.join(command_output).strip()
            })

    # Terminate the subprocess
    process.stdin.write('exit\n')
    process.stdin.flush()
    process.wait()

    return executed_commands

def generate_html(commands, output_filename):
    html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Linux CLI Recorder</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            background-color: #000;
            overflow: hidden;
        }
        #terminal {
            width: 100%;
            height: 100%;
            padding: 10px;
            box-sizing: border-box;
            background-color: #000;
            color: #fff;
            font-family: 'Courier New', monospace;
            font-size: 16px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .prompt {
            color: #0f0;
        }
        .error {
            color: #f00;
        }
        .card {
            background-color: #1c1c1c;
            color: #fff;
            border: 1px solid #fff;
            padding: 10px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            border-radius: 5px;
            opacity: 0;
            transition: opacity 1s ease-in-out;
        }
        .card.show {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div id="terminal"></div>
    <script>
        const terminal = document.getElementById('terminal');
        const commands = {commands_json};
        let currentCommandIndex = 0;

        // Function to simulate typing effect for the command or comment
        function typeText(text, className = '', delay = 50, parentElement = terminal) {
            return new Promise((resolve) => {
                let index = 0;
                function type() {
                    if (index < text.length) {
                        const span = document.createElement('span');
                        span.className = className;
                        // Replace spaces with non-breaking spaces for HTML
                        if (text[index] === ' ') {
                            span.innerHTML = '&nbsp;';
                        } else if (text[index] === '\\t') {
                            span.innerHTML = '&nbsp;&nbsp;&nbsp;&nbsp;';
                        } else {
                            span.textContent = text[index];
                        }
                        parentElement.appendChild(span);
                        parentElement.scrollTop = parentElement.scrollHeight;  // Auto-scroll
                        index++;
                        setTimeout(type, delay); // Typing speed
                    } else {
                        resolve();
                    }
                }
                type();
            });
        }

        // Function to create and display comment cards with simulated typing
        function displayCard(content) {
            return new Promise((resolve) => {
                const cardDiv = document.createElement('div');
                cardDiv.className = 'card';
                terminal.appendChild(cardDiv);
                // Trigger CSS transition
                setTimeout(() => {
                    cardDiv.classList.add('show');
                }, 10);
                terminal.scrollTop = terminal.scrollHeight;  // Auto-scroll
                // Simulate typing effect within the card
                typeText(content, '', 20, cardDiv).then(() => {
                    // Optional: Add a slight delay after card is displayed
                    setTimeout(resolve, 500);
                });
            });
        }

        async function executeNextCommand() {
            if (currentCommandIndex < commands.length) {
                const command = commands[currentCommandIndex];

                if (command.type === 'comment') {
                    // Render the comment inside a card with simulated typing
                    await displayCard(command.content);
                    currentCommandIndex++;
                    setTimeout(executeNextCommand, 500);  // Delay before next action
                } else if (command.type === 'command') {
                    // Render a terminal command and its output
                    const promptSpan = document.createElement('span');
                    promptSpan.className = 'prompt';
                    promptSpan.textContent = 'user@localhost$ ';
                    terminal.appendChild(promptSpan);
                    
                    // Type out the command with the typing effect
                    await typeText(command.command + '\\n', '', 80);
    
                    // Introduce a 2-second pause before showing the output
                    await new Promise(resolve => setTimeout(resolve, 2000));
    
                    // Render the command output
                    if (command.output) {
                        const isError = command.output.toLowerCase().includes('error') || command.output.toLowerCase().includes('failed');
                        const outputSpan = document.createElement('span');
                        if (isError) {
                            outputSpan.className = 'error';
                        }
                        // Replace spaces and tabs for HTML
                        outputSpan.innerHTML = command.output.replace(/ /g, '&nbsp;').replace(/\\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;') + '<br/>';
                        terminal.appendChild(outputSpan);
                    } else {
                        terminal.innerHTML += '<br/>';
                    }
    
                    terminal.scrollTop = terminal.scrollHeight;  // Auto-scroll to the bottom
                    currentCommandIndex++;
                    setTimeout(executeNextCommand, 500);  // Delay before next action
                }
            } else {
                // All commands executed
                const completionSpan = document.createElement('span');
                completionSpan.textContent = '\\nScript execution completed.\\n';
                terminal.appendChild(completionSpan);
                terminal.scrollTop = terminal.scrollHeight;
            }
        }

        // Start execution immediately
        executeNextCommand();

        // Resize handler
        function resizeTerminal() {
            terminal.style.height = `${window.innerHeight}px`;
        }

        window.addEventListener('resize', resizeTerminal);
        resizeTerminal();
    </script>
</body>
</html>
    '''

    # Convert the commands list to JSON format
    commands_json = json.dumps(commands)

    # Insert the JSON into the HTML template
    html_content = html_template.replace('{commands_json}', commands_json)

    # Write the final HTML content to a file
    with open(output_filename, 'w') as f:
        f.write(html_content)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate an HTML CLI trainer from a script file.')
    parser.add_argument('script_file', help='The input script file containing commands to execute')
    parser.add_argument('output_file', help='The output HTML file name')
    args = parser.parse_args()

    try:
        commands = execute_commands(args.script_file)
        generate_html(commands, args.output_file)
        print(f"HTML file generated: {args.output_file}")
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

