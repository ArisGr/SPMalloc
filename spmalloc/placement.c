// File to to be compiled into a shared library and preloaded to an executable.
// This library is used to perform data placement between Dram and Optane based on
// the data collected from the output.txt file of the placement algorithm in python.
// It begins by reading the output.txt file, and allocates data to a memory type (starting
// with optane) until it allocates all the bytes it reads from the current line. Then the 
// memory type switches until it allocates the number of bytes it reads from the next line.
// This procedure continues until the end of the program.


// compile with : g++ -shared -fPIC -o libplace.so placement.c functions.cpp  -ldl -lmemkind

#ifdef __cplusplus
extern "C" {
#endif


#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <memkind.h>
#include <limits.h>
#include <dlfcn.h>
#include <linux/limits.h>
#include <time.h>
#include <fcntl.h>
#include <string.h>
#include <pthread.h>
#define MAX_ALLOCATIONS 100
struct memkind *pmem_kind=NULL;
int err = 0, initialized = 0, dram, i = 0;
pthread_t timer_thread;
void *timer_threadproc(void *arg);
int done = 0;  
float seconds_elapsed = 0.0;
unsigned long long allocated_objects = 0;
unsigned long long allocated_bytes = 0;
unsigned long long allocations[MAX_ALLOCATIONS];
int switches;
pthread_mutex_t alloc_mutex = PTHREAD_MUTEX_INITIALIZER;

int read_allocations(const char *filename, unsigned long long allocations[], int *switches) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        return -1; 
    }

    // Read the switches value (the number of times we switch between memory types, 1st line in the output.txt file)
    if (fscanf(file, "%d", switches) != 1) {
        fprintf(stderr, "Error reading switches value\n");
        fclose(file);
        return -1; 
    }

    int i = 0; 
    while (i < MAX_ALLOCATIONS) {
        if (fscanf(file, "%llu", &allocations[i]) != 1) {
            if (feof(file)) break; // Stop reading if we reach end of file
            fprintf(stderr, "Error reading allocations[%d]\n", i);
            fclose(file);
            return -1; 
        }
        i++; // Move to the next index
    }

    fclose(file);
    return 0; 
}

__attribute__((constructor)) void init_memkind() {
 
    if (read_allocations("output.txt", allocations, &switches) == -1) {
        fprintf(stderr, "Error reading the file\n");
        return;
    }

    if(switches == 0) dram = 0; // default memory type -> Optane

    else if (allocations[i] == 0) { // if bytes to be allocated on optane = 0 -> switch to dram
        dram = 1;
        i += 1;
    } 
    else dram = 0;                  // else allocate on optane

    err = memkind_create_pmem("/mnt/pmem0", 0, &pmem_kind);   
    if(err){ 
        fprintf(stderr, "Error initializing optane\n");
    }

    if (pthread_create(&timer_thread, NULL, &timer_threadproc, NULL) != 0) {
        fprintf(stderr, "Failed to create timer thread\n");
    }
    done = 0; 
    initialized = 1;

}

__attribute__((destructor)) void del(void) {
    initialized = 0;
    done = 1;  
    pthread_join(timer_thread, NULL);   
}


void *timer_threadproc(void *arg) {
    while (!done) {
        usleep(10);  
        seconds_elapsed += 0.00001; // check allocated bytes every 10 usec
        if(i >= switches) {
            done = 1;
            return NULL;
        }
        else {
            if (allocated_bytes >= allocations[i]  && i % 2 == 0){  // even i -> allocating to optane, change to dram if we allocated all bytes from current line
                pthread_mutex_lock(&alloc_mutex);
                dram = 1;
                fprintf(stderr, "Allocated: %llu bytes on optane (second %f) (objects alive = %llu)\n", allocated_bytes, seconds_elapsed, allocated_objects);
                allocated_bytes = 0;
                i += 1;
                pthread_mutex_unlock(&alloc_mutex);
            }
            else if (allocated_bytes >= allocations[i]  && i % 2 == 1){ // odd i -> allocating to dram, change to optane if we allocated all bytes from current line
                pthread_mutex_lock(&alloc_mutex);
                dram = 0;
                fprintf(stderr, "Allocated: %llu bytes on dram (second %f)  (objects alive = %llu)\n", allocated_bytes, seconds_elapsed, allocated_objects);
                allocated_bytes = 0;
                i += 1;
                pthread_mutex_unlock(&alloc_mutex);
            }
        }
    }
    return NULL;
}

void *malloc(size_t size) 
{
    if(initialized == 0) {
        return memkind_malloc(MEMKIND_DEFAULT, size);
    }
    else{
        pthread_mutex_lock(&alloc_mutex);
        allocated_bytes += size;    // increase allocated bytes
        allocated_objects += 1;
        if(dram == 1){
            return memkind_malloc(MEMKIND_DEFAULT, size);
        }
        else{
            return memkind_malloc(pmem_kind, size);
        }
        pthread_mutex_unlock(&alloc_mutex);
    }
}

void *calloc(size_t num, size_t size) 
{
     if(initialized == 0) {
        return memkind_calloc(MEMKIND_DEFAULT, num, size);
    }
    else{
        pthread_mutex_lock(&alloc_mutex);
        allocated_bytes += num * size; // increase allocated bytes
        allocated_objects += 1;
        if(dram == 1){
            return memkind_calloc(MEMKIND_DEFAULT, num, size);
        }
        else{
            return memkind_calloc(pmem_kind, num, size);
        }
        pthread_mutex_unlock(&alloc_mutex);
        
    }
}

void *realloc(void *ptr, size_t size) 
{
    if(ptr == NULL) return malloc(size);
    
    pthread_mutex_lock(&alloc_mutex);
    if (initialized == 1) {
        allocated_bytes += size; // increase allocated bytes
        allocated_objects += 1;
        
    }
    memkind_t kind = memkind_detect_kind(ptr);
    if(kind == MEMKIND_DEFAULT)  return  memkind_realloc(MEMKIND_DEFAULT,ptr,size);
    else  return memkind_realloc(pmem_kind,ptr,size);
    pthread_mutex_unlock(&alloc_mutex);
}

void free(void *ptr) {
    if (ptr == NULL)
        return;

    pthread_mutex_lock(&alloc_mutex);
    if (initialized == 1) {
        allocated_objects -= 1;
    }
    memkind_t kind = memkind_detect_kind(ptr);      
    if(kind == MEMKIND_DEFAULT)  memkind_free(MEMKIND_DEFAULT,ptr);
    else memkind_free(pmem_kind,ptr);
    pthread_mutex_unlock(&alloc_mutex);
}

#ifdef __cplusplus
}
#endif
