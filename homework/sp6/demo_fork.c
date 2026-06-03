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
        printf("[子] PID: %d, 父 PID: %d, fork 回傳: %d\n",
               getpid(), getppid(), pid);
        sleep(1);
        printf("[子] 結束\n");
        exit(42);
    } else {
        printf("[父] PID: %d, 子 PID: %d, fork 回傳: %d\n",
               getpid(), pid, pid);

        int status;
        waitpid(pid, &status, 0);

        if (WIFEXITED(status))
            printf("[父] 子行程結束，退出碼: %d\n", WEXITSTATUS(status));
    }

    printf("[%d] 父子都會執行這行\n", getpid());
    return 0;
}
