# Web-App-based-Chess-Game
This project is a modern web application for playing chess, built using the Streamlit library in Python. Designed for ease of use and seamless online interaction, the app provides a platform for users to enjoy chess games directly in any web browser, without the need for installation or complex setup.

## File Structure
streamlit-chess-game/
├── chess_game.py          # Main Streamlit application
├── console_chess.py       # Console version
├── tests/                 # Unit tests (future)
│   ├── __init__.py
│   ├── test_chess_board.py
│   └── test_pieces.py
├── docs/                  # Additional documentation
└── assets/               # Images, icons, etc.

## Development Environment Setup

Fork and Clone
bashgit clone https://github.com/Ayush-Shah96/Web-App-based-Chess-Game.git
cd Web-App-based-Chess-Game

Create Virtual Environment
bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies
pip install streamlit

Run the Application
bashstreamlit run chess_game.py
