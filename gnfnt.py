import os
import sys
import json
import requests
import zipfile
import shutil
from pathlib import Path
from pip._vendor.rich.progress import Progress, BarColumn, DownloadColumn, TextColumn
import platform

FONT_DIR = Path.home() / ".gnfnt"
FONT_DIR.mkdir(parents=True, exist_ok=True)  # Ensure ~/.gnfnt/ exists

FONT_REPO_FILE = Path.home() / ".gnfnt/fontRepos.json"

def load_repositories():
    """Load repositories from fontRepos.json file, with error handling."""
    if not FONT_REPO_FILE.exists():
        return ["https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest"]

    try:
        with open(FONT_REPO_FILE, "r") as file:
            data = json.load(file)
            return data.get("repositories", [])
    except (json.JSONDecodeError, FileNotFoundError):
        print("⚠️ Error: Corrupted or missing fontRepos.json. Resetting to default.")
        return ["https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest"]

def save_repositories(repositories):
    """Save the list of repositories to fontRepos.json."""
    FONT_REPO_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(FONT_REPO_FILE, "w") as file:
        json.dump({"repositories": repositories}, file, indent=4)

def add_repository(url):
    """Add a new repository to fontRepos.json."""
    repositories = load_repositories()
    if url in repositories:
        print(f"✅ Repository {url} is already added.")
        return
    repositories.append(url)
    save_repositories(repositories)
    print(f"✅ Repository {url} added successfully.")

def remove_repository(url):
    """Remove a repository from fontRepos.json."""
    repositories = load_repositories()
    if url not in repositories:
        print(f"⚠️ Repository {url} not found.")
        return
    repositories.remove(url)
    save_repositories(repositories)
    print(f"✅ Repository {url} removed successfully.")

def list_repositories():
    """Display all saved font repositories."""
    repositories = load_repositories()
    if not repositories:
        print("⚠️ No repositories found.")
        return
    print("📂 Saved Font Repositories:")
    for repo in repositories:
        print(f"  - {repo}")

def get_fonts_dir():
    """Determine the system's font directory."""
    system = platform.system()
    if system == "Windows":
        return Path.home() / "AppData/Local/Microsoft/Windows/Fonts"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library/Fonts"
    else:  # Linux and UNIX-like systems
        return Path.home() / ".local/share/fonts/NerdFonts"

def is_font_installed(font_name):
    """Check if a font is already installed."""
    fonts_dir = get_fonts_dir()
    return any(fonts_dir.glob(f"{font_name}*.[to]tf"))

def get_all_nerd_fonts():
    """Fetch available fonts from all registered repositories, with improved error handling."""
    repositories = load_repositories()
    all_fonts = []
    invalid_repos = []

    for repo in repositories:
        try:
            response = requests.get(repo, timeout=10)

            # ✅ Check if response is empty before calling `.json()`
            if response.status_code == 200 and response.text.strip():
                try:
                    assets = response.json().get("assets", [])
                    fonts = [asset["name"].replace(".zip", "") for asset in assets if asset["name"].endswith(".zip")]
                    all_fonts.extend(fonts)
                except json.JSONDecodeError:
                    print(f"⚠️ Error: {repo} returned invalid JSON. Skipping...")
                    invalid_repos.append(repo)
            else:
                print(f"⚠️ Warning: No data received from {repo}. Marking as invalid.")
                invalid_repos.append(repo)

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching fonts from {repo}: {e}")
            invalid_repos.append(repo)

    # ✅ Remove invalid repositories automatically
    if invalid_repos:
        for bad_repo in invalid_repos:
            remove_repository(bad_repo)
        print("🗑️ Removed invalid repositories from fontRepos.json.")

    return list(set(all_fonts))  # Remove duplicates

def list_available_fonts():
    """Fetch and display all available Nerd Fonts with installation status icons."""
    fonts = get_all_nerd_fonts()
    
    if not fonts:
        print("❌ No fonts found from registered repositories.")
        return

    print("🎨 Available Nerd Fonts:")
    for font in sorted(fonts):  # Sorted alphabetically for better readability
        if is_font_installed(font):
            print(f"  ✅ {font}")  # Mark installed fonts with a checkmark
        else:
            print(f"  ⬇️  {font}")  # Mark available fonts with a download icon


