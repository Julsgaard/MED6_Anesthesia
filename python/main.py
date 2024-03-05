from library import server, functions

host_ip = '0.0.0.0'
server_port = 8080

# TODO: Need comments


if __name__ == '__main__':
    functions.check_for_logs_folder()
    functions.delete_empty_folders_in_logs()
    functions.create_session_folder()

    print("Server starting...")

    # Starts the server
    server.start_server(host_ip, server_port)

    print("Server stopped.")
