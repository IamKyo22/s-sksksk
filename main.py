import discord
from discord.ext import commands
from google import genai
import os

# ==========================================
# CONFIGURAÇÕES
# ==========================================
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

ID_USUARIO = 1115812841782517842
ID_TSUKI = 1115812841782517842 

PROMPT_SISTEMA = f"""
Você é a Manhattan Café, atendente da cafeteria 'Axiom'.
Estilo: Gótica, fofa e gentil.
Trate <@{ID_USUARIO}> e <@{ID_TSUKI}> como seus pombinhos do pokemon favoritos.
Responda de forma doce e gótica.
"""

# Inicialização
client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Manhattan Café v6.0 online: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == 'rp-cafeteria' or bot.user.mentioned_in(message):
        async with message.channel.typing():
            contexto = f"{PROMPT_SISTEMA}\n\nCliente: {message.author.display_name}\nFala: {message.content}\nNarrativa:"

            try:
                # MUDANÇA AQUI: Adicionamos 'models/' e usamos o 2.0-flash
                response = client.models.generate_content(
                    model="models/gemini-2.0-flash", 
                    contents=contexto
                )
                
                if response.text:
                    await message.reply(f"*{response.text.strip()}*")
                else:
                    await message.reply("⚠️ O Google bloqueou esta resposta por segurança.")
            
            except Exception as e:
                erro_msg = str(e)
                print(f"❌ Erro: {erro_msg}")
                
                # Se o 2.0 também der 404, tentamos o 1.5 com o prefixo models/
                if "404" in erro_msg:
                    try:
                        response = client.models.generate_content(
                            model="models/gemini-1.5-flash",
                            contents=contexto
                        )
                        await message.reply(f"*{response.text.strip()}*")
                    except Exception as e2:
                        await message.reply(f"❌ Erro de Modelo: `{e2}`")
                else:
                    await message.reply(f"❌ Erro: `{erro_msg[:100]}`")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
