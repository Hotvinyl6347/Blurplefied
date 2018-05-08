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

bot = commands.Bot(command_prefix=">")

message = discord.Message

@bot.event
async def on_ready():
    print(discord.__version__)
    print("Connected.")

@bot.command(pass_context=True, aliases=['blurplfy', 'blurplefier'])
async def blurplefy(ctx, arg1 = None):
    """limited event cmd"""
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
async def test(ctx):
    """Test command"""
    bleh = discord.Embed(title="Gay", color=0xFF69B4)
    bleh.set_image(url="https://xenorealms.com/rem/botmedia/bleh.gif")
    await ctx.send_message(ctx.message.channel, embed=bleh)

bot.run(config.token)
