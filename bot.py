import os
import discord
from discord.ext import commands
import random
from game import Game
from dotenv import load_dotenv
import asyncio

load_dotenv()
bot = discord.Bot(command_prefix="c!", intents=discord.Intents.all(),debug_guild=1026535125393096725)
games = {}

def random_chem_gif():
    GIFS = [
        "https://media.tenor.com/hRxU7RYOlMkAAAAC/breaking-bad-chemistry.gif",
        "https://media.tenor.com/ulLH6He-_-cAAAAC/chemistry-reaction.gif",
        "https://media.tenor.com/vHwnKMZRZA0AAAAC/beaker-muppets.gif",
        "https://media.tenor.com/Hf9rH5tLDjQAAAAM/chemicals-reaction.gif",
        "https://media.tenor.com/I0MRBBfOQ-8AAAAd/tales-of-vesperia-chemicals.gif",
        "https://media.tenor.com/SyVULRzNQUoAAAAM/gummy-bear-vat19.gif",
        "https://media.tenor.com/vVMC5thXHFMAAAAM/chemistry-reactions.gif",
        "https://media.tenor.com/jQWF0qLLwAcAAAAM/aluminum-iodine.gif",
        "https://media.tenor.com/EqBFW5y5tesAAAAC/chemistry-beakers.gif",
    ]
    return random.choice(GIFS)

@bot.command()
async def setup(ctx):
    """
    Start an Inorganic Clash of Chem game!
    """
    if ctx.guild.id in games:
        return await ctx.respond("There is already a game running in this server!", ephemeral=True)
    games[ctx.guild.id] = Game()
    embed = discord.Embed(
        title="Inorganic Clash of Chem!", 
        description="Click the ⚗️ button to join the game or the 💀 button to start!",
        color=discord.Color.random(), 
    )
    embed.set_image(url=random_chem_gif())
    view = SetupView(games[ctx.guild.id], ctx.author)

    await ctx.respond(embed=embed, view=view)

class SetupView(discord.ui.View):
    def __init__(self, game, creator):
        super().__init__()
        self.game = game
        self.creator = creator

    @discord.ui.button(label="Join", emoji='⚗', style=discord.ButtonStyle.blurple)
    async def join_button_callback(self, button, interaction):
        if self.game.running:
            await interaction.response.send_message("The game is already running, join next time!", ephemeral=True)
            return
        
        if interaction.user in self.game.players:
            await interaction.response.send_message("You are already a participant in this game!", ephemeral=True)
            return
        self.game.add_player(interaction.user)
        await interaction.response.send_message(f"{interaction.user.mention} has joined the game!")

    @discord.ui.button(label="Start", emoji='💀', style=discord.ButtonStyle.green)
    async def start_button_callback(self, button, interaction):
        if interaction.user != self.creator:
            await interaction.response.send_message(f"Only the creator ({self.creator.name}) can start this!", ephemeral=True)
            return
        
        self.game.start()
        view = ViewInv()
        await interaction.response.send_message(f"The game has begun! Please use `/inventory` and `/create`. Current Turn: {self.game.current_turn.mention}", view=view)

def display_inventory(inventory):
    s = ""
    for i in inventory:
        e = [e for e in bot.get_guild(1026535125393096725).emojis if e.name.split("_")[-1] == i][0]
        s += str(e)
    return s

