import disnake
from disnake import ButtonStyle, ModalInteraction, TextInputStyle, MessageInteraction, ChannelType, Embed, Colour
from disnake.ui import Button, TextInput, Modal, View
import re
import json

class ReportView(View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @disnake.ui.button(label="我要檢舉",custom_id="report",style=ButtonStyle.gray)
    async def reportbutton(self, button: Button, interaction: MessageInteraction):
        await interaction.response.send_modal(modal=ReportModal())

class ReportModal(Modal):
    def __init__(self) -> None:
        component = [
            TextInput(
                label="違規用戶 (名稱#四位數 or ID)",
                placeholder="如 Man頭(´・ω・)#8870 or 549056425943629825",
                custom_id="user",
                style=TextInputStyle.single_line,
                max_length=100,
                min_length=5,
                required=True
            ),
            TextInput(
                label="違規原因",
                placeholder="",
                custom_id="reason",
                style=TextInputStyle.long,
                max_length=1000,
                min_length=10,
                required=True
            ),
            TextInput(
                label="事發日期時間",
                placeholder="2023/05/30 20:41",
                custom_id="time",
                style=TextInputStyle.single_line,
                max_length=20,
                min_length=15,
                required=True
            ),

        ]
        super().__init__(
            title="惡意行為檢舉",
            custom_id="modal_id_2",
            timeout=300,
            components=component,
        )

    async def callback(self, interaction: ModalInteraction):
        try:
            value = interaction.text_values
            channel = interaction.channel
            embed = Embed(title="",colour=Colour.random())
            embed.add_field(name="違規者",value=f"`{value['user']}`",inline=False)
            embed.add_field(name="違規日期",value=f"`{value['time']}`",inline=False)
            embed.add_field(name="原因",value=f"`{value['reason']}`",inline=False)
            thread = await channel.create_thread(name=value['reason'],type=ChannelType.private_thread)
            await interaction.response.send_message(f"已創建成功! 請至 {thread.mention} 查看",ephemeral=True)
            await thread.send(content=f"{interaction.user.mention} 請協助提供證據以及圖片資料，或標註其他證人以方便管理員加快處理速度",embed=embed)
        except NameError:
            value = interaction.text_values
            channel = interaction.channel
            embed = Embed(title="",colour=Colour.random())
            embed.add_field(name="違規者",value=f"`{value['user']}`",inline=False)
            embed.add_field(name="違規日期",value=f"{value['time']}",inline=False)
            embed.add_field(name="原因",value=f"`{value['reason']}`",inline=False)
            thread = await channel.create_thread(name=value['reason'],type=ChannelType.private_thread)
            await interaction.response.send_message(f"已創建成功! 請至 {thread.mention} 查看",ephemeral=True)
            await thread.add_user(interaction.user)
            await thread.send(content=f"{interaction.user.mention} 請協助提供證據以及圖片資料，或標註其他證人以方便管理員加快處理速度",embed=embed)

class ReportPrepareModal(Modal):
    def __init__(self) -> None: 
        component = [
            TextInput(
                label="訊息內容 (不填入訊息則使用預設訊息)",
                placeholder="可使用的參數: {server} {bot}",
                custom_id="text",
                style=TextInputStyle.long,
                max_length=1000,
                min_length=0,
                required=False
            )
        ]
        super().__init__(
            title="檢舉訊息",
            custom_id="modal_id",
            timeout=300,
            components=component,

        )
    
    async def callback(self, interaction: ModalInteraction):
        with open(f"./database/guild/{interaction.guild.id}/setting.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        text = interaction.text_values["text"]
        if text == "":
            text = f"""《{interaction.guild.name}》社群檢舉系統
為了確保我們社群能保持著正向、友善及包容，
管理團隊將會協助受理檢舉並對違反規定的成員做出適當處分。
若需要更隱私的支援，您可以私訊 {interaction.guild.me.mention} 開啟和管理團隊的對話。
:point_down: 如有需要，請按下方的檢舉按鈕填寫表單，並備妥相關證據 (截圖、錄影音、消息連結) 以利管理團隊判斷。"""
            try:
                channel = interaction.guild.get_channel(int(data["message_channel"]))
                await channel.send(f"""{text}""",view=ReportView())
            except ValueError:
                await interaction.channel.send(f"""{text}""",view=ReportView())
            await interaction.response.send_message("發送成功!",ephemeral=True)
        else:
            replacements = {"{server}": interaction.guild.name, "{bot}": interaction.bot.user.mention}
            pattern = '|'.join(re.escape(key) for key in replacements.keys())
            new_text = re.sub(pattern, lambda m: replacements[m.group()], text)
            try:
                channel = interaction.guild.get_channel(int(data["message_channel"]))
                await channel.send(f"""{new_text}""",view=ReportView())
            except ValueError:
                await interaction.channel.send(f"""{new_text}""",view=ReportView())
            await interaction.response.send_message("發送成功!",ephemeral=True)