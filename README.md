# Sidescroller Engine
A simple sidescroller engine built with the Python Arcade library. Can be used to create basic platformer levels.  

## Demo
### Video
[Watch video here](https://github.com/CadenLau/Sidescroller-Engine/raw/main/assets/gameplay/###.mov)
### Screenshots
#### Gameplay
![Gameplay](assets/gameplay/###.jpg)

## Installation
### 1. Clone the repository
    git clone https://github.com/CadenLau/Sidescroller-Engine.git
    cd Sidescroller-Engine
### 2. Create and activate virtual environment
#### macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
#### Windows (PowerShell)
    python -m venv venv
    venv\Scripts\Activate.ps1
#### Windows (Command Prompt)
    python -m venv venv
    venv\Scripts\activate.bat
*Make sure you have Python 3.12+ installed. You can also upgrade pip to avoid dependency issues:*

    python -m pip install --upgrade pip
### 3. Install dependencies
    python -m pip install -r requirements.txt

## How to Run
    python main.py

## Usage
### Built-In Functions
Instantiate the game window:
    
    make_game(window_width=800  
    window_height=600, parallax=True)  
Create the player:

    make_player(scale=1.0, jump_speed=20, walk_speed=8)
Create an enemy:

    make_enemy(center_x, center_y, scale=1.0)
Create a coin:

    make_coin(center_x, center_y, scale=0.7)
Create a player:

    make_platform(width=300, height= 40, center_x, center_y)
Create a ground across the bottom of the entire level:

    make_ground()

### Player Controls
| Key | Action |
| ----------- | ----------- |
| Up arrow | Jump |
| Down arrow | Duck |
| Left arrow | Move left |
| Right arrow | Move right |
| Space bar | Attack |

## Features
- Smooth, responsive controls
- Physics-based movement and hitbox detection
- 60 FPS gameplay
- Basic attack mechanic

## Project Structure
    ├── main.py
    ├── assets/images/
    |   ├── gameplay/
    |   └── walk/
    ├── requirements.txt
    ├── LICENSE.txt
    ├── .gitignore
    └── README.md

## Built With
- [Python Arcade](https://api.arcade.academy/en/latest/)

## License
MIT License  
See [`LICENSE`](LICENSE.txt) file for details.