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
3. Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
4. Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
5. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
6. Log in to your Telegram account:
    ```bash
    python3 src/utils/telegram_sign_in.py
    ```
7. Run the bot with the following command:
    ```bash
    python3 main.py
    ```

In the future, the bot will be able to run using `docker-compose`.

## Requirements

The project dependencies listed in `requirements.txt` include:
- `annotated-types==0.7.0`
- `asyncpg==0.30.0`
- `certifi==2025.1.31`
- `loguru==0.7.3`
- `pyaes==1.6.1`
- `pydantic==2.10.6`
- `pydantic-settings==2.8.1`
- `pydantic_core==2.27.2`
- `Pyrogram==2.0.106`
- `PySocks==1.7.1`
- `python-dotenv==1.0.1`
- `sentry-sdk==2.22.0`
- `TgCrypto==1.2.5`
- `typing_extensions==4.12.2`
- `urllib3==2.3.0`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact the project maintainers.

