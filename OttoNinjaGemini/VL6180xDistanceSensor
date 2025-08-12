### **Complete Guide: VL6180X Distance Sensor on Raspberry Pi Zero W**

**Objective:** To set up a Raspberry Pi Zero W to read distance data from a VL6180X sensor and prepare the environment for more advanced robotics applications.

**Hardware Required:**

*   Raspberry Pi Zero W
*   MicroSD Card with a fresh installation of Raspberry Pi OS
*   DFRobot Raspberry Pi IO Expansion HAT
*   Youmile VL6180X Distance Sensor (or equivalent)
*   Jumper Wires (Female-to-Female)
*   Power supply for Raspberry Pi

---

### **Step 1: Hardware Assembly**

1.  **Mount HAT:** Carefully place the DFRobot IO Expansion HAT onto the Raspberry Pi Zero W's 40-pin GPIO header. Ensure all pins are aligned correctly and the HAT is seated firmly.
2.  **Locate I2C Port:** On the DFRobot HAT, find one of the 3-pin or 4-pin I2C ports. They are breakouts for the Raspberry Pi's main I2C bus.
3.  **Connect Sensor:** Use jumper wires to connect the VL6180X sensor to the HAT's I2C port.
    *   Sensor `VIN` or `VCC` -> HAT `3.3V` or `VCC` pin
    *   Sensor `GND` -> HAT `GND` pin
    *   Sensor `SCL` -> HAT `SCL` pin
    *   Sensor `SDA` -> HAT `SDA` pin

    **Crucial Check:** Ensure you are using the 3.3V supply from the HAT for the sensor. Double-check that SDA and SCL are not swapped.

---

### **Step 2: Raspberry Pi OS Initial Configuration**

1.  **Boot and Connect:** Power up your Raspberry Pi and connect to it via SSH or open a terminal.

2.  **Update System:** Always start by updating your system's package list and upgrading installed packages.
    ```bash
    sudo apt update
    sudo apt upgrade -y
    ```

3.  **Enable I2C Interface:**
    *   Run the Raspberry Pi configuration tool:
        ```bash
        sudo raspi-config
        ```
    *   Navigate to `Interface Options` -> `I2C`.
    *   Select `<Yes>` to enable the ARM I2C interface.
    *   Select `<Finish>` and reboot if prompted.

4.  **Verify I2C Connection:** Once rebooted, check if the system can see your sensor. The default address for the VL6180X is `0x29`.
    ```bash
    sudo i2cdetect -y 1
    ```
    You should see `29` in the output grid. If not, re-check your wiring from Step 1.

---

### **Step 3: Install System-Level Dependencies**

This step installs essential tools and libraries that your Python project will need, preventing the errors you saw earlier.

1.  **Install Python Build Tools & I2C Library:**
    ```bash
    sudo apt install -y python3-dev python3-venv build-essential python3-smbus i2c-tools
    ```
    *   `python3-dev`, `build-essential`: Needed to compile some Python packages.
    *   `python3-venv`: The tool for creating Python virtual environments.
    *   `python3-smbus`: **This directly solves the `ModuleNotFoundError: No module named 'smbus'` error.**

2.  **Install/Update Rust Compiler:** This is required by modern Python packages like `google-generativeai` and **prevents the `Failed building wheel for pydantic-core` error.**
    *   Run the official `rustup` installer:
        ```bash
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
        ```
    *   When prompted, choose option `1) Proceed with installation (default)`.
    *   After it finishes, configure your current shell with the command it provides:
        ```bash
        source "$HOME/.cargo/env"
        ```
    *   Verify the installation. The version should be 1.67 or newer.
        ```bash
        rustc --version
        ```

---

### **Step 4: Set Up the Python Project Environment**

Using a virtual environment is critical to avoid package conflicts.

1.  **Create a Project Directory:**
    ```bash
    mkdir ~/ninja_robot
    cd ~/ninja_robot
    ```

2.  **Create a Virtual Environment:** We will create it with access to the system-level `smbus` library you just installed.
    ```bash
    python3 -m venv --system-site-packages venv
    ```

3.  **Activate the Environment:** You must do this every time you open a new terminal to work on this project.
    ```bash
    source venv/bin/activate
    ```
    Your terminal prompt will change to show `(venv)`, indicating the environment is active.

---

### **Step 5: Create the Python Code Files**

You will create two files in your `~/ninja_robot` directory.

