#!/usr/bin/env python3
import os
import requests
import svgwrite
from github import Github
from datetime import datetime

# GitHub Terminal SVG Generator

def get_github_stats(username):
    """Fetch GitHub stats for the given username"""
    # Initialize GitHub API with token for higher rate limits
    token = os.environ.get('GITHUB_TOKEN')
    g = Github(token)
    
    try:
        # Get user
        user = g.get_user(username)
        
        # Basic user info
        stats = {
            "name": user.name or username,
            "login": username,
            "bio": user.bio,
            "company": user.company,
            "location": user.location,
            "email": user.email,
            "blog": user.blog,
            "twitter": user.twitter_username,
            "public_repos": user.public_repos,
            "public_gists": user.public_gists,
            "followers": user.followers,
            "following": user.following,
            "created_at": user.created_at.isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        # Get repositories
        repos = user.get_repos()
        
        # Calculate stars
        total_stars = 0
        languages = {}
        repos_list = []
        
        for repo in repos:
            if not repo.fork:  # Skip forks
                total_stars += repo.stargazers_count
                
                # Count languages
                if repo.language:
                    languages[repo.language] = languages.get(repo.language, 0) + 1
                
                # Add to repos list (top 10 by stars)
                repos_list.append({
                    "name": repo.name,
                    "description": repo.description,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "language": repo.language,
                    "url": repo.html_url
                })
        
        # Sort repos by stars and get top 10
        repos_list.sort(key=lambda x: x["stars"], reverse=True)
        stats["top_repos"] = repos_list[:10]
        
        # Add stars count
        stats["total_stars"] = total_stars
        
        # Add top languages
        stats["languages"] = [{"name": k, "count": v} for k, v in sorted(languages.items(), key=lambda x: x[1], reverse=True)][:5]
        
        # Get contributions (approximate from the contributions calendar)
        try:
            # This is a bit hacky as GitHub doesn't provide this directly via API
            # We're scraping the contributions from the profile page
            response = requests.get(f"https://github.com/users/{username}/contributions")
            if response.status_code == 200:
                # Count the number of contribution days
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                contributions = soup.find_all('rect', {'class': 'ContributionCalendar-day'})
                
                total_contributions = 0
                for contrib in contributions:
                    count = contrib.get('data-count')
                    if count and count.isdigit():
                        total_contributions += int(count)
                
                stats["contributions_last_year"] = total_contributions
            else:
                stats["contributions_last_year"] = "N/A"
        except Exception as e:
            print(f"Error fetching contributions: {e}")
            stats["contributions_last_year"] = "N/A"
            
        # Get pull requests and issues stats
        try:
            # Get PRs created by user
            query = f"author:{username} type:pr"
            result = g.search_issues(query)
            stats["pull_requests"] = result.totalCount
            
            # Get PRs merged (approximate - GitHub API doesn't provide this directly)
            query = f"author:{username} type:pr is:merged"
            result = g.search_issues(query)
            stats["merged_pull_requests"] = result.totalCount
            
            # Get issues created by user
            query = f"author:{username} type:issue"
            result = g.search_issues(query)
            stats["issues"] = result.totalCount
        except Exception as e:
            print(f"Error fetching PR/issue stats: {e}")
            stats["pull_requests"] = "N/A"
            stats["merged_pull_requests"] = "N/A"
            stats["issues"] = "N/A"
        
        return stats
    
    except Exception as e:
        print(f"Error fetching GitHub stats: {e}")
        return {"error": str(e)}

def create_terminal_svg(stats, output_path="terminal.svg"):
    """Create an SVG terminal with GitHub stats"""
    # SVG dimensions
    width = 800
    height = 550
    
    # Create SVG document
    dwg = svgwrite.Drawing(output_path, (width, height), debug=True)
    
    # Define styles with animations
    dwg.defs.add(dwg.style("""
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes typing {
            from { width: 0; }
            to { width: 100%; }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        @keyframes gradient {
            0% { fill: #00ff00; }
            25% { fill: #00ffff; }
            50% { fill: #0088ff; }
            75% { fill: #8800ff; }
            100% { fill: #00ff00; }
        }
        
        @keyframes glow {
            0% { filter: drop-shadow(0 0 2px rgba(0, 255, 0, 0.7)); }
            50% { filter: drop-shadow(0 0 5px rgba(0, 255, 0, 0.9)); }
            100% { filter: drop-shadow(0 0 2px rgba(0, 255, 0, 0.7)); }
        }
        
        .terminal {
            font-family: 'Fira Code', monospace;
            font-size: 14px;
        }
        
        .terminal-bg {
            fill: #0d1117;
            rx: 10;
            ry: 10;
            filter: drop-shadow(0px 5px 10px rgba(0, 0, 0, 0.5));
        }
        
        .terminal-header {
            fill: #161b22;
            rx: 10 10 0 0;
            ry: 10 10 0 0;
        }
        
        .terminal-title {
            fill: #c9d1d9;
            font-size: 14px;
            font-weight: bold;
        }
        
        .terminal-button {
            r: 6;
        }
        
        .terminal-button:hover {
            animation: pulse 0.5s infinite;
        }
        
        .close-button {
            fill: #f85149;
        }
        
        .minimize-button {
            fill: #fac24c;
        }
        
        .maximize-button {
            fill: #58a6ff;
        }
        
        .terminal-text {
            fill: #c9d1d9;
            font-size: 14px;
            animation: fadeIn 0.5s ease-in;
        }
        
        .prompt {
            fill: #7ee787;
            font-weight: bold;
        }
        
        .command {
            fill: #e6edf3;
        }
        
        .output {
            fill: #a5d6ff;
            animation: fadeIn 0.5s ease-in;
        }
        
        .error {
            fill: #f85149;
            animation: fadeIn 0.3s ease-in;
        }
        
        .help {
            fill: #d2a8ff;
        }
        
        .stats {
            fill: #79c0ff;
        }
        
        .repos {
            fill: #a5d6ff;
        }
        
        .contact {
            fill: #ffab70;
        }
        
        .skills {
            fill: #7ee787;
        }
        
        .projects {
            fill: #d2a8ff;
        }
        
        .about {
            fill: #79c0ff;
        }
        
        .welcome {
            fill: #7ee787;
            font-weight: bold;
            animation: fadeIn 1s ease-in;
        }
        
        .info {
            fill: #79c0ff;
        }
        
        .cursor {
            animation: blink 1s infinite;
        }
        
        .highlight {
            animation: gradient 8s infinite;
        }
        
        .glow {
            animation: glow 2s infinite;
        }
    """))
    
    # Terminal background with enhanced design
    dwg.add(dwg.rect((0, 0), (width, height), class_="terminal-bg", id="terminal-bg"))
    
    # Terminal header with gradient
    header = dwg.rect((0, 0), (width, 30), class_="terminal-header")
    header.set_desc(title="Terminal Header")
    dwg.add(header)
    
    # Add bottom corners fix
    dwg.add(dwg.rect((0, 25), (width, 5), fill="#161b22"))
    
    # Terminal buttons with hover effect
    close_btn = dwg.circle((20, 15), class_="terminal-button close-button")
    close_btn.set_desc(title="Close")
    dwg.add(close_btn)
    
    minimize_btn = dwg.circle((45, 15), class_="terminal-button minimize-button")
    minimize_btn.set_desc(title="Minimize")
    dwg.add(minimize_btn)
    
    maximize_btn = dwg.circle((70, 15), class_="terminal-button maximize-button")
    maximize_btn.set_desc(title="Maximize")
    dwg.add(maximize_btn)
    
    # Terminal title
    title = dwg.text("vivek@github: ~/terminal", insert=(width/2, 18), 
                    text_anchor="middle", class_="terminal-title")
    dwg.add(title)
    
    # Add a glowing hint about interactivity
    hint_bg = dwg.rect((width-250, 40), (240, 30), rx=5, ry=5, fill="#0064C8")
    dwg.add(hint_bg)
    
    hint_text = dwg.text("✨ Interactive Terminal Demo", insert=(width-130, 60), 
                       text_anchor="middle", class_="highlight glow")
    dwg.add(hint_text)
    
    # Terminal title
    dwg.add(dwg.text(f"{stats['login']}'s GitHub Terminal", (width/2, 20), text_anchor="middle", class_="terminal-title"))
    
    # Terminal content
    y_pos = 60  # Starting y position for content
    line_height = 20  # Height of each line
    
    # Welcome message
    dwg.add(dwg.text("Welcome to vivek@github Terminal!", (20, y_pos), class_="terminal welcome"))
    y_pos += line_height
    
    dwg.add(dwg.text("Type a command below or click on a suggested command:", (20, y_pos), class_="terminal info"))
    y_pos += line_height * 1.5
    
    # Available commands as clickable buttons
    commands = [
        ("help", "Show available commands"),
        ("whoami", "Display user info"),
        ("stats", "GitHub statistics"),
        ("repos", "Top repositories"),
        ("skills", "Technical skills"),
        ("projects", "Featured projects"),
        ("contact", "Contact information")
    ]
    
    # Create command buttons
    button_width = 100
    button_height = 30
    button_margin = 10
    buttons_per_row = 3
    
    for i, (cmd, desc) in enumerate(commands):
        row = i // buttons_per_row
        col = i % buttons_per_row
        
        x = 20 + col * (button_width + button_margin)
        y = y_pos + row * (button_height + button_margin)
        
        # Button group with hover effect
        button = dwg.g(class_="command-button", onclick=f"executeCommand('{cmd}')")
        
        # Button background
        button.add(dwg.rect((x, y), (button_width, button_height), 
                           fill="#21262d", rx=5, ry=5, 
                           stroke="#30363d", stroke_width=1))
        
        # Button text
        button.add(dwg.text(cmd, (x + button_width/2, y + button_height/2 + 5), 
                           text_anchor="middle", class_="terminal command"))
        
        dwg.add(button)
    
    # Move y position past the buttons
    y_pos += (len(commands) // buttons_per_row + 1) * (button_height + button_margin) + line_height
    
    # Command prompt area (fixed at bottom)
    prompt_y = height - 40
    dwg.add(dwg.rect((10, prompt_y - 5), (width - 20, 30), rx=5, ry=5, fill="#0d1117", stroke="#30363d", stroke_width=1))
    dwg.add(dwg.text("$ ", (20, prompt_y + 15), class_="terminal prompt"))
    
    # Input text area
    dwg.add(dwg.text("", (35, prompt_y + 15), class_="terminal command", id="input-text"))
    
    # Blinking cursor
    cursor = dwg.rect((35, prompt_y + 3), (2, 18), fill="#c9d1d9", id="cursor")
    cursor.add(dwg.animate("opacity", "1;0;1", dur="1s", repeatCount="indefinite"))
    dwg.add(cursor)
    
    # Output area
    output_area = dwg.g(id="output-area")
    
    # Add JavaScript for interactivity
    script = dwg.script(content="""
        // Make SVG focusable to capture keyboard events
        document.querySelector('svg').setAttribute('tabindex', '0');
        
        // Current command being typed
        let currentCommand = "";
        let cursorPosition = 35; // Initial cursor position
        let commandHistory = [];
        let historyIndex = -1;
        
        // Command output data
        const commandOutputs = {
            help: [
                "Available commands:",
                "help        - Show this help message",
                "whoami      - Display basic info about me",
                "stats       - Show my GitHub statistics",
                "repos       - List my top repositories",
                "projects    - Show my featured projects",
                "skills      - List my technical skills",
                "contact     - Show contact information"
            ],
            whoami: [
                "Name: """ + stats["name"] + """",
                "GitHub: @""" + stats["login"] + """",
                "Bio: """ + (stats["bio"] or "Not specified") + """",
                "Location: """ + (stats["location"] or "Not specified") + """",
                "GitHub user since: """ + stats["created_at"].split("T")[0] + """"
            ],
            stats: [
                "📊 GitHub Statistics",
                "-------------------",
                "Public Repositories: """ + str(stats["public_repos"]) + """",
                "Total Stars: """ + str(stats["total_stars"]) + """",
                "Followers: """ + str(stats["followers"]) + """",
                "Following: """ + str(stats["following"]) + """",
                "Pull Requests: """ + str(stats["pull_requests"]) + """",
                "Merged PRs: """ + str(stats["merged_pull_requests"]) + """",
                "Issues Opened: """ + str(stats["issues"]) + """",
                "Contributions (Last Year): """ + str(stats["contributions_last_year"]) + """"
            ],
            repos: [
                "📚 Top Repositories",
                "-------------------"
            ],
            skills: [
                "🛠️ Technical Skills",
                "------------------",
                "💻 Programming Languages: Python, JavaScript, Java",
                "🌐 Web Technologies: HTML5, CSS3, GraphQL",
                "🛠️ Frameworks & Libraries: React, Node.js, Django",
                "📦 Databases: MongoDB, MySQL, PostgreSQL",
                "🖥️ DevOps & Tools: Docker, Git, AWS",
                "🔒 Cybersecurity & Ethical Hacking: Nmap, Metasploit, Wireshark, Burp Suite, Aircrack-ng, Nikto, WifiTe"
            ],
            projects: [
                "🚀 Featured Projects",
                "------------------",
                "1. ANDRO - A cloud based remote android managment suite",
                "   GitHub: https://github.com/AryanVBW/ANDRO",
                "",
                "2. LinuxDroid - Linux on Android e.g Kali nethuter,Ubatu GUI/CLI,kali GUI,Arch Linux CLI",
                "   GitHub: https://github.com/AryanVBW/LinuxDroid",
                "",
                "3. WifiJAM - Python WiFi Deauthentication Script",
                "   GitHub: https://github.com/AryanVBW/WIFIjam"
            ],
            contact: [
                "📫 Contact Information",
                "---------------------",
                "Email: vivek.aryanvbw@gmail.com",
                "Business Email: admin@AryanVBW.live",
                "LinkedIn: https://www.linkedin.com/in/vivek-wagadare-b677a9216",
                "Twitter: https://x.com/vivekwagadare",
                "Instagram: https://instagram.com/vivekbw",
                "Instagram (Tech): https://instagram.com/aryan_technolog1es",
                "Website: https://vivek.aryanvbw.live"
            ]
        };
        
        // Add top repos to repos command
        """)
    
    # Add repos data
    repos_script = "const reposList = ["
    for i, repo in enumerate(stats.get("top_repos", [])[:5]):
        repos_script += f'"{i+1}. {repo["name"]} - ⭐ {repo["stars"]} - {repo.get("description", "No description")}",'
    repos_script += "];\n"
    repos_script += "commandOutputs.repos = commandOutputs.repos.concat(reposList);\n"
    
    script.append(repos_script)
    
    # Continue with the interactive script
    script.append("""
        // Handle keyboard input for the terminal
        document.getElementById('terminal-bg').addEventListener('click', function() {
            document.querySelector('svg').focus();
        });
        
        document.querySelector('svg').addEventListener('keydown', function(event) {
            // Handle Enter key (execute command)
            if (event.key === 'Enter' && currentCommand.trim() !== '') {
                // Add to history
                commandHistory.unshift(currentCommand);
                if (commandHistory.length > 10) commandHistory.pop();
                historyIndex = -1;
                
                // Execute command
                executeCommand(currentCommand);
                currentCommand = '';
                updateInputDisplay();
            } 
            // Handle Backspace key
            else if (event.key === 'Backspace') {
                if (currentCommand.length > 0) {
                    currentCommand = currentCommand.substring(0, currentCommand.length - 1);
                    updateInputDisplay();
                }
            }
            // Handle Up Arrow (command history)
            else if (event.key === 'ArrowUp') {
                if (commandHistory.length > 0 && historyIndex < commandHistory.length - 1) {
                    historyIndex++;
                    currentCommand = commandHistory[historyIndex];
                    updateInputDisplay();
                }
            }
            // Handle Down Arrow (command history)
            else if (event.key === 'ArrowDown') {
                if (historyIndex > 0) {
                    historyIndex--;
                    currentCommand = commandHistory[historyIndex];
                } else if (historyIndex === 0) {
                    historyIndex = -1;
                    currentCommand = '';
                }
                updateInputDisplay();
            }
            // Handle Tab key (command completion)
            else if (event.key === 'Tab') {
                event.preventDefault();
                const commands = Object.keys(commandOutputs);
                const matchingCommands = commands.filter(cmd => cmd.startsWith(currentCommand));
                
                if (matchingCommands.length === 1) {
                    currentCommand = matchingCommands[0];
                    updateInputDisplay();
                }
            }
            // Handle regular character input
            else if (event.key.length === 1) {
                currentCommand += event.key;
                updateInputDisplay();
            }
        });
        
        // Update the input display and cursor position
        function updateInputDisplay() {
            // Update input text
            const inputText = document.getElementById('input-text');
            inputText.textContent = currentCommand;
            
            // Update cursor position
            const cursor = document.getElementById('cursor');
            cursor.setAttribute('x', (35 + currentCommand.length * 8));
        }
        
        // Function to execute a command
        function executeCommand(command) {
            // Normalize command (trim and lowercase)
            command = command.trim().toLowerCase();
            
            // Clear previous output
            const outputArea = document.getElementById('output-area');
            while (outputArea.firstChild) {
                outputArea.removeChild(outputArea.firstChild);
            }
            
            // Add command to prompt with animation
            const promptText = document.createElementNS("http://www.w3.org/2000/svg", "text");
            promptText.setAttribute("x", "20");
            promptText.setAttribute("y", "80");
            promptText.setAttribute("class", "terminal prompt");
            promptText.textContent = "vivek@github:~$ ";
            promptText.style.opacity = 0;
            outputArea.appendChild(promptText);
            
            const commandText = document.createElementNS("http://www.w3.org/2000/svg", "text");
            commandText.setAttribute("x", "135");
            commandText.setAttribute("y", "80");
            commandText.setAttribute("class", "terminal command");
            commandText.textContent = command;
            commandText.style.opacity = 0;
            outputArea.appendChild(commandText);
            
            // Animate the appearance
            setTimeout(() => {
                promptText.style.opacity = 1;
                commandText.style.opacity = 1;
            }, 100);
            
            // Add output with animation delay
            setTimeout(() => {
                if (commandOutputs[command]) {
                    let yPos = 110;
                    let delay = 100;
                    
                    commandOutputs[command].forEach((line, index) => {
                        setTimeout(() => {
                            const outputLine = document.createElementNS("http://www.w3.org/2000/svg", "text");
                            outputLine.setAttribute("x", "20");
                            outputLine.setAttribute("y", yPos.toString());
                            outputLine.setAttribute("class", `terminal output ${command}`);
                            outputLine.textContent = line;
                            outputLine.style.opacity = 0;
                            outputArea.appendChild(outputLine);
                            
                            // Fade in animation
                            setTimeout(() => {
                                outputLine.style.opacity = 1;
                            }, 50);
                            
                            yPos += 20;
                        }, delay * index);
                    });
                    
                    // After all output is shown, show a new prompt
                    setTimeout(() => {
                        showNewPrompt();
                    }, delay * commandOutputs[command].length + 300);
                    
                } else if (command === 'clear') {
                    // Clear command - just clear the output area
                    showNewPrompt();
                    return;
                } else if (command === 'date') {
                    // Date command
                    const date = new Date().toLocaleString();
                    const dateLine = document.createElementNS("http://www.w3.org/2000/svg", "text");
                    dateLine.setAttribute("x", "20");
                    dateLine.setAttribute("y", "110");
                    dateLine.setAttribute("class", "terminal output");
                    dateLine.textContent = date;
                    dateLine.style.opacity = 0;
                    outputArea.appendChild(dateLine);
                    
                    setTimeout(() => {
                        dateLine.style.opacity = 1;
                        setTimeout(() => {
                            showNewPrompt();
                        }, 300);
                    }, 100);
                    
                } else if (command.startsWith('echo ')) {
                    // Echo command
                    const text = command.substring(5);
                    const echoLine = document.createElementNS("http://www.w3.org/2000/svg", "text");
                    echoLine.setAttribute("x", "20");
                    echoLine.setAttribute("y", "110");
                    echoLine.setAttribute("class", "terminal output");
                    echoLine.textContent = text;
                    echoLine.style.opacity = 0;
                    outputArea.appendChild(echoLine);
                    
                    setTimeout(() => {
                        echoLine.style.opacity = 1;
                        setTimeout(() => {
                            showNewPrompt();
                        }, 300);
                    }, 100);
                    
                } else {
                    const errorLine = document.createElementNS("http://www.w3.org/2000/svg", "text");
                    errorLine.setAttribute("x", "20");
                    errorLine.setAttribute("y", "110");
                    errorLine.setAttribute("class", "terminal error");
                    errorLine.textContent = `Command not found: ${command}. Type 'help' to see available commands.`;
                    errorLine.style.opacity = 0;
                    outputArea.appendChild(errorLine);
                    
                    setTimeout(() => {
                        errorLine.style.opacity = 1;
                        setTimeout(() => {
                            showNewPrompt();
                        }, 300);
                    }, 100);
                }
            }, 200);
        }
        
        // Function to show a new prompt after command execution
        function showNewPrompt() {
            const outputArea = document.getElementById('output-area');
            const lastElement = outputArea.lastElementChild;
            const lastY = lastElement ? parseInt(lastElement.getAttribute('y')) + 30 : 140;
            
            const newPrompt = document.createElementNS("http://www.w3.org/2000/svg", "text");
            newPrompt.setAttribute("x", "20");
            newPrompt.setAttribute("y", lastY.toString());
            newPrompt.setAttribute("class", "terminal prompt");
            newPrompt.textContent = "vivek@github:~$ ";
            newPrompt.style.opacity = 0;
            outputArea.appendChild(newPrompt);
            
            setTimeout(() => {
                newPrompt.style.opacity = 1;
                
                // Add blinking cursor at the new prompt
                const newCursor = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                newCursor.setAttribute("x", "135");
                newCursor.setAttribute("y", (lastY - 15).toString());
                newCursor.setAttribute("width", "8");
                newCursor.setAttribute("height", "16");
                newCursor.setAttribute("fill", "#FFFFFF");
                newCursor.setAttribute("class", "cursor");
                outputArea.appendChild(newCursor);
                
                // After a delay, show typing animation for a new command
                setTimeout(() => {
                    // Choose a random command to demonstrate
                    const demoCommands = ['stats', 'whoami', 'skills', 'projects'];
                    const randomCommand = demoCommands[Math.floor(Math.random() * demoCommands.length)];
                    
                    // Create text element for the typing command
                    const typingCommand = document.createElementNS("http://www.w3.org/2000/svg", "text");
                    typingCommand.setAttribute("x", "135");
                    typingCommand.setAttribute("y", lastY.toString());
                    typingCommand.setAttribute("class", "terminal command");
                    typingCommand.textContent = "";
                    outputArea.appendChild(typingCommand);
                    
                    // Simulate typing
                    let i = 0;
                    const typeInterval = setInterval(() => {
                        if (i < randomCommand.length) {
                            typingCommand.textContent += randomCommand.charAt(i);
                            newCursor.setAttribute("x", (135 + typingCommand.textContent.length * 8).toString());
                            i++;
                        } else {
                            clearInterval(typeInterval);
                            setTimeout(() => {
                                // Execute the command
                                executeCommand(randomCommand);
                            }, 500);
                        }
                    }, 150);
                }, 1000);
            }, 200);
        }
        
        // Show help by default and set up terminal with typing animation
        window.onload = function() {
            // Show welcome message with typing effect
            setTimeout(() => {
                typeCommand('help', () => {
                    executeCommand('help');
                });
            }, 500);
            
            // Focus on the SVG to enable keyboard input
            document.querySelector('svg').focus();
        };
        
        // Function to simulate typing
        function typeCommand(command, callback) {
            let i = 0;
            const inputText = document.getElementById('input-text');
            const typeInterval = setInterval(() => {
                if (i < command.length) {
                    inputText.textContent += command.charAt(i);
                    // Update cursor position
                    const cursor = document.getElementById('cursor');
                    cursor.setAttribute('x', (135 + inputText.textContent.length * 8));
                    i++;
                } else {
                    clearInterval(typeInterval);
                    setTimeout(() => {
                        inputText.textContent = '';
                        if (callback) callback();
                    }, 500);
                }
            }, 100);
        }
        
        // Make SVG focusable
        document.querySelector('svg').setAttribute('tabindex', '0');
    """)
    
    dwg.add(script)
    dwg.add(output_area)
    
    # Save SVG
    dwg.save(pretty=True)
    print(f"SVG terminal created at {output_path}")

def main():
    # Set the GitHub username
    username = "AryanVBW"  # Replace with your GitHub username
    
    # Get stats
    stats = get_github_stats(username)
    
    # Create SVG terminal
    create_terminal_svg(stats, "terminal.svg")
    
    print(f"Terminal SVG generated for {username}")

if __name__ == "__main__":
    main()
