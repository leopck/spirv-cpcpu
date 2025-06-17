; ModuleID = 'add'
target triple = "spir-unknown-unknown"
target datalayout = "e-i64:64-v16:16-v24:32-v32:32-n8:16:32:64"

define float @add(float %a, float %b) {
  %1 = fadd float %a, %b
  ret float %1
}

