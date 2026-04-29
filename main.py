import discord
from discord.ext import commands, tasks
from google import genai
import os
import asyncio

# ==========================================
# CONFIGURAÇÕES
# ==========================================
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

ID_USUARIO = 1115812841782517842
ID_TSUKI = 1115812841782517842 

PROMPT_SISTEMA = f"""
Você é a Manhattan Café, atendente da cafeteria 'Axiom'.
Estilo: Gótica, Dark Academia, fofa e gentil.
Cuidado especial com <@{ID_USUARIO}> e <@{ID_TSUKI}>.
Se falarem de Pokémon, chame-os de 'pombinhos do pokemon'.
Use descrições sensoriais e o estilo 'tsu'.
"""

# Inicialização da Nova SDK
client = genai.Client(api_key=GEMINI_API_KEY)
MODELO = "gemini-1.5-flash" # Consome menos cota que o 2.0

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(minutes=50) # Aumentei o tempo para economizar sua cota gratuita
async def rotina_da_atendente():
    channel = discord.utils.get(bot.get_all_channels(), name='rp-cafeteria')
    if channel:
        try:
            response = client.models.generate_content(
                model=MODELO, 
                contents="Narre uma ação fofa e gótica de rotina na cafeteria Axiom."
            )
            await channel.send(f"☕ *{response.text.strip()}*")
        except Exception as e:
            print(f"Erro na rotina: {e}")

@bot.event
async def on_ready():
    print(f"✅ Manhattan Café v2.0 conectada como {bot.user}")
    if not rotina_da_atendente.is_running():
        rotina_da_atendente.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == 'rp-cafeteria' or bot.user.mentioned_in(message):
        async with message.channel.typing():
            contexto = f"{PROMPT_SISTEMA}\n\nCliente: {message.author.display_name}\nFala: {message.content}\nNarrativa:"

            try:
                # Gerando conteúdo com a nova biblioteca
                response = client.models.generate_content(
                    model=MODELO,
                    contents=contexto
                )
                
                if response.text:
                    await message.reply(f"*{response.text.strip()[:1900]}*")
                else:
                    await message.reply("*Meus pensamentos se dissiparam como o vapor do café... pode repetir?*")

            except Exception as e:
                print(f"❌ ERRO: {e}")
                if "429" in str(e):
                    await message.channel.send("*(A atendente parece exausta e precisa de um descanso. [Limite de cota atingido, tente em alguns minutos])*")
                else:
                    await message.channel.send("*(A escuridão da cafeteria oscilou... tente novamente.)*")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
