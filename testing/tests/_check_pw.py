import bcrypt, sys

h = b"$2a$11$S/d8puPVByfv8.itTVJTJuHA.lEGj4ZINgLKmCU3S8UrZj1miC/V2"
print(f"hash length: {len(h)}, hash: {h}")

passwords = [
    b"P@ssw0rd", b"Admin@123", b"admin123", b"Admin123!",
    b"Jgsy@2024", b"Jgsy@2025", b"Jgsy@2026",
    b"admin", b"123456", b"password", b"Admin@123456",
    b"Jgsy@123", b"SuperAdmin@123", b"Admin2024!",
]
for p in passwords:
    try:
        if bcrypt.checkpw(p, h):
            print(f"MATCH: {p.decode()}")
            sys.exit(0)
    except Exception as e:
        print(f"Error with {p}: {e}")
        sys.exit(1)
print("No match found in common passwords")
