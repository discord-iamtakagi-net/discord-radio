from radio_stream import RadioStream
from radiko import Radiko

from env import Env

from discord import (Intents, Game)

from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

env: Env
client = commands.Bot(command_prefix='!', intents=Intents.all())
command = SlashCommand(client, sync_commands=True)
env = Env.load()
radio_stream: RadioStream

@client.event
async def on_ready():
    print(f"[radiko.discord] {client.user} として起動しました")
    radiko = Radiko(acct={'mail': env.RADIKO_MAIL, 'pass': env.RADIKO_PASS})
    if env.STATION_ID not in radiko.stations:
        return
    station_name = radiko.stations[env.STATION_ID][0]
    await client.change_presence(activity=Game(name=station_name))
    voice_channel = client.get_channel(env.VOICE_CHANNEL_ID)
    global radio_stream
    radio_stream = RadioStream(client=client, radiko=radiko, voice_channel=voice_channel, stataion_id=env.STATION_ID)
    if voice_channel:
        try:
            member = voice_channel.guild.get_member(client.user.id)
            await member.edit(nick=station_name)      
        except Exception as e:
            print(e)
        radio_stream.voice_client = await voice_channel.connect()

@command.slash(name='radio', description='ラジオを流します')
async def on_command(ctx: SlashContext):
    if not ctx.guild:
        return await ctx.send(
            content="このコマンドは DM で使用できません",
            hidden=True
        )
    global radio_stream
    voice_channel = client.get_channel(env.VOICE_CHANNEL_ID)
    if voice_channel:
        await ctx.send(
            content="ラジオのストリーミングを開始しました",
            hidden=True
        )
        radio_stream.start()
    else:
        await ctx.send(
            content="エラーが発生しました",
            hidden=True
        )


@command.slash(name='radiosel', description='ラジオ選局', options = [
        create_option(
            name="station_id",
            description="ラジオ局ID",
            option_type=str,
            required=True,
        ),
    ]
)
async def on_command(ctx: SlashContext, station_id: str):
    if not ctx.guild:
        return await ctx.send(
            content="このコマンドは DM で使用できません",
            hidden=True
        )
    global radio_stream
    if env.STATION_ID not in radio_stream.radiko.stations:
        return await ctx.send(
            content="存在しないラジオ局名です",
            hidden=True
        )
    station_name = radio_stream.radiko.stations[station_id][0]
    voice_channel = client.get_channel(env.VOICE_CHANNEL_ID)
    if voice_channel:
        await client.change_presence(activity=Game(name=station_name))
        try:
            member = voice_channel.guild.get_member(client.user.id)
            await member.edit(nick=station_name)      
        except Exception as e:
            print(e)
        await ctx.send(
            content="ラジオ局を変更しました: {}".format(station_id),
            hidden=True
        )
        radio_stream.next_station_id = station_id
    else:
        await ctx.send(
            content="エラーが発生しました",
            hidden=True
        )

client.run(env.BOT_TOKEN)
