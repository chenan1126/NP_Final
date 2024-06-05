import socket
import threading
import tkinter as tk

# 接收廣播
def receive_broadcast():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.bind(('', 6789))
    mreq = socket.inet_aton("224.1.1.1") + socket.inet_aton("0.0.0.0")
    client.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        data, _ = client.recvfrom(1024)
        menu_text.set(data.decode())

def send_order():
    order = food_var.get() + drink_var.get()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 12345))
    client.send(order.encode())
    client.close()
    tk.messagebox.showinfo("訂單", "訂單已送出")

# 設定GUI
root = tk.Tk()
root.title("點餐系統")

menu_text = tk.StringVar()
tk.Label(root, textvariable=menu_text).pack()

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
