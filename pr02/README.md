# Practical Work 2

## Goal

The goal of this practical work is to work with Bash scripts, Python and system calls using strace.

## Environment

- Ubuntu 26.04
- Python 3.14.4
- GCC 15.2.0
- Make 4.4.1
- GDB 17.1
- strace 6.19
- Valgrind 3.26.0
- htop 3.4.1

## Part 1 - report.sh

The script counts ERROR or WARN messages by module.

Run:

./report.sh logs ERROR

Result:

Module       Messages
---------------------
auth         3
payment      2
database     2

The script also supports:

./report.sh logs ERROR --top 2

Result:

Module       Messages
---------------------
auth         3
payment      2

If no arguments are provided, the script shows help and returns code 1.

## Part 2 - hello.py

The Python program reads a file and shows its size.

Run:

python3 hello.py test.txt

Result:

File size: 105 bytes

## Part 3 - strace

The trace was created with:

strace -f -o trace.txt python3 hello.py test.txt

Python made 412 system calls in total.

There were 2 read() calls related directly to reading test.txt.

The first read() call read 105 bytes. The second read() call returned 0, which means the end of the file was reached.
# Practical Work 2

## Goal

The goal of this practical work is to work with Bash scripts, Python and system calls using strace.

## Environment

- Ubuntu 26.04
- Python 3.14.4
- GCC 15.2.0
- Make 4.4.1
- GDB 17.1
- strace 6.19
- Valgrind 3.26.0
- htop 3.4.1

## Part 1 - report.sh

The script counts ERROR or WARN messages by module.

Run:

./report.sh logs ERROR

Result:

Module       Messages
---------------------
auth         3
payment      2
database     2

The script also supports:

./report.sh logs ERROR --top 2

Result:

Module       Messages
---------------------
auth         3
payment      2

If no arguments are provided, the script shows help and returns code 1.

## Part 2 - hello.py

The Python program reads a file and shows its size.

Run:

python3 hello.py test.txt

Result:

File size: 105 bytes

## Part 3 - strace

The trace was created with:

strace -f -o trace.txt python3 hello.py test.txt

Python made 412 system calls in total.

There were 2 read() calls related directly to reading test.txt.

The first read() call read 105 bytes. The second read() call returned 0, which means the end of the file was reached.

Other system calls were related to Python interpreter overhead, such as loading libraries, memory management and initialization.

## Part 4 - cat vs Python

Results:

Program                    System calls
Python                     412
cat                        142

## Conclusion

cat uses fewer system calls because it is a simple program for reading and displaying files.

Python uses more system calls because it must start the interpreter, load libraries, prepare the environment and execute the Python program.
Other system calls were related to Python interpreter overhead, such as loading libraries, memory management and initialization.

## Part 4 - cat vs Python

Results:

Program                    System calls
Python                     412
cat                        142

## Conclusion

cat uses fewer system calls because it is a simple program for reading and displaying files.

Python uses more system calls because it must start the interpreter, load libraries, prepare the environment and execute the Python program.
