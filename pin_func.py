from playwright.sync_api import sync_playwright
import time
import os

def collecting_links_to_pin(query: str, count: int):
    atr = []
    c = 0
    pin_id = 'data-test-pin-id'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720}, ignore_https_errors=True)
        page = context.new_page()

        page.route("**/*.{png,jpg,jpeg,css,woff2}", lambda route: route.abort())

        page.goto(f"https://ru.pinterest.com/search/pins/?q={query}&rs=typed", wait_until="domcontentloaded")

        while c < count:
            try:
                page.wait_for_selector(f'[{pin_id}]', timeout=10000)
            except Exception as e:
                print(f"Ошибка при ожидании элементов: {e}")
                break

            pins = page.query_selector_all(f'[{pin_id}]')

            for pin in pins:
                if c >= count:
                    break
                pin_id_value = pin.get_attribute(pin_id)
                if pin_id_value:
                    pin_url = f"https://ru.pinterest.com/pin/{pin_id_value}/"
                    if pin_url not in atr:
                        atr.append(pin_url)
                        c += 1
                        print(f"Собран пин {c}: {pin_url}")

            if c >= count:
                break

            prev_height = page.evaluate("document.body.scrollHeight")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
            new_height = page.evaluate("document.body.scrollHeight")

            if new_height == prev_height:
                print("Достигнут конец страницы или новый контент не загружается")
                break

        browser.close()

    with open("url_to_pin.txt", "w", encoding='utf-8') as file:
        file.write("\n".join(atr))

    if c < count:
        print(f"Собрано только {c} пинов из {count}, возможно, больше нет результатов.")

def collecting_links_to_img():
    path_to_img = "#mweb-unauth-container > div > div > div > div.ZZS.oy8.zI7 > div.tNl.zI7 > div > div > div > div > div > div.OVX.lnZ.mQ8.oy8.zI7 > div > div > div:nth-child(1) > div > div > div > div.MIw.QLY.Rym.fev.ojN.p6V.sLG.tZ1.wCF.zI7 > div > div > div > img"
    src = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.route("**/*.{png,jpg,jpeg,css,woff2}", lambda route: route.abort())

        with open("url_to_pin.txt", "r", encoding='utf-8') as file:
            if not file:
                print("Файл url_to_pin.txt пуст или не существует")
                return
            
            for line in file:
                url = line.strip()
                try:
                    page.goto(url, wait_until="domcontentloaded")
                    src_loc = page.locator(path_to_img).all()

                    if not src_loc:
                        print(f"Пропускаю пин {url}: изображение не найдено")
                        continue

                    for s in src_loc:
                        src_url = s.get_attribute('src')
                        if src_url and src_url.startswith("https://"):
                            src.append(src_url)
                            print(f"Собрана ссылка на изображение: {src_url}")
                        else:
                            print(f"Пропускаю пин {url}: недействительная ссылка на изображение")
                except Exception as e:
                    print(f"Пропускаю пин {url}: ошибка при загрузке ({str(e)})")

        browser.close()

        with open("url_to_img.txt", "w", encoding='utf-8') as file:
            for sr in src:
                file.write(sr + "\n")

def download_img(path: str):
    num = 1
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        with open("url_to_img.txt", "r", encoding='utf-8') as file:
            if not file:
                print("Файл url_to_img.txt пуст или не существует")
                return
            
            for src in file:
                url = src.strip()
                try:
                    response = page.goto(url, wait_until="networkidle")
                    if response.ok:
                        fmt = f"{path}/img_{num}.jpg"
                        with open(fmt, "wb") as f:
                            f.write(response.body())
                        print(f"Изображение сохранено: {fmt}")
                        num += 1
                    else:
                        print(f"Пропускаю изображение {url}: не удалось загрузить (статус {response.status})")
                except Exception as e:
                    print(f"Пропускаю изображение {url}: ошибка при загрузке ({str(e)})")

        browser.close()

        if os.path.exists("url_to_pin.txt"):
            os.remove("url_to_pin.txt")

        if os.path.exists("url_to_img.txt"):
            os.remove("url_to_img.txt")