import socket  # noqa: F401
import re
import threading
import os
import sys
import gzip

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()


def handle_client(client_socket):
    try:
        request = client_socket.recv(1024).decode("utf-8")
        header, body = request.split("\r\n\r\n", 1)
        first_line, *headers = header.split(
            "\r\n"
        )  # which is the first line of the request in the headers (request line)

        method, path, protocol = first_line.split(
            " "
        )  # split the first line into method, path and protocol

        user_agent = None
        content_encoding = None
        for header_line in headers:
            if header_line.startswith("User-Agent:"):
                user_agent = header_line.split(": ")[1]
            if header_line.startswith("Accept-Encoding:"):
                content_encoding_schemes = header_line.split(": ")[1].split(", ")
                if "gzip" in content_encoding_schemes:
                    content_encoding = content_encoding_schemes[content_encoding_schemes.index("gzip")]
                    
        # check if the path is one of the routes
        is_echo_route = re.match(r"/echo/(.*)", path)
        is_user_agent_route = re.match(r"/user-agent", path)
        is_file_route = re.match(r"/files/(.*)", path)
        
        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
            client_socket.sendall(response.encode("utf-8"))
        elif is_echo_route:
            # if the path is the echo route, return the content of the path
            if content_encoding:
                body = gzip.compress(is_echo_route.group(1).encode('utf-8'))
                content_encoding_header = f"Content-Encoding: {content_encoding}\r\n"
            else:
                body = is_echo_route.group(1).encode("utf-8")
                content_encoding_header = f""
            response_headers = f"HTTP/1.1 200 OK\r\n{content_encoding_header}Content-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n".encode("utf-8")   
            
            response = response_headers + body
            client_socket.sendall(response)
        elif is_user_agent_route:

            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}\r\n"

            client_socket.sendall(response.encode("utf-8"))
        elif is_file_route:
            file_name = is_file_route.group(1)
            directory_name = sys.argv[2]

            if method == "POST":
                with open(os.path.join(directory_name, file_name), "wb") as file:
                    file.write(body.encode("utf-8"))
                response = "HTTP/1.1 201 Created\r\n\r\n"
                client_socket.sendall(response.encode("utf-8"))
            else:
                try:
                    with open(os.path.join(directory_name, file_name), "rb") as file:

                        content = file.read()  # read the content of the file
                        headers = f"HTTP/1.1 200 OK\r\nContent-Type:application/octet-stream\r\nContent-Length: {len(content)}\r\n\r\n"
                        response = headers.encode("utf-8") + content + b"\r\n"
                except (FileNotFoundError, IsADirectoryError):
                    response = b"HTTP/1.1 404 Not Found\r\n\r\n"

                client_socket.sendall(response)

        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
            client_socket.sendall(response.encode("utf-8"))
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
