#!/bin/bash
# Script to deploy the HTML terminal to the user's website

# Make the script executable
chmod +x terminal.html

# Copy the terminal.html to the docs directory (if it exists)
if [ -d "docs" ]; then
  cp terminal.html docs/
  echo "Copied terminal.html to docs/ directory"
fi

# Instructions for manual deployment
echo "===== TERMINAL DEPLOYMENT INSTRUCTIONS ====="
echo "To deploy the interactive HTML terminal to your website:"
echo "1. Upload terminal.html to your web server"
echo "2. Make sure it's accessible at https://vivek.aryanvbw.live/terminal.html"
echo "3. The terminal will automatically demonstrate your GitHub stats"
echo ""
echo "For GitHub Pages deployment:"
echo "1. If using GitHub Pages, ensure terminal.html is in your docs/ folder or root"
echo "2. Commit and push the changes to your repository"
echo "3. The terminal will be available at https://yourusername.github.io/terminal.html"
echo "=========================================="
