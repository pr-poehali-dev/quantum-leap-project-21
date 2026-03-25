"""
Поиск товаров по названию товарного знака на Wildberries и Ozon.
Возвращает список найденных товаров с названием, продавцом, ценой и ссылкой.
"""
import json
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import time


def make_opener(extra_headers: dict = None) -> urllib.request.OpenerDirector:
    """Opener с CookieJar — автоматически сохраняет и отправляет куки"""
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    return opener


def handler(event: dict, context) -> dict:
    headers_cors = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers_cors, 'body': ''}

    try:
        body = json.loads(event.get('body') or '{}')
        query = body.get('query', '').strip()
    except Exception:
        return {'statusCode': 400, 'headers': headers_cors, 'body': json.dumps({'error': 'Invalid request'})}

    if not query:
        return {'statusCode': 400, 'headers': headers_cors, 'body': json.dumps({'error': 'Query is required'})}

    results = []
    results += search_wildberries(query)
    results += search_ozon(query)

    return {
        'statusCode': 200,
        'headers': {**headers_cors, 'Content-Type': 'application/json'},
        'body': json.dumps({'results': results, 'query': query, 'total': len(results)}, ensure_ascii=False)
    }


def search_wildberries(query: str) -> list:
    try:
        encoded = urllib.parse.quote(query)
        opener = make_opener()

        wb_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Origin': 'https://www.wildberries.ru',
            'Referer': 'https://www.wildberries.ru/',
        }

        # Шаг 1: мета (shardKey + query_param)
        meta_url = (
            f"https://search.wb.ru/exactmatch/ru/common/v9/search"
            f"?query={encoded}&resultset=catalog&limit=30&sort=popular&suppressSpellcheck=false"
        )
        req = urllib.request.Request(meta_url, headers=wb_headers)
        with opener.open(req, timeout=15) as resp:
            meta = json.loads(resp.read().decode('utf-8'))

        shard_key = meta.get('shardKey', '')
        query_param = meta.get('query', '')
        print(f"[WB] shardKey={shard_key}, query_param={query_param}")

        products = []

        if shard_key and query_param:
            time.sleep(0.3)
            # Правильный формат: catalog.wb.ru/{shardKey}/catalog?{query_param}&...
            # query_param уже содержит preset=XXXXXXX
            catalog_url = (
                f"https://catalog.wb.ru/{shard_key}/catalog"
                f"?{query_param}&resultset=catalog&limit=30&sort=popular&suppressSpellcheck=false"
            )
            print(f"[WB] catalog_url: {catalog_url}")
            req2 = urllib.request.Request(catalog_url, headers=wb_headers)
            try:
                with opener.open(req2, timeout=15) as resp2:
                    cat_data = json.loads(resp2.read().decode('utf-8'))
                    products = cat_data.get('data', {}).get('products', [])
                    print(f"[WB] products from catalog: {len(products)}, cat keys: {list(cat_data.keys())}")
            except urllib.error.HTTPError as he:
                print(f"[WB] catalog HTTP {he.code}")
                # Попробуем с shard без подпути
                shard_base = shard_key.split('/')[0]
                alt_url = (
                    f"https://catalog.wb.ru/{shard_base}/catalog"
                    f"?{query_param}&resultset=catalog&limit=30&sort=popular"
                )
                print(f"[WB] alt_url: {alt_url}")
                req3 = urllib.request.Request(alt_url, headers=wb_headers)
                try:
                    with opener.open(req3, timeout=15) as resp3:
                        cat_data3 = json.loads(resp3.read().decode('utf-8'))
                        products = cat_data3.get('data', {}).get('products', [])
                        print(f"[WB] alt products: {len(products)}")
                except Exception as e3:
                    print(f"[WB] alt error: {e3}")

        print(f"[WB] total products: {len(products)}")

        query_upper = query.upper()
        items = []

        for p in products:
            name = p.get('name', '')
            brand = p.get('brand', '')
            price = p.get('salePriceU', p.get('priceU', 0))
            price_rub = price // 100 if price else 0
            product_id = p.get('id', '')
            seller = p.get('supplier', brand or 'Неизвестно')

            name_upper = name.upper()
            brand_upper = brand.upper() if brand else ''

            match_type = None
            if query_upper in brand_upper:
                match_type = 'brand'
            elif query_upper in name_upper:
                match_type = 'name'

            if match_type:
                items.append({
                    'marketplace': 'Wildberries',
                    'name': name,
                    'brand': brand,
                    'seller': seller,
                    'price': price_rub,
                    'url': f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx",
                    'match_type': match_type,
                    'risk': 'high' if match_type == 'brand' else 'medium',
                })

        print(f"[WB] matched: {len(items)}")
        return items

    except Exception as e:
        print(f"[WB] error: {type(e).__name__}: {e}")
        return []


