import io
import config
import pytz
import pyrogram
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, Update
from pyrogram import enums, Client
from datetime import datetime
from ..database import Database
from .waktu import Waktu


class Helper():
    def __init__(self, bot: Client, message: Message):
        self.bot = bot
        self.client = bot  
        self.message = message
        self.msg = message
        self.user_id = message.from_user.id
        self.first = message.from_user.first_name
        self.last = message.from_user.last_name
        self.fullname = f'{self.first} {self.last}' if self.last else self.first
        self.premium = message.from_user.is_premium
        self.username = (
            f'@{self.message.from_user.username}'
            if self.message.from_user.username
            else "-"
        )
        self.mention = self.message.from_user.mention
        
    async def estimate_message(self, image):
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        file_id = await self.client.send_photo(chat_id=self.msg.chat.id, photo=img_byte_arr)

        file_link = f'tg://openmessage?user_id={self.msg.from_user.id}&message_id={file_id}'
        message_text = f'<a href="{file_link}">&#8203;</a>'

        return message_text

    async def escapeHTML(self, text: str):
        if text is None:
            return ''
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    async def cek_langganan_channel(self, user_id: int):
        if user_id == config.id_admin:
            return True
        try:
            member = await self.bot.get_chat_member(config.channel_1, user_id)
        except UserNotParticipant:
            return False
        try:
            member = await self.bot.get_chat_member(config.channel_2, user_id)
        except UserNotParticipant:
            return False
        try:
            member = await self.bot.get_chat_member(config.channel_3, user_id)
        except UserNotParticipant:
            return False
        try:
            member = await self.bot.get_chat_member(config.channel_4, user_id)
        except UserNotParticipant:
            return False

        status = [
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.MEMBER,
            enums.ChatMemberStatus.ADMINISTRATOR
        ]
        return member.status in status

async def pesan_langganan(self):
    link_1 = await self.bot.export_chat_invite_link(config.channel_1)
    link_2 = await self.bot.export_chat_invite_link(config.channel_2)
    link_3 = await self.bot.export_chat_invite_link(config.channel_3)
    link_4 = await self.bot.export_chat_invite_link(config.channel_4)

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('Channel base', url=link_1), InlineKeyboardButton('Group base', url=link_2)],
        [InlineKeyboardButton('Channel Support', url=link_3)]
    ])

    if not await self.cek_langganan_channel(self.user_id):
        await self.bot.send_message(self.user_id, config.pesan_join, reply_to_message_id=self.message.id, reply_markup=markup)
    else:
        markup.row(InlineKeyboardButton('Coba lagi', url=f'https://t.me/{self.bot.username}?start=start'))
        if config.channel_4 not in [config.channel_1, config.channel_2, config.channel_3]:
            await self.bot.send_message(self.user_id, config.start_msg2, reply_to_message_id=self.message.id, reply_markup=markup)
        else:
            await self.bot.send_message(self.user_id, config.start_msg, reply_to_message_id=self.message.id, reply_markup=markup)


    async def daftar_pelanggan(self):
        database = Database(self.user_id)

        nama = self.fullname

        status = 'member'
        coin = f"0_{str(self.user_id)}"
        if self.user_id == config.id_admin:
            status = 'owner'
            coin = f"9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999_{str(self.user_id)}"

        nama = await self.escapeHTML(nama)
        data = {
            '_id': self.user_id,
            'nama': nama,
            'status': f"{status}_{str(self.user_id)}",
            'coin': coin,
            'menfess': 0,
            'all_menfess': 0,
            'sign_up': self.get_time().full_time
        }
        return await database.tambah_pelanggan(data)

    async def send_to_channel_log(self, type: str = None, link: str = None):
        if type == 'log_channel':
            pesan = "INFO MESSAGE 💌\n"
            pesan += f"├ Nama -: <b>{await self.escapeHTML(self.fullname)}</b>\n"
            pesan += f"├ ID -: <code>{self.user_id}</code>\n"
            pesan += f"├ Username -: {self.username}\n"
            pesan += f"├ Mention -: {self.mention}\n"
            pesan += f"├ Kirim pesan -: <a href='tg://openmessage?user_id={self.user_id}'>{await self.escapeHTML(self.fullname)}</a>\n"
            pesan += f"├ Cek Pesan : {link}\n"
            pesan += f"└ Waktu -: {self.get_time().full_time}"
        elif type == 'log_daftar':
            pesan = "<b>📊DATA USER BERHASIL DITAMBAHKAN DIDATABASE</b>\n"
            pesan += f"├ Nama -: <b>{await self.escapeHTML(self.fullname)}</b>\n"
            pesan += f"├ ID -: <code>{self.user_id}</code>\n"
            pesan += f"├ Username -: {self.username}\n"
            pesan += f"├ Mention -: {self.mention}\n"
            pesan += f"├ Kirim pesan -: <a href='tg://openmessage?user_id={self.user_id}'>{await self.escapeHTML(self.fullname)}</a>\n"
            pesan += f"└ Telegram Premium -: {'✅' if self.premium else '❌'}"
        else:
            pesan = "Jangan Lupa main bot @chatjomblohalu_bot"
        await self.bot.send_message(config.channel_log, pesan, enums.ParseMode.HTML, disable_web_page_preview=True)

    def formatrupiah(self, uang):
        y = str(uang)
        if int(y) < 0:
            return y
        if len(y) <= 3:
            return y
        else:
            p = y[-3:]
            q = y[:-3]
            return self.formatrupiah(q) + "." + p

    def formatduration(self, durasi):
        q, r = divmod(durasi, 60)
        h, q = divmod(q, 60)
        d, h = divmod(h, 24)

        duration = ""
        if d > 0:
            duration += f"{d} Hari "
        if h > 0:
            duration += f"{h} Jam "
        if q > 0:
            duration += f"{q} Menit "
        if r > 0:
            duration += f"{r} Detik"

        return duration

    async def info_pelanggan(self):
        database = Database(self.user_id)
        pelanggan = await database.get_pelanggan(self.user_id)

        if pelanggan:
            nama = pelanggan['nama']
            status = pelanggan['status'].split("_")[0]
            waktu_daftar = pelanggan['sign_up']
            coin = int(pelanggan['coin'].split("_")[0])
            menfess = pelanggan['menfess']
            all_menfess = pelanggan['all_menfess']
            telegram_premium = self.premium

            pesan = "<b>📝 INFORMASI PELANGGAN</b>\n"
            pesan += f"├ Nama : {await self.escapeHTML(nama)}\n"
            pesan += f"├ Status : {status.capitalize()}\n"
            pesan += f"├ Telegram Premium : {'✅' if telegram_premium else '❌'}\n"
            pesan += f"├ Daftar pada : {waktu_daftar}\n"
            pesan += f"├ Coin : {self.formatrupiah(coin)}\n"
            pesan += f"├ Menfess saat ini : {menfess}\n"
            pesan += f"└ Total Menfess : {all_menfess}"
        else:
            pesan = "Anda belum terdaftar sebagai pelanggan."

        await self.bot.send_message(self.user_id, pesan, enums.ParseMode.HTML)

    async def get_time(self):
        timezone = pytz.timezone("Asia/Jakarta")
        now = datetime.now(timezone)
        time = Waktu(
            now.strftime("%Y"),
            now.strftime("%m"),
            now.strftime("%d"),
            now.strftime("%H"),
            now.strftime("%M"),
            now.strftime("%S"),
            now.strftime("%A"),
            now.strftime("%B"),
            now.strftime("%Z")
        )
        return time
