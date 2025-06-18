all: disassemble
	python3 spirv-backend-cpcpu.py

compile:
	llvm-as add.ll -o add.bc
	llvm-spirv add.bc -o add.spv
	llvm-as multi_add.ll -o multi_add.bc
	llvm-spirv multi_add.bc -o multi_add.spv

disassemble: compile
	spirv-dis add.spv -o add.dis
	spirv-dis multi_add.spv -o multi_add.dis
