//ads1256.h
#define ADS1256_H
#include <stdio.h>
#include <pigpio.h>
#include <unistd.h>
#include <stdlib.h>


// Pin definitions
#define DDRY 17
#define PDWN 27
#define CE0 8

// ADS1256 Command Set
#define CMD_WAKEUP   0x00
#define CMD_RDATA    0x01
#define CMD_RDATAC   0x03
#define CMD_SDATAC   0x0F
#define CMD_RREG     0x10
#define CMD_WREG     0x50
#define CMD_SELFCAL  0xF0
#define CMD_SELFOCAL 0xF1
#define CMD_SELFGCAL 0xF2
#define CMD_SYSOCAL  0xF3
#define CMD_SYSGCAL  0xF4
#define CMD_SYNC     0xFC
#define CMD_STANDBY  0xFD
#define CMD_RESET    0xFE

// Register addresses
#define REG_STATUS   0x00
#define REG_MUX      0x01
#define REG_ADCON    0x02
#define REG_DRATE    0x03
#define REG_IO       0x04
#define REG_OFC0     0x05
#define REG_OFC1     0x06
#define REG_OFC2     0x07
#define REG_FSC0     0x08
#define REG_FSC1     0x09
#define REG_FSC2     0x0A

// SPI Configuration
#define SPI_CHANNEL  0
#define SPI_BAUD     1000000  // 1MHz
#define SPI_FLAGS    ((1<<4) | 1)  // Mode 1


int Select_CE0(int status);
int Set_up_ads1256();

int RREG_func( unsigned handle, char *txbuf, char *rxbuf,unsigned txbuf_size, unsigned rxbuff_size);
int WREG_func(unsigned handle, char *txbuf, unsigned txbuf_size);
int RDATA_func(unsigned handle,char *rxbuf);
int WAKEUP_func(unsigned handle);
int RDATAC_func(unsigned handle);
int SDATAC_func( unsigned handle );
int SELFCAL_func( unsigned handle);
int SELFOCAL_func( unsigned handle);
int SELFGCAL_func( unsigned handle);
int SYSOCAL_func( unsigned handle);
int SYSGCAL_func( unsigned handle);
int SYNC_func ( unsigned handle);
int STANDBY_func ( unsigned handle);
int RESET_func(unsigned handle);
void gpio_clean();
void wait_DRDY();
int Get_all(unsigned handle, double *results);
unsigned long hex_to_decimal_24bit(unsigned char *data);
double convert_to_voltage_unsigned(unsigned long adc_value);







