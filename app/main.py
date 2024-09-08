import socket  # noqa: F401
import re


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, client_address = server_socket.accept()  # wait for client
    request = client_socket.recv(1024).decode("utf-8")
    headers, body = request.split("\r\n\r\n")
    method, path, protocol = headers.split(
        " "
    )  # split the first line into method, path and protocol
    regex = re.match(r"/echo/(.*+)", path)
    if path == "/":
        response = "HTTP/1.1 200 OK\r\n\r\n"
        client_socket.sendall(response.encode("utf-8"))
    elif regex:
        response = (
            f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n"
            + regex.group(1)
        )

        client_socket.sendall(response.encode("utf-8"))
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        client_socket.sendall(response.encode("utf-8"))


if __name__ == "__main__":
    main()
