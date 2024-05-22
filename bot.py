import discord
import requests
import json

client = discord.Client()

REPLICATE_API_TOKEN = 'your_replicate_api_token_here'
MODEL_VERSION = 'r8_Xp53CGqUMvCGEvDbWKBiODoOTBNm2Xd1anpJy'  # The model version you provided

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!generate'):
        prompt = message.content[len('!generate '):].strip()
        if not prompt:
            await message.channel.send("Please provide a prompt after !generate.")
            return

        await message.channel.send("Generating image...")

        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={
                "Authorization": f"Token {REPLICATE_API_TOKEN}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "version": MODEL_VERSION,
                "input": {"prompt": prompt}
            })
        )

        if response.status_code != 200:
            await message.channel.send(f"Error: {response.json().get('detail', 'Unknown error')}")
            return

        prediction = response.json()
        # Wait for the prediction to complete
        prediction_id = prediction['id']
        output_url = None

        while not output_url:
            response = requests.get(
                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                headers={"Authorization": f"Token {REPLICATE_API_TOKEN}"}
            )
            prediction = response.json()
            if prediction['status'] == 'succeeded':
                output_url = prediction['output'][0]
            elif prediction['status'] == 'failed':
                await message.channel.send("Image generation failed.")
                return

        await message.channel.send(output_url)

client.run('your_discord_bot_token_here')
