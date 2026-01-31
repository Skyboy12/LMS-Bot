#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test để kiểm tra extension lấy session_id từ LMS PTIT
"""

import json
import os
import sys

def check_extension_files():
    """Kiểm tra các file cần thiết của extension"""
    required_files = [
        "manifest.json",
        "popup.html", 
        "popup.js",
        "content.js",
        "icon48.png"
    ]
    
    print("🔍 Kiểm tra các file của extension...")
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - OK")
        else:
            print(f"❌ {file} - MISSING")
            if file != "icon48.png":  # Icon có thể không có
                return False
    
    return True

def validate_manifest():
    """Validate file manifest.json"""
    try:
        with open("manifest.json", "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        print("\n📋 Thông tin manifest:")
        print(f"   Tên: {manifest.get('name', 'N/A')}")
        print(f"   Phiên bản: {manifest.get('version', 'N/A')}")
        print(f"   Manifest version: {manifest.get('manifest_version', 'N/A')}")
        
        # Kiểm tra permissions
        permissions = manifest.get('permissions', [])
        host_permissions = manifest.get('host_permissions', [])
        
        print(f"   Permissions: {', '.join(permissions)}")
        print(f"   Host permissions: {', '.join(host_permissions)}")
        
        # Kiểm tra có đúng domain không
        if "https://lms.ptit.edu.vn/*" in host_permissions:
            print("✅ Host permission cho LMS PTIT - OK")
        else:
            print("❌ Thiếu host permission cho LMS PTIT")
            
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi đọc manifest.json: {e}")
        return False

def show_installation_guide():
    """Hiển thị hướng dẫn cài đặt"""
    print("\n📖 HƯỚNG DẪN CÀI ĐẶT EXTENSION:")
    print("="*50)
    print("1. Mở Chrome và truy cập: chrome://extensions/")
    print("2. Bật 'Developer mode' ở góc trên bên phải")
    print("3. Nhấn 'Load unpacked' và chọn thư mục 'extension_session_id'")
    print("4. Extension sẽ xuất hiện với icon trên thanh công cụ")
    print("\n📖 HƯỚNG DẪN SỬ DỤNG:")
    print("="*50)
    print("1. Truy cập https://lms.ptit.edu.vn và đăng nhập")
    print("2. Nhấn vào icon extension")
    print("3. Nhấn 'Lấy Session ID'")
    print("4. Session ID sẽ hiển thị và có thể copy")

def main():
    print("🚀 LMS PTIT Session ID Extension - Kiểm tra")
    print("="*60)
    
    # Kiểm tra các file
    if not check_extension_files():
        print("\n❌ Extension không đầy đủ file!")
        sys.exit(1)
    
    # Validate manifest
    if not validate_manifest():
        print("\n❌ Manifest không hợp lệ!")
        sys.exit(1)
    
    print("\n✅ Extension đã sẵn sàng!")
    
    # Hiển thị hướng dẫn
    show_installation_guide()
    
    print(f"\n📁 Đường dẫn extension: {os.path.abspath('.')}")

if __name__ == "__main__":
    main()