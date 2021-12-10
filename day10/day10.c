#include <stdbool.h>
#include <stdio.h>

#define STACK_SIZE 1024
#define BUFF_SIZE 1024

enum Paren {
  Round = 1,
  Square,
  Curly,
  Pointy,
};

enum Paren STACK[STACK_SIZE];
char BUFF[BUFF_SIZE];

enum Paren to_enum(char p) {
  switch (p) {
  case '(':
  case ')':
    return Round;
  case '[':
  case ']':
    return Square;
  case '{':
  case '}':
    return Curly;
  case '<':
  case '>':
    return Pointy;
  }
}

inline char closing_char(enum Paren p) {
  switch (p) {
  case Round:
    return ')';
  case Square:
    return ']';
  case Curly:
    return '}';
  case Pointy:
    return '>';
  }
}

inline long get_score(enum Paren p) {
  switch (p) {
  case Round:
    return 3;
  case Square:
    return 57;
  case Curly:
    return 1197;
  case Pointy:
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
    if (seeking_newline && c) {
      continue;
    }
    seeking_newline = false;
    switch (c) {
    case EOF:
      printf("score: %ld\n", score);
      return 0;

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
      STACK[++stack_idx] = to_enum(c);
      break;

    case ')':
    case ']':
    case '}':
    case '>':
      if (STACK[stack_idx--] != to_enum(c)) {
        score += get_score(to_enum(c));
        seeking_newline = true;
      }

      break;

    case '\n':
      stack_idx = 0;
      break;
    }
  }
}