class ViewInv(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="View Inventory", emoji='🔬', style=discord.ButtonStyle.blurple)
    async def inv_button_callback(self, button, interaction):
        game = games[interaction.guild.id] 

        if interaction.user not in game.players:
            return await interaction.response.send_message("You are not a participant in the current game.", ephemeral=True)


        embed = get_inv_embed(game, interaction.user)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="View Quests", emoji='🔍', style=discord.ButtonStyle.green)
    async def quest_button_callback(self, button, interaction):
        game = games[interaction.guild.id] 

        if interaction.user not in game.players:
            return await interaction.response.send_message("You are not a participant in the current game.", ephemeral=True)


        embed = discord.Embed(
            title="Active Quests 🧪",
            color=discord.Color.random()
        )

        if len(game.active_quests) == 0:
            embed.description = "There are no active quests at the moment!"
        else:
            for q in game.active_quests:
                embed.add_field(name=q.objective, value=f"Reward: {q.points} points!", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command()
async def leaderboard(ctx):
    """
    View the leaderboard!
    """
    if ctx.guild.id not in games:
        return await ctx.respond("There is no game running in this server! Create one with /setup", ephemeral=True)
    game = games[ctx.guild.id] 

    embed = discord.Embed(title="Inorganic Clash of Chem Leaderboard!", color=discord.Color.gold())
    for x,y in dict(sorted(game.leaderboard.items(), key=lambda item: item[1], reverse=True)).items():
        embed.add_field(name=x.name, value=f"{y} points", inline=False)
    embed.set_thumbnail(url=random_chem_gif())
    await ctx.respond(embed=embed)

def get_inv_embed(game, player):
    embed = discord.Embed(
        title="Your Inventory 🧪",
        color=discord.Color.random()
    )

    embed.add_field(name="Atoms ⚛", value=display_inventory(game.inventory[player]), inline=False)
    embed.add_field(name="Compounds ⚗️", value=", ".join(game.compound_inventory[player]), inline=False)
    return embed

@bot.command()
async def inventory(ctx):
    """
    View your inventory!
    """
    if ctx.guild.id not in games:
        return await ctx.respond("There is no game running in this server! Create one with /setup", ephemeral=True)
    game = games[ctx.guild.id] 

    if ctx.author not in game.players:
        return await ctx.respond("You are not a participant in the current game.", ephemeral=True)


    embed = get_inv_embed(game, ctx.author)

    await ctx.respond(embed=embed, ephemeral=True)

@bot.command()
async def create(ctx, compound: str):
    """
    Create a compound using its chemical forumla. If you want to pass, use PASS. 
    """
    if ctx.guild.id not in games:
        return await ctx.respond("There is no game running in this server! Create one with /setup", ephemeral=True)
    game = games[ctx.guild.id] 

    if ctx.author not in game.players:
        return await ctx.respond("You are not a participant in the current game.", ephemeral=True)

    if ctx.author != game.current_turn:
        return await ctx.respond(f"It's not your turn at the moment. Please wait for {game.current_turn} to play.", ephemeral=True)
    try:
        view = ViewInv()
        next_turn = None
        if compound.upper() == "PASS":
            game.next_turn()
            next_turn = game.current_turn
            await ctx.respond(f"{ctx.author.name} has chosen to pass this round. Next Turn: {next_turn.mention}", view=view)            
        else:
            pts, quests = game.create_compound(compound)    
            game.next_turn()
            next_turn = game.current_turn

            text = f"{ctx.author.name} has succesfully created **{compound}** {random.choice(['💥', '⚗️', '🧪'])} (+{pts} points!). Next Turn: {next_turn.mention}"

            for g in quests:
                text += f"\nBy creating this compound, {ctx.author.name} has completed the Quest: **{g.objective}** (+{g.points} points!)"

            await ctx.respond(text, view=view)

        while True:
            await asyncio.sleep(25)
            if game.current_turn == next_turn:
                game.next_turn()
                prev = next_turn
                next_turn = game.current_turn
                await ctx.channel.send(f"{prev.mention} failed to create a compound in 25 seconds. Next Turn: {next_turn.mention}", view=view)
                continue
            break

    except Exception as e:
        return await ctx.respond(str(e), ephemeral=True)

@bot.command()
async def sabotage(ctx, player: discord.Member):
    """
    Sabotage someone in exchange for 25 points. 
    """
    if ctx.guild.id not in games:
        return await ctx.respond("There is no game running in this server! Create one with /setup", ephemeral=True)
    game = games[ctx.guild.id] 

    if ctx.author not in game.players:
        return await ctx.respond("You are not a participant in the current game.", ephemeral=True)

    if ctx.author != game.current_turn:
        return await ctx.respond(f"It's not your turn at the moment. Please wait for {game.current_turn} to play.", ephemeral=True)

    if player not in game.players:
        return await ctx.respond(f"{player.mention} is not a participant in the current game.", ephemeral=True)
    
    if game.leaderboard[ctx.author] < 25:
        return await ctx.respond("You don't have 25 points to sabotage.", ephemeral=True)

    game.leaderboard[ctx.author] -= 25
    random.shuffle(game.inventory[player])
    game.inventory[player] = game.inventory[player][:len(game.inventory[player])//2]

    view = ViewInv()
    game.next_turn()
    next_turn = game.current_turn
    await ctx.respond(f"{ctx.author.mention} entered {player.mention}'s lab and sabotaged their inventory. Next turn: {next_turn.mention}", view=view)

    while True:
        await asyncio.sleep(25)
        if game.current_turn == next_turn:
            game.next_turn()
            prev = next_turn
            next_turn = game.current_turn
            await ctx.channel.send(f"{prev.mention} failed to create a compound in 25 seconds. Next Turn: {next_turn.mention}", view=view)
            continue
        break


@bot.command()
async def react(ctx, compound1: str, compound2: str):
    """
    Perform a reaction. 
    """
    if ctx.guild.id not in games:
        return await ctx.respond("There is no game running in this server! Create one with /setup", ephemeral=True)
    game = games[ctx.guild.id] 

    if ctx.author not in game.players:
        return await ctx.respond("You are not a participant in the current game.", ephemeral=True)

    if ctx.author != game.current_turn:
        return await ctx.respond(f"It's not your turn at the moment. Please wait for {game.current_turn} to play.", ephemeral=True)
    
    try:
        view = ViewInv()
        next_turn = None

        rxn, res = game.do_reaction(reactants=[compound1, compound2])

        text = f"{ctx.author.name} has succesfully performed the following reaction {random.choice(['💥', '⚗️', '🧪'])}\n\n**{rxn}**\n"
        for c in res:
            pts, quests = res[c]
            text += f"\nFor creating the compound **{c.formula}** (+{pts} points!)."
            for g in quests:
                text += f"\nBy creating this compound, {ctx.author.name} has completed the Quest: **{g.objective}** (+{g.points} points!)"
            
        game.next_turn()
        next_turn = game.current_turn
        text += f"\nNext Turn: {next_turn.mention}"
        
        await ctx.respond(text, view=view)

        while True:
            await asyncio.sleep(25)
            if game.current_turn == next_turn:
                game.next_turn()
                prev = next_turn
                next_turn = game.current_turn
                await ctx.channel.send(f"{prev.mention} failed to create a compound in 25 seconds. Next Turn: {next_turn.mention}", view=view)
                continue
            break

    except Exception as e:
        return await ctx.respond(str(e), ephemeral=True)


bot.run(os.getenv("BOT_TOKEN"))