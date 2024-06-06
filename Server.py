import socket
import threading
import pandas as pd

# 讀取菜單
def load_menu():
    food_df = pd.read_excel('menu.xlsx', sheet_name='Food')
    drinks_df = pd.read_excel('menu.xlsx', sheet_name='Drinks')
    
    menu = {}
    drinks = {}
    
    for index, row in food_df.iterrows():
        menu[str(row['ID'])] = (row['Item'], row['Price'])
        
    for index, row in drinks_df.iterrows():
        drinks[row['ID']] = (row['Item'], row['Price'])
        
    return menu, drinks

menu, drinks = load_menu()
orders = []

# TCP伺服器
def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))
    server.listen(5)
    print("TCP伺服器已啟動，等待連線...")

    while True:
        client_socket, addr = server.accept()
        print(f"接受連線: {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

def handle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            orders.append(data)
            print(f"收到訂單: {data}")
        except:
            break
    client_socket.close()

# UDP廣播伺服器
def udp_broadcast():
    import time
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    server.bind(('', 6789))
    
    message = "今日菜單:\n"
    for key, (item, price) in menu.items():
        message += f"{key}. {item} {price}\n"
    for key, (item, price) in drinks.items():
        message += f"{key}. {item} {price}\n"
    message = message.encode()
    
    while True:
        server.sendto(message, ('224.1.1.1', 6789))
        time.sleep(5)

# 計算統計
def calculate_totals():
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
        total_costs[name] = food_price + drink_price

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

if __name__ == "__main__":
    threading.Thread(target=tcp_server).start()
    threading.Thread(target=udp_broadcast).start()
    while True:
        cmd = input("輸入 'stat' 顯示統計結果: ")
        if cmd == 'stat':
            calculate_totals()
