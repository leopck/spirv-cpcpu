import struct

CPCPU_CUSTOM_OPCODE_FADD = 0x01

def parse_spirv(file_path):
    with open(file_path, "rb") as f:
        data = f.read()

    words = [int.from_bytes(data[i:i+4], byteorder="little") for i in range(0, len(data), 4)]

    # Skip SPIR-V header
    instructions = words[5:]

    output = []
    i = 0
    while i < len(instructions):
        word = instructions[i]
        word_count = word >> 16
        opcode = word & 0xFFFF

        print(f"Instruction {i}: opcode={opcode}, word_count={word_count}")
        
        if opcode == 129:  # OpFAdd
            try:
                result_type = instructions[i + 1]
                result_id = instructions[i + 2]
                operand1 = instructions[i + 3]
                operand2 = instructions[i + 4]
                print(f"Found OpFAdd (SPIR-V = 129): {operand1} + {operand2} -> {result_id}")

                output.append({
                    "opcode": CPCPU_CUSTOM_OPCODE_FADD,
                    "dst": result_id,
                    "src1": operand1,
                    "src2": operand2
                })
            except IndexError:
                print("Malformed OpFAdd — not enough operands")

        i += word_count if word_count > 0 else 1

    return output


def emit_cpcpu_binary(instructions, output_path):
    for instr in instructions:
        # This is using our custom opcode for add which is 0x01 that we converted from 129 from SPIR-V's standard
        print(f"{instr['opcode']=}")
        print(f"{instr['dst']=}")
        print(f"{instr['src1']=}")
        print(f"{instr['src2']=}")

if __name__ == "__main__":
    instrs = parse_spirv("add.spv")
    emit_cpcpu_binary(instrs, "add.cpcpu.bin")
    print("CPCPU binary generated!")

