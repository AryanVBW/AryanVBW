#!/usr/bin/env python3
"""
GitHub Profile Terminal GIF Generator
This script creates an animated terminal GIF for GitHub profiles
"""

import os
import json
import requests
import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import imageio
import textwrap
import time
from bs4 import BeautifulSoup
import numpy as np
import re
from github import Github

# Colors
BACKGROUND_COLOR = (13, 17, 23)  # Dark mode GitHub background
TEXT_COLOR = (201, 209, 217)  # Default text color
PROMPT_COLOR = (126, 231, 135)  # Green prompt
COMMAND_COLOR = (230, 237, 243)  # White command
OUTPUT_COLOR = (165, 214, 255)  # Light blue output
ERROR_COLOR = (248, 81, 73)  # Red error
HEADER_COLOR = (22, 27, 34)  # Terminal header
HELP_COLOR = (210, 168, 255)  # Purple help text
STATS_COLOR = (121, 192, 255)  # Blue stats
WELCOME_COLOR = (126, 231, 135)  # Green welcome
BUTTON_COLORS = {
    "close": (248, 81, 73),      # Red
    "minimize": (250, 194, 76),  # Yellow
    "maximize": (88, 166, 255)   # Blue
}

def get_github_stats(username, token=None):
    """Fetch GitHub statistics for the specified user"""
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    
    # Get user data
    user_url = f"https://api.github.com/users/{username}"
    user_response = requests.get(user_url, headers=headers)
    if user_response.status_code != 200:
        raise Exception(f"Failed to fetch user data: {user_response.status_code}")
    
    user_data = user_response.json()
    
    # Get repositories
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
    repos_response = requests.get(repos_url, headers=headers)
    if repos_response.status_code != 200:
        raise Exception(f"Failed to fetch repositories: {repos_response.status_code}")
    
    repos_data = repos_response.json()
    
    # Calculate total stars
    total_stars = sum(repo["stargazers_count"] for repo in repos_data)
    
    # Get top repositories by stars
    top_repos = sorted(repos_data, key=lambda x: x["stargazers_count"], reverse=True)[:5]
    top_repos_formatted = []
    for repo in top_repos:
        top_repos_formatted.append({
            "name": repo["name"],
            "stars": repo["stargazers_count"],
            "description": repo["description"] or "No description"
        })
    
    # Get contributions from GitHub profile page
    try:
        profile_url = f"https://github.com/{username}"
        profile_response = requests.get(profile_url)
        soup = BeautifulSoup(profile_response.text, 'html.parser')
        
        # Find the contributions element
        contributions_text = soup.select_one('div.js-yearly-contributions h2')
        contributions_last_year = 0
        if contributions_text:
            match = re.search(r'(\d+)', contributions_text.text)
            if match:
                contributions_last_year = int(match.group(1))
    except Exception as e:
        print(f"Failed to fetch contributions: {e}")
        contributions_last_year = 0
    
    # Get pull requests and issues count using GitHub API if token is provided
    pull_requests = 0
    merged_pull_requests = 0
    issues = 0
    
    if token:
        try:
            g = Github(token)
            user = g.get_user(username)
            
            # Count PRs and Issues
            query = f"author:{username} type:pr"
            pull_requests = g.search_issues(query).totalCount
            
            query = f"author:{username} type:pr is:merged"
            merged_pull_requests = g.search_issues(query).totalCount
            
            query = f"author:{username} type:issue"
            issues = g.search_issues(query).totalCount
        except Exception as e:
            print(f"Failed to fetch PR and issue data: {e}")
    
    # Compile stats
    stats = {
        "login": user_data["login"],
        "name": user_data["name"] or user_data["login"],
        "bio": user_data["bio"],
        "location": user_data["location"],
        "public_repos": user_data["public_repos"],
        "followers": user_data["followers"],
        "following": user_data["following"],
        "created_at": user_data["created_at"],
        "total_stars": total_stars,
        "top_repos": top_repos_formatted,
        "contributions_last_year": contributions_last_year,
        "pull_requests": pull_requests,
        "merged_pull_requests": merged_pull_requests,
        "issues": issues
    }
    
    return stats

