import pathlib

orders_path = pathlib.Path(r'C:\Users\Jessie\OneDrive\Desktop\Web_pentest\burger_site\restaurant\templates\restaurant\orders.html')
admin_path  = pathlib.Path(r'C:\Users\Jessie\OneDrive\Desktop\Web_pentest\burger_site\restaurant\templates\restaurant\admin_panel.html')

# ── Fix orders.html ──
orders_content = orders_path.read_text(encoding='utf-8')

# Replace ANY variant of the split endif (handles \r\n and \n)
import re
orders_content = re.sub(
    r"\{%\s*if order\.status == 'pending' %\}.*?{% endif\s*%\}",
    "{% if order.status == 'pending' %}⏳{% elif order.status == 'confirmed' %}✅{% else %}🍔{% endif %}",
    orders_content,
    flags=re.DOTALL
)

orders_path.write_text(orders_content, encoding='utf-8')
print('orders.html fixed')

# ── Fix admin_panel.html ──
admin_content = admin_path.read_text(encoding='utf-8')

# Fix missing spaces around == (all three statuses)
admin_content = re.sub(r"order\.status=='pending'",   "order.status == 'pending'",   admin_content)
admin_content = re.sub(r"order\.status=='confirmed'", "order.status == 'confirmed'", admin_content)
admin_content = re.sub(r"order\.status=='done'",      "order.status == 'done'",      admin_content)

# Fix the split "{% endif\n                                                %}" pattern
admin_content = re.sub(r'\{%\s*endif\s*\n\s*%\}', '{% endif %}', admin_content)

admin_path.write_text(admin_content, encoding='utf-8')
print('admin_panel.html fixed')
print('All done!')
