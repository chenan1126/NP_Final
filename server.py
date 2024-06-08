import socket
import threading
import pandas as pd
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import time
from datetime import datetime

# 读菜单
def load_menu():
    try:
        food_df = pd.read_excel('menu.xlsx', sheet_name='Food')
        drinks_df = pd.read_excel('menu.xlsx', sheet_name='Drinks')
    except FileNotFoundError:
        return {}, {}

    menu = {}
    drinks = {}

    for index, row in food_df.iterrows():
        menu[str(row['ID'])] = (row['Item'], row['Price'])

    for index, row in drinks_df.iterrows():
        drinks[row['ID']] = (row['Item'], row['Price'])

    return menu, drinks

menu, drinks = load_menu()
orders = []
order_history = []

# TCP服务器
def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))
    server.listen(5)
    print("TCP伺服器已啟動，等待連接...")

    while True:
        client_socket, addr = server.accept()
        print(f"接受連接: {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()
success_delete = False
def handle_client(client_socket):
    global success_delete
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            if data.startswith("DELETE_ORDER:"):
                success_delete = False
                order_id = data.split(":")[1].strip()  # 從客戶端接收訂單編號
                delete_order(order_id)
                if success_delete:
                    client_socket.send("SUCCESS".encode())
                else:
                    client_socket.send("ERROR: 訂單未找到".encode())
            else:
                orders.append(data)
                order_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'order': data
                })
                print(f"收到訂單: {data}")
                update_order_display()
                client_socket.send(f"訂單已成功接收".encode())
        except Exception as e:
            print(f"處理訂單時發生錯誤: {e}")
            break
    client_socket.close()

def delete_order(order_id):
    global orders
    global success_delete
    order_found = False
    for order in orders:
        if order_id in order:
            orders.remove(order)
            order_found = True
            break
    if order_found:
        print(f"訂單 {order_id} 已被刪除")
        update_order_display()
        success_delete = True
    else:
        print(f"未找到訂單 {order_id}")

# UDP广播服务器
def udp_broadcast():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    server.bind(('', 6789))

    def generate_messages():
        food_message = "今日菜單 - 餐點:\n"
        for key, (item, price) in menu.items():
            food_message += f"{key}. {item} {price}元\n"

        drink_message = "今日菜單 - 飲料:\n"
        for key, (item, price) in drinks.items():
            drink_message += f"{key}. {item} {price}元\n"

        return food_message.encode(), drink_message.encode()

    while True:
        food_message, drink_message = generate_messages()
        server.sendto(food_message, ('224.1.1.1', 6789))
        server.sendto(drink_message, ('224.1.1.1', 6789))
        time.sleep(1)

# 计算统计
def calculate_totals():
    item_counts = {item: 0 for item in menu.values()}
    drink_counts = {drink: 0 for drink in drinks.values()}
    total_costs = {}

    for order in orders:
        if isinstance(order, str):  # 確保訂單是字串類型
            name, order_items = order.split(": ")
            food, drink = order_items.split(", ")
            food_name, food_price = menu[food]
            drink_name, drink_price = drinks[drink]
            item_counts[(food_name, food_price)] += 1
            drink_counts[(drink_name, drink_price)] += 1
            total_costs[name] = total_costs.get(name, 0) + food_price + drink_price

    print("\n訂單統計:")
    for (item, price), count in item_counts.items():
        if count > 0:
            print(f"{item} {price}元 x {count}份")
    for (item, price), count in drink_counts.items():
        if count > 0:
            print(f"{item} {price}元 x {count}份")
    print("\n每人需付金額:")
    for name, cost in total_costs.items():
        print(f"{name}: {cost}元")

def update_order_display():
    order_display.configure(state='normal')
    order_display.delete(1.0, tk.END)
    order_display.insert(tk.END, "\n".join(orders))
    order_display.configure(state='disabled')

# 更新菜单功能
def update_menu():
    menu_path = filedialog.askopenfilename(title="選擇菜單檔案", filetypes=[("Excel檔案", "*.xlsx")])
    if menu_path:
        try:
            food_df = pd.read_excel(menu_path, sheet_name='Food')
            drinks_df = pd.read_excel(menu_path, sheet_name='Drinks')

            global menu, drinks
            menu = {str(row['ID']): (row['Item'], row['Price']) for index, row in food_df.iterrows()}
            drinks = {row['ID']: (row['Item'], row['Price']) for index, row in drinks_df.iterrows()}

            messagebox.showinfo("成功", "菜單已成功更新")
        except Exception as e:
            messagebox.showerror("錯誤", f"無法更新菜單: {e}")

# 显示菜单更新界面
def update_menu_gui():
    update_menu_window = tk.Toplevel(root)
    update_menu_window.title("選擇菜單")

    tk.Label(update_menu_window, text="上傳新的菜單檔案").pack(pady=10)
    tk.Button(update_menu_window, text="選擇文件", command=update_menu).pack(pady=10)

# 实时订单统计功能
def update_order_statistics():
    stats_window = tk.Toplevel(root)
    stats_window.title("訂單統計")

    stats_text = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD, state='normal', width=50, height=20)
    stats_text.pack()

    item_counts = {item: 0 for item in menu.values()}
    drink_counts = {drink: 0 for drink in drinks.values()}
    total_costs = {}

    for order in orders:
        name, order_items = order.split(": ")
        food, drink = order_items[0], order_items[1]
        food_name, food_price = menu[food]
        drink_name, drink_price = drinks[drink]
        item_counts[(food_name, food_price)] += 1
        drink_counts[(drink_name, drink_price)] += 1
        if name in total_costs:
            total_costs[name] += food_price + drink_price
        else:
            total_costs[name] = food_price + drink_price

    stats_text.insert(tk.END, "\n訂單統計:\n")
    for (item, price), count in item_counts.items():
        if count > 0:
            stats_text.insert(tk.END, f"{item} {price}元 x {count}份\n")
    for (item, price), count in drink_counts.items():
        if count > 0:
            stats_text.insert(tk.END, f"{item} {price}元 x {count}份\n")
    stats_text.insert(tk.END, "\n每人需付金額:\n")
    for name, cost in total_costs.items():
        stats_text.insert(tk.END, f"{name}: {cost}元\n")

    stats_text.configure(state='disabled')

# GUI设置
root = tk.Tk()
root.title("訂單統計")
root.geometry("600x500")
root.configure(bg='#ededad')

# 设置标签
tk.Label(root, text="當前訂單:", font=("Arial", 14), bg='#ededad', fg='#333').pack(pady=10)

# 设置带滚动条的文本框
order_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=60, height=20, bg='#fff', fg='#000', font=("Arial", 12))
order_display.pack(pady=10)

# 设置按钮框架
button_frame = tk.Frame(root, bg='#ededad')
button_frame.pack(pady=10)

# 设置按钮样式
btn_style = {'font': ("Arial", 12), 'bg': '#f0f0f0', 'fg': '#000', 'activebackground': '#d4d4d4'}

tk.Button(button_frame, text="顯示統計", command=update_order_statistics, **btn_style).pack(side=tk.LEFT, padx=10)
tk.Button(button_frame, text="選擇菜單", command=update_menu_gui, **btn_style).pack(side=tk.LEFT, padx=10)

if __name__ == "__main__":
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=udp_broadcast, daemon=True).start()
    root.mainloop()