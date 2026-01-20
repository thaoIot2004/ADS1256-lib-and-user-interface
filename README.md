# Đồ án 2: Xây dựng nền tảng đo lường và thu thập dữ liệu trong công nghiệp sử dụng Raspberry Pi

<div align="center">

![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4B-C51A4A?style=for-the-badge&logo=Raspberry-Pi)
![C](https://img.shields.io/badge/C-00599C?style=for-the-badge&logo=c&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Industry 4.0](https://img.shields.io/badge/Industry-4.0-orange?style=for-the-badge)

*Nền tảng IoT cho giám sát và thu thập dữ liệu công nghiệp thời gian thực*

</div>

---

## 📋 Mục lục

- [Giới thiệu](#-giới-thiệu)
- [Tính năng](#-tính-năng)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Liên hệ](#-liên-hệ)

---

## Giới thiệu

Cách mạng Công nghiệp 4.0 đang tạo ra sự chuyển đổi sâu rộng trong lĩnh vực sản xuất công nghiệp thông qua sự hội tụ của các công nghệ số tiên tiến. Sự phát triển của Internet tốc độ cao, các chuẩn kết nối không dây thế hệ mới và khả năng xử lý, lưu trữ dữ liệu lớn đã thúc đẩy quá trình số hóa và tự động hóa toàn diện.

Dự án này xây dựng một **nền tảng đo lường và thu thập dữ liệu công nghiệp** sử dụng Raspberry Pi, cho phép:

- Thu thập dữ liệu thời gian thực từ các cảm biến công nghiệp
- Phân tích thông minh để xây dựng mô hình "bản sao số" (Digital Twin)
- Triển khai các chiến lược tối ưu hóa vận hành và bảo trì dự đoán
- Quản lý hiệu suất thiết bị một cách hiệu quả

### Phạm vi đồ án

Đồ án tập trung vào hai thành phần chính:

1. **Thư viện C cho module ADS1256**: Driver tầng thấp được tối ưu hóa cho Raspberry Pi 4B
2. **Ứng dụng Python**: Giao diện người dùng trực quan để giám sát và thu thập dữ liệu

---

## Tính năng

- **Thư viện C hiệu năng cao** cho module ADC ADS1256
- **Giao diện người dùng thân thiện** được xây dựng bằng Python
- **Thu thập dữ liệu thời gian thực** từ 8 kênh ADC 24-bit
- **Lưu trữ và xuất dữ liệu** sang các định dạng phổ biến (CSV, JSON)
- **Hiển thị đồ thị trực quan** theo thời gian thực
- **Tích hợp SPI** cho giao tiếp tốc độ cao
- **Hỗ trợ đa nền tảng** trên Raspberry Pi OS

## Yêu cầu hệ thống

### Phần cứng

- Raspberry Pi 4 Model B (khuyến nghị 2GB RAM trở lên)
- Module ADS1256 ADC
- Cảm biến công nghiệp tương thích
- Nguồn cấp ổn định 5V

### Phần mềm

- Raspberry Pi OS 
- Python 3.8+
- GCC Compiler
- Thư viện pigpio

##  Liên hệ

**Tác giả:** Phan Thanh Thảo

- Email: thaohocgioi001@gmail.com
- Video demo: https://www.youtube.com/watch?v=3cSE0Y2A1-Q

<div align="center">
</div>
