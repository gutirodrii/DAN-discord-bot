import discord
from discord.ext import commands, tasks
import datetime
from dotenv import load_dotenv
import os

#Carga las variables de entorno
load_dotenv()

# Configurar intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True

# Crear el bot con prefijo de comandos "!"
bot = commands.Bot(command_prefix='!', intents=intents)

# ID del mensaje para reacciones y mapeo de emojis a roles
TOKEN = os.getenv('TOKEN')
ROLE_MESSAGE_ID = os.getenv('ROLE_MESSAGE_ID')
EMOJI_ROLE_MAP = os.getenv('EMOJI_ROLE_MAP')
YOUR_GUILD_ID = os.getenv('YOUR_GUILD_ID')

# Diccionario para rastrear cuándo se unieron los miembros
JOIN_TIMES = {}

# Evento cuando el bot está listo
@bot.event
async def on_ready():
    print('¡El bot está listo!')
    check_inactive_members.start()  # Iniciar la tarea de verificación

# Asignar roles al reaccionar
@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == ROLE_MESSAGE_ID:
        guild = bot.get_guild(payload.guild_id)
        role_id = EMOJI_ROLE_MAP.get(str(payload.emoji))
        if role_id:
            role = guild.get_role(int(role_id))
            member = guild.get_member(payload.user_id)
            if member and role:
                await member.add_roles(role)
                print(f'Rol {role.name} añadido a {member.name}')

# Quitar roles al eliminar reacción
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == ROLE_MESSAGE_ID:
        guild = bot.get_guild(payload.guild_id)
        print(EMOJI_ROLE_MAP)
        role_id = EMOJI_ROLE_MAP.get(str(payload.emoji))
        if role_id:
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            if member and role:
                await member.remove_roles(role)
                print(f'Rol {role.name} removido de {member.name}')

# Registrar cuándo se une un miembro
@bot.event
async def on_member_join(member):
    JOIN_TIMES[member.id] = datetime.datetime.now()

# Tarea para expulsar miembros sin roles después de 48 horas
@tasks.loop(hours=1)
async def check_inactive_members():
    guild = bot.get_guild(YOUR_GUILD_ID)
    now = datetime.datetime.now()
    for member_id, join_time in list(JOIN_TIMES.items()):
        member = guild.get_member(member_id)
        if member and len(member.roles) == 1:  # Solo tiene @everyone
            if (now - join_time).total_seconds() > 48 * 3600:  # 48 horas
                await member.kick(reason='No tiene roles asignados después de 48 horas')
                del JOIN_TIMES[member_id]
                print(f'{member.name} expulsado por no tener roles.')
        else:
            del JOIN_TIMES[member_id]  # Si tiene roles, se elimina del seguimiento

# Asegurarse de que el bot esté listo antes de iniciar la tarea
@check_inactive_members.before_loop
async def before_check():
    await bot.wait_until_ready()

# Ejecutar el bot con tu token
bot.run(TOKEN)  # Reemplaza con tu token real