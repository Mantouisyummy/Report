from typing import Optional
from disnake.ext import commands
from disnake import ApplicationCommandInteraction, Option, OptionType, TextChannel, Embed, Colour, app_commands
from core.classes import ReportModal, ReportPrepareModal, ReportView

import os
import json


class Report(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ReportView())
        print("Report Ready!")

    @commands.slash_command(name="report", description="發送一則可提供別人檢舉用戶的訊息")
    async def report(self, interaction: ApplicationCommandInteraction):
        pass

    @report.sub_command(name="message", description="發送一則可提供別人檢舉用戶的訊息")
    async def message(self, interaction: ApplicationCommandInteraction, channel:Optional[TextChannel] = Option(name="channel",description="指定發送的頻道 (不指定則以目前頻道為主)",type=OptionType.channel,required=False)):
        if interaction.user.guild_permissions.administrator:
            if os.path.isfile(f"./database/guild/{interaction.guild.id}/setting.json"):
                with open(f"./database/guild/{interaction.guild.id}/setting.json", "r", encoding="utf-8") as f:
                        data = json.load(f)
                if type(channel) == Option:
                    data["message_channel"] = ""
                else:
                    data["message_channel"] = channel.id

                with open(f"./database/guild/{interaction.guild.id}/setting.json", "w", encoding="utf-8") as f:
                    json.dump(data, f)
                await interaction.response.send_modal(modal=ReportPrepareModal())
            else:
                with open(f"./database/guild/{interaction.guild.id}/setting.json", "w", encoding="utf-8") as f:
                        dictionary = {"message_channel": channel.id}
                        json.dump(dictionary, f)
                await interaction.response.send_modal(modal=ReportPrepareModal())
        else:
            fail_embed = Embed(title=f":x: | 你需要有管理者權限才能執行此指令",colour=Colour.red())
            await interaction.response.send_message(embed=fail_embed)

    @report.sub_command(name="setup", description="設定頻道",options=[Option(name="channel",description="指定申請對話的通知頻道",type=OptionType.channel, required=True)])
    async def setup(self, interaction: ApplicationCommandInteraction, channel:Optional[TextChannel] = Option(name="channel",description="指定申請對話的通知頻道",type=OptionType.channel, required=True)):
        if interaction.user.guild_permissions.administrator:
            if isinstance(channel, TextChannel):
                await interaction.response.defer(ephemeral=True)
                if not os.path.exists(f"./database/guild/{interaction.guild.id}/"):
                    os.makedirs(f"./database/guild/{interaction.guild.id}/")
                    with open(f"./database/guild/{interaction.guild.id}/setting.json", "w", encoding="utf-8") as f:
                        dictionary = {"notification_channel": channel.id}
                        json.dump(dictionary, f)

                    success_embed = Embed(title=f"✅ | 已寫入成功!",description=f"目前的通知頻道為: {channel.mention}",colour=Colour.green())
                    await interaction.followup.send(embed=success_embed)
                else:
                    with open(f"./database/guild/{interaction.guild.id}/setting.json", "r", encoding="utf-8") as f:
                        data = json.load(f)

                    data["notification_channel"] =  channel.id

                    with open(f"./database/guild/{interaction.guild.id}/setting.json", "w", encoding="utf-8") as f:
                        json.dump(data, f)

                    success_embed = Embed(title=f"✅ | 已更新成功!",description=f"目前的通知頻道為: {channel.mention}",colour=Colour.green())
                    await interaction.followup.send(embed=success_embed)       
            else:
                await interaction.response.send_message("請選擇正確的文字頻道!",ephemeral=True)
        else:
            fail_embed = Embed(title=f":x: | 你需要有管理者權限才能執行此指令",colour=Colour.red())
            await interaction.response.send_message(embed=fail_embed)

                    
        

def setup(bot):
    bot.add_cog(Report(bot))