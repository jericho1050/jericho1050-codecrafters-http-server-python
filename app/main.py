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
    header, body = request.split("\r\n\r\n", 1)
    first_line, *headers = header.split(
        "\r\n"
    )  # which is the first line of the request in the headers (request line)

    method, path, protocol = first_line.split(
        " "
    )  # split the first line into method, path and protocol
    user_agent = headers[1].split(": ")[1]

    is_echo_route = re.match(r"/echo/(.*+)", path)
    is_user_agent_route = re.match(r"/user-agent", path)
    if path == "/":
        response = "HTTP/1.1 200 OK\r\n\r\n"
        client_socket.sendall(response.encode("utf-8"))
    elif is_echo_route:
        response = (
            f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(is_echo_route.group(1))}\r\n\r\n"
            + is_echo_route.group(1)
            + "\r\n"
        )
        client_socket.sendall(response.encode("utf-8"))
    elif is_user_agent_route:

        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}\r\n"

        client_socket.sendall(response.encode("utf-8"))

    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        client_socket.sendall(response.encode("utf-8"))


if __name__ == "__main__":
    main()
