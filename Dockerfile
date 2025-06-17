FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/spirv/bin:/opt/llvm/bin:${PATH}"

# --- Install base dependencies ---
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    cmake \
    ninja-build \
    python3 \
    python3-pip \
    libxml2-dev \
    zlib1g-dev \
    libedit-dev \
    libncurses5-dev \
    libssl-dev \
    ca-certificates \
    curl \
    wget \
    pkg-config \
    clang \
    llvm \
    libgl1-mesa-dev \
    libx11-dev \
    libxcb1-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    libxi-dev

# --- Build LLVM (release version) ---
WORKDIR /opt
RUN git clone --depth=1 https://github.com/llvm/llvm-project.git
WORKDIR /opt/llvm-project
RUN mkdir build && cd build && \
    cmake -G Ninja ../llvm \
    -DCMAKE_BUILD_TYPE=Release \
    -DLLVM_ENABLE_PROJECTS="clang;lld" \
    -DLLVM_TARGETS_TO_BUILD="X86" \
    -DLLVM_ENABLE_ASSERTIONS=ON \
    -DCMAKE_INSTALL_PREFIX=/opt/llvm && \
    ninja && ninja install

# --- Build SPIRV-LLVM-Translator ---
WORKDIR /opt
RUN git clone --depth=1 https://github.com/KhronosGroup/SPIRV-LLVM-Translator.git
WORKDIR /opt/SPIRV-LLVM-Translator
RUN mkdir build && cd build && \
    cmake -G Ninja .. \
    -DLLVM_DIR=/opt/llvm/lib/cmake/llvm \
    -DCMAKE_INSTALL_PREFIX=/opt/spirv && \
    ninja && ninja install

# --- Build SPIRV-Tools ---
WORKDIR /opt
RUN git clone --depth=1 https://github.com/KhronosGroup/SPIRV-Tools.git
WORKDIR /opt/SPIRV-Tools
RUN python3 utils/git-sync-deps && \
    mkdir build && cd build && \
    cmake -G Ninja .. \
    -DCMAKE_INSTALL_PREFIX=/opt/spirv && \
    ninja && ninja install

# --- Ready workspace ---
WORKDIR /workspace
CMD ["/bin/bash"]

