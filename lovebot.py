import discord
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
import random, aiohttp, io, os

class LoveBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.add_command(love_command)
        await self.tree.sync()
        print("✅ Slash commands synced")

bot = LoveBot()

# 🎲 Rigged love %
def rigged_love_score():
    if random.random() < 0.1:
        return random.randint(1, 30)  # 10% chance to be tragic
    return random.randint(80, 100)  # 90% chance to be soulmates

# 🖼️ Grab avatar from URL
async def fetch_avatar(session, url):
    async with session.get(url) as resp:
        if resp.status == 200:
            return Image.open(io.BytesIO(await resp.read())).convert("RGBA")
    return None

# 💘 /love slash command
@discord.app_commands.command(name="love", description="Calculate love % between you and another user")
@app_commands.describe(target="Your one true love (or mistake)")
async def love_command(interaction: discord.Interaction, target: discord.User):
    await interaction.response.defer()

    async with aiohttp.ClientSession() as session:
        pfp1 = await fetch_avatar(session, interaction.user.display_avatar.url)
        pfp2 = await fetch_avatar(session, target.display_avatar.url)

        if not pfp1 or not pfp2:
            await interaction.followup.send("🚫 Failed to fetch avatars.")
            return

        pfp1 = pfp1.resize((256, 256))
        pfp2 = pfp2.resize((256, 256))
        canvas = Image.new("RGBA", (576, 256), (0, 0, 0, 0))
        canvas.paste(pfp1, (0, 0))
        canvas.paste(pfp2, (320, 0))

        # ❤️ Draw heart
        heart = Image.new("RGBA", (64, 64))
        draw_heart = ImageDraw.Draw(heart)
        draw_heart.ellipse([0, 0, 64, 64], fill="red")
        canvas.paste(heart, (256, 96), heart)

        # 💯 Draw text
        love_score = rigged_love_score()
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        draw = ImageDraw.Draw(canvas)
        draw.text((288, 170), f"{love_score}%", font=font, fill="white", anchor="mm")

        # 📤 Send image
        with io.BytesIO() as image_binary:
            canvas.save(image_binary, "PNG")
            image_binary.seek(0)
            await interaction.followup.send(
                content=f"💘 {interaction.user.mention} + {target.mention} = true love?",
                file=discord.File(fp=image_binary, filename="love.png")
            )

# 🚀 Run using GitHub ENV
bot.run(os.environ["DISCORD_TOKEN"])
