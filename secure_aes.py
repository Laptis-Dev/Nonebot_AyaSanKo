#!/usr/bin/env python3
"""
安全的 AES 加密解密工具
"""

import os
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def get_key():
    """从环境变量获取密钥"""
    key_hex = os.environ.get("AES_KEY")
    if not key_hex:
        raise ValueError("AES_KEY 环境变量未设置")
    if len(key_hex) != 64:
        raise ValueError("AES_KEY 必须是32字节（64个十六进制字符）的密钥")
    return bytes.fromhex(key_hex)


def encrypt_file(input_file, output_file):
    """加密文件"""
    key = get_key()
    cipher = AES.new(key, AES.MODE_CBC)

    with open(input_file, "rb") as f:
        data = f.read()

    encrypted_data = cipher.encrypt(pad(data, AES.block_size))

    with open(output_file, "wb") as f:
        # 写入IV + 加密数据
        f.write(cipher.iv)
        f.write(encrypted_data)

    print(f"✅ 加密完成: {input_file} -> {output_file}")


def decrypt_file(input_file, output_file):
    """解密文件"""
    key = get_key()

    with open(input_file, "rb") as f:
        iv = f.read(16)  # 读取IV
        encrypted_data = f.read()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

    with open(output_file, "wb") as f:
        f.write(decrypted_data)

    print(f"✅ 解密完成: {input_file} -> {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法：")
        print("  python secure_aes.py encrypt <input_file> <output_file>")
        print("  python secure_aes.py decrypt <input_file> <output_file>")
        print("\n环境变量：")
        print("  export AES_KEY=64个十六进制字符的密钥")
        sys.exit(1)

    mode = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    if mode == "encrypt":
        encrypt_file(input_file, output_file)
    elif mode == "decrypt":
        decrypt_file(input_file, output_file)
    else:
        print("错误：模式必须是 'encrypt' 或 'decrypt'")
        sys.exit(1)
