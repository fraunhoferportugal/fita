#!/bin/bash
set -e
cd ./website/

echo "MAJOR_VERSION from $NEW_TAG"
MAJOR_VERSION=$(echo "$NEW_TAG" | cut -d. -f1)
echo "MAJOR_VERSION=$MAJOR_VERSION"

DOCS_DIR="./docs"
VERSIONED_DIR="./versioned_docs/version-${MAJOR_VERSION}.x"

if [ ! -d "$VERSIONED_DIR" ]; then
    echo "Versioned docs do not exist. Creating..."
    npm ci
    npm run docusaurus docs:version "${MAJOR_VERSION}.x"
    echo "Created versioned docs at $VERSIONED_DIR"
    git add .
    git commit -m "Create versioned documentation for version \"${MAJOR_VERSION}.x\""
    git push origin HEAD:$PR_HEAD_BRANCH
else
    DOCS_UPDATE_BRANCH="docs/update-pr-${PR_NUMBER}"
    git checkout -B $DOCS_UPDATE_BRANCH "$PR_HEAD_BRANCH"

    cp -r $DOCS_DIR/* $VERSIONED_DIR/
    git add .
    git commit -m "Update versioned documentation for version \"${MAJOR_VERSION}.x\"" || exit 0

    git checkout "$PR_HEAD_BRANCH"

    if git merge $DOCS_UPDATE_BRANCH; then
        echo "Merged docs updates successfully into PR branch."
    else
        echo "Merge conflict detected. Pushing docs update branch for manual resolution."
        git merge --abort
        git push origin $DOCS_UPDATE_BRANCH --force

        if ! gh pr view --head $DOCS_UPDATE_BRANCH --base $PR_HEAD_BRANCH >/dev/null 2>&1; then
            gh pr create \
              --title "Docs update for version ${MAJOR_VERSION}.x" \
              --body "⚠️ Automatic docs update could not be merged due to conflicts. Please resolve the docs changes." \
              --head $DOCS_UPDATE_BRANCH \
              --base $PR_HEAD_BRANCH
        fi

        gh pr comment "$PR_NUMBER" \
          --body "⚠️ Automatic docs update for version ${MAJOR_VERSION}.x could not be merged due to conflicts. The update branch \`${DOCS_UPDATE_BRANCH}\` has been pushed for manual resolution."
        exit 1
    fi
fi