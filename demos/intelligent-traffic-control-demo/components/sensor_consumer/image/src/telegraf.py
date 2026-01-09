def send_to_telegraf(sock, telegraf_uri, telegraf_port, data):
    print(f"Sending data to Telegraf: {data}")
    sock.sendto(data.encode(), (telegraf_uri, telegraf_port))