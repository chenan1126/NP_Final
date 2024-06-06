import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

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
root.geometry('600x400')
root.configure(bg='#ededad')

menu_text = tk.StringVar()
menu_label = tk.Label(root, textvariable=menu_text, bg='#ededad', fg='#333', font=('Helvetica', 12), justify='left')
menu_label.pack(pady=10)

name_frame = tk.Frame(root, bg='#ededad')
name_frame.pack(pady=5)
tk.Label(name_frame, text="姓名:", bg='#ededad', fg='#333', font=('Helvetica', 12)).pack(side=tk.LEFT)
name_var = tk.StringVar()
tk.Entry(name_frame, textvariable=name_var, font=('Helvetica', 12), width=30).pack(side=tk.LEFT, padx=10)

food_frame = tk.Frame(root, bg='#ededad')
food_frame.pack(pady=5)
tk.Label(food_frame, text="選擇餐點:", bg='#ededad', fg='#333', font=('Helvetica', 12)).pack(side=tk.LEFT)
food_var = tk.StringVar()
tk.Entry(food_frame, textvariable=food_var, font=('Helvetica', 12), width=30).pack(side=tk.LEFT, padx=10)

drink_frame = tk.Frame(root, bg='#ededad')
drink_frame.pack(pady=5)
tk.Label(drink_frame, text="選擇飲料:", bg='#ededad', fg='#333', font=('Helvetica', 12)).pack(side=tk.LEFT)
drink_var = tk.StringVar()
tk.Entry(drink_frame, textvariable=drink_var, font=('Helvetica', 12), width=30).pack(side=tk.LEFT, padx=10)
tk.Button(root, text="送出訂單", command=send_order).pack()

# 啟動接收廣播
threading.Thread(target=receive_broadcast, daemon=True).start()

root.mainloop()