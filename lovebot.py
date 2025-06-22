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
        await self.tree.sync()  # Global sync = needed for DM support
        print("✅ Slash commands synced globally")

bot = LoveBot()

# 🎲 Rigged love %
def rigged_love_score():
    return random.randint(1, 30) if random.random() < 0.1 else random.randint(80, 100)

# 🖼️ Grab avatar from URL
async def fetch_avatar(session, url):
    async with session.get(url) as resp:
        if resp.status == 200:
            return Image.open(io.BytesIO(await resp.read())).convert("RGBA")
    return None

# 💘 /love slash command
@discord.app_commands.command(name="love", description="Calculate love % between you and another user")
@app_commands.describe(target="The lucky (or unlucky) person")
async def love_command(interaction: discord.Interaction, target: discord.User):
    try:
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            pfp1 = await fetch_avatar(session, interaction.user.display_avatar.url)
            pfp2 = await fetch_avatar(session, target.display_avatar.url)

        if not pfp1 or not pfp2:
            await interaction.followup.send("🚫 Couldn't fetch avatars.")
            return

        # 🧠 Resize & prepare
        pfp1 = pfp1.resize((256, 256))
        pfp2 = pfp2.resize((256, 256))
        canvas = Image.new("RGBA", (576, 256), (0, 0, 0, 0))
        canvas.paste(pfp1, (0, 0))
        canvas.paste(pfp2, (320, 0))

        # ❤️ Better heart shape using polygon and curves
        heart = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw_heart = ImageDraw.Draw(heart)

        # Draw heart shape manually (polygon + pieslice)
        draw_heart.pieslice([0, 0, 32, 32], 180, 360, fill="red")       # left bump
        draw_heart.pieslice([32, 0, 64, 32], 180, 360, fill="red")      # right bump
        draw_heart.polygon([(0, 16), (32, 64), (64, 16)], fill="red")   # bottom triangle

        # Paste on canvas
        canvas.paste(heart, (256, 96), heart)

        # 💯 Draw love %
        love_score = rigged_love_score()
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()

        draw = ImageDraw.Draw(canvas)
        draw.text((288, 170), f"{love_score}%", font=font, fill="white", anchor="mm")

        # 📤 Send it
        with io.BytesIO() as image_binary:
            canvas.save(image_binary, "PNG")
            image_binary.seek(0)
            await interaction.followup.send(
                content=f"💘 {interaction.user.mention} + {target.mention} = love level {love_score}%",
                file=discord.File(fp=image_binary, filename="love.png")
            )
    except Exception as e:
        await interaction.followup.send(f"Something went wrong: {e}")

# 🔐 Safe login
bot.run(os.environ["DISCORD_TOKEN"])
