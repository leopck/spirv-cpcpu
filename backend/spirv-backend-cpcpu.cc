#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <spirv-tools/libspirv.hpp>
#include <vector>

int main(int argc, char *argv[]) {
  if (argc != 2) {
	return -1;
  }

  std::ifstream spirv_file(argv[1], std::ios::binary);
  if (!spirv_file.is_open()) {
	std::cerr << "Error opening " << argv[1] << std::endl;
	return 1;
  }

  const auto spirv_size = std::filesystem::file_size(argv[1]);  

  size_t elem_count = spirv_size / sizeof(uint32_t);
  std::vector<uint32_t> file_data(elem_count);

  spirv_file.read(reinterpret_cast<char *>(file_data.data()), spirv_size);

  if (!spirv_file) {
    std::cerr << "Error reading " << argv[1] << std::endl;
	return 2;
  }

  spirv_file.close();

  return 0;
}
