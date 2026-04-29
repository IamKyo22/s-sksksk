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
Responda de forma doce, curta e gótica.
"""

# Inicialização simplificada
client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Manhattan Café v5.0 online: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Só responde no canal rp-cafeteria
    if message.channel.name == 'rp-cafeteria' or bot.user.mentioned_in(message):
        async with message.channel.typing():
            contexto = f"{PROMPT_SISTEMA}\n\nCliente: {message.author.display_name}\nFala: {message.content}\nNarrativa:"

            try:
                # TENTATIVA DIRETA - SEM FRUFRU
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=contexto
                )
                
                if response.text:
                    await message.reply(f"*{response.text.strip()}*")
                else:
                    await message.reply("⚠️ O Google não gerou texto (pode ser filtro de segurança).")
            
            except Exception as e:
                # AQUI ESTÁ A MODIFICAÇÃO: Ele vai cuspir o erro real no seu Discord
                erro_msg = str(e)
                print(f"❌ Erro detectado: {erro_msg}")
                
                if "429" in erro_msg:
                    await message.reply("❌ **Erro 429:** Minha cota de mensagens gratuitas acabou por agora. Tente em 1 minuto.")
                elif "404" in erro_msg:
                    await message.reply("❌ **Erro 404:** O modelo 'gemini-1.5-flash' não foi encontrado. Talvez a API Key esteja em uma região errada.")
                elif "400" in erro_msg:
                    await message.reply("❌ **Erro 400:** Requisição inválida ou conteúdo bloqueado pelo Google.")
                else:
                    await message.reply(f"❌ **Erro Desconhecido:** `{erro_msg[:100]}`")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
