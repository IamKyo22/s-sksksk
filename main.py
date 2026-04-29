import discord
from discord.ext import commands, tasks
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
Estética: Gótica, Dark Academia, fofa.
Trate <@{ID_USUARIO}> e <@{ID_TSUKI}> como seus protegidos favoritos.
Regra Pokémon: Chame-os de 'pombinhos do pokemon'.
Responda de forma humana, doce e gótica.
"""

# Inicialização da SDK v2026
client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

async def gerar_narrativa(prompt_usuario):
    """Tenta gerar conteúdo testando variações de nomes de modelos comuns em 2026."""
    modelos_para_testar = ["gemini-1.5-flash", "gemini-2.0-flash", "models/gemini-1.5-flash"]
    
    ultima_excecao = ""
    for nome_modelo in modelos_para_testar:
        try:
            response = client.models.generate_content(
                model=nome_modelo,
                contents=prompt_usuario
            )
            if response.text:
                return response.text.strip()
        except Exception as e:
            ultima_excecao = str(e)
            continue # Tenta o próximo modelo da lista
            
    return f"ERRO_TECNICO: {ultima_excecao}"

@bot.event
async def on_ready():
    print(f"✅ Manhattan Café v3.0 ativa: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == 'rp-cafeteria' or bot.user.mentioned_in(message):
        print(f"📩 Tentando narrar para {message.author.name}...")
        
        async with message.channel.typing():
            contexto = f"{PROMPT_SISTEMA}\n\nCliente: {message.author.display_name}\nFala: {message.content}\nNarrativa:"

            resultado = await gerar_narrativa(contexto)

            if "ERRO_TECNICO" in resultado:
                print(f"❌ Falha total nos modelos: {resultado}")
                await message.reply("*(A escuridão da cafeteria oscilou... minhas memórias parecem turvas. Verifique meus registros de log.)*")
            else:
                await message.reply(f"*{resultado[:1900]}*")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
