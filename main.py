from playwright.sync_api import sync_playwright

def run():
    url = "https://app.notion.com/p/scripnic-ux/Developer-Handoff-Checklist-Free-40989bb9b75780b29fdcc585f7c26d48"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Устанавливаем удобное десктопное разрешение и User-Agent
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"Открываю страницу Notion: {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # 1. Ждем, пока Notion отрисует основной контент (заголовок или блоки)
        page.wait_for_selector(".notion-page-content, h1", timeout=30000)
        # Даем 3 секунды на догрузку шрифтов, иконок и скриптов
        page.wait_for_timeout(3000)
        
        # 2. Плавная прокрутка вниз для загрузки всех ленивых блоков
        print("Прокручиваю страницу для загрузки всего контента...")
        page.evaluate("""
            async () => {
                const scroller = document.querySelector('.notion-scroller') || document.documentElement;
                const totalHeight = scroller.scrollHeight;
                for (let pos = 0; pos < totalHeight; pos += 500) {
                    scroller.scrollTo(0, pos);
                    await new Promise(r => setTimeout(r, 200));
                }
                scroller.scrollTo(0, 0);
            }
        """)
        page.wait_for_timeout(2000)
        
        # 3. Растягиваем окно браузера под реальную высоту страницы Notion,
        # чтобы внутренний скролл не обрезал нижнюю часть скриншота
        full_height = page.evaluate("""
            () => {
                const scroller = document.querySelector('.notion-scroller');
                return scroller ? scroller.scrollHeight + 200 : document.body.scrollHeight;
            }
        """)
        if full_height > 900:
            page.set_viewport_size({"width": 1440, "height": full_height})
            page.wait_for_timeout(1500)
        
        # 4. Делаем финальный скриншот
        page.screenshot(path="screenshot.png", full_page=True)
        print(f"Скриншот сохранен! Итоговая высота страницы: {full_height}px")
        
        browser.close()

if __name__ == "__main__":
    run()
