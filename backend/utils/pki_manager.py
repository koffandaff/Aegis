"""
PKI Manager - Real Certificate Authority for Fsociety VPN

This module provides a complete PKI infrastructure for generating valid
X.509 certificates that work with OpenVPN.

Uses the `cryptography` library to:
- Generate RSA key pairs
- Create and manage a Certificate Authority
- Sign client certificates
- Generate TLS-Auth keys
- Create Diffie-Hellman parameters
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Tuple, Optional

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, dh
from cryptography.hazmat.backends import default_backend


class PKIManager:
    """
    Manages the PKI infrastructure for OpenVPN certificate generation.
    """
    
    def __init__(self, pki_dir: str = None):
        """
        Initialize PKI Manager.
        
        Args:
            pki_dir: Directory to store PKI files. Defaults to backend/data/pki/
        """
        if pki_dir is None:
            # Default to backend/data/pki/
            base_dir = Path(__file__).parent.parent / "data" / "pki"
        else:
            base_dir = Path(pki_dir)
        
        self.pki_dir = base_dir
        self.ca_cert_path = base_dir / "ca.crt"
        self.ca_key_path = base_dir / "ca.key"
        self.ta_key_path = base_dir / "ta.key"
        self.dh_path = base_dir / "dh.pem"
        self.server_cert_path = base_dir / "server.crt"
        self.server_key_path = base_dir / "server.key"
        
        # Ensure PKI directory exists
        self.pki_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize CA if not exists
        if not self.ca_cert_path.exists():
            self._initialize_pki()
    
    def _initialize_pki(self):
        """Initialize the complete PKI infrastructure."""
        print("[PKI] Initializing Certificate Authority...")
        
        # Generate CA
        self._generate_ca()
        
        # Generate Server Certificate
        self._generate_server_cert()
        
        # Generate TLS-Auth Key
        self._generate_ta_key()
        
        # Generate DH Parameters (this can be slow)
        self._generate_dh_params()
        
        print("[PKI] PKI initialization complete!")
    
    def _generate_ca(self):
        """Generate the Root Certificate Authority."""
        # Generate CA private key
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        
        # CA Subject
        ca_subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Maharashtra"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Mumbai"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Fsociety Security"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "VPN Services"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Fsociety Root CA"),
        ])
        
        # Build CA certificate
        ca_cert = (
            x509.CertificateBuilder()
            .subject_name(ca_subject)
            .issuer_name(ca_subject)  # Self-signed
            .public_key(ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))  # 10 years
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=True,
                    crl_sign=True,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
                critical=False
            )
            .sign(ca_key, hashes.SHA256(), default_backend())
        )
        
        # Save CA Key (encrypted in production!)
        with open(self.ca_key_path, "wb") as f:
            f.write(ca_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Save CA Certificate
        with open(self.ca_cert_path, "wb") as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
        
        print(f"[PKI] CA certificate created: {self.ca_cert_path}")
    
    def _generate_server_cert(self):
        """Generate the OpenVPN server certificate."""
        # Load CA
        ca_key, ca_cert = self._load_ca()
        
        # Generate server key
        server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Server Subject
        server_subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Maharashtra"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Fsociety Security"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Fsociety VPN Server"),
        ])
        
        # Build server certificate
        server_cert = (
            x509.CertificateBuilder()
            .subject_name(server_subject)
            .issuer_name(ca_cert.subject)
            .public_key(server_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=1825))  # 5 years
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            )
            .add_extension(
                x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=False
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(server_key.public_key()),
                critical=False
            )
            .sign(ca_key, hashes.SHA256(), default_backend())
        )
        
        # Save server key
        with open(self.server_key_path, "wb") as f:
            f.write(server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Save server certificate
        with open(self.server_cert_path, "wb") as f:
            f.write(server_cert.public_bytes(serialization.Encoding.PEM))
        
        print(f"[PKI] Server certificate created: {self.server_cert_path}")
    
    def _generate_ta_key(self):
        """Generate TLS-Auth key (256-bit random key in OpenVPN format)."""
        # OpenVPN ta.key format
        key_data = secrets.token_hex(256)  # 256 bytes = 2048 bits
        
        ta_content = f"""#
