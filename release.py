import argparse
import os
import re
import subprocess
import sys

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("version", help="patch, minor, or major")
parser.add_argument("--update", action='store_true')
args = parser.parse_args()

# Check if current directory is Git repository and it's clean
try:
    subprocess.check_output(["git", "status"], stderr=subprocess.STDOUT)
except subprocess.CalledProcessError as e:
    sys.exit("Current directory is not a Git repository or the repository is not clean")

# Build the project with Gradle
try:
    subprocess.check_call([".\gradlew.bat", "build"])
except subprocess.CalledProcessError as e:
    sys.exit("Gradle build failed")

# Read version from build.gradle.kts
try:
    with open("build.gradle.kts", "r") as file:
        lines = file.readlines()
except FileNotFoundError:
    sys.exit("File build.gradle.kts not found")

version_line = next((line for line in lines if "version =" in line), None)
if version_line is None:
    sys.exit("No version line found in build.gradle.kts")

match = re.search(r"\d+\.\d+\.\d+", version_line)
if match is None:
    sys.exit("No version found in version line")

version_number = match.group(0)
version_parts = version_number.split('.')

# Increment the correct part of the version number
if args.version == "patch":
    version_parts[2] = str(int(version_parts[2]) + 1)
elif args.version == "minor":
    version_parts[1] = str(int(version_parts[1]) + 1)
    version_parts[2] = '0'  # reset patch to 0
elif args.version == "major":
    version_parts[0] = str(int(version_parts[0]) + 1)
    version_parts[1] = version_parts[2] = '0'  # reset minor and patches to 0
else:
    sys.exit("Invalid command line argument. Must be patch, minor, or major.")

# Update version in build.gradle.kts and write file
new_version = ".".join(version_parts)
for i, line in enumerate(lines):
    if "version =" in line:
        lines[i] = re.sub(r"\d+\.\d+\.\d+", new_version, line)
        break

try:
    with open("build.gradle.kts", "w") as file:
        file.writelines(lines)
except FileNotFoundError:
    sys.exit("Error writing to build.gradle.kts")

# Commit new version in Git
subprocess.check_call(["git", "commit", "-a", "-m", "Increase version number to " + new_version])

# Create tag in Git
subprocess.check_call(["git", "tag", new_version])

# Push changes to remote
subprocess.check_call(["git", "push", "origin", "--tags"])

# Publish to mavenLocal
subprocess.check_call([".\gradlew.bat", "publishToMavenLocal"])

# Update submodule, if option is set
if args.update:
    try:
    # Check that submodule is on master
        output = subprocess.check_output(["git", "-C", "gradle-common", "symbolic-ref", "--short", "HEAD"], stderr=subprocess.STDOUT)
        if output.decode().strip() != "master":
            sys.exit("Submodule is not on 'master' branch")

        # Check that submodule is up to date
        output = subprocess.check_output(["git", "-C", "gradle-common", "rev-list", "origin/master...master"], stderr=subprocess.STDOUT)
        if output:
            sys.exit("Submodule is not up-to-date with 'origin/master'")

        # Check status of submodule
        subprocess.check_output(["git", "status", "gradle-common"], stderr=subprocess.STDOUT)

        # Read version from settings.gradle.kts
        with open("settings.gradle.kts", "r") as file:
            lines = file.readlines()
        # Extract "root project name" value
        version_line = next((line for line in lines if "rootProject.name" in line), None)
        if version_line is None:
            sys.exit("No self_version_name line found in build.gradle.kts")
        self_version_name = re.search(r'"([^"]*)', version_line).group(1)

        # Find and update corresponding line in libs.versions.toml
        with open("gradle-common/libs.versions.toml", "r") as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            if self_version_name in line:
                lines[i] = f'{self_version_name} = "{new_version}"\n'
                break
        with open("gradle-common/libs.versions.toml", "w") as file:
            file.writelines(lines)

        # Commit and push submodule changes
        subprocess.check_call(["git", "-C", "gradle-common", "commit", "-a", "-m",
                              f"Update version of {self_version_name} to {new_version}"])
        subprocess.check_call(["git", "-C", "gradle-common", "push"])

        # Commit and push main module changes
        subprocess.check_call(["git", "commit", "-a", "-m",
                               f"Update version of {self_version_name} in submodule to {new_version}"])
        subprocess.check_call(["git", "push"])
    except subprocess.CalledProcessError as e:
        sys.exit("Could not update gradle-common submodule because it is not clean or other error occurred.")