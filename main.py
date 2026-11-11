from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # Запускаем браузер в фоновом режиме (headless=True)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Переходим на нужный сайт (можете заменить на свой URL)
        url = "https://example.com"
        print(f"Открываю {url}...")
        page.goto(url, wait_until="networkidle")
        
        # Делаем скриншот всей страницы от верха до низа
        page.screenshot(path="screenshot.png", full_page=True)
        print("Скриншот успешно сохранен как screenshot.png")
        
        browser.close()

if __name__ == "__main__":
    run()
