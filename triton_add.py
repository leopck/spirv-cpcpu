import triton
import triton.language as tl
import torch

@triton.jit
def add_kernel(X, Y, Z, N):
    pid = tl.program_id(0)
    x = tl.load(X + pid)
    y = tl.load(Y + pid)
    tl.store(Z + pid, x + y)

x = torch.randn(32, dtype=torch.float32)
y = torch.randn(32, dtype=torch.float32)
z = torch.empty_like(x)

# Dump IR
import os
#os.environ["TRITON_INTERPRET"] = "1"
#os.environ["MLIR_ENABLE_DUMP"] = "1"
#os.environ["LLVM_IR_ENABLE_DUMP"] = "1"
os.environ["TRITON_CPU_BACKEND"] = "1"          # Use CPU backend
os.environ["TRITON_ALWAYS_COMPILE"] = "1"       # Force recompilation
os.environ["LLVM_IR_ENABLE_DUMP"] = "1"         # Enable LLVM IR dump
os.environ["TRITON_KERNEL_DUMP"] = "1"          # Dumps IR stages including .ll
os.environ["TRITON_DUMP_DIR"] = "./triton_ir_dump"  # Where to store dumps
add_kernel[(1,)](x, y, z, 32)

