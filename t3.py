import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# 🔑 REPLACE THIS WITH A NEW TOKEN FROM @BotFather (YOURS IS COMPROMISED!)
TOKEN = "7529053741:AAHvHUT3twui7I3GQi-91BdXFqApNcPf47Y"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_watermark_free_url(video_data):
    """Extract the best available watermark-free video URL."""
    return video_data.get("hdplay") or video_data.get("play")


async def start(update: Update, context):
    await update.message.reply_text(
        "Babe ❤️ Send me TikTok video links or playlist URLs!\n"
        "I’ll send you **watermark-free** videos with love! 💖"
    )


async def download_tiktok_videos(update: Update, context):
    user_input = update.message.text.strip()
    if not user_input:
        await update.message.reply_text("Please send a valid TikTok link!")
        return

    urls = [url.strip() for url in user_input.split(",") if url.strip()]
    tiktok_links = [url for url in urls if "tiktok.com" in url]

    if not tiktok_links:
        await update.message.reply_text("Darling 💕 Please send valid TikTok links!")
        return

    await update.message.reply_text("✨ Processing your request... Fetching watermark-free videos!")

    all_video_urls = []

    for idx, url in enumerate(tiktok_links, start=1):
        try:
            if "/playlist/" in url:
                msg = await update.message.reply_text(f"📥 Loading playlist {idx}/{len(tiktok_links)}...")
                resp = requests.get(f"https://www.tikwm.com/api/playlist/?url={url}", timeout=20)
                resp.raise_for_status()
                data = resp.json()
                videos = data.get("data", {}).get("videos", [])
                if not videos:
                    await msg.edit_text(f"❌ Playlist {idx} is empty or private.")
                    continue

                await msg.edit_text(f"✅ Found {len(videos)} videos in playlist {idx}. Preparing downloads...")
                for v in videos:
                    clean_url = get_watermark_free_url(v)
                    if clean_url:
                        all_video_urls.append(clean_url)
            else:
                # Single video
                msg = await update.message.reply_text(f"📥 Processing video {idx}/{len(tiktok_links)}...")
                resp = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=20)
                resp.raise_for_status()
                data = resp.json()
                if data.get("data"):
                    clean_url = get_watermark_free_url(data["data"])
                    if clean_url:
                        all_video_urls.append(clean_url)
                        await msg.edit_text(f"✅ Video {idx} ready!")
                    else:
                        await msg.edit_text(f"⚠️ No clean video found for link {idx}.")
                else:
                    await msg.edit_text(f"❌ Invalid TikTok link {idx}.")
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            await update.message.reply_text(f"💥 Failed to process link {idx}. Skipping...")

    if not all_video_urls:
        await update.message.reply_text("💔 Sorry baby, I couldn’t fetch any videos. Try again?")
        return

    total = len(all_video_urls)
    await update.message.reply_text(f"🚀 Sending {total} watermark-free video(s)! Hold on tight...")

    success_count = 0
    for i, video_url in enumerate(all_video_urls, start=1):
        try:
            await update.message.reply_text(f"📤 Sending video {i}/{total}...")
            await update.message.reply_video(
                video_url,
                caption="Your watermark-free TikTok video! 😘✨\nMade with love 💖"
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send video {video_url}: {e}")
            await update.message.reply_text(
                f"⚠️ Video {i} is too large (over 50MB) or unavailable.\n"
                "Telegram bots can't send files >50MB."
            )

    await update.message.reply_text(
        f"✅ Done! Successfully sent {success_count}/{total} video(s).\n"
        "Need more? Just send another link! 💕"
    )


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok_videos))
    logger.info("Bot started polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
