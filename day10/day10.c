#include <stdbool.h>
#include <stdio.h>

#define STACK_SIZE 1024
#define BUFF_SIZE 1024

char STACK[STACK_SIZE];
char BUFF[BUFF_SIZE];

static inline char matching(char p) {
  switch (p) {
  case '(':
    return ')';
  case '[':
    return ']';
  case '{':
    return '}';
  case '<':
    return '>';

  case ')':
    return '(';
  case ']':
    return '[';
  case '}':
    return '{';
  case '>':
    return '<';
  }
}

static inline long get_score(char c) {
  switch (c) {
  case ')':
    return 3;
  case ']':
    return 57;
  case '}':
    return 1197;
  case '>':
    return 25137;
  }
}

int main(int argc, char **argv) {
  if (argc != 2) {
    printf("Usage: %s <input file>\n", argv[0]);
    return 1;
  }

  FILE *fp = fopen(argv[1], "r");
  if (fp == NULL) {
    printf("Could not open %s\n", argv[1]);
    return 2;
  }

  int i = 0;
  long score = 0;
  bool seeking_newline = false;
  int stack_idx = 0;

  while (true) {
    char c = BUFF[i++];
    if (seeking_newline && c != '\n') {
      continue;
    }
    seeking_newline = false;
    switch (c) {
    case EOF:
    case '\0':
      if (fgets(BUFF, BUFF_SIZE, fp) == NULL) {
        printf("score: %ld\n", score);
        return 0;
      };
      i = 0;
      break;

    case '(':
    case '[':
    case '{':
    case '<':
      STACK[++stack_idx] = matching(c);
      break;

    case ')':
    case ']':
    case '}':
    case '>':
      if (STACK[stack_idx--] != c) {
        score += get_score(c);
        seeking_newline = true;
      }

      break;

    case '\n':
      stack_idx = 0;
      break;
    }
  }
}
