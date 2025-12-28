# 🎮 MOS Cyber Console (Renode x DE1-SoC)

## Introduction
**MOS Cyber Console** is a hybrid embedded project that integrates a Real-Time Operating System (**MOS RTOS**), Hardware Emulation (**Renode**), and Physical Hardware interaction (**DE1-SoC FPGA Board**). 

The system features a centralized Python Controller that bridges communication between the simulated STM32F4 environment and the physical world, allowing users to play interactive games using either a PC keyboard or the physical keys on the DE1-SoC board.

## 🚀 Features
* **Hybrid Architecture:** Simulates STM32F4 on Renode while communicating with real-world FPGA hardware via UART.
* **MOS RTOS Integration:** Uses MOS Shell tasks to handle command dispatching.
* **Dual Control Modes:** * **Simulation Mode:** Control via Keyboard (Arrow Keys / WASD).
    * **Hardware Mode:** Control via DE1-SoC Push Buttons (Key 0-3).
* **Game Library:**
    1.  🐍 **Cyber Snake:** A neon-styled classic snake game with bi-directional feedback (LED effects).
    2.  🎹 **Cyber Beat:** A rhythm game requiring precise timing.

## 📂 Project Structure
* `app/` & `core/`: Source code for MOS RTOS (C++).
* `emulation/`: Renode scripts for simulating the multi-machine environment.
* `de1_soc_firmware/`: C code and makefile for the DE1-SoC board interface.
* `controller.py`: The master Python launcher that manages UART connections and game processes.

## 🛠️ Prerequisites
1.  **Renode:** For STM32F4 emulation.
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