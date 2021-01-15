import discord
from discord.ext import commands
import requests as r
import keep_alive
import os
import time
import asyncio
from bs4 import BeautifulSoup as bs


TOKEN = os.getenv('TOKEN')
PREFIX = 'f!'

client = commands.Bot(command_prefix=PREFIX)
@client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game("Type f!help for help!")
        )
    print('We have logged in as {0.user}'.format(client))

# Error handling
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Didn't find a command with that name, type `{PREFIX}help` for a list of commands. \n")

# Ping
@client.command(pass_context=True)
async def ping(ctx):
    try:
        before = time.monotonic()
        message = await ctx.send("Pong!")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"Pong! Bot Latency`{int(ping)}ms` API Latency `{int(client.latency * 1000)}ms`")
        print(f'Ping {int(ping)}ms')

    except Exception as e:
        print(type(e), e)

@client.command()
async def search(ctx, *args):
    try:
        #print(args)
        args = '+'.join(args)
        print(args, ctx.author, ctx.guild.name)

        if len(args) < 1:
            await ctx.send('No arguments recieved! Try putting something after the command?')
            print('No arguments recieved! Try putting something after the command?')
            #raise ValueError('Empty args')

        else:  
            e = discord.Embed(title='Search', colour=discord.Colour.blue())
            e.set_footer(text='search on fancade.com/search')
            #e.description = '[test](https://google.com/)'

            URL = f'https://api.fancade.com/search?query={args}'
            page = r.get(URL)
            o = 'https://fancade.page.link/?ibi=com.martinmagni.fancade&isi=1280404080&apn=com.martinmagni.fancade&link=http://www.fancade.com/games/'
            #print(eval(page.content)['games'])

            g = eval(page.content)['games']

            s = ''
            c = 0
            for i in g:
                s += f'• [{i[1]}]({o}{i[0]}) by {i[2]}\n'
                c+=1
                if c >= 10:
                    break

            if len(g) >= 1:
                e.set_image(url=f'https://www.fancade.com/search/images/{g[0][0]}.jpg')
                e.description = s
            else:
                e.description = 'Nothing found'
            #print(e)
            await ctx.send(embed=e)
    except Exception as e:
        print(e)
        await ctx.send('Report this error to the bot owner:' + str(e))

@client.command(aliases=['doc'])
async def wiki(ctx, *args):
    try:
        print(args, ctx.author, ctx.guild.name)
        if len(args) < 1:
            await ctx.send('No arguments recieved! Try putting something after the command?')
            print('No arguments recieved! Try putting something after the command?')
            #raise ValueError('Empty args')

        else:
            args = '+'.join(args)
            URL = 'https://www.fancade.com/wiki/gollum/search?q=' + args
            page = r.get(URL)
            soup = bs(page.content, 'html.parser')
            
            results = soup.find(id='search-results')
            
            links = results.find_all('a')
            titles = results.find_all('span', class_='text-bold')
            descs = results.find_all('div', class_='search-context')

            dic = {'titles' : [ ['https://fancade.com'+str(link['href']) \
                                for link in links if link['href'][:14] != '/wiki/uploads/'],
                                [title.text for title in titles if title.text[:8] != 'uploads/'] ],
                    'descs' :   [desc.text for desc in descs] }
            
            if len(dic['titles'][1]) < 1:
                await ctx.send('Nothing appropriate found...')

            else:
                s = 'What did you mean?\n\n'
                l = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬',
                '🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵']

                for i in range(len(dic['titles'][1])):
                    s += f"{l[i]}) {dic['titles'][1][i]}\n"
                await ctx.send(s)

                async for message in ctx.channel.history(limit=5):
                    if message.author == client.user:
                        for i in range(len(dic['titles'][1])):
                            await message.add_reaction(l[i])
                        break


                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in l

                try:
                    reaction, user = await client.wait_for('reaction_add',
                                            timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.author.mention} You didn't react...")

                else:
                    k = [i for i in range(len(l)) if l[i] == str(reaction)][0]
                    t = dic['titles'][1][k]
                    t1 = dic['titles'][0][k]
                    e = discord.Embed(
                        title=t,
                        url=t1,
                        description=dic['descs'][k],
                        colour=discord.Colour.blue()
                    )
                    #print(dic['descs'][k])
                    e.set_footer(text='Read more at https://fancade.com/wiki')

                    await ctx.send(f'{ctx.author.mention} {args} >> {t1}',
                                    embed=e)
                    await message.delete()

    except AttributeError:
        await ctx.send('Nothing appropriate found...')

    except Exception as e:
        print(e)
        if 'Must be 2048 or fewer' in str(e):
            await ctx.send(t1)
            await message.delete()
        else:
            await ctx.send('Report this error to the bot owner:' + str(e))
            print(type(e))
            raise e

@client.command(pass_context=True, name='help')
async def _help(ctx):
    try:
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        embed.set_author(name='Help')
        embed.add_field(name=f'{PREFIX}ping',
                        value='Returns ping',
                        inline=False)
        embed.add_field(name=f'{PREFIX}search',
                        value='Returns results by searching from fancade.com/search',
                        inline=False)
        embed.add_field(name=f'{PREFIX}wiki or {PREFIX}doc',
                        value='Returns results by searching from fancade.com/wiki',
                        inline=False)

        await ctx.send(embed=embed)
    except Exception as e:
        print(e)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        print(message)
        print(message.content)

    await client.process_commands(message)


keep_alive.keep_alive()
client.run(TOKEN)
