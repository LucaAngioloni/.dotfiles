#!/usr/bin/env python3
"""
lan_scanner.py - LAN Web Interface Scanner (Production Ready)
Scansiona reti locali o remote alla ricerca di interfacce web HTTP/HTTPS.
"""

import argparse
import http.client
import ipaddress
import re
import socket
import ssl
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Tuple

# Versione e default
VERSION = "1.0.0"
DEFAULT_THREADS = 50
DEFAULT_TIMEOUT = 2.0
PROGRESS_BAR_WIDTH = 30

# Porte predefinite comuni per interfacce web
COMMON_PORTS = [80, 81, 82, 88, 3000, 5000, 8000, 8080, 8443, 8888, 9000, 10000]

# SSL context per certificati self-signed (dispositivi embedded)
SSL_CONTEXT = ssl._create_unverified_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


class Colors:
    """Colori terminali per output leggibile (auto-disabilitati se non TTY)"""

    GREEN = "\033[92m" if sys.stdout.isatty() else ""
    YELLOW = "\033[93m" if sys.stdout.isatty() else ""
    RED = "\033[91m" if sys.stdout.isatty() else ""
    BLUE = "\033[94m" if sys.stdout.isatty() else ""
    CYAN = "\033[96m" if sys.stdout.isatty() else ""
    BOLD = "\033[1m" if sys.stdout.isatty() else ""
    END = "\033[0m" if sys.stdout.isatty() else ""


