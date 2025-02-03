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
import glob
from pathlib import Path
from pip._vendor.rich.progress import Progress

def get_all_nerd_fonts():
    github_api_url = "https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest"
    response = requests.get(github_api_url)
    if response.status_code == 200:
        assets = response.json().get("assets", [])
        font_names = [asset["name"].replace(".zip", "") for asset in assets if asset["name"].endswith(".zip")]
        return font_names
    else:
        print("Error: Unable to fetch font list from GitHub.")
        sys.exit(1)

def download_and_install_font(font_name):
    base_url = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/"
    font_zip = f"{font_name}.zip"
    download_url = f"{base_url}{font_zip}"
    fonts_dir = Path.home() / ".local/share/fonts/NerdFonts"
    temp_dir = Path.home() / ".gnfnt_temp"
    
    fonts_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = temp_dir / font_zip
    
    print(f"Downloading {font_name} from {download_url}...")
    response = requests.get(download_url, stream=True)
    if response.status_code == 200:
        bar = Progress()
        task_id = bar.add_task(description="Downloading Files ...", total=None)
        bar.start()
        
        with open(zip_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    bar.advance(task_id)
                time.sleep(0.1)
        
        bar.stop()
        print(f"Downloaded {font_name}. Extracting...")
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        
        installed = False
        for font_file in temp_dir.iterdir():
            if font_file.suffix in [".ttf", ".otf"]:
                shutil.move(str(font_file), str(fonts_dir))
                print(f"Installed {font_file.name}")
                installed = True
        
        if not installed:
            print(f"Error: No valid font files found in {font_name}. The font may not exist.")
        
        zip_path.unlink()
        print(f"{font_name} installation complete.")
    else:
        print(f"Error: Failed to download {font_name}. Check the font name and try again.")
    
    shutil.rmtree(temp_dir, ignore_errors=True)

def refresh_font_cache():
    print("Refreshing font cache...")
    os.system("fc-cache -fv")
    print("Font cache updated.")

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
    print("gnfnt version 1.0.0")

def main():
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
        confirm = input("You are about to install all of the Nerd Fonts content. This is not recommended on systems with small storage sizes. Continue? [y/n] ")
        if confirm.lower() != "y":
            print("Installation aborted.")
            sys.exit(0)
        
        fonts = get_all_nerd_fonts()
    else:
        fonts = sys.argv[1:]
    
    for font in fonts:
        download_and_install_font(font)
    
    refresh_font_cache()
    print("All fonts installed successfully.")

if __name__ == "__main__":
    main()
