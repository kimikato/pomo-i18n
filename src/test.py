# test.py

from pypomo.gettext import translation

# 英語
catalog_en = translation("messages", "locales", ["en"])
print("EN Hello:", catalog_en.gettext("Hello"))
print("EN apple (1):", catalog_en.ngettext("apple", "apples", 1))
print("EN apple (2):", catalog_en.ngettext("apple", "apples", 2))

# 日本語
catalog_ja = translation("messages", "locales", ["ja"])
print("JA Hello:", catalog_ja.gettext("Hello"))
print("JA apple (1):", catalog_ja.ngettext("apple", "apples", 1))
print("JA apple (2):", catalog_ja.ngettext("apple", "apples", 2))

