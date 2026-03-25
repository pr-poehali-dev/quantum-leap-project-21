"""
Поиск товаров по названию товарного знака на Wildberries и Ozon.
Возвращает список найденных товаров с названием, продавцом, ценой и ссылкой.
"""
import json
import urllib.request
import urllib.parse
import urllib.error


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


def fetch_json(url: str, headers: dict = None, timeout: int = 12) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def search_wildberries(query: str) -> list:
    try:
        encoded = urllib.parse.quote(query)
        url = (
            f"https://search.wb.ru/exactmatch/ru/common/v9/search"
            f"?query={encoded}&resultset=catalog&limit=30&sort=popular&suppressSpellcheck=false"
        )
        data = fetch_json(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0',
            'Accept': 'application/json',
            'Origin': 'https://www.wildberries.ru',
            'Referer': 'https://www.wildberries.ru/',
        })

        items = []
        query_upper = query.upper()
        products = data.get('data', {}).get('products', [])

        for p in products:
            name = p.get('name', '')
            brand = p.get('brand', '')
            price = p.get('salePriceU', p.get('priceU', 0))
            price_rub = price // 100 if price else 0
            product_id = p.get('id', '')
            seller = p.get('supplier', brand or 'Неизвестно')

            name_upper = name.upper()
            brand_upper = brand.upper()

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
        return items
    except Exception as e:
        return []


def search_ozon(query: str) -> list:
    try:
        encoded = urllib.parse.quote(query)
        # Используем мобильный API Ozon — менее строгая защита
        url = f"https://api.ozon.ru/composer-api.bx/page/json/v2?url=%2Fsearch%2F%3Ftext%3D{encoded}%26from_global%3Dtrue"
        data = fetch_json(url, headers={
            'User-Agent': 'ozone/3.84.0 (Android 11; Samsung SM-G991B)',
            'Accept': 'application/json',
            'x-o3-app-name': 'ozonapp_android',
            'x-o3-app-version': '16.4.3(816)',
            'x-o3-device-type': 'mobile',
        })

        items = []
        query_upper = query.upper()
        widget_states = data.get('widgetStates', {})

        for key, value in widget_states.items():
            if 'searchResultsV2' not in key and 'tileGrid' not in key.lower():
                continue
            try:
                widget_data = json.loads(value) if isinstance(value, str) else value
                for item in widget_data.get('items', []):
                    name = item.get('title', item.get('name', ''))
                    brand = item.get('brand', item.get('brandName', ''))
                    if not name:
                        continue

                    # Цена
                    price = 0
                    price_data = item.get('price', {})
                    if isinstance(price_data, dict):
                        raw = price_data.get('price', '0')
                        price = int(''.join(filter(str.isdigit, str(raw))) or 0)

                    # Ссылка
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
            except Exception:
                continue
        return items
    except Exception:
        return []
