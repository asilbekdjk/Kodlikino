import requests
import time

TOKEN = "7959086132:AAG4gcZfitaQAwSailVLkhvnZzJkdiN8QLQ"
URL = f"https://api.telegram.org/bot{TOKEN}/"

ADMIN_ID = 7816557697  # Admin Telegram ID

# Kino ma'lumotlari (kod: (video_url, caption, views, reyting, ovozlar_soni))
kino_videolari = {}

# Foydalanuvchilar ro‘yxati
foydalanuvchilar = set()

# Admin menyusi uchun inline tugmalar
admin_keyboard = {
    "inline_keyboard": [
        [{"text": "🎥 Video qo‘shish", "callback_data": "add_video"}],
        [{"text": "📝 Video matni qo‘shish", "callback_data": "add_caption"}],
        [{"text": "📊 Statistika", "callback_data": "stats"}],
        [{"text": "👥 Foydalanuvchilar soni", "callback_data": "users"}],
        [{"text": "🔥 Eng ko‘p ko‘rilgan videolar", "callback_data": "top_videos"}],
        [{"text": "⭐ Eng yaxshi videolar", "callback_data": "top_rated"}],
        [{"text": "📢 Reklama yuborish", "callback_data": "broadcast"}],
    ]
}

def get_updates():
    response = requests.get(URL + "getUpdates")
    return response.json()

def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    requests.post(URL + "sendMessage", json=data)

def send_video(chat_id, video_url, caption=""):
    requests.get(URL + f"sendVideo?chat_id={chat_id}&video={video_url}&caption={caption}")

def main():
    last_update_id = None
    while True:
        updates = get_updates().get("result", [])
        if updates:
            for update in updates:
                update_id = update["update_id"]
                if last_update_id is None or update_id > last_update_id:
                    last_update_id = update_id
                    chat_id = update["message"]["chat"]["id"]
                    user_name = update["message"]["from"]["first_name"]
                    text = update["message"].get("text", "")

                    if chat_id not in foydalanuvchilar:
                        foydalanuvchilar.add(chat_id)

                    # ADMIN PANELI
                    if chat_id == ADMIN_ID:
                        if text == "/admin":
                            send_message(chat_id, "Admin menyusi:", reply_markup=admin_keyboard)

                        elif text.startswith("/add_video "):
                            args = text.split()
                            if len(args) == 3:
                                kod = args[1]
                                video_url = args[2]
                                kino_videolari[kod] = (video_url, "", 0, 0, 0)
                                send_message(chat_id, f"✅ Video {kod} kodi ostida qo‘shildi.")

                        elif text == "/stats":
                            stat_text = f"📊 Videolar soni: {len(kino_videolari)}\n👥 Foydalanuvchilar: {len(foydalanuvchilar)}"
                            send_message(chat_id, stat_text)

                        elif text == "/users":
                            send_message(chat_id, f"👥 Foydalanuvchilar soni: {len(foydalanuvchilar)}")

                        elif text == "/top_videos":
                            if kino_videolari:
                                sorted_videos = sorted(kino_videolari.items(), key=lambda x: x[1][2], reverse=True)
                                top_videos_text = "🔥 Eng ko‘p ko‘rilgan videolar:\n"
                                for kod, (video, caption, views, rating, votes) in sorted_videos[:5]:
                                    top_videos_text += f"🎥 Kod: {kod} | Ko‘rilgan: {views} marta\n"
                                send_message(chat_id, top_videos_text)
                            else:
                                send_message(chat_id, "❌ Videolar yo‘q.")

                        elif text == "/top_rated":
                            if kino_videolari:
                                sorted_videos = sorted(kino_videolari.items(), key=lambda x: x[1][3], reverse=True)
                                top_rated_text = "⭐ Eng yaxshi videolar:\n"
                                for kod, (video, caption, views, rating, votes) in sorted_videos[:5]:
                                    top_rated_text += f"🎥 Kod: {kod} | Reyting: {rating:.1f}/5\n"
                                send_message(chat_id, top_rated_text)
                            else:
                                send_message(chat_id, "❌ Reytingli videolar yo‘q.")

                        elif text.startswith("/broadcast "):
                            xabar = text[11:]
                            for user_id in foydalanuvchilar:
                                send_message(user_id, f"📢 {xabar}")
                                time.sleep(2)  # Spamdan himoya
                            send_message(chat_id, "✅ Reklama yuborildi!")

                    # FOYDALANUVCHI FUNKSIYALARI
                    else:
                        if text == "/start":
                            send_message(chat_id, f"Xush kelibsiz, {user_name}! 🎬\nKino kodini yuboring.")

                        elif text in kino_videolari:
                            video_url, caption, views, rating, votes = kino_videolari[text]
                            kino_videolari[text] = (video_url, caption, views + 1, rating, votes)
                            send_video(chat_id, video_url, caption)

                        elif text.startswith("/rate "):
                            args = text.split()
                            if len(args) == 3:
                                kod = args[1]
                                try:
                                    baho = int(args[2])
                                    if 1 <= baho <= 5:
                                        if kod in kino_videolari:
                                            video_url, caption, views, rating, votes = kino_videolari[kod]
                                            yangi_reyting = ((rating * votes) + baho) / (votes + 1)
                                            kino_videolari[kod] = (video_url, caption, views, yangi_reyting, votes + 1)
                                            send_message(chat_id, f"✅ {kod} videoga {baho}⭐ baho qo‘shildi!")
                                        else:
                                            send_message(chat_id, "❌ Bunday kod mavjud emas!")
                                    else:
                                        send_message(chat_id, "❌ Baholar 1 dan 5 gacha bo‘lishi kerak!")
                                except ValueError:
                                    send_message(chat_id, "❌ Noto‘g‘ri format! Misol: /rate 123 5")

                        else:
                            send_message(chat_id, "❌ Bunday kino kodi yo‘q! 🔍")

        time.sleep(2)

if __name__ == "__main__":
    main()