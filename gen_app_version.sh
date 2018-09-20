#!/bin/bash

# Use git master tag number as App version
# Calcuate git commit number as build number base on the 'base' tag.

ZZ_VERSION="1.0.0"
ZZ_BUILD_NUMBER="1"
ANNOTATED_TAG_NAME="base"
XCCONFIG_FILE_NAME="Version.xcconfig"

cd ${SRCROOT}

# Fail with an error message
function fail()
{
  local error=${1:-Unknown error}
  echo "Failed: $error" >&2
  exit 1
}

# Fetch the closest tag as App version
GIT_CLOSEST_TAG=$(git describe --abbrev=0 --tags)
if [[ -z "$GIT_CLOSEST_TAG" ]]; then
  fail "\`git describe --abbrev=0 --tags\` failed to fetch closest tag"
elif [ "$GIT_CLOSEST_TAG" != "$ANNOTATED_TAG_NAME" ]; then
  ZZ_VERSION=$GIT_CLOSEST_TAG
fi

# Fetch git output
GIT_DESCRIBE_OUTPUT=$(git describe --match $ANNOTATED_TAG_NAME)
if [[ -z "$GIT_DESCRIBE_OUTPUT" ]]; then
  fail "\`git describe --match $ANNOTATED_TAG_NAME\` failed to produce output"
fi

# Cut git output with delimiter "-"
GIT_COMMIT_COUNT=`echo "$GIT_DESCRIBE_OUTPUT" | cut -d '-' -f2`
if [[ -n "$GIT_COMMIT_COUNT" ]]; then
  ZZ_BUILD_NUMBER=$[$GIT_COMMIT_COUNT+1]
fi

# Write build configuration values to Xcode xcconfig
echo "// DO NOT CHANGE THIS FILE MANUALLY"$'\n' > "$XCCONFIG_FILE_NAME"
echo "ZZ_VERSION = $ZZ_VERSION" >> "$XCCONFIG_FILE_NAME"
echo "ZZ_BUILD_NUMBER = $ZZ_BUILD_NUMBER" >> "$XCCONFIG_FILE_NAME"
touch "$XCCONFIG_FILE_NAME"

# Print version information
echo " App Version: $ZZ_VERSION"
echo "Build Number: $ZZ_BUILD_NUMBER"
