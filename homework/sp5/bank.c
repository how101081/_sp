#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define INITIAL_DEPOSIT 1000000
#define NUM_THREADS 8
#define OPS_PER_THREAD 12500

long long balance = INITIAL_DEPOSIT;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void *deposit(void *arg) {
    for (int i = 0; i < OPS_PER_THREAD; i++) {
        pthread_mutex_lock(&mutex);
        balance += 100;
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

void *withdraw(void *arg) {
    for (int i = 0; i < OPS_PER_THREAD; i++) {
        pthread_mutex_lock(&mutex);
        balance -= 100;
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

int main() {
    pthread_t threads[NUM_THREADS];
    
    printf("=== Bank Account Simulation ===\n");
    printf("Initial balance: %lld\n", balance);
    printf("Threads: %d, Operations per thread: %d\n", NUM_THREADS, OPS_PER_THREAD);
    printf("Total operations: %d\n\n", NUM_THREADS * OPS_PER_THREAD);
    
    printf("Running with mutex protection...\n");
    balance = INITIAL_DEPOSIT;
    
    for (int i = 0; i < NUM_THREADS; i++) {
        if (i % 2 == 0)
            pthread_create(&threads[i], NULL, deposit, NULL);
        else
            pthread_create(&threads[i], NULL, withdraw, NULL);
    }
    
    for (int i = 0; i < NUM_THREADS; i++)
        pthread_join(threads[i], NULL);
    
    printf("Final balance: %lld\n", balance);
    printf("Expected: %lld\n", (long long)INITIAL_DEPOSIT);
    
    if (balance == INITIAL_DEPOSIT)
        printf("Result: CORRECT\n");
    else
        printf("Result: INCORRECT (difference: %lld)\n", INITIAL_DEPOSIT - balance);
    
    return 0;
}
