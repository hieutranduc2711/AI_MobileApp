# Product Context: GorillaDesk Mobile

## 1. Domain Overview
GorillaDesk là hệ thống Field Service Management (FSM) chuyên dụng cho các ngành:
- Pest Control (Kiểm soát côn trùng)
- Lawn Care (Chăm sóc cảnh quan / làm vườn)
- Pool Service (Vệ sinh hồ bơi)
- Commercial Cleaning

## 2. Tech Stack & Architecture
- **Mobile Platform:** React Native (`com.gorilladesk.rn`), Redux State Management.
- **Local Storage:** SQLite / WatermelonDB cho cơ chế Offline-First.
- **Hardware Integration:** Stripe POS Reader, Tap to Pay Android, Camera Scanner, GPS Geolocation.
- **Sync Architecture:** Mọi thao tác ngoài hiện trường (Job status, Photos, Signatures, Invoices) được ghi nhận cục bộ, sau đó đồng bộ ngầm khi có mạng.
