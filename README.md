# 🎮 MOS Cyber Console (Renode x DE1-SoC)

## 🌟 Acknowledgement & Credits
This project is an extended implementation based on the **MOS-Renode** framework. We strictly attribute the core operating system and simulation environment to the original author.

> **Original Source Code:** [https://github.com/Eplankton/mos-renode](https://github.com/Eplankton/mos-renode)  
> **Author:** Eplankton

---

## Introduction
**MOS Cyber Console** is a hybrid embedded project that integrates a Real-Time Operating System (**MOS RTOS**), Hardware Emulation (**Renode**), and Physical Hardware interaction (**DE1-SoC FPGA Board**). 

The system features a centralized Python Controller that bridges communication between the simulated STM32F4 environment and the physical world, allowing users to play interactive games using either a PC keyboard or the physical keys on the DE1-SoC board.

## 📸 Project Demo & Gallery

### 🐍 1. Cyber Snake Game
A neon-styled classic snake game running with bi-directional feedback.
![Cyber Snake Demo](pic/snake_game.png)

### 🎹 2. Cyber Beat Revolution
A rhythm game requiring precise timing, featuring visual effects and combo systems.
![Cyber Beat Demo](pic/beat_game.png)

### 🔌 3. Hardware Setup (DE1-SoC)
The physical interface using Altera DE1-SoC board, connected via UART to control the games.
![Hardware Setup](pic/hardware.jpg)

---

## 🚀 Features
* **Hybrid Architecture:** Seamless communication between simulated STM32F4 (Renode) and real-world FPGA hardware via UART.
* **MOS RTOS Integration:** Utilizes MOS Shell tasks for efficient command dispatching and multitasking.
* **Dual Control Modes:**
    * **Simulation Mode:** Control games via PC Keyboard (WASD / Arrow Keys).
    * **Hardware Mode:** Control games via DE1-SoC Push Buttons (KEY0 - KEY3).
* **Game Library:** Includes *Cyber Snake* and *Cyber Beat* with high-quality visual effects (particles, screen shake, neon glow).

---
    
## 📂 Project Structure

```text
Renode-UART-Controller/
├── app/ & core/          # Source code for MOS RTOS (C++)
├── emulation/            # Renode scripts (.resc) for STM32F4 simulation
├── de1_soc_firmware/     # C firmware and Makefile for DE1-SoC board
├── pic/                  # Images and Demo screenshots
├── controller.py         # Master Python Controller (UART Bridge & Game Launcher)
├── cyber_snake_game.py   # Snake Game Module
├── cyber_beat_game.py    # Rhythm Game Module
└── mos-renode.code-workspace # VS Code Workspace configuration

---

## 🛠️ Prerequisites
1.  **Renode:**Required for emulating the STM32F4 chip.
2.  **Python 3.x:** With `pygame` and `pyserial` libraries installed.
    ```bash
    pip install pygame pyserial
    ```
3.  **DE1-SoC Board:** (Optional) Connected via USB-Serial (e.g., COM5).
4.  **ARM GCC Toolchain:** To build the MOS firmware.

## ⚡ How to Run

### Step 1: Start the OS Emulation (Renode)
Open a terminal and execute the run script:
```bash
renode emulation\debug_config.resc
```
In the Renode Monitor window, type start to boot the OS.

### Step 2: Launch the Master Controller
Open a separate terminal on your host machine:
```bash
python controller.py
```
The controller will automatically attempt to connect to:
    * **Renode UART (localhost:3333)
    * **DE1-SoC Hardware (COM port)

### Step 3: Select a Game
Once connected, follow the on-screen instructions or use the DE1-SoC keys:
    * **Press Key 0 (or 'S') to launch Cyber Snake.
    * **Press Key 1 (or 'B') to launch Cyber Beat.

## 🔌 Hardware Setup (DE1-SoC)
Ensure the board is connected via USB. The de1_soc_firmware should be compiled and loaded onto the board to map the physical keys (KEY0-KEY3) to UART character outputs ('0'-'3').

## 📜 License
This project is based on MOS-Renode and modified for educational purposes.