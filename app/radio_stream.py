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
    current_station_id: str
    next_station_id: str = None

    def __init__(
        self,
            client: commands.Bot, 
            radiko: Radiko,
            voice_channel: VoiceChannel,
            stataion_id: str) -> None:
        self.client = client
        self.radiko = radiko
        self.voice_channel = voice_channel
        self.current_station_id = stataion_id
    

    def getStreamUrl(self):
        return 'http://f-radiko.smartstream.ne.jp/{}/_definst_/simul-stream.stream/playlist.m3u8'.format(self.current_station_id)
         

    def start(self):
        self.client.loop.create_task(self.playRadioStream())


    async def playRadioStream(self):
        while self.client.loop.is_running():

            url = self.radiko.gen_temp_chunk_m3u8_url(self.getStreamUrl(), Radiko.token)
            p = Popen("ffmpeg -y -vn -headers 'X-Radiko-AuthToken: {}' -i '{}' -acodec copy -f adts -loglevel error /dev/stdout".format(Radiko.token, url), 
                shell=True, stdout=PIPE, stderr=STDOUT, preexec_fn=os.setsid)
            source = PCMVolumeTransformer(FFmpegPCMAudio(p.stdout, pipe=True), volume=1.0)
            def endStream():
                source.cleanup()
                p.kill()

            if self.next_station_id is not None and self.next_station_id != self.current_station_id:
                self.current_station_id = self.next_station_id
                self.next_station_id = None
                source.cleanup()
                # VC 切断
                await self.voice_client.disconnect()
                # VC 再接続
                self.voice_client = await self.voice_channel.connect()      
            else:
                self.voice_client.play(source, after=lambda _: endStream())
                logger.debug('started subprocess: group id {}'.format(os.getpgid(p.pid)))

            await asyncio.sleep(10) # 10秒起きにループ