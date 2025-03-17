#!/usr/bin/env python3
import os
import json
import requests
from github import Github
from datetime import datetime

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

def main():
    # Set the GitHub username
    username = "AryanVBW"  # Replace with your GitHub username
    
    # Get stats
    stats = get_github_stats(username)
    
    # Save to JSON file
    with open('github-stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Stats updated for {username}")

if __name__ == "__main__":
    main()