def search_ozon(query: str) -> list:
    try:
        encoded = urllib.parse.quote(query)
        opener = make_opener()

        ozon_headers = {
            'User-Agent': 'ozone/3.84.0 (Android 11; Samsung SM-G991B)',
            'Accept': 'application/json',
            'x-o3-app-name': 'ozonapp_android',
            'x-o3-app-version': '16.4.3(816)',
            'x-o3-device-type': 'mobile',
        }

        # CookieJar opener автоматически обработает Set-Cookie из редиректа
        url = f"https://api.ozon.ru/composer-api.bx/page/json/v2?url=%2Fsearch%2F%3Ftext%3D{encoded}%26from_global%3Dtrue"
        req = urllib.request.Request(url, headers=ozon_headers)
        print(f"[Ozon] fetching with cookiejar")

        with opener.open(req, timeout=15) as resp:
            raw = resp.read()

        data = json.loads(raw.decode('utf-8'))
        print(f"[Ozon] top keys: {list(data.keys())[:8]}")

        items = []
        query_upper = query.upper()
        widget_states = data.get('widgetStates', {})
        print(f"[Ozon] widgets: {len(widget_states)}")

        for key, value in widget_states.items():
            if not any(k in key.lower() for k in ['search', 'tilegrid', 'catalog', 'tile']):
                continue
            try:
                widget_data = json.loads(value) if isinstance(value, str) else value
                for item in widget_data.get('items', []):
                    name = item.get('title', item.get('name', ''))
                    brand = item.get('brand', item.get('brandName', ''))
                    if not name:
                        continue

                    price = 0
                    price_data = item.get('price', {})
                    if isinstance(price_data, dict):
                        raw_p = price_data.get('price', '0')
                        price = int(''.join(filter(str.isdigit, str(raw_p))) or 0)

                    item_url = ''
                    action = item.get('action', item.get('link', {}))
                    if isinstance(action, dict):
                        item_url = action.get('link', action.get('url', ''))
                    elif isinstance(action, str):
                        item_url = action
                    if item_url and not item_url.startswith('http'):
                        item_url = 'https://www.ozon.ru' + item_url

                    name_upper = name.upper()
                    brand_upper = brand.upper() if brand else ''

                    match_type = None
                    if query_upper in brand_upper:
                        match_type = 'brand'
                    elif query_upper in name_upper:
                        match_type = 'name'

                    if match_type:
                        seller_info = item.get('seller', {})
                        seller = seller_info.get('name', brand or 'Неизвестно') if isinstance(seller_info, dict) else brand or 'Неизвестно'
                        items.append({
                            'marketplace': 'Ozon',
                            'name': name,
                            'brand': brand or 'Неизвестно',
                            'seller': seller,
                            'price': price,
                            'url': item_url,
                            'match_type': match_type,
                            'risk': 'high' if match_type == 'brand' else 'medium',
                        })
            except Exception as ex:
                print(f"[Ozon] widget err: {ex}")
                continue

        print(f"[Ozon] matched: {len(items)}")
        return items

    except Exception as e:
        print(f"[Ozon] error: {type(e).__name__}: {e}")
        return []
