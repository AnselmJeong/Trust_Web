# Trust Game Experiment Web Application

This is a web application for conducting a psychological trust game experiment using the Reflex.dev framework.

## Features

- User authentication using Firebase
- Two-section trust game experiment
- Section 1: Play as Player B
- Section 2: Play as Player A
- Data persistence using Firebase Realtime Database
- Modern, responsive UI

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Node.js and npm (for Reflex.dev)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Trust_Web
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Reflex CLI:
```bash
pip install reflex
```

## Running the Application

1. Start the development server:
```bash
reflex run
```

2. Open your browser and navigate to:
```
http://localhost:3000
```

## Project Structure

- `trust_web.py`: Main application file with UI components
- `state.py`: State management and game logic
- `firebase_config.py`: Firebase configuration
- `rxconfig.py`: Reflex configuration
- `requirements.txt`: Python dependencies

## Game Rules

### Section 1 (Player B)
- Receive an amount from Player A
- Amount is multiplied by 2
- Decide how much to return to Player A
- Profit = Amount received - Amount returned

### Section 2 (Player A)
- Start with 20 currency units
- Can send up to 50% of current balance
- Amount sent is multiplied by 2
- AI Player B decides return amount
- Profit = Amount returned - Amount sent

## Data Collection

All experiment data is stored in Firebase Realtime Database, including:
- User information
- Round-by-round decisions
- Profits and balances
- Timestamps

## License

This project is licensed under the MIT License - see the LICENSE file for details.
