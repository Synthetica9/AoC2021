SHELL=bash -o pipefail

all: day*.log Makefile

day%.log: day%/*
	make -C $(patsubst %.log,%,$@) | tee $@
