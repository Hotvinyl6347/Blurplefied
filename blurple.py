import discord
import logging
import asyncio
import time
import aiohttp

from PIL import Image, ImageEnhance, ImageSequence
import PIL
from io import BytesIO
import io
import datetime
import copy
import sys
import resizeimage
from resizeimage import resizeimage
import math

import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands.cooldowns import BucketType

bot = commands.Bot(command_prefix=">")

message = discord.Message

bot.remove_command('help')

@bot.event
async def on_connect():
    print('------')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print("Discord.py " + discord.__version__)
    print("Forked by Xeno#0001")
    print('------')
    await bot.change_presence(activity=">help for commands")

@bot.command(pass_context=True, aliases=["reboot"])
async def shutdown(ctx):
    owner = discord.utils.get(ctx.message.server.roles, name="Owner")
    if owner in ctx.message.author.roles:
        embed=discord.Embed(title="", timestamp=datetime.datetime.utcnow(), colour=0x7289da)
        embed.add_field(name="Shutting down", value="Blurplefied")
        await bot.send_message(ctx.message.channel, embed=embed)
        await bot.logout()
    else:
        await bot.send_message(ctx.message.channel, embed=discord.Embed(description="No permission.", colour=0x7289da))

@bot.command(pass_context=True)
async def help(ctx):
    embed=discord.Embed(title="", timestamp=datetime.datetime.utcnow(), colour=0x7289da)
    embed.set_author(name="Commands list")
    embed.add_field(name="Countdown", value="Time until Discord's Anniversary. \n**Usage:**\n`>countdown`")
    embed.add_field(name="Blurple", value="Check how much blurple is in an image. If used without a picture, it analyses your own profile picture, and if it has enough blurple, you will receive a role. \n**Usage:**\n`{BOT_PREFIX}blurple <@username/user ID/picture url/None/uploaded image>`")
    embed.add_field(name="Blurplefy", value="Blurplefy your image/gif! \n**Usage:**\n`>blurplefy <@username/user ID/picture url/None/uploaded image>`")
    embed.set_footer(text="Help message requested by %s#%s" % (ctx.message.author.name, ctx.message.author.discriminator))
    embed.set_thumbnail(url=bot.user.avatar_url)
    await bot.send_message(ctx.message.channel, embed=embed)

@bot.command(pass_context=True)
@commands.cooldown(rate=1, per=5, type=BucketType.user)
async def ping(ctx):
    latency=bot.latency*1000
    latency=round(latency,2)
    latency=str(latency)
    embed=discord.Embed(title="", colour=0x7289da, timestamp=datetime.datetime.utcnow())
    embed.set_author(name="Ping!")
    embed.add_field(name='Bot latency', value=latency+"ms")
    await bot.send_message(ctx.message.channel, embed=embed)

@bot.command(pass_context=True)
async def countdown(ctx):
    def strfdelta(tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)

    timeleft = datetime.datetime(2018, 5, 13) + datetime.timedelta(hours=7) - datetime.datetime.utcnow()
    embed = discord.Embed(name="", colour=0x7289da)
    embed.set_author(name="Time left until Discord's 3rd Anniversary")
    embed.add_field(name="Countdown to midnight May 13 California time (UTC-7)", value=(strfdelta(timeleft, "**{days}** days, **{hours}** hours, **{minutes}** minutes, and **{seconds}** seconds")))
    await bot.send_message(ctx.message.channel, embed=embed)

