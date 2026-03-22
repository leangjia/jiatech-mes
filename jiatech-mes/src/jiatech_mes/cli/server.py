"""Jia Tech MES CLI - Server commands."""

import os
import signal
import socket
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
import uvicorn

console = Console()

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8000
PID_FILE = '.mes_server.pid'


def _is_port_in_use(host: str, port: int) -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


def _read_pid_file() -> Optional[int]:
    """Read PID from file."""
    try:
        with open(PID_FILE, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def _write_pid_file(pid: int):
    """Write PID to file."""
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))


def _remove_pid_file():
    """Remove PID file."""
    try:
        os.remove(PID_FILE)
    except FileNotFoundError:
        pass


def _is_process_running(pid: int) -> bool:
    """Check if a process is running."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


@click.group(name='server')
def server_group():
    """Server management commands."""
    pass


@server_group.command('start')
@click.option('--host', default=DEFAULT_HOST, help='Host to bind to')
@click.option('--port', default=DEFAULT_PORT, help='Port to bind to', type=int)
@click.option('--reload', is_flag=True, help='Enable auto-reload')
@click.option('--workers', default=1, help='Number of workers')
@click.option('--log-level', default='info', help='Log level', type=click.Choice(['debug', 'info', 'warning', 'error']))
def start(host: str, port: int, reload: bool, workers: int, log_level: str):
    """Start the MES server."""
    if _is_port_in_use(host, port):
        console.print(f"[red]✗ Error: Port {port} is already in use[/red]")
        raise click.Abort()
    
    console.print("[bold green]Starting Jia Tech MES Server[/bold green]")
    console.print(f"  [cyan]Host:[/cyan] {host}")
    console.print(f"  [cyan]Port:[/cyan] {port}")
    console.print(f"  [cyan]Workers:[/cyan] {workers}")
    console.print(f"  [cyan]Reload:[/cyan] {reload}")
    console.print(f"  [cyan]Log Level:[/cyan] {log_level}")
    console.print()
    
    try:
        config = uvicorn.Config(
            'jiatech_mes.main:app',
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
            log_level=log_level,
            access_log=True,
        )
        server = uvicorn.Server(config)
        
        _write_pid_file(os.getpid())
        
        console.print(f"[green]✓ Server is running at http://{host}:{port}[/green]")
        console.print("[cyan]Press Ctrl+C to stop[/cyan]\n")
        
        server.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Server error: {e}[/red]")
        raise click.Abort()
    finally:
        _remove_pid_file()


@server_group.command('status')
def status():
    """Check server status."""
    console.print("[bold green]Server Status[/bold green]\n")
    
    pid = _read_pid_file()
    
    table = Table(show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("PID File", PID_FILE)
    
    if pid:
        table.add_row("PID", str(pid))
        table.add_row("Running", "Yes" if _is_process_running(pid) else "No")
    else:
        table.add_row("PID", "(none)")
        table.add_row("Running", "No")
    
    table.add_row("Port", str(DEFAULT_PORT))
    table.add_row("Port In Use", "Yes" if _is_port_in_use(DEFAULT_HOST, DEFAULT_PORT) else "No")
    
    console.print(table)
    
    if pid and _is_process_running(pid):
        console.print("\n[green]✓ Server is running[/green]")
    else:
        console.print("\n[yellow]✗ Server is not running[/yellow]")


@server_group.command('stop')
@click.option('--force', is_flag=True, help='Force stop')
def stop(force: bool):
    """Stop the MES server."""
    console.print("[bold red]Stopping Server[/bold red]")
    
    pid = _read_pid_file()
    
    if not pid:
        console.print("[yellow]No PID file found - server may not be running[/yellow]")
        return
    
    if not _is_process_running(pid):
        console.print("[yellow]Process not running - cleaning up PID file[/yellow]")
        _remove_pid_file()
        return
    
    try:
        if force:
            console.print(f"[red]Force stopping process {pid}...[/red]")
            os.kill(pid, signal.SIGKILL)
        else:
            console.print(f"Sending shutdown signal to process {pid}...")
            os.kill(pid, signal.SIGTERM)
        
        import time
        for _ in range(5):
            if not _is_process_running(pid):
                break
            time.sleep(0.5)
        
        _remove_pid_file()
        
        if _is_process_running(pid):
            console.print("[red]✗ Process did not stop cleanly[/red]")
            raise click.Abort()
        
        console.print("[green]✓ Server stopped successfully[/green]")
    except PermissionError:
        console.print("[red]✗ Permission denied - cannot stop server[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]✗ Error stopping server: {e}[/red]")
        raise click.Abort()


@server_group.command('restart')
@click.option('--host', default=DEFAULT_HOST, help='Host to bind to')
@click.option('--port', default=DEFAULT_PORT, help='Port to bind to', type=int)
def restart(host: str, port: int):
    """Restart the MES server."""
    console.print("[bold yellow]Restarting Server[/bold yellow]")
    
    pid = _read_pid_file()
    if pid and _is_process_running(pid):
        console.print("Stopping existing server...")
        try:
            os.kill(pid, signal.SIGTERM)
            import time
            for _ in range(5):
                if not _is_process_running(pid):
                    break
                time.sleep(0.5)
        except Exception:
            pass
    
    console.print("\nStarting server...")
    ctx = click.get_current_context()
    ctx.invoke(start, host=host, port=port, reload=False, workers=1, log_level='info')
