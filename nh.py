import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import asyncio
from discord.ui import Button, View
import datetime

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=";", intents=intents)
bot.remove_command("help")

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.watching, name="Naha")
    await bot.change_presence(activity=activity)
    try:
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées ({len(synced)})")
    except Exception as e:
        print(e)
        
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"{filename} chargé.")
            except Exception as e:
                print(f"Erreur dans {filename}: {e}")
        
@bot.event
async def on_reaction_add(reaction, user):
    if user.id == 1297695091351228497:
        await reaction.message.add_reaction(reaction.emoji)

@bot.event
async def on_reaction_remove(reaction, user):
    if user.id == 1297695091351228497:
        await reaction.message.remove_reaction(reaction.emoji, user)        


@bot.command()
async def ping(ctx):
    await ctx.message.delete() 
    before = discord.utils.utcnow()  
    message = await ctx.send("Calcul en cours...") 
    latency = (discord.utils.utcnow() - before).total_seconds() * 1000  
    ping_ms = round(bot.latency * 1000)  
    await message.edit(content=f"Le ping a pris {ping_ms} ms pour atteindre le gouvernement chinois.")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.mention_everyone:
        return

    if any(str(user.id) == "1297695091351228497" for user in message.mentions):
        try:
            await message.reply("Mon **patron** est occupé, il te répondra dans ``5 jours``")
        except discord.Forbidden:
            pass

    await bot.process_commands(message)
    
   
recent_triggers = {}
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "monstre" in message.content.lower():
        current_time = asyncio.get_event_loop().time()
        if message.author.id not in recent_triggers or current_time - recent_triggers[message.author.id] > 15:
            await message.channel.send("tripleee monstree")
            await message.channel.send("https://tenor.com/view/flight-reacts-flightreacts-tongue-tongue-laugh-gif-13724048537815479089")
            
            recent_triggers[message.author.id] = current_time
        else:
            pass

    await bot.process_commands(message)

@bot.command()
async def aide(ctx):
    embed = discord.Embed(
        title="Centre d'aide",
        description="Voici la liste des commandes disponibles :",
        color=discord.Color.blue()
    )
    embed.add_field(name=";ping", value="Vérifie si le bot répond.", inline=False)
    embed.add_field(name=";aide", value="Affiche cette aide.", inline=False)
    embed.add_field(name="/tg", value="Mute un membre. Exemple : `/tg utilisateur: @erine temps: 5m`", inline=False)
    embed.add_field(name="/démute", value="Retire le mute d’un membre.", inline=False)
    embed.add_field(name="/ban", value="Bannit un membre ou un ID.", inline=False)
    embed.add_field(name="/déban", value="Déban un utilisateur via son ID.", inline=False)
    embed.add_field(name="/expulse", value="Expulse un membre.", inline=False)
    embed.add_field(name="/purge", value="Supprime un certain nombre de messages.", inline=False)
    embed.add_field(name="/dire", value="Fait parler le bot.", inline=False)
    embed.add_field(name="/mail", value="Envoi un mail aux modérateurs")
    await ctx.send(embed=embed)

# ---

@bot.tree.command(name="tg", description="mute un membre")
@app_commands.describe(user="Membre à mute", time="Durée (ex : 5s, 10m, 2h, 1j)")
async def tg(interaction: discord.Interaction, user: discord.Member, time: str):
    unit = time[-1]
    try:
        duration = int(time[:-1])
    except ValueError:
        await interaction.response.send_message("Format invalide. Exemple : `5m` pour 5 minutes.", ephemeral=True)
        return

    if unit == "s":
        seconds = duration
    elif unit == "m":
        seconds = duration * 60
    elif unit == "h":
        seconds = duration * 3600
    elif unit == "j":
        seconds = duration * 86400
    else:
        await interaction.response.send_message("Unité invalide. Utilise s, m, h ou j.", ephemeral=True)
        return

    await user.timeout(discord.utils.utcnow() + timedelta(seconds=seconds))
    await interaction.response.send_message(f"{user.mention} ferme sa gueule pdt {time}")

cooldowns: dict[int, datetime.datetime] = {}
MAIL_CHANNEL_ID = 1351876432753594409

