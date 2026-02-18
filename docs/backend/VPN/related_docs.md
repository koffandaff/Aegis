# VPN Technical Resources Guide

This document provides a detailed breakdown of the two primary external resources used to power the Fsociety VPN module.

---

## 🔐 1. Cryptography Library
**Official Docs**: [cryptography.io](https://cryptography.io/)

This library is the cryptographic engine of our backend. We use it to manage a full **Private Key Infrastructure (PKI)** without needing external tools like Easy-RSA.

### How we use it in Fsociety:
In our [pki_manager.py](file:///e:/Fsociety/backend/utils/pki_manager.py), we use several core modules:

*   **`asymmetric.rsa`**: Used to generate 4096-bit keys for the Root CA and 2048-bit keys for clients.
    ```python
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    ```
*   **`x509.CertificateBuilder`**: Used to construct valid certificates with custom metadata (Country: IN, Org: Fsociety).
*   **`hashes.SHA256`**: The hashing algorithm used when signing certificates to ensure they haven't been tampered with.
*   **`serialization`**: This is critical for converting the internal Python key objects into the **PEM format** you see in the final `.ovpn` file.
*   **`asymmetric.dh`**: Generates the Diffie-Hellman parameters (`dh2048.pem`) required for the server to establish a secure key exchange.

---

## 🌐 2. OpenVPN Manual & Community Resources
**Official Site**: [openvpn.net](https://openvpn.net/community-resources/)

While the Cryptography library makes the "keys," the OpenVPN manual defines the "rules" for the connection tunnel.

### How we use it in Fsociety:
We follow the OpenVPN standard for **Inline Configurations**. This allows us to generate a single portable file instead of a folder full of certs.

*   **Tunnel Settings**:
    *   `dev tun`: Creates a routed IP tunnel (standard for internet privacy).
    *   `proto udp`: Used because it's faster than TCP for VPN traffic.
    *   `cipher AES-256-GCM`: We use the modern GCM mode for authenticated encryption, which is faster and more secure than older CBC modes.
    
*   **Inline Tags**:
    Our [VPN_Service.py](file:///e:/Fsociety/backend/service/VPN_Service.py#L191-L209) precisely implements the XML-style tags defined in the manual to embed our generated certificates:
    ```bash
    <ca> [Root Certificate] </ca>
    <cert> [Client Certificate] </cert>
    <key> [Private Key] </key>
    <tls-auth> [Static Key] </tls-auth>
    ```

*   **TLS-Auth**:
    We follow the security best practice of using a static "HMAC" key (`key-direction 1`) to protect the VPN against DoS attacks and port scanning.
