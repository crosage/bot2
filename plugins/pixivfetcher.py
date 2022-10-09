import aiohttp
class HttpFecher(object):
    default_timeout_time:int=10
    _default_headers: dict[str, str] = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9',
        'dnt': '1',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/101.0.4951.54 Safari/537.36'
    }
    _http_proxy_config="http://localhost:7890"
    def __init__(self,timeout,cookies:dict[str,str],headers:dict[str,str]) -> None:
        _headers=self._default_headers if headers is None else headers
        self.headers=_headers
        self.cookies=cookies
        self.timeout=timeout

    
    async def get_json_dict(self,url:str,params:dict[str,str],encodint:str):
        async with aiohttp.ClientSession(timeout=20) as session:
            async with session.get(url=url,params=params,cookies=self.cookies,proxy=self._http_proxy_config,timeout=self.timeout) as rp:
                _json=await rp.json()
                _result={"status":rp.status,"headers":rp.headers,"cookies":rp.cookies,"result":_result}
                return _result