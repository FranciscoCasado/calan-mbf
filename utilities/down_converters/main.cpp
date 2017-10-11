#include "mbed.h"

#define WRITE 0
#define READ 1
#define bitread(x,n) (1 & (x>>n))
#define bitmask(n) (~(~0UL<<n))
#define mensaje(rw, a, d) ((rw<<15) | ((a & bitmask(5))<<10) | (d & bitmask(10)))

SPI spi(D11, D12, D13); // mosi, miso, sclk, CS
DigitalOut cs(D10);

// Calculado en excel: https://www.maximintegrated.com/en/app-notes/index.mvp/id/6269
// LO = 5350MHz
// REF = 20 MHz
// R = 1 (divisor de REF, no se puede cambiar?)
// N -> 7 bits (0 a 127)
// F -> 20 bits (0 a 1048575)
const unsigned int N = 126;
const unsigned int F = 262144;
const unsigned int Flow = F & bitmask(10);
const unsigned int Fhigh = (F >> 10) & bitmask(10);

struct Registro{
    unsigned int address;
    unsigned int data;
};

const Registro setLocalAddrs = {0, 0x023};
const Registro standbyMode = {0, 0x026};
const Registro rxMode = {0, 0x02A};
const Registro doutEn = {14,0x362};

const Registro defaultReg[] = {
    {0, 0x022},  {1,0x0ff},  {2,0x1a0},  {3,0x000},  {4,0x31c},  {5,0x000}, 
    {6, 0x3ff},  {7,0x024},  {8,0x000},  {9,0x00f}, {10,0x000}, {11,0x060}, 
    {13,0x000}, {14,0x360}, {15,0x242}, {16,0x380}, {17,0x000}, {18,0x080},
    {19,0x05f}, {20,0x1ea}, {21,0x0bf}, {22,0x1b8}, {23,0x065}, {24,0x24f},
    {25,0x3a8}, {26,0x015}, {27,0x180}, {28,0x063}, {29,0x000}, {30,0x000},
    {31,0x000}, {33,0x000}, {34,0x000}, {35,0x000}, {36,0x380}, {37,0x000},
    {38,0x000}, {39,0x000}, {40,0x1aa}, {41,0x114}, {42,0x354}, {43,0x073},
    {44,0x000}, {45,0x000}, {46,0x000}, {47,0x000}, {48,0x000}, {49,0x000},
    {50,0x000}, {51,0x000}, {52,0x000}, {53,0x000}, {54,0x000}, {55,0x000},
    {56,0x0c4}, {57,0x12b}, {58,0x165}, {59,0x000}, {60,0x004}, {63,0x000}
};

const unsigned int ndReg = sizeof(defaultReg)/sizeof(Registro);

unsigned int obtenerDef(unsigned int address){
    for(int i = 0; i<ndReg; i++){
        if(defaultReg[i].address == address)
            return defaultReg[i].data;
    }
    return ~0UL;
}

void writeReg(Registro reg){
    unsigned int buf = mensaje(WRITE, reg.address, reg.data);
    cs=0;
    spi.write(buf);
    cs=1;
}

void writeReg(unsigned int address, unsigned int data){
    unsigned int buf = mensaje(WRITE, address, data);
    cs=0;
    spi.write(buf);
    cs=1;
}

void readReg(unsigned int address){
    unsigned int buf = mensaje(READ, address, 0);
    cs=0;
    spi.write(buf);
    cs=1;
}

int main() {
    cs=1;
    spi.format(16,0);
    spi.frequency(1000000);
    wait(5);
    for(int i = 0; i < ndReg; i++){
        if(!bitread(defaultReg[i].address,5)){
            writeReg(defaultReg[i]);
            if(bitread(defaultReg[i+1].address,5)){
                writeReg(setLocalAddrs);
            }
        } else {
            writeReg(defaultReg[i]);
        }
    }
    writeReg(standbyMode);
    writeReg(doutEn);
    wait(0.5);
    //writeReg(15, (obtenerDef(15) & ~bitmask(7)) | N);
    //writeReg(16, Fhigh);
    //writeReg(17, Flow);
    readReg(0);
    readReg(2);
    readReg(15);
    readReg(16);
    readReg(17);
    readReg(19);
    writeReg(14,obtenerDef(14));
    wait_us(100);
    writeReg(5,1);
    writeReg(rxMode);
    wait_ms(2);
    writeReg(5,0);
    while(1);
}