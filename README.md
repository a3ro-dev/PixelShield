# PixelShield

A Discord bot written in Python that protects your server with various moderation and utility features.

## Installation

To use `pixelshield`, you need to have Python 3.6 or above installed on your system. Follow these steps to run the bot:

1. Clone the repository:

   ```bash
   git clone https://github.com/a3ro-dev/pixelshield
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Discord bot:

   - Create a new Discord application on the [Discord Developer Portal](https://discord.com/developers/applications).
   - Add a bot to your application.
   - Copy the bot token.

4. Configure the bot:

   - Open the `discordConfig.py` file in the `configuration` directory using a text editor.

## Usage

To run the `pixelshield` bot, use the following command:

```bash
python pixelshield.py
```

## Features

- Moderation commands: kick, ban, mute, etc.
- Authentication commands: register
- Catalogue command: catalogue
- Utility commands: Server info, member info, ping, etc.

## Dependencies

- discord
- jishaku
- discord-pretty-help
- qrcode
- pillow
- bhimupipy
- platform

## Contributing

Contributions are welcome! If you have any suggestions or find any issues, please create a new issue or submit a pull request.

## License

This project is licensed under the terms of the MIT license.