**File 1: The Sensor Library**

1.  Create the library file using the `nano` text editor:
    ```bash
    nano DFRobot_VL6180X.py
    ```
2.  **Copy and paste the entire code block below** into the `nano` editor.
3.  Save and exit by pressing `Ctrl+X`, then `Y`, then `Enter`.

```python
# -*- coding: utf-8 -*
""" file DFRobot_VL6180X.py
  # DFRobot_VL6180X Class infrastructure, implementation of underlying methods
  @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @licence     The MIT License (MIT)
  @author      [yangfeng]<feng.yang@dfrobot.com> 
  @version  V1.0
  @date  2021-02-09
  @get from https://www.dfrobot.com
  @url https://github.com/DFRobot/DFRobot_VL6180X
"""
import smbus
import time
import RPi.GPIO as GPIO
class DFRobot_VL6180X:
  # IIC ADDR
  VL6180X_IIC_ADDRESS                          = 0x29

  # The sensor register address
  VL6180X_IDENTIFICATION_MODEL_ID             = 0x000
  VL6180X_SYSTEM_MODE_GPIO0                   = 0X010
  VL6180X_SYSTEM_MODE_GPIO1                   = 0X011
  VL6180X_SYSTEM_INTERRUPT_CONFIG_GPIO        = 0x014
  VL6180X_SYSTEM_INTERRUPT_CLEAR              = 0x015
  VL6180X_SYSTEM_FRESH_OUT_OF_RESET           = 0x016
  VL6180X_SYSTEM_GROUPED_PARAMETER_HOLD       = 0x017
  VL6180X_SYSRANGE_START                      = 0x018
  VL6180X_SYSRANGE_THRESH_HIGH                = 0x019
  VL6180X_SYSRANGE_THRESH_LOW                 = 0x01A
  VL6180X_SYSRANGE_INTERMEASUREMENT_PERIOD    = 0x01B
  VL6180X_SYSRANGE_MAX_CONVERGENCE_TIME       = 0x01C
  VL6180X_SYSRANGE_EARLY_CONVERGENCE_ESTIMATE = 0x022
  VL6180X_SYSRANGE_MAX_AMBIENT_LEVEL_MULT     = 0x02C
  VL6180X_SYSRANGE_RANGE_CHECK_ENABLES        = 0x02D
  VL6180X_SYSRANGE_VHV_RECALIBRATE            = 0x02E
  VL6180X_SYSRANGE_VHV_REPEAT_RATE            = 0x031
  VL6180X_SYSALS_START                        = 0x038
  VL6180X_SYSALS_THRESH_HIGH                  = 0x03A
  VL6180X_SYSALS_THRESH_LOW                   = 0x03C
  VL6180X_SYSALS_INTERMEASUREMENT_PERIOD      = 0x03E
  VL6180X_SYSALS_ANALOGUE_GAIN                = 0x03F
  VL6180X_SYSALS_INTEGRATION_PERIOD           = 0x040
  VL6180X_RESULT_RANGE_STATUS                 = 0x04D
  VL6180X_RESULT_ALS_STATUS                   = 0x04E
  VL6180X_RESULT_INTERRUPT_STATUS_GPIO        = 0x04F
  VL6180X_RESULT_ALS_VAL                      = 0x050
  VL6180X_RESULT_RANGE_VAL                    = 0x062
  VL6180X_READOUT_AVERAGING_SAMPLE_PERIOD     = 0x10A
  VL6180X_FIRMWARE_RESULT_SCALER              = 0x120
  VL6180X_I2C_SLAVE_DEVICE_ADDRESS            = 0x212
  VL6180X_INTERLEAVED_MODE_ENABLE             = 0x2A3
  
  # The valid ID of the sensor
  VL6180X_ID                                  = 0xB4
  # 8 gain modes for ambient light
  VL6180X_ALS_GAIN_20                         = 0
  VL6180X_ALS_GAIN_10                         = 1
  VL6180X_ALS_GAIN_5                          = 2
  VL6180X_ALS_GAIN_2_5                        = 3
  VL6180X_ALS_GAIN_1_67                       = 4
  VL6180X_ALS_GAIN_1_25                       = 5
  VL6180X_ALS_GAIN_1                          = 6
  VL6180X_ALS_GAIN_40                         = 7
  
  # The result of the range measurenments
  VL6180X_NO_ERR                              = 0x00
  VL6180X_ALS_OVERFLOW_ERR                    = 0x01
  VL6180X_ALS_UNDERFLOW_ERR                   = 0x02
  VL6180X_NO_ERR                              = 0x00
  VL6180X_EARLY_CONV_ERR                      = 0x06
  VL6180X_MAX_CONV_ERR                        = 0x07
  VL6180X_IGNORE_ERR                          = 0x08
  VL6180X_MAX_S_N_ERR                         = 0x0B
  VL6180X_RAW_Range_UNDERFLOW_ERR             = 0x0C
  VL6180X_RAW_Range_OVERFLOW_ERR              = 0x0D
  VL6180X_Range_UNDERFLOW_ERR                 = 0x0E
  VL6180X_Range_OVERFLOW_ERR                  = 0x0F
  
  # GPIO1 mode selection
  VL6180X_DIS_INTERRUPT                       = 0
  VL6180X_HIGH_INTERRUPT                      = 1
  VL6180X_LOW_INTERRUPT                       = 2

  # als/range interrupt mode selection
  VL6180X_INT_DISABLE                         = 0
  VL6180X_LEVEL_LOW                           = 1
  VL6180X_LEVEL_HIGH                          = 2
  VL6180X_OUT_OF_WINDOW                       = 3
  VL6180X_NEW_SAMPLE_READY                    = 4

  ''' 
    @brief  Module init
    @param  bus  Set to IICBus
    @param  addr  Set to IIC addr

  '''
  def __init__(self,iic_addr =VL6180X_IIC_ADDRESS,bus = 1):
    self.__i2cbus = smbus.SMBus(bus)
    self.__i2c_addr = iic_addr
    self.__gain = 1.0
    self.__atime =100

  ''' 
    @brief  Initialize sensor
    @param  CE  The pin number attached to the CE
    @return   return True succeed ;return False failed.

  '''
  def begin(self):
    try:
        device_id = self.__get_device_id()
    except IOError:
        return False
    if device_id != self.VL6180X_ID:
      return False
    self.__init()
    return True 

  ''' 
    @brief  Configure the default level of the INT pin and enable the GPIO1 interrupt function
    @param  mode  Enable interrupt mode
    @n            VL6180X_DIS_INTERRUPT  disabled interrupt
    @n            VL6180X_DIS_INTERRUPT  GPIO1 interrupt enabled, INT high by default
    @n            VL6180X_LOW_INTERRUPT  GPIO1 interrupt enabled, INT low by default

  '''
  def set_interrupt(self,mode):
    if(mode == self.VL6180X_DIS_INTERRUPT):
      self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSTEM_MODE_GPIO1>>8, [self.VL6180X_SYSTEM_MODE_GPIO1 & 0xFF,0x20])
    elif(mode == self.VL6180X_HIGH_INTERRUPT):
      self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSTEM_MODE_GPIO1>>8, [self.VL6180X_SYSTEM_MODE_GPIO1 & 0xFF,0x10])
    elif(mode == self.VL6180X_LOW_INTERRUPT):
      self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSTEM_MODE_GPIO1>>8, [self.VL6180X_SYSTEM_MODE_GPIO1 & 0xFF,0x30])

  ''' 
    @brief  A single range
    @return   return ranging data ,uint mm

  '''
  def range_poll_measurement(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSRANGE_START>>8, [self.VL6180X_SYSRANGE_START & 0xFF,0x01])
    time.sleep(0.05) # Add a small delay for measurement to complete
    return self.range_get_measurement()

  ''' 
    @brief  Configuration ranging period
    @param  period_ms  Measurement period, in milliseconds

  '''
  def range_set_inter_measurement_period(self,period_ms):
    if(period_ms > 10):
      if(period_ms < 2550):
        period_ms = ( period_ms / 10 ) -1
      else:
        period_ms = 254
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSRANGE_INTERMEASUREMENT_PERIOD>>8, [self.VL6180X_SYSRANGE_INTERMEASUREMENT_PERIOD & 0xFF,int(period_ms)])
  
  ''' 
    @brief  Configure the interrupt mode for ranging
    @param  mode  Enable interrupt mode
    @n              VL6180X_INT_DISABLE                           interrupt disable                   
    @n              VL6180X_LEVEL_LOW                             value < thresh_low                      
    @n              VL6180X_LEVEL_HIGH                            value > thresh_high                      
    @n              VL6180X_OUT_OF_WINDOW                         value < thresh_low OR value > thresh_high
    @n              VL6180X_NEW_SAMPLE_READY                      new sample ready                      

  '''
  def range_config_interrupt(self,mode):
    if(mode > self.VL6180X_NEW_SAMPLE_READY):
      return False
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSTEM_INTERRUPT_CONFIG_GPIO>>8, [self.VL6180X_SYSTEM_INTERRUPT_CONFIG_GPIO & 0xFF])
    value = self.__i2cbus.read_byte(self.__i2c_addr)
    value = value | mode 
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSTEM_INTERRUPT_CONFIG_GPIO>>8, [self.VL6180X_SYSTEM_INTERRUPT_CONFIG_GPIO & 0xFF,value])
  
  ''' 
    @brief  Configure the interrupt mode for the ambient light
    @param  mode  Enable interrupt mode
    @n              VL6180X_INT_DISABLE                           interrupt disable                   
    @n              VL6180X_LEVEL_LOW                             value < thresh_low                      
    @n              VL6180X_LEVEL_HIGH                            value > thresh_high                      
    @n              VL6180X_OUT_OF_WINDOW                         value < thresh_low OR value > thresh_high
    @n              VL6180X_NEW_SAMPLE_READY                      new sample ready                      

  '''
  def als_config_interrupt(self,mode):
    if(mode > self.VL6180X_NEW_SAMPLE_READY):
      return False
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSTEM_INTERRUPT_CONFIG_GPIO>>8, [self.VL6180X_SYSTEM_INTERRUPT_CONFIG_GPIO & 0xFF])
    value = self.__i2cbus.read_byte(self.__i2c_addr)
    value = value | ( mode << 3 ) 
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSTEM_INTERRUPT_CONFIG_GPIO>>8, [self.VL6180X_SYSTEM_INTERRUPT_CONFIG_GPIO & 0xFF,value])

  ''' 
    @brief Enable continuous ranging mode

  '''
  def range_start_continuous_mode(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSRANGE_START>>8, [self.VL6180X_SYSRANGE_START & 0xFF,0x01])
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSALS_START>>8, [self.VL6180X_SYSALS_START & 0xFF,0x01])
    time.sleep(0.3);
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSTEM_INTERRUPT_CLEAR>>8, [self.VL6180X_SYSTEM_INTERRUPT_CLEAR & 0xFF,7])
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSRANGE_START>>8, [self.VL6180X_SYSRANGE_START & 0xFF,0x03])
  
  ''' 
    @brief  Retrieve ranging data
    @return   return ranging data ,uint mm

  '''
  def range_get_measurement(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_RESULT_RANGE_VAL>>8, [self.VL6180X_RESULT_RANGE_VAL & 0xFF])
    value = self.__i2cbus.read_byte(self.__i2c_addr)
    return value

  ''' 
    @brief  Clear ranging interrupt

  '''
  def clear_range_interrupt(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSTEM_INTERRUPT_CLEAR>>8, [self.VL6180X_SYSTEM_INTERRUPT_CLEAR & 0xFF,1])

  ''' 
    @brief  Clear the ambient light interrupt

  '''
  def clear_als_interrupt(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSTEM_INTERRUPT_CLEAR>>8, [self.VL6180X_SYSTEM_INTERRUPT_CLEAR & 0xFF,2])

  ''' 
    @brief Single measurement of ambient light
    @return   return The light intensity,uint lux

  '''
  def als_poll_measurement(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSALS_START>>8, [self.VL6180X_SYSALS_START & 0xFF,0x01])
    return self.als_get_measurement()
  
  ''' 
    @brief  Obtain measured light data
    @return   return The light intensity,uint lux

  '''
  def als_get_measurement(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_RESULT_ALS_VAL>>8, [self.VL6180X_RESULT_ALS_VAL & 0xFF])
    a = self.__i2cbus.read_byte(self.__i2c_addr)
    b = self.__i2cbus.read_byte(self.__i2c_addr)
    value = (a<<8) | b
    result  = ((0.32*100*value)/(self.__gain*self.__atime))
    return result

  ''' 
    @brief  Enable continuous measurement of ambient light intensity mode

  '''
  def als_start_continuous_mode(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSRANGE_START>>8, [self.VL6180X_SYSRANGE_START & 0xFF,0x01])
    time.sleep(1)
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSTEM_INTERRUPT_CLEAR>>8, [self.VL6180X_SYSTEM_INTERRUPT_CLEAR & 0xFF,7])
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSALS_START>>8, [self.VL6180X_SYSALS_START & 0xFF,0x03])

  ''' 
    @brief  Configure the period for measuring light intensity
    @param  period_ms  Measurement period, in milliseconds

  '''
  def als_set_inter_measurement_period(self,period_ms):
    if(period_ms>10):
      if(period_ms<2550):
        period_ms = (period_ms/10) -1
      else:
        period_ms = 254
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSALS_INTERMEASUREMENT_PERIOD>>8, [self.VL6180X_SYSALS_INTERMEASUREMENT_PERIOD & 0xFF,int(period_ms)])
  ''' 
    @brief  turn on interleaved mode

  '''
  def start_interleaved_mode(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSRANGE_START>>8, [self.VL6180X_SYSRANGE_START & 0xFF,0x01])
    time.sleep(1)
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSTEM_INTERRUPT_CLEAR>>8, [self.VL6180X_SYSTEM_INTERRUPT_CLEAR & 0xFF,7])
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSALS_START>>8, [self.VL6180X_SYSALS_START & 0xFF,0x03])
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_INTERLEAVED_MODE_ENABLE>>8, [self.VL6180X_INTERLEAVED_MODE_ENABLE & 0xFF,0x01])

  ''' 
    @brief  Gets the interrupt state of the ranging
    @return   return status
    @n             0                        : No threshold events reported
    @n             VL6180X_LEVEL_LOW        : value < thresh_low
    @n             VL6180X_LEVEL_HIGH       : value > thresh_high
    @n             VL6180X_OUT_OF_WINDOW    : value < thresh_low OR value > thresh_high
    @n             VL6180X_NEW_SAMPLE_READY : new sample ready

  '''
  def range_get_interrupt_status(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_RESULT_INTERRUPT_STATUS_GPIO>>8, [self.VL6180X_RESULT_INTERRUPT_STATUS_GPIO & 0xFF])
    result = self.__i2cbus.read_byte(self.__i2c_addr)
    result = result & 0x07
    return result
  ''' 
    @brief  Gets the interrupt state of the measured light intensity
    @return   return status
    @n             0                        : No threshold events reported
    @n             VL6180X_LEVEL_LOW        : value < thresh_low
    @n             VL6180X_LEVEL_HIGH       : value > thresh_high
    @n             VL6180X_OUT_OF_WINDOW    : value < thresh_low OR value > thresh_high
    @n             VL6180X_NEW_SAMPLE_READY : new sample ready
    
  '''
  def als_get_interrupt_status(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_RESULT_INTERRUPT_STATUS_GPIO>>8, [self.VL6180X_RESULT_INTERRUPT_STATUS_GPIO & 0xFF])
    result = self.__i2cbus.read_byte(self.__i2c_addr)
    result = (result>>3) & 0x07
    return result
  ''' 
    @brief  turn off interleaved mode

  '''
  def __stop_interleave_mode(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSALS_START>>8, [self.VL6180X_SYSALS_START & 0xFF,0x01])
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_INTERLEAVED_MODE_ENABLE>>8, [self.VL6180X_INTERLEAVED_MODE_ENABLE & 0xFF,0x00])

  ''' 
    @brief  Gets validation information for range data
    @return Authentication information
  '''
  def get_range_result(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_RESULT_RANGE_STATUS>>8, [self.VL6180X_RESULT_RANGE_STATUS & 0xFF])
    result = self.__i2cbus.read_byte(self.__i2c_addr)>>4
    return result

  ''' 
    @brief  set IIC addr
    @param  addr  The IIC address to be modified
  '''
  def set_iic_addr(self,addr):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_I2C_SLAVE_DEVICE_ADDRESS>>8, [self.VL6180X_I2C_SLAVE_DEVICE_ADDRESS & 0xFF,addr])
    self.__i2c_addr = addr

  ''' 
    @brief  Initialize the sensor configuration
  '''
  def __init(self):
    self.__write_byte(self.VL6180X_SYSTEM_FRESH_OUT_OF_RESET, 0x01)
    time.sleep(0.1)
    
    # Required sensor settings
    self.__write_byte(0x0207, 0x01)
    self.__write_byte(0x0208, 0x01)
    self.__write_byte(0x0096, 0x00)
    self.__write_byte(0x0097, 0xfd)
    self.__write_byte(0x00e3, 0x00)
    self.__write_byte(0x00e4, 0x04)
    self.__write_byte(0x00e5, 0x02)
    self.__write_byte(0x00e6, 0x01)
    self.__write_byte(0x00e7, 0x03)
    self.__write_byte(0x00f5, 0x02)
    self.__write_byte(0x00d9, 0x05)
    self.__write_byte(0x00db, 0xce)
    self.__write_byte(0x00dc, 0x03)
    self.__write_byte(0x00dd, 0xf8)
    self.__write_byte(0x009f, 0x00)
    self.__write_byte(0x00a3, 0x3c)
    self.__write_byte(0x00b7, 0x00)
    self.__write_byte(0x00bb, 0x3c)
    self.__write_byte(0x00b2, 0x09)
    self.__write_byte(0x00ca, 0x09)
    self.__write_byte(0x0198, 0x01)
    self.__write_byte(0x01b0, 0x17)
    self.__write_byte(0x01ad, 0x00)
    self.__write_byte(0x00ff, 0x05)
    self.__write_byte(0x0100, 0x05)
    self.__write_byte(0x0199, 0x05)
    self.__write_byte(0x01a6, 0x1b)
    self.__write_byte(0x01ac, 0x3e)
    self.__write_byte(0x01a7, 0x1f)
    self.__write_byte(0x0030, 0x00)
    
    # Recommended public register settings
    self.__write_byte(self.VL6180X_SYSTEM_INTERRUPT_CONFIG_GPIO, 0x24) # IRQ on new sample
    self.__write_byte(self.VL6180X_SYSRANGE_MAX_CONVERGENCE_TIME, 0x32) # 50ms
    self.__write_byte(self.VL6180X_SYSRANGE_RANGE_CHECK_ENABLES, 0x10 | 0x01) # EWR, S/N
    self.__write_byte(self.VL6180X_SYSRANGE_EARLY_CONVERGENCE_ESTIMATE, 0x7B)
    self.__write_byte(self.VL6180X_SYSALS_INTEGRATION_PERIOD, 0x64) # 100ms
    self.set_als_gain(self.VL6180X_ALS_GAIN_1)
    self.__write_byte(self.VL6180X_SYSTEM_MODE_GPIO1, 0x10) # Set GPIO1 to Hi-Z
    
    # Set fresh out of reset to 0
    self.__write_byte(self.VL6180X_SYSTEM_FRESH_OUT_OF_RESET, 0x00)

  def __write_byte(self, register, value):
      self.__i2cbus.write_i2c_block_data(self.__i2c_addr, register >> 8, [register & 0xFF, value])
    
  ''' 
    @brief  Set Range Threshold Value
    @param  thresholdL :Lower Threshold
    @param  thresholdH :Upper threshold

  '''
  def set_range_threshold_value(self,threshold_l,threshold_h):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSRANGE_THRESH_LOW>>8, [self.VL6180X_SYSRANGE_THRESH_LOW & 0xFF,threshold_l])
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSRANGE_THRESH_HIGH>>8, [self.VL6180X_SYSRANGE_THRESH_HIGH & 0xFF,threshold_h])

  ''' 
    @brief  Set ALS Threshold Value
    @param  thresholdL :Lower Threshold
    @param  thresholdH :Upper threshold

  '''
  def set_als_threshold_value(self,threshold_l,threshold_h):
    value_l = int((threshold_l * self.__gain)/0.32)
    value_h = int((threshold_h* self.__gain)/0.32)
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSALS_THRESH_LOW>>8, [self.VL6180X_SYSALS_THRESH_LOW & 0xFF,threshold_l>>8,value_l])
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSALS_THRESH_HIGH>>8, [self.VL6180X_SYSALS_THRESH_HIGH & 0xFF,threshold_h>>8,value_h])

  ''' 
    @brief  Set the ALS gain 
    @param  gain  the value of gain(range 0-7)
    @n            20   times gain: VL6180X_ALS_GAIN_20       = 0
    @n            10   times gain: VL6180X_ALS_GAIN_10       = 1
    @n            5    times gain: VL6180X_ALS_GAIN_5        = 2
    @n            2.5  times gain: VL6180X_ALS_GAIN_2_5      = 3
    @n            1.57 times gain: VL6180X_ALS_GAIN_1_67     = 4
    @n            1.27 times gain: VL6180X_ALS_GAIN_1_25     = 5
    @n            1    times gain: VL6180X_ALS_GAIN_1        = 6
    @n            40   times gain: VL6180X_ALS_GAIN_40       = 7
    @return true :Set up the success, false :Setup failed

  '''
  def set_als_gain(self,gain):
    if(gain>7):
      return False
    if(gain == self.VL6180X_ALS_GAIN_20):
      self.__gain = 20
    elif(gain == self.VL6180X_ALS_GAIN_10):
      self.__gain = 10
    elif(gain == self.VL6180X_ALS_GAIN_5):
      self.__gain = 5.0
    elif(gain == self.VL6180X_ALS_GAIN_2_5):
      self.__gain = 2.5
    elif(gain == self.VL6180X_ALS_GAIN_1_67):
      self.__gain = 1.67
    elif(gain == self.VL6180X_ALS_GAIN_1_25):
      self.__gain = 1.25
    elif(gain == self.VL6180X_ALS_GAIN_1):
      self.__gain = 1.0
    elif(gain == self.VL6180X_ALS_GAIN_40):
      self.__gain = 40
    gain =gain | 0x40
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_SYSALS_ANALOGUE_GAIN>>8, [self.VL6180X_SYSALS_ANALOGUE_GAIN & 0xFF,gain])
    return True

  ''' 
    @brief  get the identifier of sensor
    @return Authentication information

  '''
  def __get_device_id(self):
    self.__i2cbus.write_i2c_block_data(self.__i2c_addr,self.VL6180X_IDENTIFICATION_MODEL_ID>>8, [self.VL6180X_IDENTIFICATION_MODEL_ID & 0xFF])
    id = self.__i2cbus.read_byte(self.__i2c_addr)
    return id
```

