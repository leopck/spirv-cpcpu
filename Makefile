compile:
	llvm-as add.ll -o add.bc
	llvm-spirv add.bc -o add.spv
