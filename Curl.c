#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(int argc, char *argv[]) {
    // Parse command-line arguments
    char url[] = "http://eu.httpbin.org/get";
    int port = 80;
    int verbose = 0;
    char method[10] = "GET";
    char data[100] = "";
    char content_type[100] = "";

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-v") == 0) {
            verbose = 1;
        } else if (strcmp(argv[i], "-X") == 0) {
            if (i + 1 < argc) {
                strcpy(method, argv[i + 1]);
                i++;
            } else {
                printf("Missing method argument after -X\n");
                return 1;
            }
        } else if (strcmp(argv[i], "-d") == 0) {
            if (i + 1 < argc) {
                strcpy(data, argv[i + 1]);
                i++;
            } else {
                printf("Missing data argument after -d\n");
                return 1;
            }
        } else if (strcmp(argv[i], "-H") == 0) {
            if (i + 1 < argc) {
                strcpy(content_type, argv[i + 1]);
                i++;
            } else {
                printf("Missing content-type argument after -H\n");
                return 1;
            }
        } else {
            strcpy(url, argv[i]);
        }
    }

    // Extract host and path from URL
    char protocol[10], host[100], path[100];
    sscanf(url, "%[^:]://%[^/]/%s", protocol, host, path);

    // Create socket
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return 1;
    }

    // Connect to server
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(host);
    server_addr.sin_port = htons(port);

    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("connect");
        return 1;
    }

    // Construct request string
    char request_string[1000];
    sprintf(request_string, "%s %s HTTP/1.1\r\nAccept: */*\r\nHost: %s\r\n", method, path, host);

    if (strlen(data) > 0) {
        sprintf
        (
            request_string + strlen(request_string),
            "Content-Length: %ld\r\nContent-Type: %s\r\n\r\n%s",
            strlen(data),
            content_type,
            data
        );
    } else {
        strcat(request_string, "\r\n");
    }