@bot.tree.command(name="mail", description="Envoyer un mail au développeur")
@app_commands.describe(message="Ton message")
async def mail(interaction: discord.Interaction, message: str):
    now = datetime.datetime.utcnow()
    user_id = interaction.user.id

    if user_id in cooldowns:
        cooldown_end = cooldowns[user_id]
        if now < cooldown_end:
            remaining = cooldown_end - now
            minutes, seconds = divmod(int(remaining.total_seconds()), 60)
            hours, minutes = divmod(minutes, 60)
            time_left = f"{hours}h {minutes}m {seconds}s"
            return await interaction.response.send_message(
                f"Tu dois attendre encore {time_left} avant d'envoyer un autre mail.",
                ephemeral=True
            )

    cooldowns[user_id] = now + datetime.timedelta(hours=2)
    await interaction.response.send_message("Mail envoyé au développeur.", ephemeral=True)

    embed = discord.Embed(
        title="Nouveau Mail",
        description=message,
        color=discord.Color.dark_purple()
    )
    embed.add_field(
        name="Envoyé par",
        value=f"{interaction.user.mention} ({interaction.user.id})",
        inline=False
    )
    embed.set_footer(text=now.strftime("Le %d/%m/%Y à %H:%M:%S UTC"))

    channel = bot.get_channel(MAIL_CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(MAIL_CHANNEL_ID)

    if channel:
        await channel.send(embed=embed)


@bot.tree.command(name="démute", description="Retire le timeout d'un membre")
@app_commands.describe(user="Membre à démute")
async def démute(interaction: discord.Interaction, user: discord.Member):
    await user.timeout(None)
    await interaction.response.send_message(f"{user.mention} fait attention, tu peux parler")

@bot.tree.command(name="ban", description="Ban un utilisateur")
@app_commands.describe(user="Utilisateur ou ID à bannir")
async def ban(interaction: discord.Interaction, user: str):
    try:
        member = await interaction.guild.fetch_member(int(user))
        await interaction.guild.ban(member)
        await interaction.response.send_message(f"{member} a été exécuté.")
    except:
        await interaction.guild.ban(discord.Object(id=int(user)))
        await interaction.response.send_message(f"L'utilisateur avec l'ID {user} a été exécuté")

@bot.tree.command(name="déban", description="Déban un utilisateur")
@app_commands.describe(user="ID de l'utilisateur à débannir")
async def déban(interaction: discord.Interaction, user: str):
    await interaction.guild.unban(discord.Object(id=int(user)))
    await interaction.response.send_message(f"L'utilisateur avec l'ID {user} a été débanni.")

@bot.tree.command(name="expulse", description="Expulse un membre")
@app_commands.describe(user="Membre à expulser")
async def expulse(interaction: discord.Interaction, user: discord.Member):
    await user.kick()
    await interaction.response.send_message(f"{user} a été expulsé.")

@bot.tree.command(name="purge", description="Supprime des messages")
@app_commands.describe(amount="Nombre de messages à supprimer", channel="Salon cible (optionnel)")
async def purge(interaction: discord.Interaction, amount: int, channel: discord.TextChannel = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Tu n'as pas la permission.", ephemeral=True)
        return

    target = channel or interaction.channel
    if not target.permissions_for(interaction.guild.me).manage_messages:
        await interaction.response.send_message("Je n’ai pas la permission de gérer les messages ici.", ephemeral=True)
        return

    deleted = await target.purge(limit=amount)
    await interaction.response.send_message(f"{len(deleted)} messages supprimés.", ephemeral=True)

@bot.tree.command(name="dire", description="Le bot parle")
@app_commands.describe(message="Message à envoyer", channel="Salon cible (optionnel)")
async def dire(interaction: discord.Interaction, message: str, channel: discord.TextChannel = None):
    if "@everyone" in message or "@here" in message:
        await interaction.response.send_message("je vais pas ping tout le monde.", ephemeral=True)
        return

    target = channel or interaction.channel
    await target.send(message)
    await interaction.response.send_message("Message envoyé.", ephemeral=True)
    
    
@bot.tree.command(name="dm", description="Envoie un message à un membre en mp")
async def dm(interaction: discord.Interaction, member: discord.Member, message: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("non t bizarre toi", ephemeral=True)
        return

    try:
        # envoi un mp au membre
        await member.send(message)
        await interaction.response.send_message(f"Message envoyé à {member.mention}.", ephemeral=True)

    except discord.Forbidden:
        # Si les mps du membre sont fermés
        await interaction.response.send_message(f"Impossible d'envoyer le message à {member.mention}, ses DMs sont fermés.", ephemeral=True)
    
    except discord.HTTPException:
        # si le bot est bloqué par le membre
        await interaction.response.send_message(f"Impossible d'envoyer le message à {member.mention}, il a bloqué le bot.", ephemeral=True)
        
        
@bot.tree.command(name="info", description="Info du développeur")
async def info(interaction: discord.Interaction):
    await interaction.response.send_message("https://devsxa.tiiny.site")        
                
@bot.tree.command(name="troll", description="Envoie un message avec l'identité d'un autre membre")
@app_commands.describe(user="La cible", message="Le message à envoyer")
async def troll(interaction: discord.Interaction, user: discord.Member, message: str):
    author_id = interaction.user.id
    if not interaction.user.guild_permissions.administrator and author_id != 935219381733052467:
        await interaction.response.send_message("Tu n'as pas la permission.", ephemeral=True)
        return

    try:
        webhook = await interaction.channel.create_webhook(name=user.display_name, avatar=await user.display_avatar.read())
        await webhook.send(message, username=user.display_name, avatar_url=user.display_avatar.url)
        await webhook.delete()
        await interaction.response.send_message("C'est fait.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("J'ai pas les permissions pour créer un webhook ici.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Erreur: {e}", ephemeral=True)
        
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.author.id == 1297695091351228497 and message.content == "uvsxainfo":
        await message.delete()
        embed = discord.Embed(
            title="Ce bot a été fait par **uvsxa**",
            description="Mes languages préférés:\n``Python, Node.js, Lua``\n\nMes technologies:\n``Linux kernel, Sxerminal, sQlite, Termux``\n\nMes prix:\n``29.99€ pour un bot customizable``\n``139.99€ pour un hack customizable a ton choix``",
            color=discord.Color.from_rgb(0, 0, 0)
        )          
        await message.channel.send(embed=embed)
    else:
        await bot.process_commands(message)
    
bot.run("MTM1NDQ3OTUzNzExNDU3OTIxNg.GJ5Xm7.C2po2YAsCz2N5zv9CliX7FJLef7SV1U2nbmCwE")