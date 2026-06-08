#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define MAX_CLIENTS 32
#define BUF_SIZE 2048
#define NAME_SIZE 32

typedef struct {
    int fd;
    char name[NAME_SIZE];
    int active;
} Client;

static Client clients[MAX_CLIENTS];
static int server_fd;

static void broadcast(const char *msg, int sender_fd) {
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (clients[i].active && clients[i].fd != sender_fd) {
            ssize_t r = write(clients[i].fd, msg, strlen(msg));
            (void)r;
        }
    }
}

static void send_private(const char *msg, int receiver_fd) {
    ssize_t r = write(receiver_fd, msg, strlen(msg));
    (void)r;
}

static void remove_client(int idx) {
    close(clients[idx].fd);
    printf("[disconnect] %s left\n", clients[idx].name);
    clients[idx].active = 0;
    char buf[BUF_SIZE];
    snprintf(buf, sizeof(buf), "[system] %s left the chat\n", clients[idx].name);
    broadcast(buf, -1);
}

static int find_client_by_name(const char *name) {
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (clients[i].active && strcmp(clients[i].name, name) == 0)
            return i;
    }
    return -1;
}

static int add_client(int fd) {
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (!clients[i].active) {
            clients[i].fd = fd;
            clients[i].active = 1;
            snprintf(clients[i].name, sizeof(clients[i].name), "user%d", i);
            return i;
        }
    }
    return -1;
}

static void handle_client(int idx) {
    Client *c = &clients[idx];
    char buf[BUF_SIZE];
    ssize_t n = read(c->fd, buf, sizeof(buf) - 1);
    if (n <= 0) {
        remove_client(idx);
        return;
    }
    buf[n] = '\0';
    if (buf[n-1] == '\n') buf[n-1] = '\0';

    if (buf[0] == '/') {
        if (strncmp(buf, "/quit", 5) == 0) {
            remove_client(idx);
        } else if (strncmp(buf, "/list", 5) == 0) {
            char resp[BUF_SIZE] = "[system] online users: ";
            int first = 1;
            for (int i = 0; i < MAX_CLIENTS; i++) {
                if (clients[i].active) {
                    char tmp[NAME_SIZE+4];
                    snprintf(tmp, sizeof(tmp), "%s%s", first ? "" : ", ", clients[i].name);
                    strncat(resp, tmp, sizeof(resp) - strlen(resp) - 1);
                    first = 0;
                }
            }
            strncat(resp, "\n", sizeof(resp) - strlen(resp) - 1);
            send_private(resp, c->fd);
        } else if (strncmp(buf, "/name ", 6) == 0) {
            char newname[NAME_SIZE];
            strncpy(newname, buf + 6, sizeof(newname) - 1);
            newname[sizeof(newname) - 1] = '\0';
            if (find_client_by_name(newname) >= 0) {
                send_private("[system] name already taken\n", c->fd);
            } else {
            char old[NAME_SIZE];
            memcpy(old, c->name, NAME_SIZE);
            memcpy(c->name, newname, NAME_SIZE);
                char msg[BUF_SIZE];
                snprintf(msg, sizeof(msg), "[system] %s renamed to %s\n", old, c->name);
                broadcast(msg, -1);
            }
        } else if (strncmp(buf, "/msg ", 5) == 0) {
            char target[NAME_SIZE];
            char text[BUF_SIZE];
            if (sscanf(buf + 5, "%31s %[^\n]", target, text) == 2) {
                int t = find_client_by_name(target);
                if (t >= 0) {
                    char msg[BUF_SIZE + 64];
                    snprintf(msg, sizeof(msg), "[private] %s: %s\n", c->name, text);
                    send_private(msg, clients[t].fd);
                    send_private(msg, c->fd);
                } else {
                    send_private("[system] user not found\n", c->fd);
                }
            } else {
                send_private("[system] usage: /msg <user> <message>\n", c->fd);
            }
        } else {
            send_private("[system] unknown command: /quit /list /name /msg\n", c->fd);
        }
    } else {
        char out[BUF_SIZE + 64];
        snprintf(out, sizeof(out), "[%s] %s\n", c->name, buf);
        broadcast(out, c->fd);
    }
}

static int setup_server(int port) {
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) { perror("socket"); return -1; }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind"); close(server_fd); return -1;
    }
    if (listen(server_fd, 5) < 0) {
        perror("listen"); close(server_fd); return -1;
    }
    return 0;
}

int main(int argc, char *argv[]) {
    int port = 9000;
    if (argc > 1) port = atoi(argv[1]);

    if (setup_server(port) < 0) return 1;
    printf("[server] listening on port %d\n", port);

    while (1) {
        fd_set readfds;
        FD_ZERO(&readfds);
        FD_SET(server_fd, &readfds);
        int max_fd = server_fd;

        for (int i = 0; i < MAX_CLIENTS; i++) {
            if (clients[i].active) {
                FD_SET(clients[i].fd, &readfds);
                if (clients[i].fd > max_fd) max_fd = clients[i].fd;
            }
        }

        if (select(max_fd + 1, &readfds, NULL, NULL, NULL) < 0) {
            perror("select"); break;
        }

        if (FD_ISSET(server_fd, &readfds)) {
            struct sockaddr_in cli_addr;
            socklen_t cli_len = sizeof(cli_addr);
            int cli_fd = accept(server_fd, (struct sockaddr*)&cli_addr, &cli_len);
            if (cli_fd < 0) { perror("accept"); continue; }

            int idx = add_client(cli_fd);
            if (idx < 0) {
                ssize_t r = write(cli_fd, "[system] server full\n", 20); (void)r;
                close(cli_fd);
            } else {
                char ip[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &cli_addr.sin_addr, ip, sizeof(ip));
                printf("[connect] %s (fd=%d) as %s\n", ip, cli_fd, clients[idx].name);

                char welcome[BUF_SIZE];
                snprintf(welcome, sizeof(welcome),
                    "[system] welcome! your name: %s\n"
                    "[system] commands: /quit /list /name <n> /msg <user> <text>\n",
                    clients[idx].name);
                send_private(welcome, cli_fd);

                char ann[BUF_SIZE];
                snprintf(ann, sizeof(ann), "[system] %s joined\n", clients[idx].name);
                broadcast(ann, cli_fd);
            }
        }

        for (int i = 0; i < MAX_CLIENTS; i++) {
            if (clients[i].active && FD_ISSET(clients[i].fd, &readfds)) {
                handle_client(i);
            }
        }
    }

    close(server_fd);
    return 0;
}
