[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Tn7g_Mhz)

# Companion e-ink display

This project aims to develop an E-Ink companion display that provides real-time, off-screen insights for users of Houdini or RenderMan. 

For Houdini, the display will show critical background information, such as memory usage, cache sizes, disk I/O, and live error tracking, helping users monitor system performance and identify bottlenecks while working. 

For RenderMan, the display will focus on render-specific metrics, including memory usage, disk I/O, and render performance details like texture memory usage and system bottlenecks. 

The device will offer a clean, always-on display that enhances workflow efficiency by surfacing important data not readily visible in the primary UI.

Here is a mockup:

![einkDisplay-mockup](./assets/einkDisplay-mockup.png)

## Set up notes

(Not polished yet; just adding it as I go along for now)


### 1. Flash Raspberry Pi OS and Configure

1. Download and open **Raspberry Pi Imager**.
2. Choose:
   - **OS**: Raspberry Pi OS (32-bit)
   - **Storage**: Select your SD card
3. Click the ⚙️ **Advanced Options**:
   - ✔️ Set hostname: `pi`
   - ✔️ Enable SSH (use password authentication)
   - ✔️ Username: `pi`
   - ✔️ Password: (set a password)
   - ✔️ Configure Wi-Fi:
     - SSID: (Type in the name of your wifi)
     - Password: (your Wi-Fi password)
     - Country: (your country)
4. Click **Write** to flash the SD card.

## 2. Manually Set Up Wi-Fi (If Needed)

If Wi-Fi does not connect on boot, do this:

1. Insert SD card into your Mac.
2. Open the **boot** partition (typically `/Volumes/bootfs` on macOS).
3. Create a file named `wpa_supplicant.conf`. For example:

   ```conf
   country=GB
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1

   network={
       ssid="wifi_name"
       psk="your_wifi_password"
       key_mgmt=WPA-PSK
   }
   ```
4. Also create an empty file named `ssh` to enable SSH:
    ```
    touch /Volumes/bootfs/ssh
    ```
5. Eject the SD card and insert it into the Pi. Power it on.

## 3. Connect to the Pi

1. After ~1 min, SSH into the Pi:
    ```
    ssh pi@pi.local
    # or use IP from `arp -a` or your router
    ```
    Password: (what you set earlier)

### 4. Installing the Pimoroni Software (if needed)
More [here](https://learn.pimoroni.com/article/getting-started-with-inky-phat)

1. It's a great idea to start with a fresh install of Raspberry Pi OS or, if not, then make sure that you run `sudo apt update` and `sudo apt upgrade` in the terminal to get everything up-to-date.
2. Run the following commands in the terminal:
    ```
    git clone https://github.com/pimoroni/inky
    cd inky
    ./install.sh # prompts to create a venv
    ```
3. Once that's all done, type `sudo reboot` to reboot your Pi and apply the changes to the Pi's interfaces.
4. To enter the venev,
    ```
    source ~/.virtualenvs/pimoroni/bin/activate
    ```

### 5. Clone the Project Repo
1. Once logged in:
    ```
    git clone git@github.com:NCCA/pipeline-project-AnuKritiW.git # May need to configure ssh cloning on github
    cd pipeline-project-AnuKritiW/scripts
    chmod +x sendstats.sh # makes an executable
    ```

### 6. Run the Script
1. To test:
    ```
    ./sendstats.sh
    ```
    This should execute `stats.py`