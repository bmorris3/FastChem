
# to build with cmake
# create a build directory and move into it
# $ mkdir build
# $ cd build
# generate the makefile (to do only ones, if we don't add files or change makefiles)
# don't forget the two points at the end of the command '..'.
# It runs cmake in the 'build' directory
# but with the data from the '..' directory.

cmake_minimum_required (VERSION 3.12 FATAL_ERROR)

OPTION(USE_PYTHON "Compile FastChem's Python Wrapper" OFF)


project(fastchem CXX C)


#some C++/C flags
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_CXX_FLAGS "-Wall -pedantic -MMD")


set(CMAKE_BUILD_TYPE Release)

  
#output directories
set(CMAKE_BINARY_DIR ${CMAKE_SOURCE_DIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_BINARY_DIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR})



#define the source files   
set(SRC_FASTCHEM
  fastchem_src/calc_densities.cpp
  fastchem_src/calc_electron_densities.cpp
  fastchem_src/calc_mean_mol_weight.cpp
  fastchem_src/calc_species_densities.cpp
  fastchem_src/check.cpp
  fastchem_src/fastchem.cpp
  fastchem_src/get.cpp
  fastchem_src/init_add_species.cpp
  fastchem_src/init_read_files.cpp
  fastchem_src/init_solver.cpp
  fastchem_src/init.cpp
  fastchem_src/mass_action_constant.cpp
  fastchem_src/options_read_files.cpp
  fastchem_src/set.cpp
  fastchem_src/solve_fastchem.cpp
  fastchem_src/solver_bisection.cpp
  fastchem_src/solver_coeff.cpp
  fastchem_src/solver_linsol_quadsol.cpp
  fastchem_src/solver_nelder_mead_electron.cpp
  fastchem_src/solver_newtsol.cpp
  fastchem_src/solver.cpp
  fastchem_src/species_struct.cpp)
  

set(SRC_MAIN
  model_src/model_main.cpp)

  
set(SRC_PYTHON_WRAPPER
  python/fastchem_python_wrapper.cpp)

#check for OpenMP
find_package(OpenMP)  


if (USE_PYTHON MATCHES ON)

    include(FetchContent)
    FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11
        GIT_TAG        97976c16fb7652f7faf02d76756666ef87adbe7d
    )

    FetchContent_GetProperties(pybind11)
    if(NOT pybind11_POPULATED)
        FetchContent_Populate(pybind11)
        add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR})
    endif()

  #compilation target for FastChem's Python library
  add_library(fastchem_for_py ${SRC_FASTCHEM})
  
  if (OpenMP_FOUND)
    target_compile_options(fastchem_for_py PRIVATE "${OpenMP_CXX_FLAGS}" PRIVATE "-O3" PRIVATE "-fPIC")
  else()
    target_compile_options(fastchem_for_py PRIVATE "-O3" PRIVATE "-fPIC")
  endif()

  #find the python version
  find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
  
  #compilation target for FastChem's Python wrapper
  pybind11_add_module(pyfastchem ${SRC_PYTHON_WRAPPER})
  
  #find_package(pybind11 REQUIRED)
  
  set_target_properties(pyfastchem PROPERTIES LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/python")
  
  if (OpenMP_FOUND)
    target_link_libraries(pyfastchem PRIVATE OpenMP::OpenMP_CXX)
  endif()
  
  #target_link_libraries(pyfastchem PRIVATE fastchem_for_py OpenMP::OpenMP_CXX pybind11::module)
  target_link_libraries(pyfastchem PRIVATE fastchem_for_py pybind11::module)
endif()



#compilation target for FastChem
add_library(fastchem_lib ${SRC_FASTCHEM})

if (OpenMP_FOUND)
  target_compile_options(fastchem_lib PRIVATE "${OpenMP_CXX_FLAGS}" PRIVATE "-O3")
else()
  target_compile_options(fastchem_lib PRIVATE "-O3")
endif()

#compilation target for FastChem's standalone main
add_executable(fastchem ${SRC_MAIN})


#link files for the final FastChem executable code
if (OpenMP_FOUND)
  target_link_libraries(fastchem PRIVATE fastchem_lib OpenMP::OpenMP_CXX)
endif()

target_link_libraries(fastchem PRIVATE fastchem_lib)
#target_link_libraries(fastchem PRIVATE fastchem_lib OpenMP::OpenMP_CXX)

