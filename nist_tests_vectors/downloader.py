# coding: utf-8

import requests_cache

requests_cache.install_cache(
    cache_name='nist_cache',
    backend='sqlite',
    #path=args.cache,
    expire_after=30 * 24 * 60 * 60 # 30 days
)


def download(algorithm: str, dest_dir: str):
    pass
