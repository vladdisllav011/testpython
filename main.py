from playwright.sync_api import sync_playwright

def run():
    url = "https://app.notion.com/p/scripnic-ux/Developer-Handoff-Checklist-Free-40989bb9b75780b29fdcc585f7c26d48"
    
    with sync_playwright() as p:
        # Добавляем аргумент против детекта headless-браузера
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = context.new_page()
        
        print(f"Открываю страницу: {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Ждем 10 секунд, чтобы React-приложение Notion успело отрисоваться
        print("Жду 10 секунд прогрузки скриптов...")
        page.wait_for_timeout(10000)
        
        # Выводим в лог реальный заголовок и URL (на случай редиректа или капчи)
        print("Текущий URL:", page.url)
        print("Заголовок вкладки:", page.title())
        
        # Пробуем прокрутить страницу (и внутренний скроллер Notion, и само окно)
        print("Прокручиваю страницу...")
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
        
        # Вычисляем максимальную высоту контента
        full_height = page.evaluate("""
            () => {
                const scroller = document.querySelector('.notion-scroller');
                const h1 = scroller ? scroller.scrollHeight : 0;
                const h2 = document.body ? document.body.scrollHeight : 0;
                return Math.max(h1, h2, 900);
            }
        """)
        
        # Ограничим максимальную высоту до 15000px, чтобы скриншот не оказался слишком огромным
        target_height = min(full_height + 200, 15000)
        page.set_viewport_size({"width": 1440, "height": target_height})
        page.wait_for_timeout(2000)
        
        # Делаем скриншот без падения по таймауту
        page.screenshot(path="screenshot.png", full_page=True)
        print(f"Скриншот успешно сохранен! Высота: {target_height}px")
        
        browser.close()

if __name__ == "__main__":
    run()
