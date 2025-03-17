// GitHub Terminal - Interactive GitHub Profile
document.addEventListener('DOMContentLoaded', function() {
  const terminal = document.getElementById('github-terminal');
  const terminalOutput = document.getElementById('terminal-output');
  const terminalInput = document.getElementById('terminal-input');
  const promptSpan = document.getElementById('prompt');
  
  let githubData = null;
  let commandHistory = [];
  let historyIndex = -1;
  
  // Load GitHub stats
  async function loadGitHubStats() {
    try {
      const response = await fetch('https://raw.githubusercontent.com/AryanVBW/AryanVBW/main/github-stats.json');
      if (!response.ok) {
        throw new Error('Failed to load GitHub stats');
      }
      githubData = await response.json();
      updatePrompt();
    } catch (error) {
      console.error('Error loading GitHub stats:', error);
      appendOutput('Error loading GitHub stats. Some commands may not work properly.', 'error');
    }
  }
  
  // Initialize terminal
  function initTerminal() {
    loadGitHubStats();
    focusInput();
    
    // Welcome message
    appendOutput('Welcome to AryanVBW\'s GitHub Terminal!', 'welcome');
    appendOutput('Type "help" to see available commands.', 'info');
    appendOutput('', 'spacer');
  }
  
  // Focus input field
  function focusInput() {
    terminalInput.focus();
  }
  
  // Update prompt with username
  function updatePrompt() {
    const username = githubData ? githubData.login : 'guest';
    promptSpan.textContent = `${username}@github:~$ `;
  }
  
  // Append output to terminal
  function appendOutput(text, className = '') {
    const output = document.createElement('div');
    output.className = `terminal-line ${className}`;
    
    if (Array.isArray(text)) {
      // For multi-line output
      text.forEach((line, index) => {
        if (index > 0) {
          output.appendChild(document.createElement('br'));
        }
        output.appendChild(document.createTextNode(line));
      });
    } else {
      output.textContent = text;
    }
    
    terminalOutput.appendChild(output);
    
    // Auto scroll to bottom
    terminal.scrollTop = terminal.scrollHeight;
  }
  
  // Process commands
  function processCommand(cmd) {
    // Add to history
    if (cmd.trim() !== '') {
      commandHistory.unshift(cmd);
      historyIndex = -1;
      
      // Limit history size
      if (commandHistory.length > 50) {
        commandHistory.pop();
      }
    }
    
    // Echo command
    appendOutput(`${promptSpan.textContent}${cmd}`, 'command');
    
    // Process empty command
    if (cmd.trim() === '') {
      return;
    }
    
    // Parse command and arguments
    const args = cmd.trim().split(' ');
    const command = args.shift().toLowerCase();
    
    // Execute command
    executeCommand(command, args);
  }
  
  // Execute specific command
  function executeCommand(command, args) {
    switch (command) {
      case 'help':
        showHelp();
        break;
      case 'clear':
        clearTerminal();
        break;
      case 'whoami':
        showWhoami();
        break;
      case 'stats':
        showStats();
        break;
      case 'repos':
        showRepos();
        break;
      case 'contact':
        showContact();
        break;
      case 'skills':
        showSkills();
        break;
      case 'projects':
        showProjects();
        break;
      case 'about':
        showAbout();
        break;
      case 'date':
        showDate();
        break;
      case 'echo':
        echoText(args);
        break;
      case 'ls':
        listItems();
        break;
      case 'cat':
        catFile(args);
        break;
      default:
        appendOutput(`Command not found: ${command}. Type 'help' to see available commands.`, 'error');
    }
  }
  
  // Command implementations
  function showHelp() {
    appendOutput([
      'Available commands:',
      '',
      'help        - Show this help message',
      'clear       - Clear the terminal',
      'whoami      - Display basic info about me',
      'stats       - Show my GitHub statistics',
      'repos       - List my top repositories',
      'projects    - Show my featured projects',
      'skills      - List my technical skills',
      'about       - About me',
      'contact     - Show contact information',
      'date        - Show current date and time',
      'echo [text] - Echo the text',
      'ls          - List available "files"',
      'cat [file]  - Show content of a "file"'
    ], 'help');
  }
  
  function clearTerminal() {
    terminalOutput.innerHTML = '';
  }
  
  function showWhoami() {
    if (!githubData) {
      appendOutput('GitHub data not loaded yet. Try again later.', 'error');
      return;
    }
    
    appendOutput([
      `Name: ${githubData.name}`,
      `GitHub: @${githubData.login}`,
      `Bio: ${githubData.bio || 'Not specified'}`,
      `Location: ${githubData.location || 'Not specified'}`,
      `Company: ${githubData.company || 'Not specified'}`,
      `GitHub user since: ${new Date(githubData.created_at).toLocaleDateString()}`
    ], 'info');
  }
  
  function showStats() {
    if (!githubData) {
      appendOutput('GitHub data not loaded yet. Try again later.', 'error');
      return;
    }
    
    appendOutput([
      '📊 GitHub Statistics',
      '-------------------',
      `Public Repositories: ${githubData.public_repos}`,
      `Total Stars: ${githubData.total_stars}`,
      `Followers: ${githubData.followers}`,
      `Following: ${githubData.following}`,
      `Pull Requests: ${githubData.pull_requests}`,
      `Merged PRs: ${githubData.merged_pull_requests}`,
      `Issues Opened: ${githubData.issues}`,
      `Contributions (Last Year): ${githubData.contributions_last_year}`
    ], 'stats');
  }
  
  function showRepos() {
    if (!githubData || !githubData.top_repos) {
      appendOutput('GitHub data not loaded yet. Try again later.', 'error');
      return;
    }
    
    const repoLines = ['📚 Top Repositories', '-------------------'];
    
    githubData.top_repos.forEach((repo, index) => {
      repoLines.push(`${index + 1}. ${repo.name} - ⭐ ${repo.stars} - ${repo.description || 'No description'}`);
    });
    
    appendOutput(repoLines, 'repos');
  }
  
  function showContact() {
    appendOutput([
      '📫 Contact Information',
      '---------------------',
      'Email: vivek.aryanvbw@gmail.com',
      'Business Email: admin@AryanVBW.live',
      'LinkedIn: https://www.linkedin.com/in/vivek-wagadare-b677a9216',
      'Twitter: https://x.com/vivekwagadare',
      'Instagram: https://instagram.com/vivekbw',
      'Instagram (Tech): https://instagram.com/aryan_technolog1es',
      'Website: https://vivek.aryanvbw.live'
    ], 'contact');
  }
  
  function showSkills() {
    appendOutput([
      '🛠️ Technical Skills',
      '------------------',
      '💻 Programming Languages: Python, JavaScript, Java',
      '🌐 Web Technologies: HTML5, CSS3, GraphQL',
      '🛠️ Frameworks & Libraries: React, Node.js, Django',
      '📦 Databases: MongoDB, MySQL, PostgreSQL',
      '🖥️ DevOps & Tools: Docker, Git, AWS',
      '🔒 Cybersecurity & Ethical Hacking: Nmap, Metasploit, Wireshark, Burp Suite, Aircrack-ng, Nikto, WifiTe'
    ], 'skills');
  }
  
  function showProjects() {
    appendOutput([
      '🚀 Featured Projects',
      '------------------',
      '1. ANDRO - A cloud based remote android managment suite',
      '   GitHub: https://github.com/AryanVBW/ANDRO',
      '',
      '2. LinuxDroid - Linux on Android e.g Kali nethuter,Ubatu GUI/CLI,kali GUI,Arch Linux CLI',
      '   GitHub: https://github.com/AryanVBW/LinuxDroid',
      '',
      '3. WifiJAM - Python WiFi Deauthentication Script',
      '   GitHub: https://github.com/AryanVBW/WIFIjam'
    ], 'projects');
  }
  
  function showAbout() {
    appendOutput([
      'About Me',
      '--------',
      'I\'m a passionate developer, coder, and technology geek with a knack for hacking into challenges and solving them one line of code at a time.',
      '',
      '🔭 I\'m currently working on https://vivek.aryanvbw.live',
      '🌱 I\'m constantly learning and exploring new technologies and tools.',
      '📫 How to reach me: vivek.aryanvbw@gmail.com'
    ], 'about');
  }
  
  function showDate() {
    const now = new Date();
    appendOutput(`Current date: ${now.toLocaleString()}`, 'date');
  }
  
  function echoText(args) {
    appendOutput(args.join(' '), 'echo');
  }
  
  function listItems() {
    appendOutput([
      'about.txt',
      'contact.txt',
      'projects.txt',
      'skills.txt',
      'stats.txt'
    ], 'ls');
  }
  
  function catFile(args) {
    if (args.length === 0) {
      appendOutput('Usage: cat [file]', 'error');
      return;
    }
    
    const file = args[0];
    
    switch (file) {
      case 'about.txt':
        showAbout();
        break;
      case 'contact.txt':
        showContact();
        break;
      case 'projects.txt':
        showProjects();
        break;
      case 'skills.txt':
        showSkills();
        break;
      case 'stats.txt':
        showStats();
        break;
      default:
        appendOutput(`File not found: ${file}`, 'error');
    }
  }
  
  // Handle input submission
  terminalInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      const command = terminalInput.value;
      terminalInput.value = '';
      processCommand(command);
    } else if (event.key === 'ArrowUp') {
      // Navigate command history (up)
      event.preventDefault();
      if (commandHistory.length > 0 && historyIndex < commandHistory.length - 1) {
        historyIndex++;
        terminalInput.value = commandHistory[historyIndex];
        // Move cursor to end
        setTimeout(() => {
          terminalInput.selectionStart = terminalInput.selectionEnd = terminalInput.value.length;
        }, 0);
      }
    } else if (event.key === 'ArrowDown') {
      // Navigate command history (down)
      event.preventDefault();
      if (historyIndex > 0) {
        historyIndex--;
        terminalInput.value = commandHistory[historyIndex];
      } else if (historyIndex === 0) {
        historyIndex = -1;
        terminalInput.value = '';
      }
    } else if (event.key === 'Tab') {
      // Simple tab completion
      event.preventDefault();
      const input = terminalInput.value.toLowerCase();
      
      const commands = [
        'help', 'clear', 'whoami', 'stats', 'repos', 'contact', 
        'skills', 'projects', 'about', 'date', 'echo', 'ls', 'cat'
      ];
      
      for (const cmd of commands) {
        if (cmd.startsWith(input)) {
          terminalInput.value = cmd;
          break;
        }
      }
    }
  });
  
  // Handle terminal clicks (focus input)
  terminal.addEventListener('click', focusInput);
  
  // Initialize
  initTerminal();
});
