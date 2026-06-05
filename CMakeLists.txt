cmake_minimum_required(VERSION 3.5)
project(ORB_SLAM2_PYTHON_BINDING)

IF(NOT CMAKE_BUILD_TYPE)
  SET(CMAKE_BUILD_TYPE Release)
ENDIF()

MESSAGE("Build type: " ${CMAKE_BUILD_TYPE})

LIST(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake_modules)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}  -Wall  -O3 -march=native ")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall   -O3 -march=native")

# ORB_SLAM2 selects std::chrono::steady_clock when COMPILEDWITHC11 is defined.
add_definitions(-DCOMPILEDWITHC11)

# C++17 is required. These bindings include ORB_SLAM2's System.h, which pulls in
# Pangolin (via Viewer.h); recent Pangolin uses sigslot, which needs >= C++14.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
message(STATUS "Using C++${CMAKE_CXX_STANDARD}.")

# ---------------------------------------------------------------------------
# Path to the ORB_SLAM2 *source* tree.
# `make install` for this fork installs the ORB_SLAM2 headers/library to
# CMAKE_INSTALL_PREFIX (found below via find_package(ORB_SLAM2)), but it does
# NOT install the bundled Thirdparty (DBoW2 / g2o) headers or their .so files.
# Those are still required to compile and link these bindings, so we pull them
# straight from the source tree. Override with -DORB_SLAM2_SOURCE_DIR=... .
# ---------------------------------------------------------------------------
set(ORB_SLAM2_SOURCE_DIR "/tmp/ORB_SLAM2" CACHE PATH "Path to the ORB_SLAM2 source tree (for bundled Thirdparty headers/libs)")
if(NOT EXISTS "${ORB_SLAM2_SOURCE_DIR}/Thirdparty/DBoW2/lib/libDBoW2.so")
  message(FATAL_ERROR "Could not find the ORB_SLAM2 Thirdparty libraries under "
                      "ORB_SLAM2_SOURCE_DIR='${ORB_SLAM2_SOURCE_DIR}'. Point "
                      "-DORB_SLAM2_SOURCE_DIR at the built ORB_SLAM2 source tree.")
endif()

# Python 3 (interpreter + development headers + NumPy headers).
find_package(Python3 COMPONENTS Interpreter Development NumPy REQUIRED)
# Boost.Python must match the Python version (e.g. python312 for Python 3.12).
find_package(Boost 1.45.0 REQUIRED COMPONENTS python${Python3_VERSION_MAJOR}${Python3_VERSION_MINOR})
find_package(OpenCV REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(ORB_SLAM2 REQUIRED)
find_package(Pangolin)

# RPATH fiddling for the library, so that the installed version can find the linked libraries
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

include_directories(
${PROJECT_SOURCE_DIR}/src
${ORB_SLAM2_INCLUDE_DIR}
${ORB_SLAM2_SOURCE_DIR}
${ORB_SLAM2_SOURCE_DIR}/Thirdparty/g2o
${EIGEN3_INCLUDE_DIR}
${Boost_INCLUDE_DIRS}
${Python3_INCLUDE_DIRS}
${Python3_NumPy_INCLUDE_DIRS}
)
if (Pangolin_FOUND)
  include_directories(${Pangolin_INCLUDE_DIRS})
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)

set(TARGET_MODULE_NAME orbslam2)
add_library(${TARGET_MODULE_NAME} SHARED
src/ORBSlamPython.cpp
src/pyboost_cv2_converter.cpp
src/pyboost_cv3_converter.cpp)
# Use old-style DT_RPATH (not DT_RUNPATH): the installed libORB_SLAM2.so has no
# rpath and locates its own libDBoW2.so / libg2o.so dependencies only via the
# loader path. DT_RPATH on this module is searched for those transitive
# dependencies too (DT_RUNPATH would not be), so the module is importable
# without setting LD_LIBRARY_PATH at runtime.
set_target_properties(${TARGET_MODULE_NAME} PROPERTIES
  PREFIX ""
  LINK_FLAGS "-Wl,--disable-new-dtags")

target_link_libraries(${TARGET_MODULE_NAME}
${ORB_SLAM2_LIBRARIES}
${ORB_SLAM2_SOURCE_DIR}/Thirdparty/DBoW2/lib/libDBoW2.so
${ORB_SLAM2_SOURCE_DIR}/Thirdparty/g2o/lib/libg2o.so
${OpenCV_LIBS}
${Boost_LIBRARIES}
${Python3_LIBRARIES}
)
if (Pangolin_FOUND)
  target_link_libraries(${TARGET_MODULE_NAME} ${Pangolin_LIBRARIES})
endif()

# Install into the directory the interpreter actually imports from. This is
# distribution-dependent (Debian/Ubuntu use "dist-packages", most others
# "site-packages"), so ask Python rather than guessing the folder name.
# Override with -DPYTHON_SITE_PACKAGES=... if you want a different location.
if(NOT PYTHON_SITE_PACKAGES)
  execute_process(
    COMMAND "${Python3_EXECUTABLE}" -c "import sysconfig; print(sysconfig.get_path('platlib'))"
    OUTPUT_VARIABLE PYTHON_SITE_PACKAGES
    OUTPUT_STRIP_TRAILING_WHITESPACE)
endif()
message(STATUS "Installing orbslam2 module to: ${PYTHON_SITE_PACKAGES}")
install(TARGETS ${TARGET_MODULE_NAME} DESTINATION "${PYTHON_SITE_PACKAGES}")
# Ship hand-written type stubs next to the compiled module so editors / type
# checkers (Pylance, Pyright, ty) resolve the API. A .pyi adjacent to the .so is
# the standard discovery location for a C-extension's stubs.
install(FILES ${PROJECT_SOURCE_DIR}/stubs/orbslam2.pyi DESTINATION "${PYTHON_SITE_PACKAGES}")
