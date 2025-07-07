all: disassemble
	python3 spirv-backend-cpcpu.py add.spv add.cpcpu.bin
	python3 spirv-backend-cpcpu.py multi_add.spv multi_add.cpcpu.bin
	bazelisk build //backend:spirv-backend-cpcpu

compile:
	llvm-as add.ll -o add.bc
	llvm-spirv add.bc -o add.spv
	llvm-as multi_add.ll -o multi_add.bc
	llvm-spirv multi_add.bc -o multi_add.spv

disassemble: compile
	spirv-dis add.spv -o add.dis
	spirv-dis multi_add.spv -o multi_add.dis
