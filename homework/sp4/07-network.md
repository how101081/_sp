# 第 7 章：網路程式設計

## 7.1 Socket 簡介

Socket 是網路通訊的端點，提供跨機器的行程間通訊。Linux 使用 Berkeley Socket API。

### Socket 類型

| 類型 | 說明 |
|------|------|
| `SOCK_STREAM` | TCP — 可靠、有序、雙向 |
| `SOCK_DGRAM` | UDP — 不可靠、無連線 |
| `SOCK_RAW` | 原始封包 |

## 7.2 TCP Server

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket 建立失敗");
        return 1;
    }
    
    // 設定 socket 選項（避免 TIME_WAIT）
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(8080),
        .sin_addr.s_addr = INADDR_ANY
    };
    
    if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind 失敗");
        return 1;
    }
    
    if (listen(server_fd, 5) < 0) {
        perror("listen 失敗");
        return 1;
    }
    
    printf("Server 監聽在 port 8080...\n");
    
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    
    int client_fd = accept(server_fd,
                           (struct sockaddr *)&client_addr,
                           &client_len);
    
    if (client_fd < 0) {
        perror("accept 失敗");
        return 1;
    }
    
    char buf[1024] = {0};
    read(client_fd, buf, sizeof(buf));
    printf("收到: %s\n", buf);
    
    const char *resp = "Hello from server!";
    write(client_fd, resp, strlen(resp));
    
    close(client_fd);
    close(server_fd);
    
    return 0;
}
```

## 7.3 TCP Client

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket 建立失敗");
        return 1;
    }
    
    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(8080)
    };
    
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
    
    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("connect 失敗");
        return 1;
    }
    
    const char *msg = "Hello from client!";
    write(sock, msg, strlen(msg));
    
    char buf[1024] = {0};
    read(sock, buf, sizeof(buf));
    printf("Server 回應: %s\n", buf);
    
    close(sock);
    return 0;
}
```

## 7.4 並行 Server（多行程）

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/wait.h>
#include <signal.h>

void handle_client(int client_fd) {
    char buf[1024];
    int n = read(client_fd, buf, sizeof(buf) - 1);
    buf[n] = '\0';
    printf("行程 %d 處理: %s\n", getpid(), buf);
    
    const char *resp = "HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello, World!";
    write(client_fd, resp, strlen(resp));
    close(client_fd);
    exit(0);
}

int main() {
    signal(SIGCHLD, SIG_IGN);  // 避免殭屍行程
    
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(8080),
        .sin_addr.s_addr = INADDR_ANY
    };
    
    bind(server_fd, (struct sockaddr *)&addr, sizeof(addr));
    listen(server_fd, 10);
    
    printf("並行 Server 啟動 (PID: %d)\n", getpid());
    
    while (1) {
        struct sockaddr_in client;
        socklen_t len = sizeof(client);
        int client_fd = accept(server_fd, (struct sockaddr *)&client, &len);
        
        if (fork() == 0) {
            close(server_fd);
            handle_client(client_fd);
        }
        
        close(client_fd);
    }
    
    close(server_fd);
    return 0;
}
```

## 7.5 UDP Server / Client

### UDP Server

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main() {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    
    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(9090),
        .sin_addr.s_addr = INADDR_ANY
    };
    
    bind(sock, (struct sockaddr *)&addr, sizeof(addr));
    
    printf("UDP Server 監聽在 port 9090...\n");
    
    char buf[1024];
    struct sockaddr_in client;
    socklen_t len = sizeof(client);
    
    int n = recvfrom(sock, buf, sizeof(buf), 0,
                     (struct sockaddr *)&client, &len);
    buf[n] = '\0';
    printf("收到: %s\n", buf);
    
    sendto(sock, "OK", 2, 0,
           (struct sockaddr *)&client, len);
    
    close(sock);
    return 0;
}
```

### UDP Client

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main() {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    
    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(9090)
    };
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
    
    sendto(sock, "Hello UDP", 9, 0,
           (struct sockaddr *)&addr, sizeof(addr));
    
    char buf[1024];
    socklen_t len = sizeof(addr);
    int n = recvfrom(sock, buf, sizeof(buf), 0,
                     (struct sockaddr *)&addr, &len);
    buf[n] = '\0';
    printf("Server 回應: %s\n", buf);
    
    close(sock);
    return 0;
}
```

## 7.6 select() — 多工 I/O

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/select.h>

int main() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(8080),
        .sin_addr.s_addr = INADDR_ANY
    };
    
    bind(server_fd, (struct sockaddr *)&addr, sizeof(addr));
    listen(server_fd, 5);
    
    fd_set read_fds;
    int max_fd = server_fd;
    
    while (1) {
        FD_ZERO(&read_fds);
        FD_SET(server_fd, &read_fds);
        
        struct timeval tv = {5, 0};
        
        int ret = select(max_fd + 1, &read_fds, NULL, NULL, &tv);
        
        if (ret < 0) {
            perror("select 錯誤");
            break;
        } else if (ret == 0) {
            printf("等待連線中...\n");
            continue;
        }
        
        if (FD_ISSET(server_fd, &read_fds)) {
            struct sockaddr_in client;
            socklen_t len = sizeof(client);
            int client_fd = accept(server_fd,
                                   (struct sockaddr *)&client, &len);
            
            char buf[1024];
            int n = read(client_fd, buf, sizeof(buf) - 1);
            buf[n] = '\0';
            printf("收到: %s", buf);
            
            write(client_fd, "OK\n", 3);
            close(client_fd);
        }
    }
    
    close(server_fd);
    return 0;
}
```

## 7.7 HTTP 請求解析範例

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

void handle_http(int client_fd) {
    char buf[4096];
    int n = read(client_fd, buf, sizeof(buf) - 1);
    buf[n] = '\0';
    
    // 簡單解析 HTTP 請求（僅示範）
    char method[16], path[256];
    sscanf(buf, "%s %s", method, path);
    
    printf("Method: %s, Path: %s\n", method, path);
    
    char *body = "<html><body><h1>Hello!</h1></body></html>";
    char resp[1024];
    snprintf(resp, sizeof(resp),
             "HTTP/1.1 200 OK\r\n"
             "Content-Type: text/html\r\n"
             "Content-Length: %zu\r\n"
             "\r\n"
             "%s",
             strlen(body), body);
    
    write(client_fd, resp, strlen(resp));
    close(client_fd);
}

int main() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(8080),
        .sin_addr.s_addr = INADDR_ANY
    };
    
    bind(server_fd, (struct sockaddr *)&addr, sizeof(addr));
    listen(server_fd, 5);
    
    printf("HTTP Server at http://localhost:8080\n");
    
    while (1) {
        struct sockaddr_in client;
        socklen_t len = sizeof(client);
        int client_fd = accept(server_fd,
                               (struct sockaddr *)&client, &len);
        
        if (fork() == 0) {
            close(server_fd);
            handle_http(client_fd);
            exit(0);
        }
        close(client_fd);
    }
    
    close(server_fd);
    return 0;
}
```

## 小結

- TCP 提供可靠連線，適用於大多數網路應用
- UDP 輕量無連線，適用於即時通訊
- `select()` 實現單執行緒多工 I/O
- 可透過 fork 實現並行伺服器
