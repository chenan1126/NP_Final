import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk

# 全局菜单变量
menu = {}
drinks = {}

# 接收廣播並解析菜單
def receive_broadcast():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.bind(('', 6789))
    mreq = socket.inet_aton("224.1.1.1") + socket.inet_aton("0.0.0.0")
    client.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        data, _ = client.recvfrom(1024)
        text = data.decode()
        if text.startswith("今日菜單 - 餐點:"):
            menu_text.set(text)
            parse_menu(text, 'food')
        elif text.startswith("今日菜單 - 飲料:"):
            drinks_text.set(text)
            parse_menu(text, 'drink')
        update_comboboxes()

def parse_menu(data, category):
    lines = data.split('\n')[1:]  # Skip the first line
    if category == 'food':
        global menu
        menu = {}
        for line in lines:
            if '. ' in line:
                key, value = line.split('. ', 1)
                if ' ' in value:
                    item, price = value.rsplit(' ', 1)
                    try:
                        price = int(price.rstrip('元'))
                        menu[key] = (item, price)
                    except ValueError:
                        continue
    elif category == 'drink':
        global drinks
        drinks = {}
        for line in lines:
            if '. ' in line:
                key, value = line.split('. ', 1)
                if ' ' in value:
                    item, price = value.rsplit(' ', 1)
                    try:
                        price = int(price.rstrip('元'))
                        drinks[key] = (item, price)
                    except ValueError:
                        continue

def update_comboboxes():
    food_combobox['values'] = [f"{key}. {menu[key][0]} {menu[key][1]}元" for key in menu]
    drink_combobox['values'] = [f"{key}. {drinks[key][0]} {drinks[key][1]}元" for key in drinks]

def send_order():
    name = name_var.get()
    food = food_var.get()
    drink = drink_var.get()
    if not name or not food or not drink:
        messagebox.showerror("錯誤", "所有欄位均為必填")
        return
    food_key = food.split(". ")[0]
    drink_key = drink.split(". ")[0]
    if food_key not in menu or drink_key not in drinks:
        messagebox.showerror("錯誤", "請輸入有效的餐點和飲料編號")
        return
    order = f"{name}: {food_key}{drink_key}"
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 12345))
    client.send(order.encode())
    client.close()
    messagebox.showinfo("訂單", "訂單已送出")

# 設定GUI
root = tk.Tk()
root.title("點餐系統")
root.geometry('800x600')
root.configure(bg='#ededad')

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=1)

menu_text = tk.StringVar()
menu_label = tk.Label(root, textvariable=menu_text, bg='#ededad', fg='#333', font=('微軟正黑體', 12), justify='left')
menu_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')

drinks_text = tk.StringVar()
drinks_label = tk.Label(root, textvariable=drinks_text, bg='#ededad', fg='#333', font=('微軟正黑體', 12), justify='left')
drinks_label.grid(row=1, column=1, padx=10, pady=10, sticky='w')

name_frame = tk.Frame(root, bg='#ededad')
name_frame.grid(row=2, column=0, columnspan=2, pady=5, padx=10, sticky='n')
tk.Label(name_frame, text="姓　　名:", bg='#ededad', fg='#333', font=('微軟正黑體', 12)).pack(side=tk.LEFT)
name_var = tk.StringVar()
tk.Entry(name_frame, textvariable=name_var, font=('微軟正黑體', 12), width=30).pack(side=tk.LEFT, padx=10)

food_frame = tk.Frame(root, bg='#ededad')
food_frame.grid(row=3, column=0, columnspan=2, pady=5, padx=10, sticky='n')
tk.Label(food_frame, text="選擇餐點:", bg='#ededad', fg='#333', font=('微軟正黑體', 12)).pack(side=tk.LEFT)
food_var = tk.StringVar()
food_combobox = ttk.Combobox(food_frame, textvariable=food_var, font=('微軟正黑體', 12), width=28)
food_combobox.pack(side=tk.LEFT, padx=10)

drink_frame = tk.Frame(root, bg='#ededad')
drink_frame.grid(row=4, column=0, columnspan=2, pady=5, padx=10, sticky='n')
tk.Label(drink_frame, text="選擇飲料:", bg='#ededad', fg='#333', font=('微軟正黑體', 12)).pack(side=tk.LEFT)
drink_var = tk.StringVar()
drink_combobox = ttk.Combobox(drink_frame, textvariable=drink_var, font=('微軟正黑體', 12), width=28)
drink_combobox.pack(side=tk.LEFT, padx=10)

tk.Button(root, text="送出訂單", font=('微軟正黑體', 12), command=send_order).grid(row=5, column=0, columnspan=2, pady=10, sticky='n')

# 啟動接收廣播
threading.Thread(target=receive_broadcast, daemon=True).start()

root.mainloop()
