#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script quản lý question_ammount và question_answer_start trong quiz_list.json
Sử dụng Ctrl+C để kết thúc
"""

import json
import os
from typing import Dict, List, Any

FILE_PATH = "quiz_list.json"
BACKUP_PATH = "quiz_list.json.bak"


def load_quiz_data() -> Dict[str, Any]:
    """Đọc dữ liệu từ file quiz_list.json"""
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file {FILE_PATH}")
        return {"quiz_ids": {}, "quiz_data": {"question_ammount": [], "question_answer_start": []}}
    except json.JSONDecodeError:
        print(f"❌ File {FILE_PATH} không đúng định dạng JSON")
        return {"quiz_ids": {}, "quiz_data": {"question_ammount": [], "question_answer_start": []}}


def save_quiz_data(data: Dict[str, Any]) -> bool:
    """Lưu dữ liệu vào file quiz_list.json"""
    try:
        # Tạo backup trước khi lưu
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, 'r', encoding='utf-8') as f:
                backup_data = f.read()
            with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
                f.write(backup_data)
        
        # Lưu dữ liệu mới
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Lỗi khi lưu file: {e}")
        return False


def display_current_data(data: Dict[str, Any]):
    """Hiển thị dữ liệu hiện tại"""
    question_ammount = data.get("quiz_data", {}).get("question_ammount", [])
    question_answer_start = data.get("quiz_data", {}).get("question_answer_start", [])
    
    print("\n" + "="*60)
    print("📊 DỮ LIỆU HIỆN TẠI")
    print("="*60)
    print(f"Số lượng question_ammount: {len(question_ammount)}")
    print(f"Số lượng question_answer_start: {len(question_answer_start)}")
    
    if len(question_ammount) <= 20:
        print(f"\nquestion_ammount: {question_ammount}")
    else:
        print(f"\nquestion_ammount (10 đầu): {question_ammount[:10]}")
        print(f"question_ammount (10 cuối): {question_ammount[-10:]}")
    
    if len(question_answer_start) <= 20:
        print(f"\nquestion_answer_start: {question_answer_start}")
    else:
        print(f"\nquestion_answer_start (10 đầu): {question_answer_start[:10]}")
        print(f"question_answer_start (10 cuối): {question_answer_start[-10:]}")
    print("="*60)


def show_menu():
    """Hiển thị menu"""
    print("\n" + "="*60)
    print("📋 MENU QUẢN LÝ QUIZ DATA")
    print("="*60)
    print("1. Xem dữ liệu hiện tại")
    print("2. Thêm/Sửa question_ammount (tự động)")
    print("3. Xóa giá trị trong question_ammount")
    print("4. Thêm/Sửa question_answer_start (tự động)")
    print("5. Xóa giá trị trong question_answer_start")
    print("6. Đặt lại toàn bộ question_ammount")
    print("7. Đặt lại toàn bộ question_answer_start")
    print("8. Lưu và thoát")
    print("\nNhấn Ctrl+C để thoát bất kỳ lúc nào")
    print("="*60)


def add_or_edit_question_ammount(data: Dict[str, Any]):
    """Thêm hoặc sửa giá trị trong question_ammount (tự động xác định)"""
    try:
        question_ammount = data["quiz_data"]["question_ammount"]
        current_length = len(question_ammount)
        
        print(f"\n📊 Số lượng phần tử hiện tại: {current_length}")
        if current_length > 0:
            print(f"   Phạm vi index: 0 - {current_length - 1}")
            print(f"   Index {current_length} trở đi: Thêm mới")
        
        index = int(input("\nNhập index (vị trí): "))
        
        if index < 0:
            print("❌ Index không thể âm")
            return
        
        value = int(input("Nhập giá trị: "))
        
        # Tự động xác định thêm hay sửa
        if index < current_length:
            # Vị trí đã tồn tại -> Sửa
            old_value = question_ammount[index]
            question_ammount[index] = value
            
            if save_quiz_data(data):
                print(f"✏️  Đã SỬA tại index {index}: {old_value} → {value}")
                print("💾 Đã lưu thay đổi")
        else:
            # Vị trí chưa tồn tại -> Thêm
            # Nếu index vượt quá length, tự động mở rộng với giá trị 0
            while len(question_ammount) < index:
                question_ammount.append(0)
            
            question_ammount.append(value)
            
            if save_quiz_data(data):
                print(f"➕ Đã THÊM tại index {index}: {value}")
                if index > current_length:
                    print(f"   (Đã tự động thêm {index - current_length} phần tử 0 ở giữa)")
                print("💾 Đã lưu thay đổi")
                
    except ValueError:
        print("❌ Giá trị không hợp lệ")


def add_or_edit_question_answer_start(data: Dict[str, Any]):
    """Thêm hoặc sửa giá trị trong question_answer_start (tự động xác định)"""
    try:
        question_answer_start = data["quiz_data"]["question_answer_start"]
        current_length = len(question_answer_start)
        
        print(f"\n📊 Số lượng phần tử hiện tại: {current_length}")
        if current_length > 0:
            print(f"   Phạm vi index: 0 - {current_length - 1}")
            print(f"   Index {current_length} trở đi: Thêm mới")
        
        index = int(input("\nNhập index (vị trí): "))
        
        if index < 0:
            print("❌ Index không thể âm")
            return
        
        value = int(input("Nhập giá trị: "))
        
        # Tự động xác định thêm hay sửa
        if index < current_length:
            # Vị trí đã tồn tại -> Sửa
            old_value = question_answer_start[index]
            question_answer_start[index] = value
            
            if save_quiz_data(data):
                print(f"✏️  Đã SỬA tại index {index}: {old_value} → {value}")
                print("💾 Đã lưu thay đổi")
        else:
            # Vị trí chưa tồn tại -> Thêm
            # Nếu index vượt quá length, tự động mở rộng với giá trị 0
            while len(question_answer_start) < index:
                question_answer_start.append(0)
            
            question_answer_start.append(value)
            
            if save_quiz_data(data):
                print(f"➕ Đã THÊM tại index {index}: {value}")
                if index > current_length:
                    print(f"   (Đã tự động thêm {index - current_length} phần tử 0 ở giữa)")
                print("💾 Đã lưu thay đổi")
                
    except ValueError:
        print("❌ Giá trị không hợp lệ")



def delete_question_ammount(data: Dict[str, Any]):
    """Xóa giá trị trong question_ammount"""
    try:
        question_ammount = data["quiz_data"]["question_ammount"]
        print(f"\nSố lượng phần tử: {len(question_ammount)}")
        
        index = int(input("Nhập vị trí cần xóa (0-{}): ".format(len(question_ammount)-1)))
        if 0 <= index < len(question_ammount):
            removed_value = question_ammount.pop(index)
            
            if save_quiz_data(data):
                print(f"✅ Đã xóa giá trị {removed_value} tại vị trí {index}")
                print("💾 Đã lưu thay đổi")
        else:
            print("❌ Vị trí không hợp lệ")
    except ValueError:
        print("❌ Giá trị không hợp lệ")


def delete_question_answer_start(data: Dict[str, Any]):
    """Xóa giá trị trong question_answer_start"""
    try:
        question_answer_start = data["quiz_data"]["question_answer_start"]
        print(f"\nSố lượng phần tử: {len(question_answer_start)}")
        
        index = int(input("Nhập vị trí cần xóa (0-{}): ".format(len(question_answer_start)-1)))
        if 0 <= index < len(question_answer_start):
            removed_value = question_answer_start.pop(index)
            
            if save_quiz_data(data):
                print(f"✅ Đã xóa giá trị {removed_value} tại vị trí {index}")
                print("💾 Đã lưu thay đổi")
        else:
            print("❌ Vị trí không hợp lệ")
    except ValueError:
        print("❌ Giá trị không hợp lệ")



def reset_question_ammount(data: Dict[str, Any]):
    """Đặt lại toàn bộ question_ammount"""
    print("\n⚠️  CẢNH BÁO: Thao tác này sẽ xóa toàn bộ dữ liệu question_ammount hiện tại!")
    confirm = input("Bạn có chắc chắn? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        try:
            values_str = input("\nNhập các giá trị cách nhau bởi dấu phẩy (vd: 4,4,4,2,4): ")
            values = [int(v.strip()) for v in values_str.split(",")]
            data["quiz_data"]["question_ammount"] = values
            
            if save_quiz_data(data):
                print(f"✅ Đã đặt lại question_ammount với {len(values)} giá trị")
                print("💾 Đã lưu thay đổi")
        except ValueError:
            print("❌ Giá trị không hợp lệ")
    else:
        print("❌ Đã hủy thao tác")


def reset_question_answer_start(data: Dict[str, Any]):
    """Đặt lại toàn bộ question_answer_start"""
    print("\n⚠️  CẢNH BÁO: Thao tác này sẽ xóa toàn bộ dữ liệu question_answer_start hiện tại!")
    confirm = input("Bạn có chắc chắn? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        try:
            values_str = input("\nNhập các giá trị cách nhau bởi dấu phẩy (vd: 0,0,0,0): ")
            values = [int(v.strip()) for v in values_str.split(",")]
            data["quiz_data"]["question_answer_start"] = values
            
            if save_quiz_data(data):
                print(f"✅ Đã đặt lại question_answer_start với {len(values)} giá trị")
                print("💾 Đã lưu thay đổi")
        except ValueError:
            print("❌ Giá trị không hợp lệ")
    else:
        print("❌ Đã hủy thao tác")


def main():
    """Hàm chính"""
    print("\n" + "="*60)
    print("🚀 CHƯƠNG TRÌNH QUẢN LÝ QUIZ DATA")
    print("="*60)
    print("Đang tải dữ liệu...")
    
    data = load_quiz_data()
    
    # Đảm bảo cấu trúc dữ liệu đúng
    if "quiz_data" not in data:
        data["quiz_data"] = {}
    if "question_ammount" not in data["quiz_data"]:
        data["quiz_data"]["question_ammount"] = []
    if "question_answer_start" not in data["quiz_data"]:
        data["quiz_data"]["question_answer_start"] = []
    
    print("✅ Đã tải dữ liệu thành công")
    
    try:
        while True:
            show_menu()
            choice = input("\nNhập lựa chọn của bạn: ").strip()
            
            if choice == "1":
                display_current_data(data)
            elif choice == "2":
                add_or_edit_question_ammount(data)
            elif choice == "3":
                delete_question_ammount(data)
            elif choice == "4":
                add_or_edit_question_answer_start(data)
            elif choice == "5":
                delete_question_answer_start(data)
            elif choice == "6":
                reset_question_ammount(data)
            elif choice == "7":
                reset_question_answer_start(data)
            elif choice == "8":
                print("\n💾 Đang lưu và thoát...")
                if save_quiz_data(data):
                    print("✅ Đã lưu thành công!")
                print("👋 Tạm biệt!")
                break
            else:
                print("❌ Lựa chọn không hợp lệ. Vui lòng chọn lại.")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Đã nhận Ctrl+C")
        save = input("Bạn có muốn lưu thay đổi trước khi thoát? (y/n): ").strip().lower()
        if save == 'y':
            if save_quiz_data(data):
                print("✅ Đã lưu thành công!")
        print("👋 Tạm biệt!")


if __name__ == "__main__":
    main()
