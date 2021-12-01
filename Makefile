all: day1.log

day%.log: day%/*
	make -C $(patsubst %.log,%,$@) | tee $@
