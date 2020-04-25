import logging
from enum import Enum
from random import randint,choice
import discord
from discord.ext import commands
from dadjokes import Dadjoke
from core import checks
import box
import json
import string
from core.models import PermissionLevel

Cog = getattr(commands, "Cog", object)

logger = logging.getLogger("Modmail")


def escape(text: str, *, mass_mentions: bool = False, formatting: bool = False) -> str:
    """Get text with all mass mentions or markdown escaped.

    Parameters
    ----------
    text : str
        The text to be escaped.
    mass_mentions : `bool`, optional
        Set to :code:`True` to escape mass mentions in the text.
    formatting : `bool`, optional
        Set to :code:`True` to escpae any markdown formatting in the text.

    Returns
    -------
    str
        The escaped text.

    """
    if mass_mentions:
        text = text.replace("@everyone", "@\u200beveryone")
        text = text.replace("@here", "@\u200bhere")
    if formatting:
        text = text.replace("`", "\\`").replace("*", "\\*").replace("_", "\\_").replace("~", "\\~")
    return text

class RPS(Enum):
    sasso = "\N{MOYAI}"
    carta = "\N{PAGE FACING UP}"
    forbici = "\N{BLACK SCISSORS}"

class RPSParser:
    def __init__(self, argument):
        argument = argument.lower()
        if argument == "sasso":
            self.choice = RPS.sasso
        elif argument == "carta":
            self.choice = RPS.carta
        elif argument == "forbici":
            self.choice = RPS.forbici
        else:
            self.choice = None
