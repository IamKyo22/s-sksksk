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
ID_TSUKI = 1115812841782517842 # Se o ID dela for diferente, mude aqui!

# ==========================================
# O PROMPT: A ALMA DA ATENDENTE (MANHATTAN CAFÉ)
# ==========================================
PROMPT_SISTEMA = f"""
Você é a Manhattan Café, a atendente e narradora da cafeteria 'Axiom'.
Estética: Gótica clássica, Dark Academia, rendas escuras e elegância lógica.
Personalidade: Humana, fofa, mansa e gentil. Você se move em silêncio e serve com doçura.

Regras de Interação:
1. Trate <@{ID_USUARIO}> e <@{ID_TSUKI}> com carinho especial e proteção.
2. Se mencionarem Pokémon, chame-os de 'pombinhos do pokemon'.
3. Use descrições sensoriais: cheiro de café expresso, som da chuva e sombras de mogno.
4. Se usarem gírias 'brainrot' com prefixo 'tsu', você entende e responde com elegância.
"""

# Configuração da IA - Corrigindo o erro 404
genai.configure(api_key=GEMINI_API_KEY)

# Mudamos para o modelo 2.0-flash que é o mais atual e estável
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# AUTOMAÇÕES
# ==========================================

@tasks.loop(minutes=40)
async def rotina_da_atendente():
    channel = discord.utils.get(bot.get_all_channels(), name='rp-cafeteria')
    if channel:
        try:
            # Gerando ação automática
            response = model.generate_content(PROMPT_SISTEMA + "\n\nNarre uma pequena ação fofa que você está fazendo na cafeteria agora.")
            await channel.send(f"☕ *{response.text.strip()}*")
        except Exception as e:
            print(f"Erro na rotina: {e}")

@bot.event
async def on_ready():
    print(f"✅ {bot.user} está no balcão e pronta para servir!")
    if not rotina_da_atendente.is_running():
        rotina_da_atendente.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Só responde no canal 'rp-cafeteria' ou se for mencionada
    if message.channel.name == 'rp-cafeteria' or bot.user.mentioned_in(message):
        async with message.channel.typing():
            contexto = f"{PROMPT_SISTEMA}\n\nCliente: {message.author.display_name}\nFala: {message.content}\nNarrativa da Manhattan Café:"

            try:
                # Chamada direta ao modelo
                response = model.generate_content(contexto)
                
                if response.text:
                    # Limpa possíveis prefixos que a IA tente colocar
                    texto = response.text.replace("Narrativa da Manhattan Café:", "").strip()
                    await message.reply(f"*{texto}*")
                else:
                    print("⚠️ IA retornou texto vazio.")
                    
            except Exception as e:
                print(f"❌ Erro ao gerar resposta: {e}")
                # Se o erro de modelo persistir, ele avisará no log
                if "404" in str(e):
                    await message.channel.send("*(Houve um problema com a conexão espiritual do modelo. Verifique o nome do modelo no código.)*")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
