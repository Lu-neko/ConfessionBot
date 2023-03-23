import discord
from discord import app_commands
import traceback
import aiohttp
import random
import os
import dotenv

dotenv.load_dotenv()

MY_GUILD = discord.Object(id=os.getenv("GUILD_ID"))

class ConfessionBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = ConfessionBot(intents=intents)

states = ["grey", "blue", "yellow", "green", "red"]

class Confession(discord.ui.Modal, title='Confession'):

    confession = discord.ui.TextInput(
        label='Detail your confession',
        style=discord.TextStyle.long,
        placeholder='A few years ago, I was...',
        max_length=4000,
    )

    def __init__(self, anonymous):
        super().__init__()
        self.anonymous = anonymous

    async def on_submit(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(os.getenv("WEBHOOK_URL"), session=session)
            embed = discord.Embed(color=4378602, description=self.confession.value)
            if self.anonymous:
                pfp = states.pop(0)
                await webhook.send("", embed=embed, username=f"Anonymous {pfp.capitalize()}",
                    avatar_url=f"https://ia903204.us.archive.org/4/items/discordprofilepictures/discord{pfp}.png")
                random.shuffle(states)
                states.append(pfp)
                print(states)
            else:
                await webhook.send("", embed=embed, username=interaction.user.display_name,
                    avatar_url=interaction.user.display_avatar.url)
        await interaction.response.send_message("Your confession has been sent!", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("Oops! Something went wrong.", ephemeral=True)

        traceback.print_exception(type(error), error, error.__traceback__)

@client.tree.command(description="Send a confession")
@app_commands.describe(anonymous="If you want to post this confession anonymously or not")
async def confession(interaction: discord.Interaction, anonymous:bool):
    await interaction.response.send_modal(Confession(anonymous))

client.run(os.getenv("TOKEN"))