# 2048 bit OpenVPN static key
#
-----BEGIN OpenVPN Static key V1-----
{self._format_hex_key(key_data)}
-----END OpenVPN Static key V1-----
"""
        with open(self.ta_key_path, "w") as f:
            f.write(ta_content)
        
        print(f"[PKI] TLS-Auth key created: {self.ta_key_path}")
    
    def _format_hex_key(self, hex_string: str) -> str:
        """Format hex string into 16-byte lines for OpenVPN static key."""
        lines = []
        for i in range(0, len(hex_string), 32):
            lines.append(hex_string[i:i+32])
        return "\n".join(lines)
    
    def _generate_dh_params(self):
        """Generate Diffie-Hellman parameters (2048-bit)."""
        print("[PKI] Generating DH parameters (this may take a moment)...")
        
        # Generate DH parameters
        parameters = dh.generate_parameters(
            generator=2,
            key_size=2048,
            backend=default_backend()
        )
        
        # Serialize to PEM
        dh_pem = parameters.parameter_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.ParameterFormat.PKCS3
        )
        
        with open(self.dh_path, "wb") as f:
            f.write(dh_pem)
        
        print(f"[PKI] DH parameters created: {self.dh_path}")
    
    def _load_ca(self) -> Tuple:
        """Load CA certificate and key from disk."""
        with open(self.ca_key_path, "rb") as f:
            ca_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        
        with open(self.ca_cert_path, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())
        
        return ca_key, ca_cert
    
    def generate_client_certificate(self, client_name: str) -> Tuple[str, str]:
        """
        Generate a client certificate signed by the CA.
        
        Args:
            client_name: Unique identifier for the client (e.g., username_serverid)
        
        Returns:
            Tuple of (certificate_pem, private_key_pem)
        """
        # Load CA
        ca_key, ca_cert = self._load_ca()
        
        # Generate client key
        client_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Client Subject
        client_subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Maharashtra"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Fsociety Security"),
            x509.NameAttribute(NameOID.COMMON_NAME, client_name),
        ])
        
        # Build client certificate
        client_cert = (
            x509.CertificateBuilder()
            .subject_name(client_subject)
            .issuer_name(ca_cert.subject)
            .public_key(client_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))  # 1 year
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            )
            .add_extension(
                x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
                critical=False
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(client_key.public_key()),
                critical=False
            )
            .sign(ca_key, hashes.SHA256(), default_backend())
        )
        
        # Serialize to PEM
        cert_pem = client_cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
        key_pem = client_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        return cert_pem, key_pem
    
    def get_ca_certificate(self) -> str:
        """Get the CA certificate as PEM string."""
        with open(self.ca_cert_path, "r") as f:
            return f.read()
    
    def get_ta_key(self) -> str:
        """Get the TLS-Auth key content."""
        with open(self.ta_key_path, "r") as f:
            return f.read()
    
    def get_server_files(self) -> dict:
        """
        Get all server-side PKI files for OpenVPN server setup.
        
        Returns:
            Dict with ca_cert, server_cert, server_key, ta_key, dh_params
        """
        files = {}
        
        with open(self.ca_cert_path, "r") as f:
            files['ca_cert'] = f.read()
        
        with open(self.server_cert_path, "r") as f:
            files['server_cert'] = f.read()
        
        with open(self.server_key_path, "r") as f:
            files['server_key'] = f.read()
        
        with open(self.ta_key_path, "r") as f:
            files['ta_key'] = f.read()
        
        with open(self.dh_path, "r") as f:
            files['dh_params'] = f.read()
        
        return files


# Singleton instance
pki_manager = PKIManager()
