import json
import logging
import os
from dataclasses import asdict, dataclass, field, fields
from typing import List

import requests
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def get_author_name(author, lang):
    for x_lang, name in author["name"].items():
        if x_lang == lang:
            return name


def cf_bulk(data):
    print("write config to cloudflare")
    path = f"/client/v4/accounts/{config.CF_ACCOUNT}/storage/kv/namespaces/{config.CF_KV_NS_ID}/bulk"
    url = f"https://api.cloudflare.com{path}"
    headers = {
        "Authorization": f"Bearer {config.CF_API_TOKEN}",
        "Content-Type": "application/json",
    }
    resp = requests.put(url, headers=headers, json=data, timeout=30)
    print(resp.text)
    # conn = http.client.HTTPSConnection("api.cloudflare.com")
    # conn.request("PUT", path, data, headers=headers)
    # resp = conn.getresponse()
    # print(resp.status, resp.reason, resp.msg)
    # print(resp.read())


@dataclass
class Quote:
    author: str
    quote: str
    tags: List[str] = field(default_factory=list)


# ...
class Quotes:
    def __init__(self):
        self.quotes = {}

    def add_quote(self, quote, lang):
        x = self.quotes.get(lang, None)
        if x is None:
            self.quotes[lang] = []
        self.quotes[lang].append(quote)

    def to_file(self):
        for lang, quotes in self.quotes.items():
            with open(f"quotes_{lang}.json", "w") as stream:
                stream.write(json.dumps([asdict(q) for q in quotes]))

    def to_cf_kv(self):
        for lang, quotes in self.quotes.items():
            i = 0
            data = [
                {"key": f"total_{lang}", "value": str(len(quotes)), "metadata": {}},
            ]
            for quote in quotes:
                data.append(
                    {
                        "key": f"{lang}_{i}",
                        "value": json.dumps(asdict(quote)),
                    }
                )
                i += 1
            # with open(f"kv_{lang}.json", "w") as stream:
            #     stream.write(json.dumps(data))
            #     cf_bulk(f"kv_{lang}.json")
            cf_bulk(data)


@dataclass(init=False)
class Configuration:
    CF_API_TOKEN: str
    CF_ACCOUNT: str
    CF_KV_NS_ID: str


def load_system_env():
    for _field in fields(config):
        env_key = _field.name
        if env_key.isupper():
            env_value = os.getenv(env_key)
            if env_value is not None:
                if _field.type == bool:
                    if env_value.lower() == "true":
                        env_value = True
                    else:
                        env_value = False
                setattr(config, env_key, env_value)
            else:
                logging.info(f"from system env no env {env_key}")  # noqa


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    out = Quotes()
    config = Configuration()
    load_system_env()
    with open("data.yaml", "r") as stream:
        data = load(stream, Loader=Loader)
        print(data)
        for item in data:
            quotes = item["quotes"]
            for quote in quotes:
                tags = quote.pop("tags", [])
                for lang, text in quote.items():
                    if text is not None:
                        # print(lang, text)
                        author = get_author_name(item["author"], lang)
                        q = Quote(author, text, tags)
                        # print(asdict(q))
                        out.add_quote(q, lang)
    out.to_file()
    out.to_cf_kv()
