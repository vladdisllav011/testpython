import os
import requests
from playwright.sync_api import sync_playwright

def send_to_telegram(token, chat_id, file_path, caption=""):
    if not token or not chat_id:
        print("TG_TOKEN или TG_CHAT_ID не заданы, пропускаю отправку в Telegram.")
        return
    url = f"https://telegram.org{token}/sendDocument"
    with open(file_path, "rb") as f:
        response = requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption},
            files={"document": f}
        )
    print(f"Отправка {file_path} в Telegram: статус {response.status_code}")

def run():
    url = os.environ.get(
        "TARGET_URL", 
        "https://notion.com"
    ).strip()
    
    tg_token = os.environ.get("TG_TOKEN", "").strip()
    # Берем chat_id из запроса n8n, если передан, иначе из секретов GitHub
    tg_chat_id = os.environ.get("CUSTOM_CHAT_ID") or os.environ.get("TG_CHAT_ID", "")
    tg_chat_id = tg_chat_id.strip()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        temp_context = browser.new_context()
        temp_page = temp_context.new_page()
        real_ua = temp_page.evaluate("navigator.userAgent").replace("HeadlessChrome", "Chrome")
        temp_context.close()
        
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=real_ua,
            locale="en-US"
        )
        page = context.new_page()
        
        print(f"Открываю страницу: {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(10000)
        
        page_title = page.title() or "Без названия"
        print("Заголовок:", page_title)
        
        # Прокручиваем страницу для прогрузки всего контента
        page.evaluate("""
            async () => {
                const scroller = document.querySelector('.notion-scroller') || document.scrollingElement || document.body;
                const totalHeight = scroller.scrollHeight;
                for (let pos = 0; pos < totalHeight; pos += 600) {
                    scroller.scrollTo(0, pos);
                    window.scrollTo(0, pos);
                    await new Promise(r => setTimeout(r, 200));
                }
                scroller.scrollTo(0, 0);
                window.scrollTo(0, 0);
            }
        """)
        page.wait_for_timeout(3000)
        
        # 1. Сохраняем многостраничный PDF (до изменения высоты окна, чтобы красиво разбился на листы A4)
        page.emulate_media(media="screen")
        page.pdf(path="page.pdf", format="A4", print_background=True)
        print("PDF сохранен как page.pdf")
        
        # 2. Вычисляем полную высоту и делаем длинный PNG-скриншот без сжатия
        full_height = page.evaluate("""
            () => {
                const scroller = document.querySelector('.notion-scroller');
                const h1 = scroller ? scroller.scrollHeight : 0;
                const h2 = document.body ? document.body.scrollHeight : 0;
                return Math.max(h1, h2, 900);
            }
        """)
        target_height = min(full_height + 200, 15000)
        page.set_viewport_size({"width": 1440, "height": target_height})
        page.wait_for_timeout(2000)
        
        page.screenshot(path="screenshot.png", full_page=True)
        print("Скриншот сохранен как screenshot.png")
        
        browser.close()

    # Отправляем оба файла в Telegram
    send_to_telegram(tg_token, tg_chat_id, "screenshot.png", caption=f"📸 Скриншот: {page_title}\n🔗 {url}")
    send_to_telegram(tg_token, tg_chat_id, "page.pdf", caption=f"📄 PDF версия: {page_title}")

if __name__ == "__main__":
    run()
