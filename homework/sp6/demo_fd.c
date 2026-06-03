#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

int main() {
    const char *filename = "test.txt";
    const char *msg = "Hello, File Descriptor!\n";

    // === 寫入檔案 ===
    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open 寫入失敗");
        exit(1);
    }
    printf("開啟的 FD: %d\n", fd);

    ssize_t written = write(fd, msg, strlen(msg));
    printf("寫入 %zd bytes\n", written);
    close(fd);

    // === 讀取檔案 ===
    fd = open(filename, O_RDONLY);
    if (fd < 0) {
        perror("open 讀取失敗");
        exit(1);
    }
    printf("開啟的 FD: %d\n", fd);

    char buf[256] = {0};
    ssize_t bytes = read(fd, buf, sizeof(buf) - 1);
    printf("讀取 %zd bytes: %s", bytes, buf);
    close(fd);

    // === FD 分配規則 ===
    printf("\n=== FD 分配規則 ===\n");
    close(STDOUT_FILENO);
    int new_fd = open("fd_demo.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    printf("關閉 stdout(1) 後，open 拿到 FD: %d\n", new_fd);
    close(new_fd);

    return 0;
}
