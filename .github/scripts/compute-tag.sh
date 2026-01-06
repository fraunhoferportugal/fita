#!/bin/bash
set -e

CHART_FILE="deploy/chart/Chart.yaml"

if [ -n "$APP_BUMP" ] && [ "$APP_BUMP" != "none" ]; then
  app_bump="$APP_BUMP"
else
  app_bump=$(yq -r '.annotations."relsync/bump"' "$CHART_FILE")
fi

latest_tag=$(git tag -l | sort -Vr | head -n1)
latest_tag=${latest_tag:-0.0.0}
echo "Latest tag: $latest_tag"
echo "App bump \"$app_bump\" on \"$latest_tag\""

base_version=$(yq -r '.annotations."relsync/base-version"' "$CHART_FILE")
current_version=$(yq -r '.version' "$CHART_FILE")
if [ "$base_version" != "null" ]; then
  yq -i ".version = \"$base_version\"" "$CHART_FILE"
else
  base_version=$current_version
fi
echo "Chart bump \"$app_bump\" on \"$base_version\" - (current version: \"$current_version\")"

relsync_exit_code=0
output=$(
  relsync bump "$app_bump" \
    --chart-bump-type "$app_bump" \
    --create-tag \
    -o json
) || relsync_exit_code=$?

if [ $relsync_exit_code -ne 0 ]; then
  echo "relsync returned $relsync_exit_code, stopping execution gracefully"
  echo "new-tag=skipped" >> "$GITHUB_OUTPUT"
  exit 0
fi

new_tag=$(echo "$output" | jq -r '.newTag')
echo "new-tag=$new_tag"
echo "new-tag=$new_tag" >> "$GITHUB_OUTPUT"
