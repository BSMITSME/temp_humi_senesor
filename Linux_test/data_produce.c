#include <stdio.h>
#include <stdlib.h>
#include <unistd.h> // 시스템 호출을 위한 헤더파일, read()
#include <string.h>
#include <time.h>
// 프로세스의 상태를 관리하고, 자식 프록세스의 종료를 기다리는 데 사용되는 헤더 파일 중 하나
#include <sys/wait.h> 
#include <MQTTClient.h>

#define MQTT_BROKER_ADDRESS "tcp://localhost:1883"
#define MQTT_CLIENT_ID "temperature_sensor_client"
#define MQTT_TOPIC "test/temphumi"
#define MQTT_TOPIC1 "test/temp"
#define MQTT_TOPIC2 "test/humi"

struct message {
    long msg_type;
    char msg_text[MAX_TEXT];
};

void sendToMQTT(char *topic, const char *value) {
    MQTTClient client;
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    int rc;

    MQTTClient_create(&client, MQTT_BROKER_ADDRESS, MQTT_CLIENT_ID, MQTTCLIENT_PERSISTENCE_NONE, NULL);
    conn_opts.keepAliveInterval = 20;
    conn_opts.cleansession = 1;

    if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS) {
        fprintf(stderr, "Failed to connect to MQTT broker: %d\n", rc);
        exit(EXIT_FAILURE);
    }
    MQTTClient_message pubmsg = MQTTClient_message_initializer;
    pubmsg.payload = (void *)value;
    pubmsg.payloadlen = strlen(value);
    pubmsg.qos = 1;
    pubmsg.retained = 0;

    MQTTClient_publishMessage(client, topic, &pubmsg, NULL);

    MQTTClient_disconnect(client, 10000);
    MQTTClient_destroy(&client);
}



int main() {
    // 시그너 핸들러 설정
    // "SIGCHLD" 시그널(자식 프로세스 종료 시 발생)에 대한 핸들러 함수 signalHandler
    // signal(SIGCHLD, signalHandler);

    //파이프를 생성
    // pipefd[2] : 읽기와 쓰기 모두에 사용
    // pipefd[0] : 파이프의 읽기
    // pipefd[1] : 파이프의 쓰기
    int pipefd[2]; //pipefd 배열에 파일 디스크립터가 저장된다.

    // pid_t : 프로세스 식별자를 나타내기 위한 데이터 타입
    pid_t child_pid; 

    // pipe()함수가 성공적으로 생성되면 0을 반환하고, 실패하면 -1 반환
    if (pipe(pipefd) == -1) { 
        perror("pipe");
        exit(EXIT_FAILURE);
        // 터미널에서 출력되는 모습 : pipe: [Error message]
    }
    // fork() 함수를 호출하여 새로운 프로세스 생성 (부모 프로세스와 거의 동일한 복사본 생성), 별개의 실행경로
    // 자식 프로세스 생성이 실패했을 때 
    if ((child_pid = fork()) == -1) {
        perror("fork"); // perror : print error
        exit(EXIT_FAILURE);
        // 터미널에서 출력되는 모습 : fork: [Error message]
    }
    
    // 자식 프로세스 생성이 성공했을 때  
    if (child_pid == 0) {
        // 자식 프로세스에서 실행되는 코드
        // Close write end of the pipe
        close(pipefd[1]);

        // Read from the pipe
        // char receivedString[100];
        // ssize_t bytes_read;

        // while (1) {
        //     bytes_read = read(pipefd[0], receivedString, sizeof(receivedString));
        //     if (bytes_read == -1){
        //         perror("read");
        //         exit(EXIT_FAILURE);
        //     }
        //     // receivedString[strcspn(receivedString, "\n")] = 0; // 개행 문자 제거
        //     printf("Consumer received: %s\n", receivedString);
        //     fflush(stdout);
            
        // }
        // Read from the pipe
        char receivedString[100];
        while (1) {
            if (read(pipefd[0], receivedString, sizeof(receivedString)) > 0) {
                // Process the received string value
		        receivedString[strcspn(receivedString, "\n")] = 0; // 개행 문자 제거
                printf("Consumer received: %s\n", receivedString);

                char *token = strtok((char *)receivedString, ":");
	       
                // Keep printing tokens while one of the
                // delimiters present in str[].
                int i=0;
                while (token != NULL)
                {
                    strcpy( senval[i], token);
                    printf("%s\n", token);
                    token = strtok(NULL, ":");
                    i++;
                }

                sendToMQTT(topics[i], senval[i]);
            }
        }

        // Close read end of the pipe
        close(pipefd[0]);
    } else {
        // 부모 프로세스에서 실행되는 코드
        // Close read end of the pipe
        close(pipefd[0]);
        // 출력값을 파이프로
        dup2(pipefd[1], STDOUT_FILENO);
        // // Execute the abcExec program, 실패하면 에러 표시 -> execl: [Error message]
        // if (execl("./temperature", "temperature", NULL) == -1) {
        //     perror("execl");
        //     exit(EXIT_FAILURE);
        // }
        srand(time(NULL));

        while (1) {
            int temperature = rand() % 50;
            printf("temperature: %d\n", temperature);
            fflush(stdout);
            sleep(1);
        }

        // Close write end of the pipe
        close(pipefd[1]);
    }

    return 0;
}

