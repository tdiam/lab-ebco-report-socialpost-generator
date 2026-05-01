#!/usr/bin/env -S /home/theodore/.local/bin/dotenvx run -- uv run --with deepl

import json
import os
import sys
from pathlib import Path

from deepl import DeepLClient


lang_file = Path(sys.argv[1])
deepl = DeepLClient(os.getenv('DEEPL_API_KEY'), send_platform_info=False)

target_lang = (
    lang_file.stem
    if lang_file.stem in ['en-GB', 'pt-PT']
    else lang_file.stem.split('-')[0]
)


def get_translation(text, *, lang):
    return deepl.translate_text(
        text, source_lang='en', target_lang=lang, tag_handling='html'
    ).text


def walk_translate(obj, *, lang):
    if isinstance(obj, str):
        return get_translation(obj, lang=lang)

    if isinstance(obj, dict):
        return {
            k: v if k.startswith('$') else walk_translate(v, lang=lang)
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [walk_translate(o, lang=lang) for o in obj]

    return obj


with open(lang_file, 'r+', encoding='utf-8') as fp:
    translated = walk_translate(json.load(fp), lang=target_lang)
    fp.seek(0)
    fp.truncate()
    fp.write(json.dumps(translated, indent=2, ensure_ascii=False))
