import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Replace with your bot token
TOKEN = "7825400904:AAEZahOPs_kqHWknBbOc4znCqzY-HiQlkuA"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def extract_video_links_from_playlist(playlist_url):
    # Placeholder function for extracting video links from a TikTok playlist
    response = requests.get(f"https://www.tikwm.com/api/playlist/?url={playlist_url}").json()
    if response.get("data"):
        return [video["play"] for video in response["data"]["videos"]]
    return []

async def start(update: Update, context):
    await update.message.reply_text("Babe❤️ send TikTok links or playlist URLs, and I'll download the videos for you!")

async def download_tiktok_videos(update: Update, context):
    tiktok_urls = update.message.text.strip().split(",")
    valid_links = [url.strip() for url in tiktok_urls if "tiktok.com" in url]

    if not valid_links:
        await update.message.reply_text("Darling💕 Please Kindly send valid TikTok links!")
        return

    for url in valid_links:
        if "/playlist/" in url:
            video_links = extract_video_links_from_playlist(url)
            if not video_links:
                await update.message.reply_text(f"❌ Failed to retrieve playlist: {url}")
                continue
            await update.message.reply_text(f"Downloading {len(video_links)} videos from playlist, please wait...")
            valid_links.extend(video_links)
        
    for tiktok_url in valid_links:
        api_url = f"https://www.tikwm.com/api/?url={tiktok_url}"
        response = requests.get(api_url).json()
        
        if response.get("data"):
            video_url = response["data"]["play"]
            await update.message.reply_video(video_url, caption=f"You're Welcome Baby 😊❤️Here is your TikTok video!")
        else:
            await update.message.reply_text(f"❌ Failed to download: {tiktok_url}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok_videos))
    
    # Run bot
    app.run_polling()

if __name__ == "__main__":
    main()