class Fun(Cog):
    """Qualche comando Divertente"""
  
    ball = [
        "Come vedo, sì",
        "È certo",
        "È decisamente così",
        "Più probabilmente",
        "A vista è buono",
        "I segni indicano sì",
        "Senza dubbio",
        "Si",
        "Si, devinitivamente",
        "Puoi contarci",
        "Risposta confusa, riprova",
        "Chiedi più tardi",
        "Meglio non dirtelo ora",
        "Non posso predire ora",
        "Concentrati e chiedi di nuovo",
        "Non contarci",
        "La mia risposta è no",
        "Le mie sorgenti dicono no",
        "A vista non è cosi buono",
        "Molto dubbioso"
    ]
    def __init__(self,bot):
        super().__init__()
        self.bot = bot
        #self.db = bot.plugin_db.get_partition(self)
        
    @commands.command()
    async def choose(self, ctx, *choices):
        """Choose between multiple options.

        To denote options which include whitespace, you should use
        double quotes.
        """
        choices = [escape(c, mass_mentions=True) for c in choices]
        if len(choices) < 2:
            await ctx.send(_("Not enough options to pick from."))
        else:
            await ctx.send(choice(choices))
            
    @commands.command()
    async def roll(self, ctx, number: int = 6):
        """Roll a random number.

        The result will be between 1 and `<number>`.

        `<number>` defaults to 6.
        """
        author = ctx.author
        if number > 1:
            n = randint(1, number)
            await ctx.send("{author.mention} :game_die: {n} :game_die:".format(author=author, n=n))
        else:
            await ctx.send(_("{author.mention} Maybe higher than 1? ;P").format(author=author))
            
    @commands.command()
    async def flip(self,ctx):
        """Flip a coin"""
        answer = choice(["HEADS!*","TAILS!*"])
        await ctx.send(f"*Flips a coin and...{answer}")
        
    @commands.command()
    async def rps(self,ctx,your_choice:RPSParser):
        """Gioca a Sasso, Carta, Forbici"""
        author = ctx.author
        player_choice = your_choice.choice
        if not player_choice:
            return await ctx.send("Questa non è un'opzione valida. Prova sasso, carta o forbici.")
        bot_choice = choice((RPS.sasso, RPS.carta, RPS.forbici))
        cond = {
            (RPS.sasso, RPS.carta): False,
            (RPS.sasso, RPS.forbici): True,
            (RPS.carta, RPS.sasso): True,
            (RPS.carta, RPS.forbici): False,
            (RPS.forbici, RPS.sasso): False,
            (RPS.forbici, RPS.carta): True,
        }
        if bot_choice == player_choice:
            outcome = None  # Tie
        else:
            outcome = cond[(player_choice, bot_choice)]
        if outcome is True:
            await ctx.send(f"{bot_choice.value} Hai vinto, {author.mention}!")
        elif outcome is False:
            await ctx.send(f"{bot_choice.value} Hai perso, {author.mention}!")
        else:
            await ctx.send(f"{bot_choice.value} Siamo pari, {author.mention}!")
    @commands.command(name="8ball",aliases=["8"])
    async def _8ball(self, ctx, *, question: str):
        """Ask 8 ball a question.

        Question must end with a question mark.
        """
        if question.endswith("?") and question != "?":
            await ctx.send((choice(self.ball) if question != "testù?" else "testù, testù, testù testù! testù testù testù"))
        else:
            await ctx.send("Quella non sembra una domanda.")

    @commands.command(aliases=["badjoke"])
    async def dadjoke(self,ctx):
        """Gives a random Dadjoke"""
        x = Dadjoke()
        await ctx.send(x.joke)
        
    @commands.command()
    async def lmgtfy(self, ctx, *, search_terms: str):
        """Create a lmgtfy link."""
        search_terms = escape(
            search_terms.replace("+", "%2B").replace(" ", "+"), mass_mentions=True
        )
        await ctx.send("<https://lmgtfy.com/?q={}>".format(search_terms))
        
    @commands.command()
    async def say(self,ctx,* ,message):
        """Fai dire qualcosa al bot"""
        msg = escape(message,mass_mentions=True)
        await ctx.send(msg)
    @commands.command()
    async def reverse(self, ctx, *, text):
        """!otseT out li etrevnI"""
        text =  escape("".join(list(reversed(str(text)))),mass_mentions=True)
        await ctx.send(text)
        
    @commands.command()
    async def meme(self, ctx):
        """Da un meme a caso. La roba della vita."""
        r = await self.bot.session.get("https://www.reddit.com/r/dankmemes/top.json?sort=top&t=day&limit=500")
        r = await r.json()
        r = box.Box(r)
        data = choice(r.data.children).data
        img = data.url
        title = data.title
        upvotes = data.ups
        downvotes = data.downs
        em = discord.Embed(color=ctx.author.color, title=title)
        em.set_image(url=img)
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        em.set_footer(text=f"👍{upvotes} | 👎 {downvotes}")
        await ctx.send(embed=em)
    @commands.command()
    async def emojify(self, ctx, *, text: str):
        """Converte il testo in emoji!"""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        to_send = ""
        for char in text:
            if char == " ":
                to_send += " "
            elif char.lower() in 'qwertyuiopasdfghjklzxcvbnm':
                to_send += f":regional_indicator_{char.lower()}:  "
            elif char in '1234567890':
                numbers = {
                    "1": "one",
                    "2": "two",
                    "3": "three",
                    "4": "four",
                    "5": "five",
                    "6": "six",
                    "7": "seven",
                    "8": "eight",
                    "9": "nine",
                    "0": "zero"
                }
                to_send += f":{numbers[char]}: "
            else:
                return await ctx.send("I caratteri devono essere una lettera o un numero.  Tutto il resto non è supportato.")
        if len(to_send) > 2000:
            return await ctx.send("L'emoji è troppo grande per adattarsi a un messaggio!")
        await ctx.send(to_send)
        
    @commands.command()
    @commands.guild_only()
    async def roast(self, ctx,*, user: discord.Member = None):
        '''Insulterò qualcuno per te!'''
   
        msg = f"Hey, {user.mention}! " if user is not None else ""
        roasts = ["Ti darei uno sguardo cattivo ma ne hai già uno.", "Se hai due facce, almeno una rendila carina.", "Sembra che la tua faccia abbia preso fuoco e qualcuno abbia cercato di spegnerlo con un martello. LOL!", "Sembra che la tua faccia abbia preso fuoco e qualcuno abbia cercato di spegnerlo con un martello.", "Mi piacerebbe vedere le cose dal tuo punto di vista, ma non riesco ad avere la testa così in alto nel sedere.", "Gli scienziati affermano che l'universo è composto da neutroni, protoni ed elettroni. Si sono dimenticati di menzionare i deficienti.", "Perché è accettabile per te essere un idiota, ma non per me segnalarlo?", "Solo perché ne hai uno non significa che devi comportarti come tale.", "Un giorno andrai lontano... e spero che tu rimanga lì.", "Errore, riprova... aspetta,  sei tu l'errore!", "No, quei pantaloni non ti fanno sembrare più grasso, come potrebbero?", "Risparmia il fiato: ne avrai bisogno per far saltare il tuo appuntamento.", "Se vuoi davvero sapere degli errori, dovresti chiedere ai tuoi genitori.", " Qualunque sia il tipo di look che stavi cercando, ti sei perso.", "Ehi, hai qualcosa sul mento ... no, la terza in basso.", "Non so cosa ti rende così stupido, ma funziona davvero.", "Sei la prova che l'evoluzione può andare al contrario.", "I cervelli non sono tutto. Nel tuo caso non sono niente.", "Ti ho pensato oggi. Mi ha ricordato di portare fuori la spazzatura.", "Sei così brutto quando ti guardi allo specchio, il tuo riflesso distoglie lo sguardo.", "Veloce - controlla il tuo viso! Ho appena trovato il tuo naso nei miei affari.", "È meglio lasciare che qualcuno pensi che sei stupido piuttosto che aprire la bocca e dimostrarlo.", "Sei una persona così bella, intelligente, meravigliosa. Oh mi dispiace, pensavo che avessimo una competizione di bugie.", "Ti darei uno schiaffo ma non voglio far sembrare la tua faccia migliore.", "Hai il diritto di tacere perché qualunque cosa tu dica probabilmente sarà comunque stupida."]
        if str(user.id) == str(ctx.bot.user.id):
            return await ctx.send(f"Uh?!! Bel tentativo! Non insulterò me stesso. Invece ora insulto te!\n\n {ctx.author.mention} {choice(roasts)}")
        await ctx.send(f"{msg} {choice(roasts)}")

    @commands.command(aliases=['sc'])
    @commands.guild_only()
    async def smallcaps(self,ctx,*,message):
        """ᴄᴏɴᴠᴇʀᴛᴇ ɪʟ ᴛᴜᴏ ᴛᴇꜱᴛᴏ ᴀ ᴜɴ ᴍᴀɪᴜꜱᴄᴏʟᴏ ᴘɪᴄᴄᴏʟᴏ!!"""
        alpha = list(string.ascii_lowercase)     
        converter = ['ᴀ', 'ʙ', 'ᴄ', 'ᴅ', 'ᴇ', 'ꜰ', 'ɢ', 'ʜ', 'ɪ', 'ᴊ', 'ᴋ', 'ʟ', 'ᴍ', 'ɴ', 'ᴏ', 'ᴘ', 'ǫ', 'ʀ', 'ꜱ', 'ᴛ', 'ᴜ', 'ᴠ', 'ᴡ', 'x', 'ʏ', 'ᴢ']
        new = ""
        exact = message.lower()
        for letter in exact:
            if letter in alpha:
                index = alpha.index(letter)
                new += converter[index]
            else:
                new += letter
        await ctx.send(new)
    
            
    @commands.command()
    async def cringe(self,ctx,* ,message):
        """rEnDe iL TeStO CrInGe!!"""
        text_list = list(message) #convert string to list to be able to edit it
        for i in range(0,len(message)):
            if i % 2 == 0:
                text_list[i]= text_list[i].lower()
            else:
                text_list[i]=text_list[i].upper()
        message ="".join(text_list) #convert list back to string(message) to print it as a word
        await ctx.send(message)

      
def setup(bot):
    bot.add_cog(Fun(bot))    





        
    
    

    
    
