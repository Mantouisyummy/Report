import asyncio
import re
import os
import aiohttp
import json

from disnake import Message, Game, Status, ChannelType, Embed, Colour, MessageInteraction, ButtonStyle, PermissionOverwrite, Webhook, File, SelectOption
from disnake.abc import Messageable
from disnake.utils import get
from disnake.ext.commands import InteractionBot
from disnake.ui import Button, StringSelect
from datetime import timezone, timedelta
from core.classes import ReportModal

class Bot(InteractionBot):
    def __init__(self,  *args, **kwargs):
        self.author = None
        self.admin = None
        """
        :param conversation: Conversation instance
        :param args: args
        :param kwargs: kwargs
        """
        super().__init__(*args, **kwargs)


    async def on_ready(self):
        await self.change_presence(activity=Game("檢舉系統  V1.0 開源by.饅頭"), status=Status.online)
        for file in os.listdir('./cogs'):  # 抓取所有cog資料夾裡的檔案
            if file.endswith('.py'):  # 判斷檔案是否是python檔
                try:
                    # 載入cog,[:-3]是字串切片,為了把.py消除
                    self.load_extension(f'cogs.{file[:-3]}')
                    print(f'✅ 已加載 {file}')
                except Exception as error:  # 如果cog未正確載入
                    print(f'❌ {file} 發生錯誤  {error}')
    
    async def on_message(self, message:Message):
        if message.author == self.user:
            return
        if message.channel.type == ChannelType.private:
            if self.admin is not None:
                name = f"dialog-{message.author.id}"
                channel = get(self.admin.guild.text_channels, name=str(name))
                if channel:
                    webhooks = await channel.webhooks()
                    for webhook in webhooks:
                        if "客服用" == webhook.name:
                            async with aiohttp.ClientSession() as session:
                                webhook = Webhook.from_url(webhook.url, session=session)
                                await webhook.send(content=message.content, username=self.author.name, avatar_url=self.author.avatar.url)
                            break
                    else:
                        webhook = await channel.create_webhook(name="客服用",reason="作為客服頻道使用的webhook") 
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(webhook.url, session=session)
                            await webhook.send(content=message.content, username=self.author.name, avatar_url=self.author.avatar.url)
            else:
                    try:
                        embed = Embed(title="請確認您要與管理團隊對話的請求",description=
                                    """如果您想要舉報成員，請確保提前準備好盡可能多的證據。
                                            
                                    👇 若要和管理團隊進行對話，請按下方按鈕聯繫我們。""",colour=Colour.red())
                        components = [
                            Button(label="開始對話",custom_id=f"open_dialogue_{message.author.id}")
                        ]
                        await message.channel.send(embed=embed,components=components)
                    except KeyError:
                        fail_embed = Embed(title=f":x: | 無法使用此功能，因管理團隊未設定通知對話頻道，望請見諒。",colour=Colour.red())
                        await message.author.send(embed=fail_embed)

        if message.channel.type != ChannelType.private:                    
            if self.admin == message.author:
                name = f"dialog-{self.author.id}"
                channel = get(self.admin.guild.text_channels, name=str(name))
                if channel:
                    message = f"團隊人員 | {self.admin.name}: {message.content}"
                    user = self.get_user(self.author.id)
                    await user.send(content=message)
                else:
                    pass

    async def on_message_interaction(self, interaction:MessageInteraction):

        if interaction.data.custom_id == f"report":
            await interaction.response.send_modal(modal=ReportModal())
        try:
            if interaction.data.custom_id == f"open_dialogue_{interaction.author.id}":
                embed = Embed(title="確定要聯繫管理團隊嗎?",colour=Colour.red())
                components = [
                    Button(label="我確定!",custom_id=f"confirm_open_dialogue_{interaction.author.id}",style=ButtonStyle.green)
                ]
                await interaction.response.send_message(embed=embed,components=components)
            
            elif interaction.data.custom_id == f"confirm_open_dialogue_{interaction.author.id}":
                self.author = interaction.author
                channel = self.get_channel(1121725584414888059) #之後改掉
                embed = Embed(title="正在聯繫中....",colour=Colour.light_gray())
                await interaction.response.edit_message(embed=embed, view=None)

                notification_embed = Embed(title="叮咚!",description=f"來自 {interaction.user.name} 的對話請求\n可處理的團隊人員請點底下按鈕以接手請求。",colour=Colour.random())
                components = [
                    Button(label="接手",custom_id=f"take_over_dialogue")
                ]
                await channel.send(embed=notification_embed,components=components)

            elif interaction.data.custom_id == f"take_over_dialogue":
                self.admin = interaction.author
                category = interaction.channel.category
                overwrites = {
                    interaction.author: PermissionOverwrite(view_channel=True, read_messages=True),
                    interaction.guild.me: PermissionOverwrite(view_channel=True, read_messages=True),
                    interaction.guild.default_role: PermissionOverwrite(view_channel=False)
                }
                channel = await interaction.guild.create_text_channel(name=f"dialog-{self.author.id}",category=category, overwrites=overwrites)
                embed = Embed(title=f"此對話已由 {interaction.user.name} 接手",colour=Colour.green())
                user = self.get_user(self.author.id)
                success_embed = Embed(title=f"聯繫成功! 和你對話的團隊人員為: {self.admin.name}",description="⚠️請注意，團隊人員有權隨時關閉此對話，如有任何疑慮或糾紛請至管理團隊所在群組處理。⚠️",colour=Colour.green())
                await user.send(embed=success_embed)

                await interaction.response.edit_message(embed=embed,view=None)
                await interaction.followup.send(f"你和對方的對話頻道: {channel.mention}",ephemeral=True)

                admin_embed = Embed(title="對話管理面板",description="您可以透過底下按鈕來選擇對此對話的執行動作\n※第一次對話時，對方訊息會延遲兩三秒發送為正常現象。※",colour=Colour.random())
                components = [
                    Button(label="關閉對話",custom_id=f"close_dialogue_{self.admin.id}",style=ButtonStyle.red),
                    Button(label="刪除對話",custom_id=f"delate_dialogue_{self.admin.id}",style=ButtonStyle.blurple)
                ]
                await channel.send(embed=admin_embed, components=components)

            elif interaction.data.custom_id == f"close_dialogue_{self.admin.id}":
                await interaction.channel.edit(name=f"closed-dialog-{self.author.id}")
                close_embed = Embed(title=f"團隊已關閉對話! 祝您有個美好的一天🎉\n如果可以，可以考慮花點時間幫這次對話評分喔!",colour=Colour.red())

                options = [
                    SelectOption(label="⭐",description="1星",value="⭐"),
                    SelectOption(label="⭐⭐",description="2星",value="⭐⭐"),
                    SelectOption(label="⭐⭐⭐",description="3星",value="⭐⭐⭐"),
                    SelectOption(label="⭐⭐⭐⭐",description="4星",value="⭐⭐⭐⭐"),
                    SelectOption(label="⭐⭐⭐⭐⭐",description="5星",value="⭐⭐⭐⭐⭐"),
                ]
                components = [
                    StringSelect(placeholder="⭐為這次的對話評分",custom_id="star_rate",max_values=1,min_values=1,options=options)
                ]

                user = self.get_user(self.author.id)
                await user.send(embed=close_embed,components=components)

                conversation_record = await interaction.channel.history(limit=None).flatten()  # 讀取頻道的歷史訊息
                text = ""  # 將字串變為空
                for message in conversation_record:  # 利用迴圈讀取歷史訊息
                    if (
                        message.author.id != interaction.guild.me.id
                        and message.content != ""
                    ):  # 排除機器人的訊息和內容空白
                        now = message.created_at.astimezone(
                            timezone(offset=timedelta(hours=8))
                        )  # 將時區變為台灣時區
                        text = f"{now.year}/{now.month}/{now.day} {now.hour}:{now.minute} - {message.author.display_name}: {message.content}\n{text}"
                with open(f"chat.txt", "w", encoding="utf-8") as chat:
                    chat.write(text)  # 將訊息寫入至chat.txt
                components = [
                    Button(label="刪除對話",custom_id=f"delate_dialogue_{self.admin.id}",style=ButtonStyle.blurple)
                ]
                await interaction.channel.send("對話紀錄:",file=File("chat.txt"),components=components)
                os.remove("chat.txt")

            elif interaction.data.custom_id == f"delate_dialogue_{self.admin.id}":
                await interaction.response.send_message("正在刪除....")
                await asyncio.sleep(1)
                await interaction.channel.delete()
            
            elif interaction.data.custom_id == f"star_rate":
                value = interaction.data.values[0]
                await interaction.response.edit_message(f"感謝你的評分🎉🎉🎉 你評了: {value}",view=None, embed=None)
                channel = self.get_channel(1121725584414888059) #之後改掉
                embed = Embed(title=f"{self.author.name} 的對話評分",description=f"星數:\n{value}",colour=Colour.yellow())
                await channel.send(embed=embed)
        except AttributeError:
            pass


