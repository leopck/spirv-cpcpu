import argparse
import struct

CPCPU_CUSTOM_OPCODE_FADD = 0x01
CPCPU_CUSTOM_OPCODE_TYPE_FLOAT = 0x02
CPCPU_CUSTOM_OPCODE_TYPE_FUNCTION = 0x03
CPCPU_CUSTOM_OPCODE_FUNCTION_PARAMETER = 0x04

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

        if opcode == 22:  # OpTypeFloat
            try:
                result_id = instructions[i + 1]
                width = instructions[i + 2]
                print(f"Found OpTypeFlaot (SPIR-V = {opcode}): {result_id} {width}")
                output.append({
                    "opcode": CPCPU_CUSTOM_OPCODE_TYPE_FLOAT,
                    "name": result_id,
                    "width": width,
                })
            except IndexError:
                print("Malformed OpTypeFloat")
        elif opcode == 33:  # OpTypeFunction
            try:
                result_id = instructions[i + 1]
                return_type = instructions[i + 2]
                param_types = []
                n = 3
                while n < word_count:
                    param_types.append(instructions[i + n])
                    n += 1
                print(f"Found OpTypeFunction (SPIR-V = {opcode}; type = {return_type}): {result_id} {word_count} {param_types}")
                output.append({
                    "opcode": CPCPU_CUSTOM_OPCODE_TYPE_FUNCTION,
                    "name": result_id,
                    "return_type": return_type,
                    "param_types": ",".join(map(str, param_types)),
                })
            except IndexError:
                print("Malformed OpTypeFunction")
        if opcode == 55:  # OpFunctionParameter
            try:
                result_type = instructions[i + 1]
                result_id = instructions[i + 2]
                print(f"Found OpFunctionParameter (SPIR-V = {opcode}): {result_type} {result_id}")
                output.append({
                    "opcode": CPCPU_CUSTOM_OPCODE_FUNCTION_PARAMETER,
                    "result_type": result_type,
                    "result_id": result_id,
                })
            except IndexError:
                print("Malformed OpFunctionParameter")
        elif opcode == 129:  # OpFAdd
            try:
                result_type = instructions[i + 1]
                result_id = instructions[i + 2]
                operand1 = instructions[i + 3]
                operand2 = instructions[i + 4]
                print(f"Found OpFAdd (SPIR-V = {opcode}; type = {result_type}): {result_id} <- {operand1} + {operand2}")

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
    with open(output_path, "w") as f:
        for instr in instructions:
            # This is using our custom opcode for add which is 0x01 that we converted from 129 from SPIR-V's standard
            if instr["opcode"] == CPCPU_CUSTOM_OPCODE_FADD:
                print(f"{instr['opcode']=}")
                print(f"{instr['dst']=}")
                print(f"{instr['src1']=}")
                print(f"{instr['src2']=}")
                f.write(f"FADD dst={instr['dst']} src1={instr['src1']} src2={instr['src2']}\n")
            elif instr["opcode"] == CPCPU_CUSTOM_OPCODE_TYPE_FLOAT:
                print(f"{instr['opcode']=}")
                print(f"{instr['name']=}")
                print(f"{instr['width']=}")
                f.write(f"TYPE_FLOAT id={instr['name']} width={instr['width']}\n")
            elif instr["opcode"] == CPCPU_CUSTOM_OPCODE_TYPE_FUNCTION:
                print(f"{instr['opcode']=}")
                print(f"{instr['name']=}")
                print(f"{instr['return_type']=}")
                print(f"{instr['param_types']=}")
                f.write(f"TYPE_FUNCTION id={instr['name']} return_type={instr['return_type']} param_types={instr['param_types']}\n")
            elif instr["opcode"] == CPCPU_CUSTOM_OPCODE_FUNCTION_PARAMETER:
                print(f"{instr['opcode']=}")
                print(f"{instr['result_type']=}")
                print(f"{instr['result_id']=}")
                f.write(f"FUNCTION_PARAMETER id={instr['result_id']} result_type={instr['result_type']}\n")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("spv")
    parser.add_argument("bin")
    return parser.parse_args()


def main():
    args = parse_args()
    instrs = parse_spirv(args.spv)
    emit_cpcpu_binary(instrs, args.bin)
    print("CPCPU binary generated!")


if __name__ == "__main__":
    main()
