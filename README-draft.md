[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Tn7g_Mhz)

# PiPeline - a companion e-ink display to assist artists

`PiPeline` is a lightweight, always-on companion display designed to support artists and technical directors during production workflows. It provides real-time system statistics to help quickly identify compute-heavy bottlenecks, alongside a customizable reference image display. By offering critical information and visual guidance at a glance, `PiPeline` enhances studio efficiency without disrupting the artist's main workspace.

The system is designed with flexibility in mind, allowing new profiles — such as render farm monitors or task-specific dashboards — to be easily added by pipeline engineers as production needs evolve.

> ## Table of Contents:
> - [Features](#features)
> - [Required Hardware](#required-hardware)
> - [Setting up the Pi](#setting-up-the-pi)
> - [Installation](#installation)
> - [Usage](#usage)
> - [Testing](#testing)
> - [Branching and PRs](#branching-and-prs)
> - [References](#references)

## Features

## Required Hardware
In addition to your developer machine (this project is mac-compatible so far), you would need the following:
1. Raspberry Pi Zero 2 W
2. MicroSD Card (Minimum 8GB storage)
3. Raspberry Pi power adapter
4. E-Ink Display
    - Pimoroni Inky pHAT (or compatible Inky series display)
    - Connection: GPIO header (SPI)
5. (optional) Keyboard, Mouse, and Monitor if you prefer to do initial setup without SSH.

\** Both the pi and dev machine must be on the same network.

## Setting up the Pi

Before installing PiPeline, you need to prepare your Raspberry Pi by installing the operating system and enabling remote access.

### Flash Raspberry Pi OS
1. Download and install the [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. Insert your MicroSD card into your computer.
3. In the Imager:
    Choose OS: Raspberry Pi OS (64-bit), or whatever is recommended
    Choose Storage: Select your MicroSD card
4. After clicking `Next`, click `Edit Settings`.
    * Set hostname (e.g., pi)
    * Set username and password
    * Configure Wi-Fi (SSID, password, country)
    * Enable SSH
5. Click Write to flash the SD card.

### Insert and Boot
1. Insert the flashed MicroSD card into the Raspberry Pi.
2. Connect the E-Ink display to the GPIO header.
3. Power on the Pi.

### Connect to the Pi via SSH
After the Pi boots (~1 minute), connect from your computer:
```
ssh pi@pi.local
```
If `pi.local` doesn't work, find the Pi's IP address using your router settings or a tool like `arp -a`.

### (Optional) Set Up SSH Key Authentication
To avoid typing your password every time you connect:
1. Check if you have an SSH key:
```
ls ~/.ssh/id_ed25519.pub
```
2. If you don't have one, generate it:
```
ssh-keygen -t ed25519 -C "your_email@example.com"
```
3. Copy the key to the Pi:
```
ssh-copy-id pi@pi.local
```
After this, you should be able to SSH into your Pi without typing your password each time.

## Installation

<!-- 1. Enable SPI and I2C under "Interface Options" with the command:
```
sudo raspi-config
``` -->

The steps below use installation scripts. If you prefer setting things up manually, see [Manual Setup Instructions](./assets/docs/manual-setup.md).

### On Developer Machine

1. On your Mac, clone the project and run the install script
(To get stats, scripts would have to be run from your Mac)
```
git clone git@github.com:NCCA/pipeline-project-AnuKritiW.git
cd pipeline-project-AnuKritiW
chmod +x install-mac.sh
./install-mac.sh
```

### On the Pi

1. Clone the project and run the install script:
```
git clone git@github.com:NCCA/pipeline-project-AnuKritiW.git
cd pipeline-project-AnuKritiW
chmod +x install-pi.sh
./install-pi.sh
```

2. Reboot the pi
```
sudo reboot
```

## Usage

### On Developer Machine

1. Run the stats script to send stats to the pi
```
cd scripts
chmod +x sendstats.sh
./sendstats.sh
```

This script is a continuously running script that will send CPU usage, GPU usage and Memory usage to the pi every 2 minutes.

### On the Pi

1. On the pi, run the web app
```
cd pipeline-project-AnuKritiW/web_app
python app.py
```

On Safari, visit `http://<ip>:5000`
TODO: (On other browsers, some settings need to be changed to access)

2. Choose the profile you would like to load up on the pi

## Testing

### Run the complete test suite
```
cd pipeline-project-AnuKritiW
source ~/.virtualenvs/pimoroni/bin/activate
pytest tests/
```

### Test coverage
```
cd pipeline-project-AnuKritiW
source ~/.virtualenvs/pimoroni/bin/activate
pytest --cov=web_app tests/
```

### Continuous Integration with GitHub Actions
All unit tests located in the tests/ directory are run automatically on each push and pull request.
<!-- TODO: CI workflow ensures that installation scripts and project dependencies remain valid across updates -->
The workflow file is located at:
```
.github/workflows/tests.yml
```

## Branching and PRs

Feature branches and bug-fix branches were used consistently to ensure the `main` branch remained stable and production-ready.

* **Feature Branches**: Each feature/functionality, such as the initial application build, test suite development, and CI integration, was developed on a separate branch to isolate changes.
* **Pull Requests (PRs)**: All changes were merged into the main branch through well-documented PRs. Each PR included a detailed description of the changes, making it easy to trace the purpose of merge commits.
    * PR history can be found [here](https://github.com/NCCA/pipeline-project-AnuKritiW/pulls?q=is%3Apr+is%3Aclosed)
* **Commit History**: The commit history consists of small, meaningful commits that clearly document the development process. Since this is an assignment submission, features and bug fixes were not squashed before merging to preserve a transparent record of interactions with the repository.

## References

ChatGPT was used for
* Generating initial HTML code templates, which were subsequently modified and adapted to project needs.
* Brainstorming and refining UI wording.
* Understanding Flask concepts more quickly, including:
    * Evaluating Flask, FastAPI, and other backend frameworks to select the most suitable option.
    * Getting design recommendations for abstraction (e.g. Jinja template inheritance)
* Debugging and troubleshooting issues during development.
* All suggestions provided by ChatGPT were critically reviewed and adapted as necessary to ensure correctness and alignment with the project requirements.