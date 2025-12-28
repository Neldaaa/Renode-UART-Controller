#include <stdint.h>

#define KEY_BASE       0xFF200050
#define UART0_BASE     0xFFC02000

// Con trỏ thanh ghi
volatile int * KEY_ptr = (int *) KEY_BASE;
volatile int * UART0_DATA_ptr = (int *) UART0_BASE;
volatile int * UART0_LSR_ptr  = (int *) (UART0_BASE + 0x14); 

// --- Setup UART ---
volatile int * UART0_LCR_ptr  = (int *) (UART0_BASE + 0x0C); 
volatile int * UART0_DLL_ptr  = (int *) (UART0_BASE + 0x00); 
volatile int * UART0_DLH_ptr  = (int *) (UART0_BASE + 0x04); 

void UART_init() {
    *UART0_LCR_ptr = 0x83; // Bật DLAB
    *UART0_DLL_ptr = 0x36; // 115200 baud
    *UART0_DLH_ptr = 0x00;
    *UART0_LCR_ptr = 0x03; // 8-bit mode
}

void UART_send(char c) {
    while (!((*UART0_LSR_ptr) & 0x20)); // Chờ buffer trống
    *UART0_DATA_ptr = c;
}

int main(void) {
    int key_val;

    UART_init(); 
    UART_send('O'); UART_send('K'); UART_send('\n');

    while (1) {
        // 1. Đọc trực tiếp trạng thái nút nhấn
        key_val = *(KEY_ptr) & 0xF; 

        if (key_val != 0) {
            // 2. Kiểm tra nút nào được nhấn và Gửi UART
            // Logic này lấy từ code thành công của bạn
            
            if (key_val & 0x1)      UART_send('0'); // KEY 0
            else if (key_val & 0x2) UART_send('1'); // KEY 1
            else if (key_val & 0x4) UART_send('2'); // KEY 2
            else if (key_val & 0x8) UART_send('3'); // KEY 3

            // 3. [QUAN TRỌNG] Chờ buông phím (Wait for release)
            // Copy y nguyên từ code LED thành công của bạn
            // Tác dụng: Chống rung tuyệt đối, chỉ gửi 1 ký tự mỗi lần nhấn.
            while (*(KEY_ptr) != 0); 
        }
    }
    return 0;
}