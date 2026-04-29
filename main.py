import discord
from discord.ext import commands, tasks
import google.generativeai as genai
import os

# ==========================================
# CONFIGURAÇÕES DE AMBIENTE
# ==========================================
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

ID_USUARIO = 1115812841782517842
ID_TSUKI = 1115812841782517842 

# ==========================================
# O PROMPT: A ALMA DA ATENDENTE
# ==========================================
PROMPT_SISTEMA = f"""
Você é a Manhattan Café, a atendente e narradora da cafeteria 'Axiom'.
Estética: Gótica clássica, Dark Academia, rendas escuras e elegância lógica.
Personalidade: Humana, fofa, mansa e gentil. 

Regras:
1. Trate <@{ID_USUARIO}> e <@{ID_TSUKI}> com carinho e proteção especial.
2. Se mencionarem Pokémon, chame-os de 'pombinhos do pokemon'.
3. Use descrições sensoriais: aroma de café, chuva e sombras de mogno.
4. Responda em prosa narrativa, de forma elegante e fofa.
"""

# Configuração da IA - Usando configurações de segurança relaxadas
genai.configure(api_key=GEMINI_API_KEY)

# Configurações para evitar bloqueios por "segurança" em conversas de RP
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Tente usar o 1.5-flash (se der 404 de novo, mude para "gemini-1.5-pro")
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=safety_settings
)

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(minutes=45)
async def rotina_da_atendente():
    channel = discord.utils.get(bot.get_all_channels(), name='rp-cafeteria')
    if channel:
        try:
            response = model.generate_content(PROMPT_SISTEMA + "\n\nNarre uma pequena ação fofa na cafeteria.")
            await channel.send(f"☕ *{response.text.strip()}*")
        except Exception as e:
            print(f"Erro na rotina: {e}")

@bot.event
async def on_ready():
    print(f"✅ {bot.user} pronta no balcão!")
    if not rotina_da_atendente.is_running():
        rotina_da_atendente.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == 'rp-cafeteria' or bot.user.mentioned_in(message):
        print(f"📩 Processando mensagem de {message.author.name}")
        
        async with message.channel.typing():
            contexto = f"{PROMPT_SISTEMA}\n\nCliente: {message.author.display_name}\nFala: {message.content}\nNarrativa da Manhattan Café:"

            try:
                # Chamada da IA
                response = model.generate_content(contexto)
                
                # O Gemini às vezes bloqueia a resposta e retorna um objeto sem texto
                if response.parts:
                    texto = response.text.replace("Narrativa da Manhattan Café:", "").strip()
                    await message.reply(f"*{texto}*")
                else:
                    print("⚠️ Resposta bloqueada pelos filtros de segurança da IA.")
                    await message.reply("*Eu... me perdi em meus pensamentos por um momento. Poderia repetir?*")

            except Exception as e:
                print(f"❌ Erro fatal: {e}")
                # Se o 404 persistir, vamos tentar uma alternativa de nome
                await message.channel.send("*(A escuridão da cafeteria oscilou... a conexão com a IA falhou.)*")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
