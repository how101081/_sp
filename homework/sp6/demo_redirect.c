#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/wait.h>

void demo_stdout_redirect() {
    printf("=== stdout 重導向 ===\n");

    int fd = open("output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) { perror("open"); exit(1); }

    printf("這行會顯示在終端機\n");

    dup2(fd, STDOUT_FILENO);
    close(fd);

    printf("這行會寫入 output.txt\n");
    printf("這行也是\n");

    fflush(stdout);
}

void demo_stdin_redirect() {
    printf("\n=== stdin 重導向 ===\n");

    int fd = open("output.txt", O_RDONLY);
    if (fd < 0) { perror("open"); exit(1); }

    dup2(fd, STDIN_FILENO);
    close(fd);

    char line[256];
    while (fgets(line, sizeof(line), stdin))
        printf("讀到: %s", line);
}

void demo_ls_redirect() {
    printf("\n=== fork + exec + dup2 (ls > ls_out.txt) ===\n");

    pid_t pid = fork();

    if (pid == 0) {
        int fd = open("ls_out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
        dup2(fd, STDOUT_FILENO);
        close(fd);

        execlp("ls", "ls", "-la", NULL);
        _exit(1);
    }

    wait(NULL);
    printf("ls 輸出已儲存到 ls_out.txt\n");
}

int main() {
    demo_stdout_redirect();

    dup2(open("/dev/tty", O_WRONLY), STDOUT_FILENO);

    demo_stdin_redirect();

    dup2(open("/dev/tty", O_RDONLY), STDIN_FILENO);

    demo_ls_redirect();

    return 0;
}
