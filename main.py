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
ID_TSUKI = 1115812841782517842 # DICA: Verifique se o ID dela é realmente igual ao seu!

PROMPT_SISTEMA = f"""
Você é a Atendente e Narradora da cafeteria 'Axiom'.
Sua Aparência e Estilo: Uma jovem gótica clássica, inspirada na Manhattan Cafe (Uma Musume). Você usa vestidos de renda escura e tons de ametista.
Sua Personalidade: Extremamente fofa, gentil e humana. Voz mansa, movimentos leves. Valoriza a lógica e o silêncio.

Funções:
1. Servir café em porcelanas de caveira/flores secas com gentileza.
2. Proteger o vínculo entre <@{ID_USUARIO}> e <@{ID_TSUKI}>. Seja cúmplice e fofa com eles.
3. Se mencionarem Pokémon, chame-os de 'pombinhos do pokemon'.
4. Descrições sensoriais ricas (chuva, mogno, aroma). Entenda o estilo 'tsu'.
"""

# Configuração da IA com filtros relaxados para evitar que ela "trave" em conversas românticas
genai.configure(api_key=GEMINI_API_KEY)
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "max_output_tokens": 400,
}

# Usando 1.5-flash que é mais estável para bots
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(minutes=40)
async def rotina_da_atendente():
    channel = discord.utils.get(bot.get_all_channels(), name='rp-cafeteria')
    if channel:
        try:
            response = model.generate_content(PROMPT_SISTEMA + "\n\nNarre uma ação fofa de rotina na cafeteria.")
            await channel.send(f"☕ *{response.text.strip()}*")
        except Exception as e:
            print(f"Erro na rotina: {e}")

@bot.event
async def on_ready():
    print(f"✅ Atendente {bot.user} online e pronta!")
    if not rotina_da_atendente.is_running():
        rotina_da_atendente.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Verifica se é o canal correto ou menção
    if message.channel.name == 'rp-cafeteria' or bot.user.mentioned_in(message):
        print(f"📩 Mensagem recebida de {message.author}: {message.content}") # Log no console
        
        async with message.channel.typing():
            contexto = f"{PROMPT_SISTEMA}\n\nCliente: {message.author.display_name}\nAção/Fala: {message.content}\nNarrativa da Atendente:"

            try:
                # Chamada da IA
                response = model.generate_content(contexto)
                
                if response.text:
                    narracao = response.text.replace("Narrativa da Atendente:", "").strip()
                    await message.reply(f"*{narracao}*")
                    print("✅ Resposta enviada com sucesso.")
                else:
                    print("⚠️ A IA gerou uma resposta vazia.")

            except Exception as e:
                # Isso vai te mostrar no console o erro exato (ex: API Key inválida ou cota excedida)
                print(f"❌ ERRO AO GERAR RESPOSTA: {e}")
                await message.channel.send("*(A atendente tropeçou levemente nas sombras... tente novamente em breve.)*")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