@bot.command(aliases=['blurplfygif', 'blurplefiergif'])
@commands.cooldown(rate=1, per=90, type=BucketType.user)
async def blurplefygif(ctx, arg1 = None):
    picture = None

    await bot.send_message(ctx.message.channel, "<@%s>, starting blurple image analysis (Please note that this may take a while)")


    start = time.time()
    if arg1 != None:
        if "<@!" in arg1:
            arg1 = arg1[:-1]
            arg1 = arg1[3:]
        if "<@" in arg1:
            arg1 = arg1[:-1]
            arg1 = arg1[2:]
        if arg1.isdigit() == True:
            try:
                user = await bot.get_user_info(int(arg1))
                picture = user.avatar_url
            except Exception:
                await bot.send_message(ctx.message.channel, "Please send a valid user mention/ID")
        else:
            picture = arg1
    else:
        link = ctx.message.attachments
        if len(link) != 0:
            for image in link:
                picture = image.url

    if picture == None:
        picture = ctx.author.avatar_url

    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(picture) as r:
                response = await r.read()
    except ValueError:
        await bot.send_message(ctx.message.channel, "<@%s>, please link a valid image URL")
        return

    colourbuffer = 20

    try:
        im = Image.open(BytesIO(response))
    except Exception:
        await bot.send_message(ctx.message.channel, "<@%s>, please link a valid image URL")
        return

    if im.format != 'GIF':
        return

    imsize = list(im.size)
    impixels = imsize[0]*imsize[1]

    maxpixelcount = 1562500

    end = time.time()
    await bot.send_message(ctx.message.channel, "<@%s>, image fetched, analysing image (This process can sometimes take a while depending on the size of the image) ({end - start:.2f}s)')
    start = time.time()
    if impixels > maxpixelcount:
        downsizefraction = math.sqrt(maxpixelcount/impixels)
        im = resizeimage.resize_width(im, (imsize[0]*downsizefraction))
        imsize = list(im.size)
        impixels = imsize[0]*imsize[1]
        end = time.time()
        await bot.send_message(ctx.message.channel, "<@%s>, image resized smaller for easier processing ({end-start:.2f}s)')
        start = time.time()

    def imager(im):
        frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
        newgif = []

        for frame in frames:

            frame = frame.convert(mode='L')
            frame = ImageEnhance.Contrast(frame).enhance(1000)
            frame = frame.convert(mode='RGB')

            img = frame.load()

            for x in range(imsize[0]):
                i = 1
                for y in range(imsize[1]):
                    pixel = img[x,y]

                    if pixel != (255, 255, 255):
                        img[x,y] = (114, 137, 218)

            newgif.append(frame)

        image_file_object = io.BytesIO()

        gif = newgif[0]
        gif.save(image_file_object, format='gif', save_all=True, append_images=newgif[1:], loop=0)

        image_file_object.seek(0)
        return image_file_object

    with aiohttp.ClientSession() as session:
        start = time.time()
        image = await bot.loop.run_in_executor(None, imager, im)
        end = time.time()
        await bot.send_file(ctx.message.channel, fp=image, filename='image.gif')

@bot.command(pass_context=True, aliases=['blurplfy', 'blurplefier'])
@commands.cooldown(rate=1, per=60, type=BucketType.user)
async def blurplefy(ctx, arg1 = None):
    """Blurplefy your image/gif!"""
    picture = None
    await bot.send_message(ctx.message.channel, "<@%s>, starting blurple image analysis (Please note that this may take a while)" % ctx.message.author.id)


    start = time.time()
    if arg1 != None:
        if "<@!" in arg1:
            arg1 = arg1[:-1]
            arg1 = arg1[3:]
        if "<@" in arg1:
            arg1 = arg1[:-1]
            arg1 = arg1[2:]
        if arg1.isdigit() == True:
            try:
                user = await bot.get_user_info(int(arg1))
                picture = user.avatar_url
            except Exception:
                pass
        else:
            picture = arg1
    else:
        link = ctx.message.attachments
        if len(link) != 0:
            for image in link:
                picture = image.url

    if picture == None:
        picture = ctx.author.avatar_url

    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(picture) as r:
                response = await r.read()
    except ValueError:
        await bot.send_message(ctx.message.channel, "<@%s>, please link a valid image URL" % ctx.message.author.id)
        return

    colourbuffer = 20

    try:
        im = Image.open(BytesIO(response))
    except Exception:
        await bot.send_message(ctx.message.channel, "<@%s>, please link a valid image URL" % ctx.message.author.id)
        return

    imsize = list(im.size)
    impixels = imsize[0]*imsize[1]
    #1250x1250 = 1562500
    maxpixelcount = 1562500

    try:
        i = im.info["version"]
        isgif = True
        gifloop = int(im.info["loop"])
    except Exception:
        isgif = False




    end = time.time()
    #await ctx.send(f'{ctx.message.author.display_name}, image fetched, analysing image (This process can sometimes take a while depending on the size of the image) ({end - start:.2f}s)')
    start = time.time()
    if impixels > maxpixelcount:
        downsizefraction = math.sqrt(maxpixelcount/impixels)
        im = resizeimage.resize_width(im, (imsize[0]*downsizefraction))
        imsize = list(im.size)
        impixels = imsize[0]*imsize[1]
        end = time.time()
        #await ctx.send(f'{ctx.message.author.display_name}, image resized smaller for easier processing ({end-start:.2f}s)')
        start = time.time()

    def imager(im):
        im = im.convert(mode='L')
        im = ImageEnhance.Contrast(im).enhance(1000)
        im = im.convert(mode='RGB')

        img = im.load()

        for x in range(imsize[0]-1):
            i = 1
            for y in range(imsize[1]-1):
                pixel = img[x,y]

                if pixel != (255, 255, 255):
                    img[x,y] = (114, 137, 218)

        image_file_object = io.BytesIO()
        im.save(image_file_object, format='png')
        image_file_object.seek(0)
        return image_file_object

    def gifimager(im, gifloop):
        frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
        newgif = []

        for frame in frames:

            frame = frame.convert(mode='L')
            frame = ImageEnhance.Contrast(frame).enhance(1000)
            frame = frame.convert(mode='RGB')

            img = frame.load()

            for x in range(imsize[0]):
                i = 1
                for y in range(imsize[1]):
                    pixel = img[x,y]

                    if pixel != (255, 255, 255):
                        img[x,y] = (114, 137, 218)

            newgif.append(frame)

        image_file_object = io.BytesIO()

        gif = newgif[0]
        gif.save(image_file_object, format='gif', save_all=True, append_images=newgif[1:], loop=0)

        image_file_object.seek(0)
        return image_file_object


    with aiohttp.ClientSession() as session:
        start = time.time()
        if isgif == False:
            image = await bot.loop.run_in_executor(None, imager, im)
        else:
            image = await bot.loop.run_in_executor(None, gifimager, im, gifloop)
        end = time.time()
        #await ctx.send(f"{ctx.author.display_name}, image data extracted ({end - start:.2f}s)")
        if isgif == False:
            await bot.send_file(ctx.message.channel, fp=image, filename='image.png')
        else:
            await bot.send_file(ctx.message.channel, fp=image, filename='image.gif')

@bot.command(pass_context=True)
@commands.cooldown(rate=1, per=60, type=BucketType.user)
async def blurple(ctx, arg1 = None):
    picture = None

    await bot.send_message(ctx.message.channel, "<@%s>, starting blurple image analysis (Please note that this may take a while)")


    start = time.time()
    if arg1 != None:
        if "<@!" in arg1:
            arg1 = arg1[:-1]
            arg1 = arg1[3:]
        if "<@" in arg1:
            arg1 = arg1[:-1]
            arg1 = arg1[2:]
        if arg1.isdigit() == True:
            try:
                user = await bot.get_user_info(int(arg1))
                picture = user.avatar_url
            except Exception:
                pass
        else:
            picture = arg1
    else:
        link = ctx.message.attachments
        if len(link) != 0:
            for image in link:
                picture = image.url

    if picture == None:
        picture = ctx.author.avatar_url

    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(picture) as r:
                response = await r.read()
    except ValueError:
        await bot.send_message(ctx.message.channel, "<@%s>, please link a valid image URL")
        return

    colourbuffer = 20

    try:
        im = Image.open(BytesIO(response))
    except Exception:
        await bot.send_message(ctx.message.channel, "<@%s>, please link a valid image URL")
        return

    im = im.convert('RGBA')
    imsize = list(im.size)
    impixels = imsize[0]*imsize[1]
    #1250x1250 = 1562500
    maxpixelcount = 1562500

    end = time.time()
    #await ctx.send(f'{ctx.message.author.display_name}, image fetched, analysing image (This process can sometimes take a while depending on the size of the image) ({end - start:.2f}s)')
    start = time.time()
    if impixels > maxpixelcount:
        downsizefraction = math.sqrt(maxpixelcount/impixels)
        im = resizeimage.resize_width(im, (imsize[0]*downsizefraction))
        imsize = list(im.size)
        impixels = imsize[0]*imsize[1]
        end = time.time()
        await bot.send_message(ctx.message.channel, "<@%s>, image resized smaller for easier processing ({end-start:.2f}s)')
        start = time.time()

    def imager(im):
        global noofblurplepixels
        noofblurplepixels = 0
        global noofwhitepixels
        noofwhitepixels = 0
        global noofdarkblurplepixels
        noofdarkblurplepixels = 0
        global nooftotalpixels
        nooftotalpixels = 0
        global noofpixels
        noofpixels = 0

        blurple = (114, 137, 218)
        darkblurple = (78, 93, 148)
        white = (255, 255, 255)

        img = im.load()

        for x in range(imsize[0]):
            i = 1
            for y in range(imsize[1]):
                pixel = img[x,y]
                check = 1
                checkblurple = 1
                checkwhite = 1
                checkdarkblurple = 1
                for i in range(3):
                    if not(blurple[i]+colourbuffer > pixel[i] > blurple[i]-colourbuffer):
                        checkblurple = 0
                    if not(darkblurple[i]+colourbuffer > pixel[i] > darkblurple[i]-colourbuffer):
                        checkdarkblurple = 0
                    if not(white[i]+colourbuffer > pixel[i] > white[i]-colourbuffer):
                        checkwhite = 0
                    if checkblurple == 0 and checkdarkblurple == 0 and checkwhite == 0:
                        check = 0
                if check == 0:
                    img[x,y] = (0, 0, 0, 255)
                if check == 1:
                    nooftotalpixels += 1
                if checkblurple == 1:
                    noofblurplepixels += 1
                if checkdarkblurple == 1:
                    noofdarkblurplepixels += 1
                if checkwhite == 1:
                    noofwhitepixels += 1
                noofpixels += 1

        image_file_object = io.BytesIO()
        im.save(image_file_object, format='png')
        image_file_object.seek(0)
        return image_file_object

    with aiohttp.ClientSession() as session:
        start = time.time()
        image = await bot.loop.run_in_executor(None, imager, im)
        end = time.time()
        #await ctx.send(f"{ctx.author.display_name}, image data extracted ({end - start:.2f}s)")
        image = await bot.send_message(ctx.message.channel, fp=image, filename='image.png')

        blurplenesspercentage = round(((nooftotalpixels/noofpixels)*100), 2)
        percentblurple = round(((noofblurplepixels/noofpixels)*100), 2)
        percentdblurple = round(((noofdarkblurplepixels/noofpixels)*100), 2)
        percentwhite = round(((noofwhitepixels/noofpixels)*100), 2)

        embed = discord.Embed(Title = "", colour = 0x7289DA)
        embed.add_field(name="Total amount of Blurple", value="{blurplenesspercentage}%", inline=False)
        embed.add_field(name="Blurple (rgb(114, 137, 218))", value="{percentblurple}%", inline=True)
        embed.add_field(name="White (rgb(255, 255, 255))", value="{percentwhite}\%", inline=True)
        embed.add_field(name="Dark Blurple (rgb(78, 93, 148))", value="{percentdblurple}\%", inline=True)
        embed.add_field(name="Guide", value="Blurple, White, Dark Blurple = Blurple, White, and Dark Blurple (respectively) \nBlack = Not Blurple, White, or Dark Blurple", inline=False)
        embed.set_footer(text="Please note: Discord slightly reduces quality of the images, therefore the percentages may be slightly inaccurate. | Content requested by {ctx.author}")
        await bot.send_message(ctx.message.channel, embed=embed, file=image)

        if blurplenesspercentage > 75 and picture == ctx.author.avatar_url and percentblurple > 5:
            await bot.send_message(ctx.message.channel, "<@%s>, your profile pic has enough blurple (over 75% in total and over 5% blurple)!")
            await ctx.author.add_roles(blurpleuserrole)
        elif picture == ctx.author.avatar_url and blurpleuserrole not in ctx.author.roles:
            await bot.send_message(ctx.message.channel, "<@%s>, your profile pic does not have enough blurple (over 75% in total and over 5% blurple). However, this colour detecting algorithm is automated, so if you believe your pfp is blurple enough, then we apologize for the faulty algorithm. (Not sure how to make a blurple logo? Type >blurplefy!)")

@bot.command(pass_context=True)
async def test(ctx):
    """Test command"""
    bleh = discord.Embed(title="Gay", color=0xFF69B4)
    bleh.set_image(url="https://xenorealms.com/rem/botmedia/bleh.gif")
    await bot.send_message(ctx.message.channel, embed=bleh)

bot.run(config.token)
