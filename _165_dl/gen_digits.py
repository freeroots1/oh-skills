import os
code = """
#include <stdio.h>
#include <string.h>
#include <openssl/md5.h>

const char *target = "2d9d5942943a1323";

int check(const char *pwd) {
    unsigned char hash[MD5_DIGEST_LENGTH];
    char hex[33];
    MD5((unsigned char*)pwd, strlen(pwd), hash);
    for (int i = 0; i < 16; i++) {
        sprintf(hex + i*2, "%02x", hash[i]);
    }
    hex[32] = 0;
    return strncmp(hex + 8, target, 16) == 0;
}

int main() {
    char pwd[10];
    long count = 0;
    // Try 6-digit numbers
    for (int a = 48; a < 58; a++) {
    for (int b = 48; b < 58; b++) {
    for (int c = 48; c < 58; c++) {
    for (int d = 48; d < 58; d++) {
    for (int e = 48; e < 58; e++) {
    for (int f = 48; f < 58; f++) {
        pwd[0]=a; pwd[1]=b; pwd[2]=c;
        pwd[3]=d; pwd[4]=e; pwd[5]=f;
        pwd[6]=0;
        if (check(pwd)) { printf("FOUND: %s\n", pwd); return 0; }
        count++;
        if (count % 5000000 == 0) fprintf(stderr, "p: %ld\n", count);
    }}}}}
    printf("6-digit done: %ld\n", count);
    // Try 7-digit numbers
    for (int a = 48; a < 58; a++) {
    for (int b = 48; b < 58; b++) {
    for (int c = 48; c < 58; c++) {
    for (int d = 48; d < 58; d++) {
    for (int e = 48; e < 58; e++) {
    for (int f = 48; f < 58; f++) {
    for (int g = 48; g < 58; g++) {
        pwd[0]=a; pwd[1]=b; pwd[2]=c;
        pwd[3]=d; pwd[4]=e; pwd[5]=f;
        pwd[6]=g; pwd[7]=0;
        if (check(pwd)) { printf("FOUND: %s\n", pwd); return 0; }
        count++;
        if (count % 5000000 == 0) fprintf(stderr, "p7: %ld\n", count);
    }}}}}}}
    printf("7-digit done: %ld\n", count);
    return 1;
}
"""
with open("/tmp/crack_digits.c", "w") as f:
    f.write(code)
print("Written OK")