import sys

def download_and_install_font(font_name, index, total):
    """Download and install a specific Nerd Font with a live progress bar."""
    if is_font_installed(font_name):
        print(f"✅ {font_name} is already installed. Skipping download.")
        return

    base_url = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/"
    font_zip = f"{font_name}.zip"
    download_url = f"{base_url}{font_zip}"
    fonts_dir = get_fonts_dir()
    temp_dir = Path.home() / ".gnfnt_temp"

    fonts_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    zip_path = temp_dir / font_zip

    response = requests.get(download_url, stream=True)
    total_size = int(response.headers.get("content-length", 0))

    if response.status_code == 200:
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
        ) as progress:
            task_id = progress.add_task("[cyan]Downloading...", total=total_size)

            with open(zip_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        progress.update(task_id, advance=len(chunk))

        # ✅ Clear previous two lines and update live status
        sys.stdout.write("\033[F\033[K" * 2)  # Moves cursor up 2 lines and clears them
        print(f"File: {font_name} ({index}/{total})")
        print("Installing...")

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        installed = False
        for font_file in temp_dir.iterdir():
            if font_file.suffix in [".ttf", ".otf"]:
                destination = fonts_dir / font_file.name
                if destination.exists():
                    print(f"⚠️ {font_file.name} already exists. Skipping installation.")
                else:
                    shutil.move(str(font_file), str(destination))
                    installed = True

        zip_path.unlink()
        shutil.rmtree(temp_dir, ignore_errors=True)

        sys.stdout.write("\033[F\033[K")  # Clear previous line
        print(f"✅ Installed: {font_name} ({index}/{total})")

    else:
        print(f"❌ Error: Failed to download {font_name}. Check the font name and try again.")
    #refresh_font_cache()


def print_help():
    """Display help message."""
    print(r"""
          _____                    _____                _____                                                            
         /\    \                  /\    \              /\    \                                                           
        /::\    \                /::\    \            /::\    \                                                          
       /::::\    \              /::::\    \           \:::\    \                                                         
      /::::::\    \            /::::::\    \           \:::\    \                                                        
     /:::/\:::\    \          /:::/\:::\    \           \:::\    \                                                       
    /:::/  \:::\    \        /:::/__\:::\    \           \:::\    \                                                      
   /:::/    \:::\    \      /::::\   \:::\    \          /::::\    \                                                     
  /:::/    / \:::\    \    /::::::\   \:::\    \        /::::::\    \                                                    
 /:::/    /   \:::\ ___\  /:::/\:::\   \:::\    \      /:::/\:::\    \                                                   
/:::/____/  ___\:::|    |/:::/__\:::\   \:::\____\    /:::/  \:::\____\                                                  
\:::\    \ /\  /:::|____|\:::\   \:::\   \::/    /   /:::/    \::/    /                                                  
 \:::\    /::\ \::/    /  \:::\   \:::\   \/____/   /:::/    / \/____/                                                   
  \:::\   \:::\ \/____/    \:::\   \:::\    \      /:::/    /                                                            
   \:::\   \:::\____\       \:::\   \:::\____\    /:::/    /                                                             
    \:::\  /:::/    /        \:::\   \::/    /    \::/    /                                                              
     \:::\/:::/    /          \:::\   \/____/      \/____/                                                               
      \::::::/    /            \:::\    \                                                                                
       \::::/    /              \:::\____\                                                                               
        \::/____/                \::/    /                                                                               
                                  \/____/                                                                                
                                                                                                                         
          _____                    _____                    _____                    _____                               
         /\    \                  /\    \                  /\    \                  /\    \                              
        /::\____\                /::\    \                /::\    \                /::\    \                             
       /::::|   |               /::::\    \              /::::\    \              /::::\    \                            
      /:::::|   |              /::::::\    \            /::::::\    \            /::::::\    \                           
     /::::::|   |             /:::/\:::\    \          /:::/\:::\    \          /:::/\:::\    \                          
    /:::/|::|   |            /:::/__\:::\    \        /:::/__\:::\    \        /:::/  \:::\    \                         
   /:::/ |::|   |           /::::\   \:::\    \      /::::\   \:::\    \      /:::/    \:::\    \                        
  /:::/  |::|   | _____    /::::::\   \:::\    \    /::::::\   \:::\    \    /:::/    / \:::\    \                       
 /:::/   |::|   |/\    \  /:::/\:::\   \:::\    \  /:::/\:::\   \:::\____\  /:::/    /   \:::\ ___\                      
/:: /    |::|   /::\____\/:::/__\:::\   \:::\____\/:::/  \:::\   \:::|    |/:::/____/     \:::|    |                     
\::/    /|::|  /:::/    /\:::\   \:::\   \::/    /\::/   |::::\  /:::|____|\:::\    \     /:::|____|                     
 \/____/ |::| /:::/    /  \:::\   \:::\   \/____/  \/____|:::::\/:::/    /  \:::\    \   /:::/    /                      
         |::|/:::/    /    \:::\   \:::\    \            |:::::::::/    /    \:::\    \ /:::/    /                       
         |::::::/    /      \:::\   \:::\____\           |::|\::::/    /      \:::\    /:::/    /                        
         |:::::/    /        \:::\   \::/    /           |::| \::/____/        \:::\  /:::/    /                         
         |::::/    /          \:::\   \/____/            |::|  ~|               \:::\/:::/    /                          
         /:::/    /            \:::\    \                |::|   |                \::::::/    /                           
        /:::/    /              \:::\____\               \::|   |                 \::::/    /                            
        \::/    /                \::/    /                \:|   |                  \::/____/                             
         \/____/                  \/____/                  \|___|                   ~~                                   
                                                                                                                         
          _____                   _______                   _____                _____                    _____          
         /\    \                 /::\    \                 /\    \              /\    \                  /\    \         
        /::\    \               /::::\    \               /::\____\            /::\    \                /::\    \        
       /::::\    \             /::::::\    \             /::::|   |            \:::\    \              /::::\    \       
      /::::::\    \           /::::::::\    \           /:::::|   |             \:::\    \            /::::::\    \      
     /:::/\:::\    \         /:::/~~\:::\    \         /::::::|   |              \:::\    \          /:::/\:::\    \     
    /:::/__\:::\    \       /:::/    \:::\    \       /:::/|::|   |               \:::\    \        /:::/__\:::\    \    
   /::::\   \:::\    \     /:::/    / \:::\    \     /:::/ |::|   |               /::::\    \       \:::\   \:::\    \   
  /::::::\   \:::\    \   /:::/____/   \:::\____\   /:::/  |::|   | _____        /::::::\    \    ___\:::\   \:::\    \  
 /:::/\:::\   \:::\    \ |:::|    |     |:::|    | /:::/   |::|   |/\    \      /:::/\:::\    \  /\   \:::\   \:::\    \ 
/:::/  \:::\   \:::\____\|:::|____|     |:::|    |/:: /    |::|   /::\____\    /:::/  \:::\____\/::\   \:::\   \:::\____\\
\::/    \:::\   \::/    / \:::\    \   /:::/    / \::/    /|::|  /:::/    /   /:::/    \::/    /\:::\   \:::\   \::/    /
 \/____/ \:::\   \/____/   \:::\    \ /:::/    /   \/____/ |::| /:::/    /   /:::/    / \/____/  \:::\   \:::\   \/____/ 
          \:::\    \        \:::\    /:::/    /            |::|/:::/    /   /:::/    /            \:::\   \:::\    \     
           \:::\____\        \:::\__/:::/    /             |::::::/    /   /:::/    /              \:::\   \:::\____\    
            \::/    /         \::::::::/    /              |:::::/    /    \::/    /                \:::\  /:::/    /    
             \/____/           \::::::/    /               |::::/    /      \/____/                  \:::\/:::/    /     
                                \::::/    /                /:::/    /                                 \::::::/    /      
                                 \::/____/                /:::/    /                                   \::::/    /       
                                  ~~                      \::/    /                                     \::/    /        
                                                           \/____/                                       \/____/         
                                                                                                                         
    Author: Joshua Ayers
    Licence: MIT

Usage: gnfnt [options] <font_name1> <font_name2> ...
Options:
  -h, --help       Show this help message and exit
  -v, --version    Show the version information and exit
  -l, --list       List all available Nerd Fonts
  --repos          Show all saved font repositories
  -a "url"         Add a new font repository
  -r "url"         Remove a font repository
  -f "file.zip"    Install fonts from a ZIP archive
  -f "file.ttf"    Install an individual font file
  -f "file1.ttf file2.otf file3.zip" Install multiple fonts
  *                Install all Nerd Fonts (Warning: Large storage required)
""")

def refresh_font_cache():
    """Refresh the system font cache after installation."""
    print("Refreshing font cache...")
    system = platform.system()
    if system == "Windows":
        print("On Windows, fonts should be available after restarting the application.")
    elif system == "Darwin":
        os.system("sudo atsutil databases -remove")
    else:
        os.system("fc-cache -fv")
    print("Font cache updated.")

def install_font_file_or_zip(file_paths):
    """Install fonts from individual .ttf/.otf files or a .zip archive."""
    fonts_dir = get_fonts_dir()
    fonts_dir.mkdir(parents=True, exist_ok=True)

    for file_path in file_paths:
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ Error: The file '{file_path}' does not exist.")
            continue

        if file_path.suffix.lower() in [".ttf", ".otf"]:
            # ✅ Install individual font files
            destination = fonts_dir / file_path.name
            if destination.exists():
                print(f"⚠️ {file_path.name} is already installed. Skipping.")
            else:
                shutil.copy(str(file_path), str(destination))
                print(f"✅ Installed {file_path.name}")

        elif file_path.suffix.lower() == ".zip":
            # ✅ Extract and install fonts from a ZIP archive
            temp_dir = Path.home() / ".gnfnt_temp"
            temp_dir.mkdir(parents=True, exist_ok=True)

            try:
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)

                installed = False
                for font_file in temp_dir.iterdir():
                    if font_file.suffix in [".ttf", ".otf"]:
                        destination = fonts_dir / font_file.name
                        if destination.exists():
                            print(f"⚠️ {font_file.name} is already installed. Skipping.")
                        else:
                            shutil.move(str(font_file), str(destination))
                            print(f"✅ Installed {font_file.name}")
                            installed = True

                if not installed:
                    print("❌ No valid font files found in the ZIP archive.")

            except zipfile.BadZipFile:
                print("❌ Error: Invalid ZIP file.")

            shutil.rmtree(temp_dir, ignore_errors=True)

        else:
            print(f"⚠️ Unsupported file type: {file_path.name}. Skipping.")

    refresh_font_cache()

