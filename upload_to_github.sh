#!/bin/bash

echo "🚀 Uploading Semantic EPE to GitHub..."

# Replace YOUR_USERNAME with your actual GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ GitHub username required!"
    exit 1
fi

echo "📡 Adding GitHub remote..."
git remote add origin https://github.com/$GITHUB_USERNAME/Semantic-EPE.git

echo "🔄 Setting main branch..."
git branch -M main

echo "⬆️ Pushing to GitHub..."
git push -u origin main

echo "🏷️ Pushing tag..."
git push origin v1.0.0

echo "✅ Upload completed!"
echo "🌐 Repository available at: https://github.com/$GITHUB_USERNAME/Semantic-EPE"
echo ""
echo "🎯 Next steps:"
echo "1. Visit your repository on GitHub"
echo "2. Add topics: euring, epe, ornithology, bird-ringing, semantic-web, fastapi, react"
echo "3. Enable GitHub Pages for documentation (optional)"
echo "4. Share with colleagues!"