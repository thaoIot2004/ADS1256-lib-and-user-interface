#include <stdio.h>
#include <pigpio.h>
#include <unistd.h>
#include <stdlib.h>
// REMEMBER: CE0 must low when communication
// Check DRDY pin must low to start communication 
// Remember delay follow datasheet to receive data exactly 
// the frequency used in the code is 1Mhz
	#define DRDY 17
	#define PDWN 27
	#define CE0 8
	

	
//CE0 enable & CE0 Disable
int Select_CE0(int status)
{
	if(status == 1 )
	{
		gpioWrite(CE0,1);
		return 1;
	}
	else if (status == 0)
	{
		gpioWrite(CE0,0);
		return 1;
	}
	else 
	{
		return -1;
	}
}

// clean
void gpio_clean()
{
	gpioTerminate();
}
//wait DRDY low
void wait_DRDY()
{
	while(gpioRead(DRDY)==1)
	{
		usleep(1);
	}
}

//Set up function
int Set_up_ads1256()
{

	if (gpioInitialise() < 0)
	{
		//printf("pigpio initialisation failed\n");
		gpioTerminate();
		return -1;
	}
	//printf("pigpio initialised successfully!\n");
	// configure pin out/in
	gpioSetMode(DRDY, PI_INPUT);
	gpioSetMode(PDWN, PI_OUTPUT);
    gpioSetMode(CE0,PI_OUTPUT);
    gpioWrite(PDWN,1);
    gpioWrite(CE0,1);
    // configure SPI
	unsigned spiChan=0; // Main SPI, MISO:9, MOSI:10, SCLK:11, CE0:8, CE1:7
	unsigned baud = 1000000;//1MHz
	unsigned spiFlags = (1<<4)| 1;//1; // take data in rising edge
	// SPI open
	int handle = spiOpen(spiChan,baud,spiFlags);
	if (handle < 0) 
	{
		//printf("Spi open fail");
		gpioTerminate();
		exit(1);
	}
	//printf("Spi open successfully\n");
	return handle;
}




// Example: RREG_func(handle,txbuf,rxbuf,sizeof(txbuf).rxbuff(rxbuf))
// Ouput: number of bytes received
int RREG_func( unsigned handle, char *txbuf, char *rxbuf,unsigned txbuf_size, unsigned rxbuff_size)
{
	
	if (spiXfer(handle,txbuf,NULL,txbuf_size) < 0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	}
	else
	{
		usleep(50);//delay50us f=1MHz
		int result1 = spiXfer(handle,NULL,rxbuf,rxbuff_size);
		if (result1 < 0) 
		{
			perror("ERROR: SPI Receive ");
			return -1;
		}
		else
		{
			return result1;
		}
	}
}
//Example: WREG_func(handle, txbuf,sizeof(txbuf)) 
//Output: number of bytes sent
int WREG_func(unsigned handle, char *txbuf, unsigned txbuf_size)
{
	int result = spiXfer(handle, txbuf, NULL,txbuf_size);
	if (result < 0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	} 
	else
	{
		return result;
	}
}

// 
int RDATA_func(unsigned handle,char *rxbuf)
{
    char RDATA[1]={0x01};

    if (spiXfer(handle, RDATA, NULL, 1) < 0) 
    {
        perror("ERROR: SPI Trans");
        return -1;
    }
    
        usleep(50);// delay50us f=1MHz
        int result = spiXfer(handle,NULL, rxbuf,3);

        if (result < 0) 
        {
            perror("ERROR: SPI Receive fail");
            return -1;
        }
        
     return result;
        
}
int WAKEUP_func(unsigned handle)
{
	char WAKEUP[1] ={0x00};
	if (spiXfer(handle,WAKEUP,NULL,1) <0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	}
	else 
	{
		return 0;
	}
}

// remember data next will delay 24us
int RDATAC_func(unsigned handle)
{
	char RDATAC[1] = {0x03};
	if (spiXfer(handle,RDATAC,NULL,1) <0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	}
	else 
	{
		return 0;
	}
	
}
//Stop RDATAC Use SDATAC
int SDATAC_func( unsigned handle )
{
	char SDATAC[1] = {0x0F};
	if (spiXfer(handle,SDATAC,NULL,1) < 0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	}
	else 
	{
		return 0;
	}
	usleep(50);
}

int SELFCAL_func( unsigned handle)
{
	char SELFCAL[1] = {0xF0};
	if (spiXfer(handle,SELFCAL,NULL,1) <0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	}
	else 
	{
		return 0;
	}
	usleep(50);
}

int SELFOCAL_func( unsigned handle)
{
	char SELFOCAL[1] = {0xF1};
	if (spiXfer(handle,SELFOCAL,NULL,1) <0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	}
	else 
	{
		return 0;
	}
	usleep(50);
}

int SELFGCAL_func( unsigned handle)
{
	char SELFGCAL[1] = {0xF2};
	if (spiXfer(handle,SELFGCAL,NULL,1) <0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	}
	else 
	{
		return 0;
	}
	usleep(50);
}

int SYSOCAL_func( unsigned handle)
{
	char SYSOCAL[1] = {0xF3};
	if (spiXfer(handle,SYSOCAL,NULL,1) <0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	}
	else 
	{
		return 0;
	}
	usleep(50);
}

int SYSGCAL_func( unsigned handle)
{
	char SYSGCAL[1] = {0xF4};
	if (spiXfer(handle,SYSGCAL,NULL,1) <0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	}
	else 
	{
		return 0;
	}
	usleep(50);
}
// ??? link with WAKEUP???
int SYNC_func ( unsigned handle)
{
	char SYNC[1] = {0xFC};
	if (spiXfer(handle,SYNC,NULL,1) <0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	}
	else 
	{
		return 0;
	}
	
}


int STANDBY_func ( unsigned handle)
{
	char STANDBY[1] = {0xFD};
	if (spiXfer(handle,STANDBY,NULL,1) <0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	}
	else 
	{
		return 0;
	}
}

int RESET_func(unsigned handle)
{
	char RESET[1] = {0xFE};
	if (spiXfer(handle,RESET,NULL,1) <0)
	{
		perror("ERROR: SPI Trans");
		return -1;
	}
	else 
	{
		return 0;
	}
}
// aino0-ain7 
int Get_all(unsigned handle, double *results)
{
	
	//data converter

	unsigned long hex_to_decimal_24bit(unsigned char *data)
	{
		unsigned long value = 0;

		value = ((unsigned long)data[0] << 16) |
				((unsigned long)data[1] << 8)  |
				((unsigned long)data[2]);

		return value;
	}

	double convert_to_voltage_unsigned(unsigned long adc_value)
	{
		double vref = 5; // điện áp tham chiếu
		return (double)adc_value * vref / 8388607.0; // 2^23-1
	}
    unsigned char channels[8] = {0x08,0x18,0x28,0x38,0x48,0x58,0x68,0x78};
    unsigned char rxbuf2[3];

    for (int i = 0; i < 8; i++)
    {
        wait_DRDY();
        unsigned char txbuf[3] = {0x50 | 0x01, 0x00, channels[i]}; 
        WREG_func(handle, (char*)txbuf, 3);
        usleep(10);
        SYNC_func(handle);
        usleep(24);
        WAKEUP_func(handle);
        usleep(300);
        wait_DRDY();
        RDATA_func(handle, (char*)rxbuf2);
        unsigned long dmc = hex_to_decimal_24bit(rxbuf2);
        double voltage = convert_to_voltage_unsigned(dmc);
        results[i] = voltage;
    }

    return 0;
}