def get_local_ip() -> Optional[str]:
    """
    Rileva l'IP della macchina sulla connessione attiva.
    Usa un socket UDP fittizio connesso a un indirizzo pubblico
    per determinare l'interfaccia di uscita senza inviare pacchetti reali.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            # 8.8.8.8:53 è Google DNS, non viene inviato traffico reale
            s.connect(("8.8.8.8", 53))
            ip = s.getsockname()[0]
            return ip
    except Exception:
        return None


def parse_port_range(port_arg: str) -> List[int]:
    """
    Parse argomento porte: '80', '80,443', '80-90', 'common'
    """
    ports = []
    port_arg = port_arg.strip()

    if port_arg.lower() == "common":
        return COMMON_PORTS.copy()

    for part in port_arg.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))

    # Rimuovi duplicati e ordina
    return sorted(set(ports))


def parse_target(target: str) -> List[str]:
    """
    Parse target network:
    - 'auto' -> rileva IP locale + /24
    - '192.168.1.0/24' -> CIDR notation
    - '192.168.1.1-254' -> IP range (ultimo ottetto o full IP)
    - '192.168.1.50' -> singolo host
    """
    if target.lower() == "auto":
        local_ip = get_local_ip()
        if not local_ip:
            raise ValueError(
                "Impossibile rilevare IP automaticamente. Specifica il target manualmente."
            )
        # Estrai base /24 dall'IP locale
        base = ".".join(local_ip.split(".")[:3])
        target = f"{base}.0/24"
        print(
            f"{Colors.CYAN}[INFO]{Colors.END} Rilevato IP locale: {local_ip}, uso rete {target}"
        )

    # CIDR notation
    if "/" in target:
        try:
            network = ipaddress.ip_network(target, strict=False)
            return [str(ip) for ip in network.hosts()]
        except ValueError as e:
            raise ValueError(f"CIDR non valido: {e}")

    # Range con dash
    if "-" in target:
        start, end = target.split("-", 1)
        start_ip = start.strip()

        # Se end contiene punti, è un IP completo (192.168.1.1-192.168.1.100)
        if "." in end:
            end_ip = end.strip()
            ip_start = int(ipaddress.ip_address(start_ip))
            ip_end = int(ipaddress.ip_address(end_ip))
            return [str(ipaddress.ip_address(i)) for i in range(ip_start, ip_end + 1)]
        else:
            # Solo ultimo ottetto (192.168.1.1-100)
            base = ".".join(start_ip.split(".")[:-1])
            last_octet_start = int(start_ip.split(".")[-1])
            last_octet_end = int(end)
            return [f"{base}.{i}" for i in range(last_octet_start, last_octet_end + 1)]

    # Singolo host
    try:
        ipaddress.ip_address(target)
        return [target]
    except ValueError:
        raise ValueError(f"Target non valido: {target}")


def get_html_title(html: str) -> Optional[str]:
    """Estrai titolo HTML"""
    try:
        match = re.search(
            r"<title[^>]*>([^<]*)</title>", html, re.IGNORECASE | re.DOTALL
        )
        if match:
            title = match.group(1).strip()
            title = re.sub(r"\s+", " ", title)  # normalizza spazi
            return title[:70]
    except Exception:
        pass
    return None


def check_web_interface(ip: str, port: int, timeout: float) -> Optional[dict]:
    """
    Controlla se IP:porta ha un'interfaccia web.
    Prova HTTP e HTTPS (se la porta suggerisce TLS o se c'è redirect).
    """
    protocols = []

    # Porte tipicamente HTTPS
    if port in [443, 8443]:
        protocols.append(("https", True))
    else:
        protocols.append(("http", False))
        # Per porte standard HTTP, prova anche HTTPS (alcuni dispositivi hanno entrambi)
        if port == 80:
            protocols.append(("https", True))

    for proto, use_ssl in protocols:
        try:
            if use_ssl:
                conn = http.client.HTTPSConnection(
                    ip, port, timeout=timeout, context=SSL_CONTEXT
                )
            else:
                conn = http.client.HTTPConnection(ip, port, timeout=timeout)

            conn.request(
                "GET",
                "/",
                headers={
                    "Host": ip,
                    "User-Agent": "Mozilla/5.0 (LAN Scanner)",
                    "Accept": "text/html,*/*",
                    "Accept-Encoding": "identity",
                    "Connection": "close",
                },
            )

            response = conn.getresponse()
            status = response.status

            # Gestione redirect HTTP->HTTPS
            if status in (301, 302, 307, 308) and not use_ssl:
                location = response.getheader("Location", "")
                if "https://" in location:
                    conn.close()
                    try:
                        conn = http.client.HTTPSConnection(
                            ip, port, timeout=timeout, context=SSL_CONTEXT
                        )
                        conn.request(
                            "GET",
                            "/",
                            headers={"Host": ip, "User-Agent": "Mozilla/5.0"},
                        )
                        response = conn.getresponse()
                        status = response.status
                        use_ssl = True
                    except Exception:
                        pass

            server = response.getheader("Server", "")
            content_type = response.getheader("Content-Type", "")

            # Leggi body solo se HTML o generic 200
            title = None
            if status == 200 or "text/html" in content_type:
                try:
                    body = response.read(8192).decode("utf-8", errors="ignore")
                    title = get_html_title(body)
                except Exception:
                    pass

            conn.close()

            return {
                "ip": ip,
                "port": port,
                "protocol": "https" if use_ssl else "http",
                "url": f"{'https' if use_ssl else 'http'}://{ip}:{port}/",
                "status": status,
                "server": server,
                "title": title,
            }

        except (socket.timeout, ConnectionRefusedError, OSError):
            continue
        except Exception:
            continue

    return None


class LanScanner:
    def __init__(
        self,
        targets: List[str],
        ports: List[int],
        threads: int,
        timeout: float,
        verbose: bool,
    ):
        self.targets = targets
        self.ports = ports
        self.threads = threads
        self.timeout = timeout
        self.verbose = verbose
        self.found = []
        self.lock = threading.Lock()
        self.completed = 0
        self.total = len(targets) * len(ports)
        self.start_time = 0.0
        self.last_progress_update = 0.0

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Formatta secondi in HH:MM:SS"""
        seconds = max(0, int(seconds))
        hours, rem = divmod(seconds, 3600)
        minutes, secs = divmod(rem, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def _print_progress(self, force: bool = False):
        """Mostra progress bar con ETA (su TTY)"""
        if self.total <= 0:
            return

        now = time.time()
        if not force and (now - self.last_progress_update) < 0.2:
            return

        self.last_progress_update = now
        ratio = self.completed / self.total
        filled = int(ratio * PROGRESS_BAR_WIDTH)
        bar = "█" * filled + "-" * (PROGRESS_BAR_WIDTH - filled)

        elapsed = now - self.start_time if self.start_time else 0.0
        if self.completed > 0 and elapsed > 0:
            rate = self.completed / elapsed
            eta_seconds = (self.total - self.completed) / rate if rate > 0 else 0.0
            eta = self._format_duration(eta_seconds)
        else:
            eta = "--:--"

        line = f"[{bar}] {ratio * 100:6.2f}% ({self.completed}/{self.total}) ETA {eta}"

        if sys.stdout.isatty():
            print(f"\r{Colors.BLUE}{line}{Colors.END}", end="", flush=True)
        elif self.verbose or force:
            print(f"{Colors.BLUE}[INFO]{Colors.END} {line}")

    def scan_host_port(self, ip: str, port: int):
        """Scan singolo host:porta"""
        result = check_web_interface(ip, port, self.timeout)

        with self.lock:
            self.completed += 1

            if result:
                self.found.append(result)
                color = Colors.GREEN
                proto = result["protocol"].upper()
                status = result["status"]

                info_parts = []
                if result["server"]:
                    info_parts.append(f"Server: {result['server']}")
                if result["title"]:
                    info_parts.append(f"Title: {result['title']}")
                info_str = " | ".join(info_parts)

                if sys.stdout.isatty():
                    print()

                print(
                    f"{color}[FOUND]{Colors.END} {result['ip']}:{result['port']} ({proto}) - HTTP {status} {info_str}"
                )
                print(f"       URL: {result['url']}")

            self._print_progress()

    def run(self):
        """Esecuzione scan parallelo"""
        print(f"{Colors.BOLD}Avvio scansione:{Colors.END}")
        print(f"  Target: {len(self.targets)} host")
        print(f"  Porte: {len(self.ports)} ({', '.join(map(str, self.ports))})")
        print(f"  Threads: {self.threads}")
        print(f"  Timeout: {self.timeout}s")
        print(f"  Totale controlli: {self.total}")
        print()

        start_time = time.time()
        self.start_time = start_time
        self.last_progress_update = 0.0
        self._print_progress(force=True)

        try:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = []
                for ip in self.targets:
                    for port in self.ports:
                        futures.append(executor.submit(self.scan_host_port, ip, port))

                # Attendi completamento gestendo interrupt
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        if self.verbose:
                            if sys.stdout.isatty():
                                print()
                            print(f"{Colors.RED}[ERROR]{Colors.END} {e}")

        except KeyboardInterrupt:
            print(
                f"\n{Colors.YELLOW}[WARN]{Colors.END} Scansione interrotta dall'utente"
            )
            remaining = self.total - self.completed
            print(f"       Completati: {self.completed}, Mancanti: {remaining}")

        with self.lock:
            self._print_progress(force=True)
            if sys.stdout.isatty():
                print()

        duration = time.time() - start_time
        return duration

    def report(self, output_file: Optional[str] = None):
        """Genera report finale"""
        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}RIEPILOGO{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")

        if not self.found:
            print("Nessun dispositivo con interfaccia web trovato.")
            print("\nSuggerimenti:")
            print("  - Verifica che i dispositivi siano accesi e connessi")
            print("  - Prova ad aumentare il timeout (--timeout 5) se la rete è lenta")
            print("  - Verifica firewall o VLAN che potrebbero isolare i dispositivi")
        else:
            # Raggruppa per IP
            by_ip = {}
            for item in self.found:
                ip = item["ip"]
                if ip not in by_ip:
                    by_ip[ip] = []
                by_ip[ip].append(item)

            print(f"Trovati {len(self.found)} endpoint su {len(by_ip)} dispositivi\n")

            for ip in sorted(by_ip.keys(), key=lambda x: int(ipaddress.ip_address(x))):
                services = sorted(by_ip[ip], key=lambda x: x["port"])
                print(f"{Colors.BOLD}{ip}{Colors.END}")
                for svc in services:
                    proto = svc["protocol"].upper()
                    color = Colors.GREEN if svc["status"] == 200 else Colors.YELLOW
                    print(
                        f"  {color}●{Colors.END} Port {svc['port']} ({proto}) - HTTP {svc['status']}"
                    )
                    print(f"    {Colors.CYAN}{svc['url']}{Colors.END}")
                    if svc["title"]:
                        print(f"    Title: {svc['title']}")
                    if svc["server"]:
                        print(f"    Server: {svc['server']}")
                print()

            # Salva su file se richiesto
            if output_file:
                try:
                    with open(output_file, "w") as f:
                        f.write(f"# LAN Scanner Results\n")
                        f.write(
                            f"# Found {len(self.found)} endpoints on {len(by_ip)} devices\n\n"
                        )
                        for ip in sorted(by_ip.keys()):
                            for svc in by_ip[ip]:
                                f.write(f"{svc['url']}\n")
                    print(
                        f"{Colors.GREEN}[OK]{Colors.END} Risultati salvati in: {output_file}"
                    )
                except IOError as e:
                    print(
                        f"{Colors.RED}[ERROR]{Colors.END} Impossibile scrivere file: {e}"
                    )


def main():
    parser = argparse.ArgumentParser(
        description="LAN Web Interface Scanner - Trova dispositivi con interfaccia web",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  %(prog)s                          # Scansione automatica rete locale /24
  %(prog)s 192.168.1.0/24           # Scansione CIDR specifico
  %(prog)s 192.168.1.1-50           # Scansione range IP
  %(prog)s 10.0.0.0/16 -p 80,443   # Scansione grande rete, porte specifiche
  %(prog)s auto -p 8080-8090 -t 100 # Auto-detect + range porte + 100 threads
        """,
    )

    parser.add_argument(
        "target",
        nargs="?",
        default="auto",
        help='Target: "auto", CIDR (192.168.1.0/24), range (192.168.1.1-254) o singolo IP. Default: auto',
    )
    parser.add_argument(
        "-p",
        "--ports",
        default="common",
        help='Porte: "common" (default), lista "80,443,8080" o range "80-90"',
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=DEFAULT_THREADS,
        help=f"Numero di thread paralleli. Default: {DEFAULT_THREADS}",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout connessione in secondi. Default: {DEFAULT_TIMEOUT}",
    )
    parser.add_argument(
        "-o", "--output", help="File di output per salvare gli URL trovati"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Mostra progresso dettagliato"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    args = parser.parse_args()

    # Parse input
    try:
        targets = parse_target(args.target)
    except ValueError as e:
        print(f"{Colors.RED}[ERROR]{Colors.END} {e}", file=sys.stderr)
        sys.exit(1)

    try:
        ports = parse_port_range(args.ports)
    except ValueError as e:
        print(f"{Colors.RED}[ERROR]{Colors.END} Porte non valide: {e}", file=sys.stderr)
        sys.exit(1)

    # Validazioni
    if args.threads < 1 or args.threads > 500:
        print(
            f"{Colors.RED}[ERROR]{Colors.END} Threads devono essere tra 1 e 500",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.timeout < 0.1 or args.timeout > 60:
        print(
            f"{Colors.RED}[ERROR]{Colors.END} Timeout deve essere tra 0.1 e 60 secondi",
            file=sys.stderr,
        )
        sys.exit(1)

    # Warning per scansioni grandi
    total_checks = len(targets) * len(ports)
    if total_checks > 10000:
        print(
            f"{Colors.YELLOW}[WARN]{Colors.END} Stai per eseguire {total_checks} controlli."
        )
        print(f"       Questo potrebbe richiedere tempo e generare traffico di rete.")
        response = input("       Continuare? [y/N]: ")
        if response.lower() != "y":
            sys.exit(0)

    # Esecuzione
    scanner = LanScanner(
        targets=targets,
        ports=ports,
        threads=args.threads,
        timeout=args.timeout,
        verbose=args.verbose,
    )

    duration = scanner.run()
    scanner.report(args.output)

    print(f"\n{Colors.BLUE}[INFO]{Colors.END} Completato in {duration:.1f} secondi")


if __name__ == "__main__":
    main()
