#!/bin/bash

REPO_URL="https://android.googlesource.com/platform/frameworks/support"
TARGET_DIR="/tmp/androidx-clone-test"

echo "🧹 Cleaning up any previous test directory..."
rm -rf "$TARGET_DIR"

echo "🚀 Starting full clone of AndroidX monorepo..."
echo "URL: $REPO_URL"
echo "This might take a while. Please wait..."
echo "------------------------------------------------"

# Start timer
START_TIME=$(date +%s)

# Run clone
git clone "$REPO_URL" "$TARGET_DIR"

# End timer
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo "------------------------------------------------"
echo "✅ Clone completed!"
echo "⏱️  Time taken: ${MINUTES}m ${SECONDS}s ($DURATION seconds total)"

echo "📦 Checking disk size..."
SIZE=$(du -sh "$TARGET_DIR" | cut -f1)
echo "💾 Total size on disk: $SIZE"

echo "🧹 Cleaning up test directory..."
rm -rf "$TARGET_DIR"
echo "Done!"
