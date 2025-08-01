#!/usr/bin/env python
"""
Eticaret projesini 8001 portunda çalıştırmak için script
"""
import os
import sys
import subprocess

def main():
    """Django sunucusunu 8001 portunda başlat"""
    # Virtual environment'ın aktif olup olmadığını kontrol et
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Virtual environment aktif")
    else:
        print("⚠️  Virtual environment aktif değil. 'source venv/bin/activate' komutunu çalıştırın.")
    
    # Port numarasını settings'den al
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eticaret.settings')
        import django
        from django.conf import settings
        django.setup()
        
        port = getattr(settings, 'DEVELOPMENT_PORT', 8001)
        print(f"🚀 Django sunucusu {port} portunda başlatılıyor...")
        
        # Django sunucusunu başlat
        subprocess.run([sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{port}'])
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        print("🔧 Alternatif olarak manuel başlatma:")
        print("   python manage.py runserver 127.0.0.1:8001")

if __name__ == "__main__":
    main()