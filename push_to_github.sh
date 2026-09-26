#!/bin/bash

# GitHub Push Helper Script
# Makes it easy to push your project to GitHub

echo "=================================="
echo "🚀 GitHub Push Helper"
echo "=================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository"
    echo "   Run: git init"
    exit 1
fi

# Get GitHub username
read -p "Enter your GitHub username: " username

if [ -z "$username" ]; then
    echo "❌ Error: Username cannot be empty"
    exit 1
fi

# Repository name
repo_name="fde-nyc-taxi-pipeline"

echo ""
echo "📦 Repository: https://github.com/$username/$repo_name"
echo ""
echo "⚠️  IMPORTANT: Before running this script:"
echo "   1. Go to https://github.com/new"
echo "   2. Create a new repository named: $repo_name"
echo "   3. Make it PUBLIC"
echo "   4. Do NOT initialize with README (we already have one)"
echo ""

read -p "Have you created the repository on GitHub? (yes/no): " created

if [ "$created" != "yes" ]; then
    echo ""
    echo "Please create the repository first, then run this script again."
    echo "Visit: https://github.com/new"
    exit 0
fi

echo ""
echo "🔧 Setting up remote..."

# Remove existing remote if any
git remote remove origin 2>/dev/null

# Add new remote
git remote add origin "https://github.com/$username/$repo_name.git"

echo "✅ Remote added: origin -> https://github.com/$username/$repo_name.git"
echo ""
echo "📤 Pushing to GitHub..."
echo ""

# Add all files
git add .

# Commit if there are changes
if ! git diff --cached --quiet; then
    echo "📝 Committing changes..."
    git commit -m "Enhanced: Professional README and advanced dashboard

- Added enterprise-grade README with badges and documentation
- Created advanced interactive dashboard with charts
- Improved project structure and documentation
- Added GitHub push helper script

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
fi

# Set branch to main
git branch -M main

# Push to GitHub
echo ""
echo "Pushing to main branch..."
if git push -u origin main; then
    echo ""
    echo "=================================="
    echo "✅ SUCCESS! Project pushed to GitHub"
    echo "=================================="
    echo ""
    echo "🔗 Your repository:"
    echo "   https://github.com/$username/$repo_name"
    echo ""
    echo "📊 View your project online:"
    echo "   https://github.com/$username/$repo_name"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Record your Loom video (see LOOM_VIDEO_GUIDE.md)"
    echo "   2. Add the Loom link to README.md"
    echo "   3. Push the update: git add README.md && git commit -m 'Add demo video' && git push"
    echo "   4. Submit both URLs (GitHub + Loom)"
    echo ""
else
    echo ""
    echo "=================================="
    echo "❌ ERROR: Push failed"
    echo "=================================="
    echo ""
    echo "Common issues:"
    echo "  1. Repository doesn't exist on GitHub"
    echo "     → Create it at https://github.com/new"
    echo ""
    echo "  2. Authentication failed"
    echo "     → You may need to use a Personal Access Token"
    echo "     → See: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"
    echo ""
    echo "  3. Repository already exists with content"
    echo "     → Try: git pull origin main --rebase"
    echo "     → Then: git push -u origin main"
    echo ""
    exit 1
fi
