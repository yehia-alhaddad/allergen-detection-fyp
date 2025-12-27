"""Create a GitHub repository via API.
Requires env var GITHUB_TOKEN with repo scope.
Usage: python scripts/create_github_repo.py <repo_name> [private]
"""
import os, sys, requests

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/create_github_repo.py <repo_name> [private]")
        sys.exit(1)
    repo_name = sys.argv[1]
    private = (sys.argv[2].lower() == 'true') if len(sys.argv) > 2 else True

    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Set GITHUB_TOKEN env var with 'repo' scope.")
        sys.exit(1)

    # Get user
    u = requests.get('https://api.github.com/user', headers={'Authorization': f'Bearer {token}'}).json()
    login = u.get('login')
    if not login:
        print("Failed to retrieve user; check token.")
        sys.exit(1)

    # Create repo
    payload = {
        'name': repo_name,
        'private': private,
        'description': 'Allergen detection system (FastAPI + Next.js)'
    }
    r = requests.post('https://api.github.com/user/repos', json=payload, headers={'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'})
    if r.status_code >= 300:
        print("Failed:", r.status_code, r.text)
        sys.exit(1)
    j = r.json()
    print("Created:", j.get('full_name'))
    print("Clone URL:", j.get('clone_url'))
    print("SSH URL:", j.get('ssh_url'))

if __name__ == '__main__':
    main()
