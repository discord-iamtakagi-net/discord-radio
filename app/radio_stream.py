import asyncio

from logger import logger
import os

from subprocess import PIPE, STDOUT, Popen

from radiko import Radiko

from discord import (VoiceChannel, VoiceClient)
from discord import (VoiceChannel, VoiceClient, FFmpegPCMAudio, PCMVolumeTransformer)
from discord.ext import commands

class RadioStream():

    radiko: Radiko
    client: commands.Bot
    voice_client: VoiceClient
    voice_channel: VoiceChannel
    station_id: str
    stream_task: asyncio.Task

    def __init__(
        self,
            client: commands.Bot, 
            radiko: Radiko,
            voice_channel: VoiceChannel,
            stataion_id: str) -> None:
        self.client = client
        self.radiko = radiko
        self.voice_channel = voice_channel
        self.station_id = stataion_id
    
    def getStreamUrl(self):
        return 'http://f-radiko.smartstream.ne.jp/{}/_definst_/simul-stream.stream/playlist.m3u8'.format(self.station_id)
    
    async def connect(self):
        self.voice_client = await self.voice_channel.connect()
    
    async def disconnect(self):
        await self.voice_client.disconnect()
        self.voice_client = None

    async def start(self):
        self.stream_task = self.client.loop.create_task(self.playRadioStream())
        await self.stream_task

    async def playRadioStream(self):
        while self.client.loop.is_running():

            url = self.radiko.gen_temp_chunk_m3u8_url(self.getStreamUrl(), Radiko.token)
            p =  Popen("ffmpeg -y -vn -headers 'X-Radiko-AuthToken: {}' -i '{}' -acodec copy -f adts -loglevel error /dev/stdout".format(Radiko.token, url), 
                shell=True, stdout=PIPE, stderr=STDOUT, preexec_fn=os.setsid)
            source = PCMVolumeTransformer(FFmpegPCMAudio(p.stdout, pipe=True), volume=1.0)
            
            if self.voice_client and not self.voice_client.is_playing():
                self.voice_client.play(source, after=lambda _: p.kill())
            
            logger.debug('started subprocess: group id {}'.format(os.getpgid(p.pid)))

            await asyncio.sleep(10) # 10秒起きにループ