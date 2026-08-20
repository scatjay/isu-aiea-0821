# -*- coding: utf-8 -*-
"""改完內容跑這支，版本與時間戳自動同步。

🔴 為什麼要有這支：
   頁面上的改版戳記原本是手打的，而且散在兩個地方（index.html 的 PAGE_VER
   和 verStamp、還有 version.json）。今天 8/20 已經因此錯過兩次：
     · 16:27 的時候頁面寫 17:10
     · 20:50 推上去的版本，頁面還寫 v3.8 · 17:30
   手打的東西一定會忘記。改成「跑一支腳本，時間從系統來」就不會錯。

用法：
    python bump.py "單元3、4 對準貼文"     # 版本自動 +0.1
    python bump.py --ver v4.0 "大改版"      # 指定版本
"""
import io
import re
import sys
import json
import argparse
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML = 'index.html'
VJSON = 'version.json'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('note', nargs='?', default='', help='這次改了什麼（會顯示在頁面上）')
    ap.add_argument('--ver', help='指定版本，例如 v4.0。不給就自動 +0.1')
    a = ap.parse_args()

    h = open(HTML, encoding='utf-8').read()

    m = re.search(r"var PAGE_VER = '(v[\d.]+)'", h)
    if not m:
        print('找不到 PAGE_VER'); sys.exit(1)
    cur = m.group(1)

    if a.ver:
        new = a.ver
    else:
        # v3.9 -> v4.0
        major, minor = cur[1:].split('.')
        minor = int(minor) + 1
        if minor >= 10:
            major, minor = int(major) + 1, 0
        new = 'v%s.%s' % (major, minor)

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    # ① index.html 的常數
    h = h.replace("var PAGE_VER = '%s'" % cur, "var PAGE_VER = '%s'" % new, 1)

    # ② 戳記那一行：改成由 JS 從 version.json 填，HTML 裡只留 fallback
    h = re.sub(
        r'<p class="ver" id="verStamp">[^<]*</p>',
        '<p class="ver" id="verStamp">%s　·　%s 更新%s</p>'
        % (new, now, ('（%s）' % a.note) if a.note else ''),
        h, count=1)

    open(HTML, 'w', encoding='utf-8', newline='').write(h)

    # ③ version.json —— 舊版偵測與戳記共用同一份事實
    json.dump({'v': new, 't': now, 'note': a.note, '_': '頁面版本'},
              open(VJSON, 'w', encoding='utf-8'),
              ensure_ascii=False)

    print('  %s -> %s' % (cur, new))
    print('  時間戳 %s（取自系統時間，不是手打）' % now)
    if a.note:
        print('  說明: %s' % a.note)
    print('')
    print('  接著：git add index.html version.json && git commit && git push')


if __name__ == '__main__':
    main()