def main():
    """Main function to handle user input and execute font installations."""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    arg = sys.argv[1]

    if arg in ["-h", "--help"]:
        print_help()
        sys.exit(0)

    if arg in ["-v", "--version"]:
        print("gnfnt version 1.6.0")
        sys.exit(0)

    if arg in ["-l", "--list"]:
        list_available_fonts()
        sys.exit(0)

    if arg in ["--repos"]:
        list_repositories()
        sys.exit(0)

    if arg == "-a" and len(sys.argv) > 2:
        add_repository(sys.argv[2])
        sys.exit(0)

    if arg == "-r" and len(sys.argv) > 2:
        remove_repository(sys.argv[2])
        sys.exit(0)

    if arg == "-f" and len(sys.argv) > 2:
        install_font_file_or_zip(sys.argv[2:])
        sys.exit(0)

    if arg == "*":
        confirm = input("⚠️ You are about to install ALL Nerd Fonts. This may use large storage. Continue? [y/n] ")
        if confirm.lower() != "y":
            print("❌ Installation aborted.")
            sys.exit(0)

        fonts = [f for f in get_all_nerd_fonts() if not is_font_installed(f)]
    else:
        fonts = [f for f in sys.argv[1:] if not is_font_installed(f)]

    if not fonts:
        print("✅ All specified fonts are already installed. No download needed.")
        sys.exit(0)

    total_fonts = len(fonts)
    for index, font in enumerate(fonts, start=1):
        download_and_install_font(font, index, total_fonts)

    #refresh_font_cache()
    print("🎉 All fonts installed successfully.")


if __name__ == "__main__":
    main()
