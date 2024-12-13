# write a python script to scrap all of https://github.com/sintel-dev/Orion
import os
import base64

from github import Github, Auth

def save_content(path, content):
    """Helper to save content to file"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        if isinstance(content, str):
            f.write(content.encode('utf-8'))
        else:
            f.write(content)

def scrape_github_repo(owner="sintel-dev", repo="Orion", token=None, output_dir=None):
    """
    Scrape content from a GitHub repository using PyGithub.
    Collects source code, documentation, README, and issues.
    
    Args:
        owner (str): 
            Repository owner
        repo (str):
            Repository name
        token (str): 
            GitHub access token
        output_dir (str):
            Path to save files.
    """
    output_dir = output_dir or f"{repo}_content"

    if token:
        auth = Auth.Token(token)
        g = Github(auth=auth)
    else:
        g = Github()
    
    repository = g.get_repo(f"{owner}/{repo}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get and save README
    try:
        readme = repository.get_readme()
        save_content(f"{output_dir}/README.md", base64.b64decode(readme.content))
        print("Downloaded README")
    except Exception as e:
        print(f"Error downloading README: {e}")
    
    # Get and save source code and documentation
    contents = repository.get_contents("orion") + repository.get_contents("docs")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repository.get_contents(file_content.path))
        else:
            try:
                print(f"Downloading {file_content.path}")
                file_path = os.path.join(output_dir, file_content.path)
                save_content(file_path, base64.b64decode(file_content.content))
            except Exception as e:
                print(f"Error downloading {file_content.path}: {e}")
    
    # Get and save issues
    issues_dir = f"{output_dir}/issues"
    os.makedirs(issues_dir, exist_ok=True)
    
    issues = repository.get_issues(state='all')
    for issue in issues:
        try:
            issue_content = {
                'number': issue.number,
                'title': issue.title,
                'body': issue.body,
                'state': issue.state,
                'created_at': str(issue.created_at),
                'comments': [comment.body for comment in issue.get_comments()]
            }
            
            file_path = f"{issues_dir}/issue_{issue.number}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                for key, value in issue_content.items():
                    f.write(f"{key}: {value}\n\n")
            
            print(f"Downloaded issue #{issue.number}")
        except Exception as e:
            print(f"Error downloading issue #{issue.number}: {e}")

if __name__ == "__main__":
    token = os.getenv('GITHUB_TOKEN')
    scrape_github_repo(token=token, output_dir='orion_contents')

