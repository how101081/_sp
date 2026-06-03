#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork 失敗");
        exit(1);
    }

    if (pid == 0) {
        printf("[子] 執行 ls 命令前 (PID: %d)\n", getpid());

        char *args[] = {"ls", "-la", NULL};
        execvp("ls", args);

        perror("execvp 失敗");
        _exit(127);
    }

    int status;
    waitpid(pid, &status, 0);

    if (WIFEXITED(status))
        printf("\n[父] 子行程結束，退出碼: %d\n", WEXITSTATUS(status));

    return 0;
}
