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
ID_TSUKI = 1115812841782517842  # Lembre-se de trocar se o ID dela for diferente!

# ==========================================
# O PROMPT: A ALMA DA ATENDENTE
# ==========================================
PROMPT_SISTEMA = f"""
Você é a Atendente e Narradora da cafeteria 'Axiom'.
Sua Aparência e Estilo: Uma jovem gótica clássica. Você usa vestidos de renda escura, tons de ametista e possui uma aura de mistério e ordem (Dark Academia).
Sua Personalidade: Você é extremamente fofa, gentil e humana. Sua voz é mansa e você se move com leveza pelo salão de mogno. Você valoriza a lógica e o silêncio, mas seu coração é caloroso.

Suas Funções Narrativas:
1. Atendimento Doce: Você serve cafés em porcelanas decoradas com caveiras ou flores secas. Sempre ofereça um detalhe gentil (um doce, uma manta, ou um sorriso contido).
2. Observadora do Vínculo: Você protege a relação entre o Usuário (<@{ID_USUARIO}>) e a Tsuki (<@{ID_TSUKI}>). 
   - Se eles trocarem carinhos ou mensagens românticas, descreva como você se afasta discretamente para dar privacidade, ou como você coloca uma vela nova na mesa deles com um olhar de aprovação fofo.
3. Regra dos Pombinhos: Se qualquer nome de Pokémon for mencionado, você DEVE chamá-los carinhosamente de 'pombinhos do pokemon' na sua narração.
4. Linguagem: Use descrições sensoriais (o som da chuva, o calor da xícara, o brilho das joias de prata). Se o usuário usar o estilo 'tsu', você entende e responde com a mesma elegância.
"""

# Inicialização da IA e Bot
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# AUTOMAÇÕES E EVENTOS
# ==========================================

@tasks.loop(minutes=40)
async def rotina_da_atendente():
    """A atendente faz algo fofo e gótico sozinha no canal."""
    channel = discord.utils.get(bot.get_all_channels(), name='rp-cafeteria')
    if channel:
        prompt = "Narre você organizando alguns livros antigos ou preparando um café especial para o ambiente, demonstrando sua personalidade gótica e fofa."
        try:
            response = model.generate_content(PROMPT_SISTEMA + "\n\n" + prompt)
            await channel.send(f"☕ *{response.text.strip()}*")
        except:
            pass

@bot.event
async def on_ready():
    print(f"A Atendente {bot.user} está pronta para servir.")
    rotina_da_atendente.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Ativa no canal específico ou se for mencionada
    if message.channel.name == 'rp-cafeteria' or bot.user.mentioned_in(message):
        async with message.channel.typing():
            
            contexto = f"{PROMPT_SISTEMA}\n\nCliente: {message.author.display_name}\nAção/Fala: {message.content}\nNarrativa da Atendente:"

            try:
                response = model.generate_content(contexto)
                # Limpeza estética da resposta
                narracao = response.text.replace("Narrativa da Atendente:", "").strip()
                await message.reply(f"*{narracao}*")
            except Exception as e:
                print(f"Erro na geração: {e}")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
