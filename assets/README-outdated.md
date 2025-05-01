[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Tn7g_Mhz)

# Companion e-ink display

## Progress notes

1. Retrieves System stats (CPU, RAM and Disk) from a Mac and updates the display every 2 minutes.
![einkDisplay-progress-2](./assets/demo_images/einkDisplay-progress-2.jpeg)

2. Displays a chosen reference image.
![einkDisplay-image-progress-1](./assets/demo_images/einkDisplay-image-progress-1.jpeg)

3. Wrote a Flask web application. For now it has two profiles -- stats and images
![webApp-progress-1](./assets/demo_images/webApp-HomePage.png)

4. When the web app is first run, the eink display automatically shows a splash screen

![einkDisplay-splashscreen](./assets/demo_images/einkDisplay-splashscreen.jpeg)

5. Stats

More needs to be added here but for now it just as a run/stop toggle

![webApp-statsprofilecard](./assets/demo_images/webApp-StatsProfile.png)

6. Image Display
![webApp-imageprofilecard](./assets/demo_images/webApp-ImageProfile.png)

TODO:

Web-app:
1. Polish UI
2. Issue: when GPIO pins are in use by splashscreen, the UI still shows the stats script as having run though nothing happens on the display
3. see if its possible to set up a name url for the <your-ip>:5000 situation

eink display:
1. Polish UI
2. (wishlist) dynamic UI for profiles so users can select what information they would like displayed from the web app

tests:
1. ~~Add tests for app.py~~ (basic added)
2. Add tests for scripts
3. (wishlist) github actions

Packaging:
1. Check install script

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

### 2. Manually Set Up Wi-Fi (If Needed)

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

### 3. Connect to the Pi

1. After ~1 min, SSH into the Pi:
    ```
    ssh pi@pi.local
    # or use IP from `arp -a` or your router
    ```
    Password: (what you set earlier)

    (if using a phone hotspot, ensure the band is 2.4Ghz)

    to prevent needing to input the pi password each time,
    `ls ~/.ssh/id_rsa.pub` OR `ls ~/.ssh/id_ed25519.pub` (preferred)
    if file exists, copy the key e.g. `ssh-copy-id -i ~/.ssh/id_ed25519.pub pi@pi.local`

    if no file, `ssh-keygen -t ed25519 -C "your_email@example.com"`
    and then copy the key `ssh-copy-id pi@pi.local`

    and then test that no password is needed when `ssh pi@pi.local`


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

## Testing notes

on the pi, `pytest tests/`
to test coverage, `pytest --cov=web_app tests/`

## References

Ak, F., 2025. *InkyPi*. Github. Available from: https://github.com/fatihak/InkyPi [Accessed 10 February 2025].

Pallets, 2024. *Template Designer Documentation*. Available from: https://jinja.palletsprojects.com/en/stable/templates/ [Accessed 21 April 2025].

Pimoroni, 2024. *Getting Started with Inky pHAT*. Available from: https://learn.pimoroni.com/article/getting-started-with-inky-phat#displaying-text-on-inky-phat [Accessed 15 March 2025].

The Robotics Back-End, 2024. *Raspberry Pi – Create a Flask Server*. Available from: https://roboticsbackend.com/raspberry-pi-create-a-flask-server/ [Accessed 16 April 2025].

Ward, R., 2023. *spotipi-eink*. Github. Available from: https://github.com/ryanwa18/spotipi-eink?tab=readme-ov-file [Accessed 10 February 2025].

Zhang, D., 2024. *The E-ink Desk Accessory I've Always Wanted.* [video]. YouTube. Available from: https://www.youtube.com/watch?v=d9forDotXkI&ab_channel=DavidZhang [Accessed 10 February 2025]

ChatGPT was used for
* Generating initial HTML code templates, which were subsequently modified and adapted to project needs.
* Brainstorming and refining UI wording.
* Understanding Flask concepts more quickly, including:
    * Evaluating Flask, FastAPI, and other backend frameworks to select the most suitable option.
    * Getting design recommendations for abstraction (e.g. Jinja template inheritance)
* Debugging and troubleshooting issues during development.
* All suggestions provided by ChatGPT were critically reviewed and adapted as necessary to ensure correctness and alignment with the project requirements.