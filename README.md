# gnfnt - Get Nerd Fonts Installer

`gnfnt` is a simple Python-based command-line tool to automate the installation of Nerd Fonts on Linux, macOS, and Windows. It fetches the latest fonts directly from the Nerd Fonts GitHub repository and installs them on your system.

## Features
- Install one or more Nerd Fonts by specifying their names.
- Install **all** Nerd Fonts using the `*` argument.
- Automatically updates the system font cache.
- Works on Linux, macOS, and Windows.

---

## Installation

### **Linux & macOS**
1. **Install Python** (if not already installed):
   ```bash
   sudo apt install python3 python3-pip   # Debian/Ubuntu
   sudo dnf install python3 python3-pip   # Fedora
   brew install python3                   # macOS (via Homebrew)
   ```

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/gnfnt.git
   cd gnfnt
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install `gnfnt` Globally**:
   ```bash
   sudo make install
   ```

5. **Run `gnfnt`**:
   ```bash
   gnfnt FiraCode JetBrainsMono
   ```

6. **To Uninstall**:
   ```bash
   sudo make uninstall
   ```

---

### **Windows**
1. **Install Python** (if not installed):
   - Download and install Python from [python.org](https://www.python.org/downloads/)
   - Ensure `pip` is installed by running:
     ```powershell
     python -m ensurepip --default-pip
     ```

2. **Clone the Repository**:
   ```powershell
   git clone https://github.com/yourusername/gnfnt.git
   cd gnfnt
   ```

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Add `gnfnt` to Path** (optional for global access):
   ```powershell
   $env:Path += ";$PWD"
   ```

5. **Run `gnfnt`**:
   ```powershell
   python gnfnt.py FiraCode JetBrainsMono
   ```

---

## **Usage**
```bash
gnfnt [options] <font_name1> <font_name2> ...
```

### **Options**
| Option          | Description |
|---------------|-------------|
| `-h, --help`  | Show help message with ASCII art. |
| `-v, --version`  | Show the version information. |
| `*`  | Install all Nerd Fonts (Warning: Large storage required). |

### **Example Usage**
```bash
gnfnt FiraCode Hack JetBrainsMono
```

### **Install All Fonts**
```bash
gnfnt *
```
You will be prompted with:
```
You are about to install all of the Nerd Fonts content. This is not recommended on systems with small storage sizes. Continue? [y/n]
```
Press `y` to proceed, `n` to cancel.

---

## **License**
MIT License.

---