**File 2: The Main Application**

1.  Create your main application script:
    ```bash
    nano run_distance_sensor.py
    ```
2.  **Copy and paste the entire code block below** into the `nano` editor.
3.  Save and exit by pressing `Ctrl+X`, then `Y`, then `Enter`.

```python
# -*- coding: utf-8 -*
import time
import sys
# Import the VL6180X library you just created
import DFRobot_VL6180X

# --- Configuration ---
# I2C bus, 1 for Raspberry Pi Zero, 2, 3, etc.
I2C_BUS = 1
# Default I2C Address for the VL6180X sensor
SENSOR_ADDRESS = 0x29

print("--- VL6180X Distance Sensor Test ---")
print("Initializing sensor...")

# Create a sensor instance
sensor = DFRobot_VL6180X.DFRobot_VL6180X(iic_addr=SENSOR_ADDRESS, bus=I2C_BUS)

# Initialize the sensor
# The begin() function returns True on success, False on failure.
if not sensor.begin():
    print("Error: Failed to initialize the VL6180X sensor.")
    print("Please check your wiring and run 'sudo i2cdetect -y 1' to verify.")
    sys.exit(1)

print("Sensor initialized successfully.")
print("Starting measurements (press Ctrl+C to exit)...")
print("-" * 40)

try:
    while True:
        # Get a distance measurement in millimeters (mm)
        distance_mm = sensor.range_poll_measurement()

        # The sensor returns 255 on error or if the object is out of range.
        if distance_mm == 255:
            print("Status: Out of range or measurement error")
        else:
            print(f"Distance: {distance_mm} mm")

        # Wait for half a second before the next measurement
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nProgram stopped by user.")
    sys.exit(0)
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")
    sys.exit(1)

```

---

### **Step 6: Install Python Packages and Run**

1.  **Ensure Virtual Environment is Active:** Your prompt should look like `(venv) pi@raspberrypi:~/ninja_robot $`. If not, run `source venv/bin/activate`.

2.  **Install Packages:** Now, install all the Python libraries you need. This may take a while, especially on a Pi Zero.
    ```bash
    pip install --upgrade pip
    pip install RPi.GPIO google-generativeai SpeechRecognition gTTS pygame Flask google-cloud-speech
    ```

3.  **Run the Application:**
    ```bash
    python3 run_distance_sensor.py
    ```

**Expected Output:**

You should see the initialization messages, followed by continuous distance readings:

```
--- VL6180X Distance Sensor Test ---
Initializing sensor...
Sensor initialized successfully.
Starting measurements (press Ctrl+C to exit)...
----------------------------------------
Distance: 45 mm
Distance: 46 mm
Status: Out of range or measurement error
Distance: 112 mm
...
```

You have now successfully set up your distance sensor and a robust development environment for your robot project
