#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <semaphore.h>
#include <time.h>

#define BUFFER_SIZE 5
#define NUM_ITEMS 20

int buffer[BUFFER_SIZE];
int in = 0, out = 0;
int count = 0;

pthread_mutex_t mutex;
sem_t empty;
sem_t full;

void *producer(void *arg) {
    int id = *(int *)arg;
    
    for (int i = 0; i < NUM_ITEMS; i++) {
        int item = i * 100 + id;
        
        sem_wait(&empty);
        pthread_mutex_lock(&mutex);
        
        buffer[in] = item;
        printf("Producer %d: produced item %d at buffer[%d]\n", id, item, in);
        in = (in + 1) % BUFFER_SIZE;
        count++;
        
        pthread_mutex_unlock(&mutex);
        sem_post(&full);
        
        usleep(rand() % 10000);
    }
    
    return NULL;
}

void *consumer(void *arg) {
    int id = *(int *)arg;
    
    for (int i = 0; i < NUM_ITEMS; i++) {
        sem_wait(&full);
        pthread_mutex_lock(&mutex);
        
        int item = buffer[out];
        printf("Consumer %d: consumed item %d from buffer[%d]\n", id, item, out);
        buffer[out] = -1;
        out = (out + 1) % BUFFER_SIZE;
        count--;
        
        pthread_mutex_unlock(&mutex);
        sem_post(&empty);
        
        usleep(rand() % 10000);
    }
    
    return NULL;
}

int main() {
    pthread_t prod, cons;
    int prod_id = 1, cons_id = 1;
    
    pthread_mutex_init(&mutex, NULL);
    sem_init(&empty, 0, BUFFER_SIZE);
    sem_init(&full, 0, 0);
    
    printf("=== Producer-Consumer Problem ===\n");
    printf("Buffer size: %d, Items to produce/consume: %d\n\n", BUFFER_SIZE, NUM_ITEMS);
    
    srand(time(NULL));
    
    pthread_create(&prod, NULL, producer, &prod_id);
    pthread_create(&cons, NULL, consumer, &cons_id);
    
    pthread_join(prod, NULL);
    pthread_join(cons, NULL);
    
    printf("\nAll items produced and consumed.\n");
    printf("Final buffer count: %d (expected: 0)\n", count);
    
    pthread_mutex_destroy(&mutex);
    sem_destroy(&empty);
    sem_destroy(&full);
    
    return 0;
}
