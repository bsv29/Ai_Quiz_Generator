$RepoRoot = "C:\Users\BH V S S N RAJU\Desktop\projects\ai_quiz_generator"
Set-Location $RepoRoot
Write-Output "Working directory: $PWD"

if (-not (Test-Path ".git")) {
    Write-Output "Initializing new git repository..."
    git init
} else {
    Write-Output ".git already exists; using existing repo."
}

Write-Output "Staging all files..."
git add -A

# Check for staged changes
$staged = git diff --cached --name-only
if ($staged) {
    Write-Output "Committing staged changes..."
    git commit -m "Initial commit via script"
} else {
    Write-Output "No staged changes to commit"
}

Write-Output "Setting branch to 'main'..."
git branch -M main

$remoteUrl = "https://github.com/bsv29/Ai_Quiz_Generator.git"
$hasOrigin = git remote | Select-String -Pattern '^origin$'
if ($hasOrigin) {
    Write-Output "Updating existing origin remote to $remoteUrl"
    git remote set-url origin $remoteUrl
} else {
    Write-Output "Adding origin remote $remoteUrl"
    git remote add origin $remoteUrl
}

Write-Output "Attempting to push to origin main..."
try {
    git push -u origin main
    Write-Output "Push finished. Published repo: https://github.com/bsv29/Ai_Quiz_Generator"
} catch {
    Write-Output "Push failed with error: $_"
    Write-Output "Common causes: authentication required. To fix, either:\n - run 'gh auth login' to authenticate with GitHub CLI, or\n - configure a personal access token and use 'git remote set-url origin https://<TOKEN>@github.com/USERNAME/REPO.git', or\n - set up a credential helper. Then re-run: git push -u origin main"
    exit 1
}