def create_frame(width, height, stats, command="", output=None, cursor_visible=True, typing_index=None):
    """Create a single frame of the terminal animation"""
    # Create a new image with the specified dimensions
    image = Image.new("RGB", (width, height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)
    
    # Use default font since custom fonts can be problematic
    font = ImageFont.load_default()
    bold_font = ImageFont.load_default()
    
    # Attempt to use a better font if available on the system
    try:
        # Try to use a system font that's likely to be available
        system_fonts = [
            "Arial.ttf",
            "DejaVuSansMono.ttf",
            "Menlo.ttf",
            "Monaco.ttf",
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/Monaco.ttf",
            "/Library/Fonts/Arial.ttf"
        ]
        
        for system_font in system_fonts:
            try:
                if os.path.exists(system_font):
                    font = ImageFont.truetype(system_font, 12)
                    bold_font = ImageFont.truetype(system_font, 12)
                    break
            except Exception:
                continue
    except Exception:
        # If all else fails, stick with the default font
        pass
    
    # Draw terminal window with rounded corners
    # For now, we'll use a rectangle since PIL doesn't support rounded corners directly
    draw.rectangle([(0, 0), (width, height)], fill=BACKGROUND_COLOR, outline=None)
    
    # Draw terminal header
    draw.rectangle([(0, 0), (width, 30)], fill=HEADER_COLOR, outline=None)
    
    # Draw terminal buttons
    for i, (name, color) in enumerate(BUTTON_COLORS.items()):
        center_x = 20 + i * 25
        center_y = 15
        radius = 6
        draw.ellipse([(center_x - radius, center_y - radius), 
                      (center_x + radius, center_y + radius)], 
                     fill=color)
    
    # Draw terminal title
    title = f"{stats['login']}'s GitHub Terminal"
    title_width = draw.textlength(title, font=bold_font)
    draw.text((width // 2 - title_width // 2, 8), title, fill=TEXT_COLOR, font=bold_font)
    
    # Draw prompt and command
    prompt = "vivek@github:~$ "
    draw.text((20, 50), prompt, fill=PROMPT_COLOR, font=bold_font)
    
    if typing_index is not None and typing_index >= 0:
        # For typing animation
        visible_command = command[:typing_index]
        draw.text((20 + draw.textlength(prompt, font=bold_font), 50), 
                  visible_command, fill=COMMAND_COLOR, font=font)
        
        # Draw cursor at the end of the visible command
        if cursor_visible:
            cursor_x = 20 + draw.textlength(prompt, font=bold_font) + draw.textlength(visible_command, font=font)
            draw.rectangle([(cursor_x, 48), (cursor_x + 8, 64)], fill=TEXT_COLOR)
    else:
        # Regular command display
        draw.text((20 + draw.textlength(prompt, font=bold_font), 50), 
                  command, fill=COMMAND_COLOR, font=font)
        
        # Draw cursor if visible
        if cursor_visible and not output:
            cursor_x = 20 + draw.textlength(prompt, font=bold_font) + draw.textlength(command, font=font)
            draw.rectangle([(cursor_x, 48), (cursor_x + 8, 64)], fill=TEXT_COLOR)
    
    # Draw output if provided
    if output:
        y_position = 80
        for line in output:
            # Handle text wrapping for long lines
            wrapped_lines = textwrap.wrap(line, width=80)  # Adjust width as needed
            for wrapped_line in wrapped_lines:
                draw.text((20, y_position), wrapped_line, fill=OUTPUT_COLOR, font=font)
                y_position += 20
    
    return image

def create_terminal_gif(stats, output_path="terminal.gif"):
    """Create an animated terminal GIF with GitHub stats"""
    width, height = 800, 500
    frames = []
    
    # Command outputs
    command_outputs = {
        "help": [
            "Available commands:",
            "help        - Show this help message",
            "whoami      - Display basic info about me",
            "stats       - Show my GitHub statistics",
            "repos       - List my top repositories",
            "projects    - Show my featured projects",
            "skills      - List my technical skills",
            "contact     - Show contact information"
        ],
        "whoami": [
            f"Name: {stats['name']}",
            f"GitHub: @{stats['login']}",
            f"Bio: {stats['bio'] or 'Not specified'}",
            f"Location: {stats['location'] or 'Not specified'}",
            f"GitHub user since: {stats['created_at'].split('T')[0]}"
        ],
        "stats": [
            "📊 GitHub Statistics",
            "-------------------",
            f"Public Repositories: {stats['public_repos']}",
            f"Total Stars: {stats['total_stars']}",
            f"Followers: {stats['followers']}",
            f"Following: {stats['following']}",
            f"Pull Requests: {stats['pull_requests']}",
            f"Merged PRs: {stats['merged_pull_requests']}",
            f"Issues Opened: {stats['issues']}",
            f"Contributions (Last Year): {stats['contributions_last_year']}"
        ],
        "repos": [
            "📚 Top Repositories",
            "-------------------"
        ] + [f"{i+1}. {repo['name']} - ⭐ {repo['stars']} - {repo['description']}" 
             for i, repo in enumerate(stats.get("top_repos", [])[:5])],
        "skills": [
            "🛠️ Technical Skills",
            "------------------",
            "💻 Programming Languages: Python, JavaScript, Java",
            "🌐 Web Technologies: HTML5, CSS3, GraphQL",
            "🛠️ Frameworks & Libraries: React, Node.js, Django",
            "📦 Databases: MongoDB, MySQL, PostgreSQL",
            "🖥️ DevOps & Tools: Docker, Git, AWS",
            "🔒 Cybersecurity & Ethical Hacking: Nmap, Metasploit, Wireshark, Burp Suite, Aircrack-ng, Nikto, WifiTe"
        ],
        "projects": [
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
        "contact": [
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
    }
    
    # Create intro frames (empty terminal with blinking cursor)
    for i in range(10):
        frames.append(create_frame(width, height, stats, cursor_visible=(i % 2 == 0)))
    
    # Define commands to demonstrate
    demo_commands = ["help", "whoami", "stats", "skills", "projects", "repos", "contact"]
    
    for command in demo_commands:
        # Typing animation frames
        for i in range(len(command) + 1):
            frames.append(create_frame(width, height, stats, command, typing_index=i))
        
        # Pause after typing
        for i in range(5):
            frames.append(create_frame(width, height, stats, command, cursor_visible=(i % 2 == 0)))
        
        # Show output
        frames.append(create_frame(width, height, stats, command, output=command_outputs[command]))
        
        # Pause on output
        for i in range(20):
            frames.append(create_frame(width, height, stats, command, output=command_outputs[command]))
    
    # Save as GIF
    imageio.mimsave(output_path, frames, duration=0.1)
    print(f"Terminal GIF created at {output_path}")

def main():
    # Set the GitHub username
    username = "AryanVBW"  # Replace with your GitHub username
    
    # Get GitHub token from environment variable
    token = os.environ.get("GITHUB_TOKEN")
    
    # Fetch GitHub stats
    stats = get_github_stats(username, token)
    
    # Create terminal GIF
    create_terminal_gif(stats, "terminal.gif")
    print(f"Terminal GIF generated for {username}")

if __name__ == "__main__":
    main()
