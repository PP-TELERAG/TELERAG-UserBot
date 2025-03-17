# TELERAG User Bot

TELERAG User Bot is a part of the TELERAG project. This bot automates several tasks to enhance user experience and streamline information management.

## Features

1. **Automatic Channel Subscription**: The bot automatically subscribes to channels it is not already subscribed to. If it is already subscribed, the channel is ignored. Subscription is managed by checking sources in a master source table.
2. **Continuous Publication Monitoring**: The bot continuously monitors publications to ensure up-to-date information.
3. **Filtering and Preprocessing**: The bot filters and preprocesses the information to ensure relevance and quality.
4. **Database Integration**: The bot transmits the processed information to the source database for further use.

## Getting Started

To get started with TELERAG User Bot, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/TELERAG-UserBot.git
    ```
2. Navigate to the project directory:
    ```bash
    cd TELERAG-UserBot
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Configure the bot with your settings.

## Requirements

The project dependencies listed in `requirements.txt` include:
- `annotated-types==0.7.0`
- `asyncpg==0.30.0`
- `pydantic==2.10.6`
- `pydantic-settings==2.8.1`
- `pydantic_core==2.27.2`
- `python-dotenv==1.0.1`
- `typing_extensions==4.12.2`

## Usage

Run the bot with the following command:
```bash
python3 main.py
```

## Contributing

We welcome contributions! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact the project maintainers.

