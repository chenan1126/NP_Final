import socket
import threading
import tkinter as tk
from tkinter import messagebox

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
        menu_text.set(data.decode())
        parse_menu(data.decode())

def parse_menu(data):
    global menu, drinks
    lines = data.split('\n')
    menu = {}
    drinks = {}
    for line in lines:
        if '. ' in line:
            key, value = line.split('. ', 1)
            if ' ' in value:
                item, price = value.rsplit(' ', 1)
                try:
                    price = int(price)
                    if key.isdigit():
                        menu[key] = (item, price)
                    elif key.isalpha():
                        drinks[key] = (item, price)
                except ValueError:
                    continue

def send_order():
    name = name_var.get()
    food = food_var.get()
    drink = drink_var.get()
    if not name or not food or not drink:
        messagebox.showerror("錯誤", "所有欄位均為必填")
        return
    if food not in menu or drink not in drinks:
        messagebox.showerror("錯誤", "請輸入有效的餐點和飲料編號")
        return
    order = f"{name}: {food}{drink}"
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 12345))
    client.send(order.encode())
    client.close()
    messagebox.showinfo("訂單", "訂單已送出")

# 設定GUI
root = tk.Tk()
root.title("點餐系統")
root.geometry('380x400')

menu_text = tk.StringVar()
tk.Label(root, textvariable=menu_text).pack()

tk.Label(root, text="姓名:").pack()
name_var = tk.StringVar()
tk.Entry(root, textvariable=name_var).pack()

tk.Label(root, text="選擇餐點:").pack()
food_var = tk.StringVar()
tk.Entry(root, textvariable=food_var).pack()

tk.Label(root, text="選擇飲料:").pack()
drink_var = tk.StringVar()
tk.Entry(root, textvariable=drink_var).pack()

tk.Button(root, text="送出訂單", command=send_order).pack()

# 啟動接收廣播
threading.Thread(target=receive_broadcast, daemon=True).start()

root.mainloop()
