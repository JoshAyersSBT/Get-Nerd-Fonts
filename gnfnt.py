#!/usr/bin/env python3

# Get Nerd Fonts 
# By Joshua Ayers
# Licence: MIT
import os
import sys
import requests
import zipfile
import shutil
import time
from pathlib import Path
from pip._vendor.rich.progress import Progress, BarColumn, DownloadColumn, TextColumn
import platform

def get_all_nerd_fonts():
    """Fetch the list of all available Nerd Fonts from GitHub releases."""
    github_api_url = "https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest"
    response = requests.get(github_api_url)
    if response.status_code == 200:
        assets = response.json().get("assets", [])
        font_names = [asset["name"].replace(".zip", "") for asset in assets if asset["name"].endswith(".zip")]
        return font_names
    else:
        print("Error: Unable to fetch font list from GitHub.")
        sys.exit(1)

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
    font_files = list(fonts_dir.glob(f"{font_name}*.[to]tf"))  # Check for TTF and OTF files
    return len(font_files) > 0

def download_and_install_font(font_name):
    """Download and install a specific Nerd Font."""
    fonts_dir = get_fonts_dir()

    # Check if font is already installed
    if is_font_installed(font_name):
        print(f"✅ {font_name} is already installed. Skipping download.")
        return

    base_url = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/"
    font_zip = f"{font_name}.zip"
    download_url = f"{base_url}{font_zip}"
    temp_dir = Path.home() / ".gnfnt_temp"

    fonts_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    zip_path = temp_dir / font_zip

    print(f"⬇️ Downloading {font_name} from {download_url}...")

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

        print(f"📦 Extracting {font_name}...")

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
                    print(f"✅ Installed {font_file.name}")
                    installed = True

        if not installed:
            print(f"⚠️ Error: No valid font files found in {font_name}. The font may not exist.")

        zip_path.unlink()
        print(f"🎉 {font_name} installation complete.")
    else:
        print(f"❌ Error: Failed to download {font_name}. Check the font name and try again.")

    shutil.rmtree(temp_dir, ignore_errors=True)

def refresh_font_cache():
    """Refresh the system font cache after installation."""
    print("🔄 Refreshing font cache...")
    system = platform.system()
    if system == "Windows":
        print("ℹ️ On Windows, fonts should be available after restarting the application.")
    elif system == "Darwin":
        os.system("sudo atsutil databases -remove")
    else:
        os.system("fc-cache -fv")
    print("✅ Font cache updated.")


def print_version():
    """Display version information."""
    print("gnfnt version 1.2.0")

def print_help():
    print("""
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
      *                Install all Nerd Fonts (Warning: Large storage required)
    """)

def print_version():
    """Display version information."""
    print("gnfnt version 1.2.0")

def main():
    """Main function to handle user input and execute font installations."""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    if sys.argv[1] in ["-h", "--help"]:
        print_help()
        sys.exit(0)

    if sys.argv[1] in ["-v", "--version"]:
        print_version()
        sys.exit(0)

    if sys.argv[1] == "*":
        confirm = input("⚠️ You are about to install all of the Nerd Fonts content. This is not recommended on systems with small storage sizes. Continue? [y/n] ")
        if confirm.lower() != "y":
            print("❌ Installation aborted.")
            sys.exit(0)

        fonts = get_all_nerd_fonts()
    else:
        fonts = sys.argv[1:]

    for font in fonts:
        download_and_install_font(font)

    refresh_font_cache()
    print("🎉 All fonts installed successfully.")

if __name__ == "__main__":
    main()