## AntiSocialSocialBot v1 for Discord
## 02/12/2018 RGUNN
## DO NOT DISTRIBUTE!
## Be advised not to change any of the below code, as it may prevent ASSBot from working correctly
## Please contact Riordan to request updates / changes
## https://assbot.atspace.tv/
## Please don't tell Waldron I used json he wont be happy


import discord
from discord.ext import commands
import asyncio
import youtube_dl
import requests
import json
from time import time
import os

clientVer = 999

def errorembed (desc, ico):
    emb = discord.Embed(description = desc)
    emb.set_author(name = "Error", icon_url = ico)

    return emb


def next (id):
    queue[id].pop(0)
    if queue[id] != []:
        print("Next Track")
        emb = discord.Embed(title = "**" + queue[id][0]["name"] + "**")
        emb.set_author(name = "Now Playing", icon_url = "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
        emb.set_thumbnail(url = queue[id][0]["img"])
        if queue[id][0]["album"] != "y":
            emb.add_field(name = "Album", value = queue[id][0]["album"])
            emb.add_field(name="Artists" if "," in queue[id][0]["artists"] else "Artist", value=queue[id][0]["artists"])
        else:
            emb.add_field(name="Channel", value=queue[id][0]["artists"])
        emb.add_field(name = "Duration", value = queue[id][0]["length"])
        emb.add_field(name = "Requested By", value = queue[id][0]["user"])
        coro = bot.send_message(bot.get_channel(channels[id]), embed = emb)
        asyncio.run_coroutine_threadsafe(coro, bot.loop)
        queue[id][0]["player"].start()
    else:
        channels.pop(id)
        if bot.voice_client_in(bot.get_server(id)) is not None:
            coro = bot.voice_client_in(bot.get_server(id)).disconnect()
            asyncio.run_coroutine_threadsafe(coro, bot.loop)

DiscordApiKey = "NTE4NzkxNzYwMzAyODMzNjg1.Dvam6w.tKUAHjNP3dHc4CZbth0lxcfFpLs"

chars = ["%", "&", "?", "*", ";", "#"]

custom = {}
choices = {}
queue = {}
players = {}
channels = {}
NPMessage = {}

try:
    chnls = json.load(open("channels.json", "r"))
except FileNotFoundError:
    chnls = {}
    json.dump(chnls, open("channels.json", "w"))

bot = commands.Bot(command_prefix = ".")

bot.remove_command("help")

@bot.event
async def on_ready ():
    print("Online!\nWith ID:", bot.user.id)


@bot.command(pass_context = True)
async def play (ctx, *args):
    if len(args) == 1 and args[0].isdigit() and int(args[0]) > 0:
        if ctx.message.server.id not in choices or int(args[0]) > len(choices[ctx.message.server.id]["ids"]):
            await bot.say(embed = errorembed("**Before you can make a choice, you need a list of content to choose from.\n To search for content, use *.play [s|a|p|y] <SearchTerm>*\nFor more information, please see the xhelp command.**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
        elif ctx.message.author.voice.voice_channel is None:
            await bot.say(embed = errorembed("**You must first join a voice channel before making a selection.**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
        elif bot.voice_client_in(ctx.message.server) is not None and (ctx.message.author.voice.voice_channel.id != bot.voice_client_in(ctx.message.server).channel.id):
            await bot.say(embed = errorembed("**You must be in the same voice channel as xAlpha before making a selection**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
        else:
            await bot.delete_message(choices[ctx.message.server.id]["msgs"][0])
            await bot.delete_message(choices[ctx.message.server.id]["msgs"][1])

            token = json.loads(requests.post("https://accounts.spotify.com/api/token", data = {"grant_type" : "refresh_token", "refresh_token":"AQCAXwoJXyQKXxu_UwIlMDyk8m1S7KNx1TnjC0fwkIyx_FX3cAUj7qb9F9kgZ7QnpjTPHru0AOHP4Ld8B8w4HYRsJD5akSQucOCbbIQK5_ta6BWVtUnpQPxtYN9YYdgWeJLPHw"}, headers = {"Authorization" : "Basic MWQxMTAzMWEzZTdjNDEzZmJlNDA5ZTA0MmEwNDAxODU6ZTJlZDY2MDIwZDEyNGJlOGJiNzMwOTY2YWZkMDQwOWU="}).content)["access_token"]

            if ctx.message.server.id not in queue:
                queue[ctx.message.server.id] = []

            if bot.voice_client_in(ctx.message.server) is None:
                await bot.join_voice_channel(ctx.message.author.voice.voice_channel)

            empty = True if queue[ctx.message.server.id] == [] else False

            if ctx.message.server.id not in channels:
                channels[ctx.message.server.id] = ctx.message.channel.id

            voiceClient = bot.voice_client_in(ctx.message.server)

            # SONG

            if choices[ctx.message.server.id]["type"] == "s":
                songInfo = json.loads(requests.get("https://api.spotify.com/v1/tracks/" + choices[ctx.message.server.id]["ids"][int(args[0]) - 1], headers = {"Authorization" : "Bearer " + token}).content)
                choices.pop(ctx.message.server.id)
                ytURL = "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&key=AIzaSyA9NNsKgVtiaiuZ3B9mhGSQCgkoTZgzAFI&q=" + (songInfo["name"] + " " + songInfo["artists"][0]["name"]).replace("&", "%26").replace("?", "%3F")
                ytLink = json.loads(requests.get(ytURL).content)["items"][0]["id"]["videoId"]
                player = await voiceClient.create_ytdl_player("https://youtu.be/" + ytLink, after = lambda: next(ctx.message.server.id))
                waitEmbed = discord.Embed(description="**Loading Song *" + songInfo["name"] + "* to queue.**\n\nThis shouldn't take too long....")
                waitEmbed.set_author(name="Please Wait", icon_url="https://i.imgur.com/jtaLgsl.gif")
                waitEmbed.set_thumbnail(url=songInfo["album"]["images"][0]["url"])
                msg = await bot.say(embed=waitEmbed)
                await asyncio.sleep(0.1)

                queue[ctx.message.server.id].append({"name" : songInfo["name"], "img" : songInfo["album"]["images"][0]["url"], "player" : player, "artists" : ", ".join([artist["name"] for artist in songInfo["artists"]]), "album" : songInfo["album"]["name"], "explicit" : songInfo["explicit"], "length" : str(round(songInfo["duration_ms"] / 60000, 2)), "user": ctx.message.author.name})
                await bot.delete_message(msg)

                if empty:
                    queue[ctx.message.server.id][0]["player"].start()
                    emb = discord.Embed(title="**" + queue[ctx.message.server.id][0]["name"] + "**")
                    emb.set_author(name="Now Playing", icon_url="https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
                    emb.set_thumbnail(url=queue[ctx.message.server.id][0]["img"])
                    emb.add_field(name="Album", value=queue[ctx.message.server.id][0]["album"])
                    emb.add_field(name="Artists" if "," in queue[ctx.message.server.id][0]["artists"] else "Artist", value=queue[ctx.message.server.id][0]["artists"])
                    emb.add_field(name="Duration", value=queue[ctx.message.server.id][0]["length"])
                    emb.add_field(name="Requested By", value=queue[ctx.message.server.id][0]["user"])
                    await bot.say(embed=emb)
                    empty = False
                else:
                    artists = ", ".join([artist["name"] for artist in songInfo["artists"]])
                    emb = discord.Embed(title = "**" + songInfo["name"] + "**")
                    emb.set_author(name = "Added to Queue", icon_url = "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
                    emb.set_thumbnail(url = songInfo["album"]["images"][0]["url"])
                    emb.add_field(name = "Type", value = "Song")
                    emb.add_field(name = "Artists" if "," in artists else "Artist", value = artists)
                    emb.add_field(name = "Album", value = songInfo["album"]["name"])
                    emb.add_field(name = "Duration", value = str(round(songInfo["duration_ms"] / 60000, 2)))
                    emb.add_field(name = "Requested By", value = ctx.message.author.name)

                    await bot.say(embed=emb)

            # ALBUM

            elif choices[ctx.message.server.id]["type"] == "a":
                albumInfo = json.loads(requests.get("https://api.spotify.com/v1/albums/" + choices[ctx.message.server.id]["ids"][int(args[0]) - 1], headers = {"Authorization" : "Bearer " + token}).content)
                choices.pop(ctx.message.server.id)
                waitEmbed = discord.Embed(description="**Loading Album *" + albumInfo["name"] + "* and adding tracks to Queue...**\n\nThis may take some time depending on the ammount of tracks in the playlist and the speed of your internet connection.")
                waitEmbed.set_author(name="Please Wait", icon_url="https://i.imgur.com/jtaLgsl.gif")
                waitEmbed.set_thumbnail(url=albumInfo["images"][0]["url"])
                msg = await bot.say(embed=waitEmbed)
                for track in albumInfo["tracks"]["items"]:
                    await asyncio.sleep(0.1)
                    ytURL = "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&key=AIzaSyA9NNsKgVtiaiuZ3B9mhGSQCgkoTZgzAFI&q=" + (track["name"] + " " + track["artists"][0]["name"]).replace("&", "%26").replace("?", "%3F")
                    ytLink = json.loads(requests.get(ytURL).content)["items"][0]["id"]["videoId"]
                    player = await voiceClient.create_ytdl_player("https://youtu.be/" + ytLink, after = lambda: next(ctx.message.server.id))

                    queue[ctx.message.server.id].append({"name" : track["name"], "img" : albumInfo["images"][0]["url"], "player" : player, "artists" : ", ".join([artist["name"] for artist in track["artists"]]), "album" : albumInfo["name"], "explicit" : track["explicit"], "length" : str(round(track["duration_ms"] / 60000, 2)), "user": ctx.message.author.name})

                    if empty:
                        queue[ctx.message.server.id][0]["player"].start()
                        emb = discord.Embed(title="**" + queue[ctx.message.server.id][0]["name"] + "**")
                        emb.set_author(name="Now Playing", icon_url="https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
                        emb.set_thumbnail(url=queue[ctx.message.server.id][0]["img"])
                        emb.add_field(name="Album", value=queue[ctx.message.server.id][0]["album"])
                        emb.add_field(name="Artists" if "," in queue[ctx.message.server.id][0]["artists"] else "Artist", value=queue[ctx.message.server.id][0]["artists"])
                        emb.add_field(name="Duration", value=queue[ctx.message.server.id][0]["length"])
                        emb.add_field(name="Requested By", value=queue[ctx.message.server.id][0]["user"])
                        await bot.say(embed=emb)
                        empty = False
                await bot.delete_message(msg)

                artists = ", ".join([artist["name"] for artist in albumInfo["artists"]])
                emb = discord.Embed(title = "**" + albumInfo["name"] + "**")
                emb.set_author(name = "Added to Queue", icon_url = "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
                emb.set_thumbnail(url = albumInfo["images"][0]["url"])
                emb.add_field(name = "Type", value = "Album")
                emb.add_field(name = "Artists" if "," in artists else "Artist", value = artists)
                emb.add_field(name = "Number of Tracks", value = str(len(albumInfo["tracks"]["items"])))
                emb.add_field(name = "Requested By", value = ctx.message.author.name)

                await bot.say(embed=emb)

            # PLAYLIST

            elif choices[ctx.message.server.id]["type"] == "p":
                playlistInfo = json.loads(requests.get("https://api.spotify.com/v1/playlists/" + choices[ctx.message.server.id]["ids"][int(args[0]) - 1], headers = {"Authorization" : "Bearer " + token}).content)
                choices.pop(ctx.message.server.id)
                waitEmbed = discord.Embed(description="**Loading Playlist *" + playlistInfo["name"] + "* and adding tracks to Queue...**\n\nThis may take some time depending on the ammount of tracks in the playlist and the speed of your internet connection.")
                waitEmbed.set_author(name="Please Wait", icon_url="https://i.imgur.com/jtaLgsl.gif")
                waitEmbed.set_thumbnail(url=playlistInfo["images"][0]["url"] if playlistInfo["images"] != [] else "https://i.imgur.com/7a0n7ly.jpg")
                msg = await bot.say(embed=waitEmbed)
                for track in playlistInfo["tracks"]["items"]:
                    await asyncio.sleep(0.1)
                    track = track["track"]
                    ytURL = "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&key=AIzaSyA9NNsKgVtiaiuZ3B9mhGSQCgkoTZgzAFI&q=" + (track["name"] + " " + track["artists"][0]["name"]).replace("&", "%26").replace("?", "%3F")
                    ytLink = json.loads(requests.get(ytURL).content)["items"][0]["id"]["videoId"]
                    player = await voiceClient.create_ytdl_player("https://youtu.be/" + ytLink, after = lambda: next(ctx.message.server.id))

                    queue[ctx.message.server.id].append({"name" : track["name"], "img" : track["album"]["images"][0]["url"], "player" : player, "artists" : ", ".join([artist["name"] for artist in track["artists"]]), "album" : track["album"]["name"], "explicit" : track["explicit"], "length" : str(round(track["duration_ms"] / 60000, 2)), "user": ctx.message.author.name})

                    if empty:
                        queue[ctx.message.server.id][0]["player"].start()
                        emb = discord.Embed(title="**" + queue[ctx.message.server.id][0]["name"] + "**")
                        emb.set_author(name="Now Playing", icon_url="https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
                        emb.set_thumbnail(url=queue[ctx.message.server.id][0]["img"])
                        emb.add_field(name="Album", value=queue[ctx.message.server.id][0]["album"])
                        emb.add_field(name="Artists" if "," in queue[ctx.message.server.id][0]["artists"] else "Artist", value=queue[ctx.message.server.id][0]["artists"])
                        emb.add_field(name="Duration", value=queue[ctx.message.server.id][0]["length"])
                        emb.add_field(name="Requested By", value=queue[ctx.message.server.id][0]["user"])
                        await bot.say(embed=emb)
                        empty = False
                await bot.delete_message(msg)

                emb = discord.Embed(title = "**" + playlistInfo["name"] + "**")
                emb.set_author(name = "Added to Queue", icon_url = "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
                emb.set_thumbnail(url = playlistInfo["images"][0]["url"] if playlistInfo["images"] != [] else "https://i.imgur.com/7a0n7ly.jpg")
                emb.add_field(name = "Type", value = "Playlist")
                emb.add_field(name = "Number of Tracks", value = str(len(playlistInfo["tracks"]["items"])))
                emb.add_field(name = "Requested By", value = ctx.message.author.name)

                await bot.say(embed=emb)

            # YOUTUBE

            elif choices[ctx.message.server.id]["type"] == "y":
                videoInfo = json.loads(requests.get("https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&key=AIzaSyA9NNsKgVtiaiuZ3B9mhGSQCgkoTZgzAFI&id=" + choices[ctx.message.server.id]["ids"][int(args[0]) - 1]).content)
                choices.pop(ctx.message.server.id)
                waitEmbed = discord.Embed(description="**Loading Video *" + videoInfo["items"][0]["snippet"]["title"] + "* to queue.**\n\nThis shouldn't take too long....")
                waitEmbed.set_author(name="Please Wait", icon_url="https://i.imgur.com/jtaLgsl.gif")
                waitEmbed.set_thumbnail(url=videoInfo["items"][0]["snippet"]["thumbnails"]["maxres"]["url"] if "maxres" in videoInfo["items"][0]["snippet"]["thumbnails"] else videoInfo["items"][0]["snippet"]["thumbnails"]["default"]["url"])
                msg = await bot.say(embed=waitEmbed)
                player = await voiceClient.create_ytdl_player("https://youtu.be/" + videoInfo["items"][0]["id"],  after = lambda: next(ctx.message.server.id))
                duration = videoInfo["items"][0]["contentDetails"]["duration"]
                time = duration[2:duration.find("M")] + "." + (duration[duration.find("M") + 1:duration.find("S")] if len(duration[duration.find("M") + 1:duration.find("S")]) == 2 else "0" + duration[duration.find("M") + 1:duration.find("S")])

                queue[ctx.message.server.id].append({"name" : videoInfo["items"][0]["snippet"]["title"], "img" : videoInfo["items"][0]["snippet"]["thumbnails"]["maxres"]["url"] if "maxres" in videoInfo["items"][0]["snippet"]["thumbnails"] else videoInfo["items"][0]["snippet"]["thumbnails"]["default"]["url"], "player" : player, "artists" : videoInfo["items"][0]["snippet"]["channelTitle"], "album" : "y", "explicit" : True if "contentRating" in videoInfo["items"][0]["contentDetails"] and videoInfo["items"][0]["contentDetails"]["contentRating"]["ytRating"] == "ytAgeRestricted" else False, "length" : time, "user": ctx.message.author.name})
                await bot.delete_message(msg)

                if empty:
                    queue[ctx.message.server.id][0]["player"].start()
                    emb = discord.Embed(title="**" + queue[ctx.message.server.id][0]["name"] + "**")
                    emb.set_author(name="Now Playing", icon_url="https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
                    emb.set_thumbnail(url=queue[ctx.message.server.id][0]["img"])
                    emb.add_field(name="Channel", value=queue[ctx.message.server.id][0]["artists"])
                    emb.add_field(name="Duration", value=queue[ctx.message.server.id][0]["length"])
                    emb.add_field(name="Requested By", value=queue[ctx.message.server.id][0]["user"])
                    await bot.say(embed=emb)
                    empty = False
                else:
                    emb = discord.Embed(title = "**" + videoInfo["items"][0]["snippet"]["title"] + "**")
                    emb.set_author(name = "Added to Queue", icon_url = "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
                    emb.set_thumbnail(url = videoInfo["items"][0]["snippet"]["thumbnails"]["maxres"]["url"] if "maxres" in videoInfo["items"][0]["snippet"]["thumbnails"] else videoInfo["items"][0]["snippet"]["thumbnails"]["default"]["url"])
                    emb.add_field(name = "Type", value = "YouTube Video")
                    emb.add_field(name = "Channel", value = videoInfo["items"][0]["snippet"]["channelTitle"])
                    emb.add_field(name = "Duration", value = time)
                    emb.add_field(name = "Requested By", value = ctx.message.author.name)

                    await bot.say(embed = emb)

    elif len(args) < 2:
        await bot.say(":warning: Please specify the name and type of content you wish to play in the form `.play <type> <name>`\ne.g. `.play s thunderclouds`\nRun `xhelp` for more information on the play command")
    else:
        if ctx.message.server.id in choices:
            await bot.delete_message(choices[ctx.message.server.id]["msgs"][0])
            await bot.delete_message(choices[ctx.message.server.id]["msgs"][1])
            choices.pop(ctx.message.server.id)
        search = " ".join(args[1:])

        # SONG

        if (args[0].lower() == "s" or args[0].lower() == "song") and not any(char in search for char in chars):
            token = json.loads(requests.post("https://accounts.spotify.com/api/token", data = {"grant_type" : "refresh_token", "refresh_token":"AQCAXwoJXyQKXxu_UwIlMDyk8m1S7KNx1TnjC0fwkIyx_FX3cAUj7qb9F9kgZ7QnpjTPHru0AOHP4Ld8B8w4HYRsJD5akSQucOCbbIQK5_ta6BWVtUnpQPxtYN9YYdgWeJLPHw"}, headers = {"Authorization" : "Basic MWQxMTAzMWEzZTdjNDEzZmJlNDA5ZTA0MmEwNDAxODU6ZTJlZDY2MDIwZDEyNGJlOGJiNzMwOTY2YWZkMDQwOWU="}).content)["access_token"]
            songs = json.loads(requests.get("https://api.spotify.com/v1/search?type=track&limit=10&q=" + search, headers = {"Authorization" : "Bearer " + token}).content)["tracks"]["items"]
            if len(songs) == 0:
                await bot.say(embed=errorembed("**No results found for *" + search + "***\n\nCheck the spelling of the song name and try again, or try searching youtube with *.play [y|youtube] <SearchTerm>*", "https://i.imgur.com/DnqRA7s.gif"))
            else:
                choices[ctx.message.server.id] = {"type": "s", "msgs":[ctx.message] , "ids" : [song["id"] for song in songs]}
                choiceEmbed = discord.Embed(title = "Please select which song you wish to play by using .play <Number>", colour = discord.Colour.green())
                for num, song in enumerate(songs, start = 1):
                    choiceEmbed.add_field(inline = False, name = str(num), value = ", ".join([artist["name"] for artist in song["artists"]]) + " - **" + song["name"] + "**")
                choiceEmbed.set_author(name = "Search results for " + search, icon_url = "https://i.imgur.com/IO640k1.gif")
                choices[ctx.message.server.id]["msgs"].append(await bot.say(embed = choiceEmbed))

        # ALBUM

        elif (args[0].lower() == "a" or args[0].lower() == "album") and not any(char in search for char in chars):
            token = json.loads(requests.post("https://accounts.spotify.com/api/token", data = {"grant_type" : "refresh_token", "refresh_token":"AQCAXwoJXyQKXxu_UwIlMDyk8m1S7KNx1TnjC0fwkIyx_FX3cAUj7qb9F9kgZ7QnpjTPHru0AOHP4Ld8B8w4HYRsJD5akSQucOCbbIQK5_ta6BWVtUnpQPxtYN9YYdgWeJLPHw"}, headers = {"Authorization" : "Basic MWQxMTAzMWEzZTdjNDEzZmJlNDA5ZTA0MmEwNDAxODU6ZTJlZDY2MDIwZDEyNGJlOGJiNzMwOTY2YWZkMDQwOWU="}).content)["access_token"]
            albums = json.loads(requests.get("https://api.spotify.com/v1/search?type=album&limit=10&q=" + search, headers = {"Authorization" : "Bearer " + token}).content)["albums"]["items"]
            if len(albums) == 0:
                await bot.say(embed=errorembed("**No results found for *" + search + "***\n\nCheck the spelling of the album name and try again.", "https://i.imgur.com/DnqRA7s.gif"))
            else:
                choices[ctx.message.server.id] = {"type": "a", "msgs":[ctx.message], "ids" : [album["id"] for album in albums]}
                choiceEmbed = discord.Embed(title = "Please select which album you wish to play by using .play <Number>", colour = discord.Colour.blue())
                for num, album in enumerate(albums, start = 1):
                    choiceEmbed.add_field(inline = False, name = str(num), value = ", ".join([artist["name"] for artist in album["artists"]]) + " - **" + album["name"] + "**")
                choiceEmbed.set_author(name = "Search results for " + search, icon_url = "https://i.imgur.com/IO640k1.gif")
                choices[ctx.message.server.id]["msgs"].append(await bot.say(embed = choiceEmbed))

        # PLAYLIST

            # URL

        elif args[0].lower() == "p" or args[0].lower() == "playlist":
            if "open.spotify.com/playlist/" in search or ("open.spotify.com/user/" in search and "/playlist" in search):
                if ctx.message.author.voice.voice_channel is None:
                    await bot.say(embed = errorembed("**You must first join a voice channel before playing a playlist.**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
                elif bot.voice_client_in(ctx.message.server) is not None and (ctx.message.author.voice.voice_channel.id != bot.voice_client_in(ctx.message.server).channel.id):
                    await bot.say(embed = errorembed("**You must be in the same voice channel as xAlpha before playing a playlist**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
                else:
                    if ctx.message.server.id not in queue:
                        queue[ctx.message.server.id] = []
                    empty = True if queue[ctx.message.server.id] == [] else False
                    if bot.voice_client_in(ctx.message.server) is None:
                        await bot.join_voice_channel(ctx.message.author.voice.voice_channel)
                    voiceClient = bot.voice_client_in(ctx.message.server)

                    if "open.spotify.com/playlist/" in search:
                        index = search.find("open.spotify.com/playlist/") + 26
                        playlistID = search[index : index + 22]
                    elif "https://open.spotify.com/user/" in search:
                        index = search.find("/playlist/") + 10
                        playlistID = search[index : index + 22]
                    token = json.loads(requests.post("https://accounts.spotify.com/api/token", data = {"grant_type" : "refresh_token", "refresh_token":"AQCAXwoJXyQKXxu_UwIlMDyk8m1S7KNx1TnjC0fwkIyx_FX3cAUj7qb9F9kgZ7QnpjTPHru0AOHP4Ld8B8w4HYRsJD5akSQucOCbbIQK5_ta6BWVtUnpQPxtYN9YYdgWeJLPHw"}, headers = {"Authorization" : "Basic MWQxMTAzMWEzZTdjNDEzZmJlNDA5ZTA0MmEwNDAxODU6ZTJlZDY2MDIwZDEyNGJlOGJiNzMwOTY2YWZkMDQwOWU="}).content)["access_token"]
                    playlist = json.loads(requests.get("https://api.spotify.com/v1/playlists/" + playlistID, headers = {"Authorization" : "Bearer " + token}).content)
                    if "error" in playlist:
                        await bot.say(embed=errorembed("**Invalid Playlist**\n\nThe URL for the playlist you provided was invalid.\nPlease make sure that the playlist is set to *public* in Spotify, or try searching for the playlist with *.play [p|playlist] <SearchTerm>*", "https://i.imgur.com/DnqRA7s.gif"))
                    else:
                        await bot.delete_message(ctx.message)
                        waitEmbed = discord.Embed(description = "**Loading Playlist *" + playlist["name"] + "* and adding tracks to Queue...**\n\nThis may take some time depending on the ammount of tracks in the playlist and the speed of your internet connection.")
                        waitEmbed.set_author(name = "Please Wait", icon_url = "https://i.imgur.com/jtaLgsl.gif")
                        waitEmbed.set_thumbnail(url = playlist["images"][0]["url"] if playlist["images"] != [] else "https://i.imgur.com/7a0n7ly.jpg" )
                        msg = await bot.say(embed = waitEmbed)
                        for track in playlist["tracks"]["items"]:
                            await asyncio.sleep(0.1)
                            track = track["track"]
                            ytURL = "https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&key=AIzaSyA9NNsKgVtiaiuZ3B9mhGSQCgkoTZgzAFI&q=" + (track["name"] + " " + track["artists"][0]["name"]).replace("&", "%26").replace("?", "%3F")
                            ytLink = json.loads(requests.get(ytURL).content)["items"][0]["id"]["videoId"]
                            player = await voiceClient.create_ytdl_player("https://youtu.be/" + ytLink, after = lambda: next(ctx.message.server.id))

                            queue[ctx.message.server.id].append({"name" : track["name"], "img" : track["album"]["images"][0]["url"], "player" : player, "artists" : ", ".join([artist["name"] for artist in track["artists"]]), "album" : track["album"]["name"], "explicit" : track["explicit"], "length" : str(round(track["duration_ms"] / 60000, 2)), "user": ctx.message.author.name})

                            if empty:
                                queue[ctx.message.server.id][0]["player"].start()
                                emb = discord.Embed(title="**" + queue[ctx.message.server.id][0]["name"] + "**")
                                emb.set_author(name="Now Playing", icon_url="https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
                                emb.set_thumbnail(url=queue[ctx.message.server.id][0]["img"])
                                emb.add_field(name="Album", value=queue[ctx.message.server.id][0]["album"])
                                emb.add_field(name="Artists" if "," in queue[ctx.message.server.id][0]["artists"] else "Artist", value=queue[ctx.message.server.id][0]["artists"])
                                emb.add_field(name="Duration", value=queue[ctx.message.server.id][0]["length"])
                                emb.add_field(name="Requested By", value=queue[ctx.message.server.id][0]["user"])
                                await bot.say(embed=emb)
                                empty = False

                        await bot.delete_message(msg)

                        emb = discord.Embed(title = "**" + playlist["name"] + "**")
                        emb.set_author(name = "Added to Queue", icon_url = "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
                        emb.set_thumbnail(url = playlist["images"][0]["url"] if playlist["images"] != [] else "https://i.imgur.com/7a0n7ly.jpg")
                        emb.add_field(name = "Type", value = "Playlist")
                        emb.add_field(name = "Number of Tracks", value = str(len(playlist["tracks"]["items"])))
                        emb.add_field(name = "Requested By", value = ctx.message.author.name)

                        await bot.say(embed=emb)
            # SEARCH

            elif not any(char in search for char in chars):
                token = json.loads(requests.post("https://accounts.spotify.com/api/token", data = {"grant_type" : "refresh_token", "refresh_token":"AQCAXwoJXyQKXxu_UwIlMDyk8m1S7KNx1TnjC0fwkIyx_FX3cAUj7qb9F9kgZ7QnpjTPHru0AOHP4Ld8B8w4HYRsJD5akSQucOCbbIQK5_ta6BWVtUnpQPxtYN9YYdgWeJLPHw"}, headers = {"Authorization" : "Basic MWQxMTAzMWEzZTdjNDEzZmJlNDA5ZTA0MmEwNDAxODU6ZTJlZDY2MDIwZDEyNGJlOGJiNzMwOTY2YWZkMDQwOWU="}).content)["access_token"]
                playlists = json.loads(requests.get("https://api.spotify.com/v1/search?type=playlist&limit=10&q=" + search, headers = {"Authorization" : "Bearer " + token}).content)["playlists"]["items"]
                if len(playlists) == 0:
                    await bot.say(embed=errorembed("**No results found for *" + search + "***\n\nCheck the spelling of the playlist name and try again.", "https://i.imgur.com/DnqRA7s.gif"))
                else:
                    choices[ctx.message.server.id] = {"type": "p", "msgs":[ctx.message] , "ids" : [playlist["id"] for playlist in playlists]}
                    choiceEmbed = discord.Embed(title = "Please select which playlist you wish to play by using .play <Number>", colour = discord.Colour.gold())
                    for num, playlist in enumerate(playlists, start = 1):
                        choiceEmbed.add_field(inline = False, name = str(num), value = (playlist["owner"]["display_name"] if playlist["owner"]["display_name"] != None else playlist["owner"]["external_urls"]["spotify"][30:]) + " - **" + playlist["name"] + "**")
                    choiceEmbed.set_author(name = "Search results for " + search, icon_url = "https://i.imgur.com/IO640k1.gif")
                    choices[ctx.message.server.id]["msgs"].append(await bot.say(embed = choiceEmbed))
            else:
                await bot.say(":warning: Please specify the name and type of content you wish to play in the form `.play <type> <name>`\ne.g. `.play s thunderclouds`\nRun `xhelp` for more information on the play command")


        # YOUTUBE

            # URL

        elif args[0].lower() == "y" or args[0].lower() == "youtube.com":
            if "youtu.be/" in search or "youtube.com/watch?v=" in search:
                if ctx.message.author.voice.voice_channel is None:
                    await bot.say(embed = errorembed("**You must first join a voice channel before playing a video.**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
                elif bot.voice_client_in(ctx.message.server) is not None and (ctx.message.author.voice.voice_channel.id != bot.voice_client_in(ctx.message.server).channel.id):
                    await bot.say(embed = errorembed("**You must be in the same voice channel as xAlpha before playing a video**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
                else:
                    if ctx.message.server.id not in queue:
                        queue[ctx.message.server.id] = []
                    empty = True if queue[ctx.message.server.id] == [] else False
                    if bot.voice_client_in(ctx.message.server) is None:
                        await bot.join_voice_channel(ctx.message.author.voice.voice_channel)
                    voiceClient = bot.voice_client_in(ctx.message.server)

                    videoID = ""
                    if "youtu.be/" in search:
                        videoID = search[search.find("youtu.be/") + 9 : search.find("?") if "?" in search else None]
                    elif "youtube.com/watch?v=" in search:
                        videoID = search[search.find("youtube.com/watch?v=") + 20 : search.find("&") if "&" in search else None]
                    videoInfo = json.loads(requests.get("https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&key=AIzaSyA9NNsKgVtiaiuZ3B9mhGSQCgkoTZgzAFI&id=" + videoID).content)
                    if "error" in videoInfo or videoInfo["pageInfo"]["totalResults"] == 0:
                        await bot.say(embed=errorembed("**Invalid Video URL**\n\nThe URL for the video you provided was invalid.\nPlease check that the URL is correct, or try searching for the video with *.play [y|youtube] <SearchTerm>*", "https://i.imgur.com/DnqRA7s.gif"))
                    else:
                        waitEmbed = discord.Embed(description="**Loading Video *" + videoInfo["items"][0]["snippet"]["title"] + "* to queue.**\n\nThis shouldn't take too long....")
                        waitEmbed.set_author(name="Please Wait", icon_url="https://i.imgur.com/jtaLgsl.gif")
                        waitEmbed.set_thumbnail(url=videoInfo["items"][0]["snippet"]["thumbnails"]["maxres"]["url"] if "maxres" in videoInfo["items"][0]["snippet"]["thumbnails"] else videoInfo["items"][0]["snippet"]["thumbnails"]["default"]["url"])
                        msg = await bot.say(embed=waitEmbed)
                        player = await voiceClient.create_ytdl_player("https://youtu.be/" + videoInfo["items"][0]["id"], after = lambda: next(ctx.message.server.id))
                        duration = videoInfo["items"][0]["contentDetails"]["duration"]
                        time = duration[2:duration.find("M")] + "." + (duration[duration.find("M") + 1:duration.find("S")] if len(duration[duration.find("M") + 1:duration.find("S")]) == 2 else "0" + duration[duration.find("M") + 1:duration.find("S")])
                        await asyncio.sleep(0.1)

                        queue[ctx.message.server.id].append({"name" : videoInfo["items"][0]["snippet"]["title"], "img" : videoInfo["items"][0]["snippet"]["thumbnails"]["maxres"]["url"] if "maxres" in videoInfo["items"][0]["snippet"]["thumbnails"] else videoInfo["items"][0]["snippet"]["thumbnails"]["default"]["url"], "player" : player, "artists" : videoInfo["items"][0]["snippet"]["channelTitle"], "album" : "y", "explicit" : True if "contentRating" in videoInfo["items"][0]["contentDetails"] and videoInfo["items"][0]["contentDetails"]["contentRating"]["ytRating"] == "ytAgeRestricted" else False, "length" :time, "user": ctx.message.author.name})
                        await bot.delete_message(msg)

                        if empty:
                            queue[ctx.message.server.id][0]["player"].start()
                            emb = discord.Embed(title="**" + queue[ctx.message.server.id][0]["name"] + "**")
                            emb.set_author(name="Now Playing", icon_url="https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
                            emb.set_thumbnail(url=queue[ctx.message.server.id][0]["img"])
                            emb.add_field(name="Channel", value=queue[ctx.message.server.id][0]["artists"])
                            emb.add_field(name="Duration", value=queue[ctx.message.server.id][0]["length"])
                            emb.add_field(name="Requested By", value=queue[ctx.message.server.id][0]["user"])
                            await bot.say(embed=emb)
                        else:
                            emb = discord.Embed(title = "**" + videoInfo["items"][0]["snippet"]["title"] + "**")
                            emb.set_author(name = "Added to Queue", icon_url = "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
                            emb.set_thumbnail(url = videoInfo["items"][0]["snippet"]["thumbnails"]["maxres"]["url"] if "maxres" in videoInfo["items"][0]["snippet"]["thumbnails"] else videoInfo["items"][0]["snippet"]["thumbnails"]["default"]["url"])
                            emb.add_field(name = "Type", value = "YouTube Video")
                            emb.add_field(name = "Channel", value = videoInfo["items"][0]["snippet"]["channelTitle"])
                            emb.add_field(name = "Duration", value = time)
                            emb.add_field(name = "Requested By", value = ctx.message.author.name)
                            await bot.say(embed = emb)

            # SEARCH

            elif not any(char in search for char in chars):
                videos = json.loads(requests.get("https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=10&type=video&key=AIzaSyA9NNsKgVtiaiuZ3B9mhGSQCgkoTZgzAFI&q=" + search).content)
                if videos["pageInfo"]["totalResults"] == 0:
                    await bot.say(embed=errorembed("**No results found for *" + search + "***\n\nCheck the spelling of the video and try again.", "https://i.imgur.com/DnqRA7s.gif"))
                else:
                    choices[ctx.message.server.id] = {"type": "y", "msgs":[ctx.message] , "ids" : [video["id"]["videoId"] for video in videos["items"]]}
                    choiceEmbed = discord.Embed(title = "Please select which video you wish to play by using .play <Number>", colour = discord.Colour.red())
                    for num, video in enumerate(videos["items"], start=1):
                        choiceEmbed.add_field(inline = False, name = str(num), value = video["snippet"]["channelTitle"] + " - **" + video["snippet"]["title"] + "**")
                    choiceEmbed.set_author(name = "Search results for " + search, icon_url = "https://i.imgur.com/IO640k1.gif")
                    choices[ctx.message.server.id]["msgs"].append(await bot.say(embed = choiceEmbed))
            else:
                await bot.say(":warning: Please specify the name and type of content you wish to play in the form `.play <type> <name>`\ne.g. `.play s thunderclouds`\nRun `xhelp` for more information on the play command")
        else:
            await bot.say(":warning: Please specify the name and type of content you wish to play in the form `.play <type> <name>`\ne.g. `.play s thunderclouds`\nRun `xhelp` for more information on the play command")


@bot.command(pass_context = True)
async def skip (ctx):
    if ctx.message.author.voice.voice_channel is None or (bot.voice_client_in(ctx.message.server) is not None and (ctx.message.author.voice.voice_channel.id != bot.voice_client_in(ctx.message.server).channel.id)):
        await bot.say(embed = errorembed("**You must be in the same voice channel as ASSBot to Skip the current song**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
    elif ctx.message.server.id in queue and queue[ctx.message.server.id] != []:
        queue[ctx.message.server.id][0]["player"].stop()
        await bot.say(":track_next: Track Skipped!")
    else:
        await bot.say(embed = errorembed("**There are no tracks in the queue**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))

@bot.command(pass_context = True)
async def clear (ctx):
    if ctx.message.author.voice.voice_channel is None or (bot.voice_client_in(ctx.message.server) is not None and (ctx.message.author.voice.voice_channel.id != bot.voice_client_in(ctx.message.server).channel.id)):
        await bot.say(embed = errorembed("**You must be in the same voice channel as ASSBot to clear the queue**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
    elif ctx.message.server.id in queue and queue[ctx.message.server.id] != []:
        queue[ctx.message.server.id][0]["player"].stop()
        if ctx.message.server.id in queue:
            queue.pop(ctx.message.server.id)
            await bot.voice_client_in(bot.get_server(ctx.message.server.id)).disconnect()
        await bot.say(":stop_button: Queue Cleared!")
    else:
        await bot.say(embed=errorembed("**The Queue is already empty!**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))

@bot.command(pass_context = True)
async def pause (ctx):
    if ctx.message.author.voice.voice_channel is None or (bot.voice_client_in(ctx.message.server) is not None and (ctx.message.author.voice.voice_channel.id != bot.voice_client_in(ctx.message.server).channel.id)):
        await bot.say(embed = errorembed("**You must be in the same voice channel as ASSBot to pause the current song**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
    elif ctx.message.server.id in queue and queue[ctx.message.server.id] != []:
        if queue[ctx.message.server.id][0]["player"].is_playing() is True:
            queue[ctx.message.server.id][0]["player"].pause()
            await bot.say(":pause_button: Track Paused!")
        else:
            queue[ctx.message.server.id][0]["player"].resume()
            await bot.say(":arrow_forward: Track Resumed!")
    else:
        await bot.say(embed=errorembed("**There are no tracks in the queue**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))

@bot.command(pass_context = True)
async def earrape (ctx):
    if ctx.message.author.voice.voice_channel is None or (bot.voice_client_in(ctx.message.server) is not None and (ctx.message.author.voice.voice_channel.id != bot.voice_client_in(ctx.message.server).channel.id)):
        await bot.say(embed = errorembed("**You must be in the same voice channel as ASSBot to earrape the current song**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
    elif ctx.message.server.id in queue and queue[ctx.message.server.id] != []:
        queue[ctx.message.server.id][0]["player"].volume = 2.0
        await bot.say("Earraped the current song!")
    else:
        await bot.say(embed=errorembed("**There are no tracks in the queue**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))

@bot.command(pass_context = True)
async def qu (ctx):
    if ctx.message.server.id in queue and queue[ctx.message.server.id] != []:
        queueEmbed = discord.Embed(title = "Music Queue for" + ctx.message.server.name, colour = discord.Colour.teal())
        for num, item in enumerate(queue[ctx.message.server.id] if len(queue[ctx.message.server.id]) <= 20 else queue[ctx.message.server.id][:20], start=1):
            queueEmbed.add_field(inline=False, name="1. (Now Playing)" if num == 1 else str(num), value=item["artists"] + " - **" + item["name"] + "** \t" + item["length"] + " \t*" + item["user"] + "*")
        if len(queue[ctx.message.server.id]) > 20:
            queueEmbed.add_field(inline = False, name = "+ " + str(len(queue[ctx.message.server.id]) - 20) + " More Tracks ", value = "\u200b")
        queueEmbed.set_author(name = "Queue", icon_url = "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
        await bot.say(embed = queueEmbed)
    else:
        await bot.say(embed=errorembed("**There are no tracks in the queue**", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))

@bot.command(pass_context = True)
async def update (ctx, *args):
    chid = " ".join(args)
    if not ctx.message.author.server_permissions.administrator:
        await bot.say(embed = errorembed("**Permissions Error!**\nTo run this command, you must have the 'Administrator' Permission. Please contact a server owner if you beleive this is a mistake", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
    elif chid == "":
        await bot.say("**:loud_sound: Welcome to the ASSBot 'Make-A-Room' Channel Updater function!**\nTo create a 'Make-A-Room' channel, first make a channel, right click it and select 'Copy ID'.\nYou can then run this command again with the syntax:\n*.update ID*")
    else:
        vc = bot.get_channel(chid)
        if vc is None:
            await bot.say(embed = errorembed("**Channel Not Found...**\nPlease check you haven't included any accidental spaces or made a typo in the channel ID", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
        elif vc.server != ctx.message.server:
            await bot.say(embed = errorembed("**Channel Not Found...**\nPlease check you haven't included any accidental spaces or made a typo in the channel ID", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
        elif vc.type != discord.ChannelType.voice:
            await bot.say(embed = errorembed("**Wrong Channel Type**\nThe channel you provided is not a voice channel, so cannot be used as a 'Make-A-Room' Channel\nPlease provide the ID of a voice channel.", "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif"))
        else:
            chnls[ctx.message.server.id] = vc.id
            json.dump(chnls, open("channels.json", "w"))

            emb = discord.Embed(description = "**Successfully updated channel!**\n Join the designated channel to create a custom room!")
            emb.set_author(name="Success!", icon_url = "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
            await bot.say(embed = emb)

@bot.command(pass_context = True)
async def help ():
    emb = discord.Embed(title = "Commands", color = discord.Color.purple())

    emb.set_author(name = "Help", icon_url = "https://loading.io/spinners/ellipsis/lg.discuss-ellipsis-preloader.gif")
    emb.add_field(inline = False, name = ".play", value = "**.play [s|song] <Song>**\nSearches for a song on Spotify\n**.play [a|album] <Album>**\nSearches for an album on Spotify\n**.play [p|playlist] <Playlist|URL>**\nSearches for a playlist on spotify if a title is provided, or plays from a URL if provided instead\n**.play [y|Youtube] <Video>**\nSearches for a video on YouTube or plays from a YouTube URL if provided")
    emb.add_field(inline = False, name = ".skip", value = "Skips the currently playing track")
    emb.add_field(inline = False, name = ".clear", value = "Clears the Queue")
    emb.add_field(inline = False, name = ".pause", value = "Pauses / Resumes the currently playing track")
    emb.add_field(inline = False, name = ".qu", value = "Displays the Queue")

    await bot.say(embed = emb)

async def channel ():
    await asyncio.sleep(5)
    while True:
        for server in chnls:
            vc = bot.get_channel(chnls[server])
            if vc is not None:
                for member in vc.voice_members:
                    delete = [False, None]
                    if vc.server.id in custom:
                        for ch in custom[vc.server.id]:
                            if custom[vc.server.id][ch][1] == member.id:
                                delete = [True, ch]
                    if delete[0] is True:
                        await bot.delete_channel(bot.get_channel(delete[1]))
                        custom[vc.server.id].pop(delete[1])
                    name = member.name if member.nick is None else member.nick
                    room = await bot.create_channel(vc.server, name + ("' " if name[-1] == "s" else "'s ") + "Sanctuary", type = discord.ChannelType.voice)
                    await bot.move_member(member, room)
                    if room.server.id in custom:
                        custom[room.server.id][room.id] = [None, member.id]
                    else:
                        custom[room.server.id] = {room.id : [None, member.id]}
            else:
                chnls.pop(server)
                json.dump(chnls, open("channels.json", "w"))

        for serverID in custom:
            for roomID in custom[serverID]:
                if custom[serverID][roomID][0] is not None and time() - custom[serverID][roomID][0] > 120:
                    await bot.delete_channel(bot.get_channel(roomID))
                    custom[serverID].pop(roomID)
                    break
                elif custom[serverID][roomID][0] is None and bot.get_channel(roomID).voice_members == []:
                    custom[serverID][roomID][0] = time()
                elif custom[serverID][roomID][0] is not None and bot.get_channel(roomID).voice_members != []:
                    custom[serverID][roomID][0] = None

        await asyncio.sleep(1)

async def autoUpdate ():
    while True:
        print("Checking for updates...")
        serverVer = json.loads(requests.get("http://assbot.atspace.tv/ver.json").content)
        if serverVer["version"] > clientVer:
            print("Update Found! Downloading...")
            new = requests.get(serverVer["url"]).content
            with open("new.py", "w+b") as file:
                file.write(new)
            print("Successfully Downloaded\nBeginning Installation...")
            await asyncio.sleep(3)
            os.system("python update.py")
            await bot.close()
        else:
            print("ASSBot is up to date!")
        await asyncio.sleep(1800)

bot.loop.create_task(channel())
bot.loop.create_task(autoUpdate())

bot.run(DiscordApiKey)

