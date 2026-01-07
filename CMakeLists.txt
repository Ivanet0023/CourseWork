cmake_minimum_required(VERSION 4.1)
project(Solitaire)

set(CMAKE_CXX_STANDARD 20)

add_library(Solitaire SHARED main.cpp)
set_target_properties(Solitaire PROPERTIES PREFIX "")
target_link_options(Solitaire PRIVATE -static)