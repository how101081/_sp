#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

#define NUM_PHILOSOPHERS 5

pthread_mutex_t forks[NUM_PHILOSOPHERS];
pthread_t philosophers[NUM_PHILOSOPHERS];
int meals[NUM_PHILOSOPHERS] = {0};

void *philosopher(void *arg) {
    int id = *(int *)arg;
    int left = id;
    int right = (id + 1) % NUM_PHILOSOPHERS;
    
    for (int i = 0; i < 3; i++) {
        printf("Philosopher %d is thinking\n", id);
        usleep(rand() % 50000);
        
        if (id % 2 == 0) {
            pthread_mutex_lock(&forks[left]);
            printf("Philosopher %d picked up fork %d (left)\n", id, left);
            pthread_mutex_lock(&forks[right]);
            printf("Philosopher %d picked up fork %d (right)\n", id, right);
        } else {
            pthread_mutex_lock(&forks[right]);
            printf("Philosopher %d picked up fork %d (right)\n", id, right);
            pthread_mutex_lock(&forks[left]);
            printf("Philosopher %d picked up fork %d (left)\n", id, left);
        }
        
        printf("Philosopher %d is eating\n", id);
        meals[id]++;
        usleep(rand() % 50000);
        
        printf("Philosopher %d put down forks\n", id);
        pthread_mutex_unlock(&forks[left]);
        pthread_mutex_unlock(&forks[right]);
    }
    
    return NULL;
}

int main() {
    int ids[NUM_PHILOSOPHERS];
    
    printf("=== Dining Philosophers Problem ===\n");
    printf("Number of philosophers: %d\n\n", NUM_PHILOSOPHERS);
    
    srand(time(NULL));
    
    for (int i = 0; i < NUM_PHILOSOPHERS; i++) {
        pthread_mutex_init(&forks[i], NULL);
        ids[i] = i;
    }
    
    for (int i = 0; i < NUM_PHILOSOPHERS; i++)
        pthread_create(&philosophers[i], NULL, philosopher, &ids[i]);
    
    for (int i = 0; i < NUM_PHILOSOPHERS; i++)
        pthread_join(philosophers[i], NULL);
    
    printf("\n=== Results ===\n");
    for (int i = 0; i < NUM_PHILOSOPHERS; i++)
        printf("Philosopher %d ate %d meals\n", i, meals[i]);
    
    for (int i = 0; i < NUM_PHILOSOPHERS; i++)
        pthread_mutex_destroy(&forks[i]);
    
    return 0;
}
