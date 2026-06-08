#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define BUF_SIZE 2048

static int connect_to_server(const char *host, int port) {
    struct hostent *he = gethostbyname(host);
    if (!he) {
        fprintf(stderr, "unknown host: %s\n", host);
        return -1;
    }

    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) { perror("socket"); return -1; }

    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    memcpy(&addr.sin_addr, he->h_addr_list[0], he->h_length);

    if (connect(fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("connect"); close(fd); return -1;
    }
    return fd;
}

int main(int argc, char *argv[]) {
    const char *host = "127.0.0.1";
    int port = 9000;

    if (argc > 1) host = argv[1];
    if (argc > 2) port = atoi(argv[2]);

    int fd = connect_to_server(host, port);
    if (fd < 0) return 1;

    printf("connected to %s:%d\n", host, port);

    while (1) {
        fd_set readfds;
        FD_ZERO(&readfds);
        FD_SET(STDIN_FILENO, &readfds);
        FD_SET(fd, &readfds);

        if (select(fd + 1, &readfds, NULL, NULL, NULL) < 0) {
            perror("select"); break;
        }

        if (FD_ISSET(STDIN_FILENO, &readfds)) {
            char buf[BUF_SIZE];
            if (!fgets(buf, sizeof(buf), stdin)) break;

            if (write(fd, buf, strlen(buf)) < 0) {
                perror("write"); break;
            }
        }

        if (FD_ISSET(fd, &readfds)) {
            char buf[BUF_SIZE];
            ssize_t n = read(fd, buf, sizeof(buf) - 1);
            if (n <= 0) {
                printf("[disconnected]\n");
                break;
            }
            buf[n] = '\0';
            printf("%s", buf);
            fflush(stdout);
        }
    }

    close(fd);
    return 0;
}
