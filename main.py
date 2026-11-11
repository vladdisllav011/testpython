import os
from playwright.sync_api import sync_playwright

def run():
    # Берем ссылку из поля ввода GitHub Actions (или используем запасную, если запущено локально)
    url = os.environ.get(
        "TARGET_URL", 
        "https://notion.com"
    ).strip()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # Получаем актуальный User-Agent и убираем метку Headless
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
        
        print("Жду 10 секунд прогрузки контента...")
        page.wait_for_timeout(10000)
        print("Заголовок вкладки:", page.title())
        
        # Прокручиваем страницу вниз и возвращаем наверх
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
        
        # Вычисляем полную высоту контента
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
        print(f"Скриншот успешно сохранен! Высота: {target_height}px")
        
        browser.close()

if __name__ == "__main__":
    run()
