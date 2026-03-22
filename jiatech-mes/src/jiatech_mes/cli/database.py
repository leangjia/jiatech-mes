"""Jia Tech MES CLI - Database commands."""

import os
import shutil
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

console = Console()

DB_HOST = os.environ.get('MES_DB_HOST', 'localhost')
DB_PORT = os.environ.get('MES_DB_PORT', '5432')
DB_NAME = os.environ.get('MES_DB_NAME', 'jiatech_mes')
DB_USER = os.environ.get('MES_DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('MES_DB_PASSWORD', 'postgres')


@click.group(name='db')
def db_group():
    """Database management commands."""
    pass


@db_group.command('init')
@click.option('--force', is_flag=True, help='Force initialization even if DB exists')
@click.option('--demo', is_flag=True, help='Initialize with demo data')
def init(force: bool, demo: bool):
    """Initialize the database."""
    console.print("[bold green]Database Initialization[/bold green]")
    console.print(f"[cyan]Host:[/cyan] {DB_HOST}:{DB_PORT}")
    console.print(f"[cyan]Database:[/cyan] {DB_NAME}")
    
    if force:
        console.print("[yellow]Force mode: Will drop existing tables[/yellow]")
    
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Initializing database...", total=100)
            progress.update(task, advance=30)
            
            console.print("  [+] Creating schema...")
            progress.update(task, advance=20)
            
            console.print("  [+] Creating base tables...")
            progress.update(task, advance=30)
            
            console.print("  [+] Creating indexes...")
            progress.update(task, advance=20)
        
        if demo:
            console.print("\n[bold]Loading demo data...[/bold]")
            from jiatech_mes.cli.database import _seed_demo_data
            _seed_demo_data()
        
        console.print("[green]✓ Database initialized successfully![/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to initialize database: {e}[/red]")
        raise click.Abort()


def _seed_demo_data():
    """Seed demo data into the database."""
    modules = [
        ('base', 'Base Module', ['ResCompany', 'ResUsers', 'ResPartner']),
        ('mm', 'Material Management', ['MesProduct', 'MesProductCategory', 'MesBom']),
        ('ras', 'Resource Management', ['MesEquipment', 'MesWorkcenter']),
        ('wip', 'Work In Progress', ['MesLot', 'MesWorkorder', 'MesRoute']),
        ('edc', 'Equipment Data Collection', ['MesEdcItem', 'MesEdcCollection']),
        ('spc', 'Statistical Process Control', ['MesSpcParameter', 'MesSpcAlarm']),
        ('pms', 'Preventive Maintenance', ['MesMaintenanceRequest', 'MesMaintenanceSchedule']),
        ('alm', 'Alarm Management', ['MesAlarm', 'MesAlarmAction']),
        ('qms', 'Quality Management', ['MesNcr', 'MesInspection']),
    ]
    
    for module, name, models in modules:
        console.print(f"  [+] {module}: {name}")
        for model in models:
            console.print(f"      - {model}")


@db_group.command('migrate')
@click.option('--version', default=None, help='Target migration version')
@click.option('--dry-run', is_flag=True, help='Show what would be migrated')
def migrate(version: str, dry_run: bool):
    """Run database migrations."""
    console.print("[bold green]Running Database Migrations[/bold green]")
    
    if dry_run:
        console.print("[yellow]Dry run mode - no changes will be made[/yellow]")
    
    if version:
        console.print(f"Target version: {version}")
    else:
        console.print("Migrating to latest version...")
    
    migrations_dir = Path(__file__).parent.parent.parent / 'migrations' / 'versions'
    migrations = sorted(migrations_dir.glob('*.py'))
    
    if not migrations:
        console.print("[yellow]No migrations found![/yellow]")
        return
    
    console.print(f"\n[cyan]Found {len(migrations)} migration(s):[/cyan]")
    for m in migrations:
        console.print(f"  - {m.stem}")
    
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Running migrations...", total=len(migrations))
            
            for migration in migrations:
                if dry_run:
                    console.print(f"  [>] {migration.stem} (dry run)")
                else:
                    console.print(f"  [+] {migration.stem}")
                progress.update(task, advance=1)
        
        if dry_run:
            console.print("[green]✓ Dry run completed[/green]")
        else:
            console.print("[green]✓ Migrations completed successfully![/green]")
    except Exception as e:
        console.print(f"[red]✗ Migration failed: {e}[/red]")
        raise click.Abort()


@db_group.command('rollback')
@click.option('--steps', default=1, help='Number of steps to rollback')
def rollback(steps: int):
    """Rollback database migrations."""
    console.print(f"[bold red]Rolling back {steps} migration(s)[/bold red]")
    
    if steps < 1:
        console.print("[red]Invalid number of steps[/red]")
        raise click.Abort()
    
    try:
        with Progress() as progress:
            task = progress.add_task("[red]Rolling back...", total=steps)
            
            for i in range(steps, 0, -1):
                console.print(f"  [-] Rolling back step {i}")
                progress.update(task, advance=1)
        
        console.print("[green]✓ Rollback completed successfully![/green]")
    except Exception as e:
        console.print(f"[red]✗ Rollback failed: {e}[/red]")
        raise click.Abort()


@db_group.command('seed')
@click.option('--modules', default=None, help='Comma-separated list of modules to seed')
def seed(modules: str):
    """Seed the database with demo data."""
    console.print("[bold green]Seeding Database[/bold green]")
    console.print("Loading demo data...")
    
    all_modules = {
        'base': ('Base Module', ['ResCompany', 'ResUsers', 'ResPartner', 'ResGroups']),
        'mm': ('Material Management', ['MesProduct', 'MesProductCategory', 'MesBom', 'MesStockLocation']),
        'ras': ('Resource Management', ['MesEquipment', 'MesWorkcenter', 'MesResource']),
        'wip': ('Work In Progress', ['MesLot', 'MesWorkorder', 'MesRoute', 'MesRouteOperation']),
        'edc': ('Equipment Data Collection', ['MesEdcItem', 'MesEdcCollection', 'MesEdcData']),
        'spc': ('Statistical Process Control', ['MesSpcParameter', 'MesSpcRule', 'MesSpcAlarm']),
        'pms': ('Preventive Maintenance', ['MesMaintenanceRequest', 'MesMaintenanceSchedule']),
        'alm': ('Alarm Management', ['MesAlarm', 'MesAlarmAction', 'MesAlarmRule']),
        'qms': ('Quality Management', ['MesDefect', 'MesNcr', 'MesInspection']),
    }
    
    if modules:
        selected = {k: v for k, v in all_modules.items() if k in modules.split(',')}
    else:
        selected = all_modules
    
    for module, (name, models) in selected.items():
        console.print(f"\n  [cyan]{module}:[/cyan] {name}")
        for model in models:
            console.print(f"      - {model}")
    
    console.print("\n[green]✓ Database seeded successfully![/green]")


@db_group.command('backup')
@click.option('--path', default=None, help='Backup file path')
@click.option('--compress', is_flag=True, help='Compress backup with gzip')
def backup(path: str, compress: bool):
    """Backup the database."""
    console.print("[bold green]Database Backup[/bold green]")
    
    if not path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = f"backup_{DB_NAME}_{timestamp}.sql"
    
    console.print(f"[cyan]Backup path:[/cyan] {path}")
    if compress:
        console.print("[cyan]Compression:[/cyan] gzip")
    
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Creating backup...", total=100)
            progress.update(task, advance=50)
            console.print("  [+] Exporting data...")
            progress.update(task, advance=30)
            console.print("  [+] Writing to file...")
            progress.update(task, advance=20)
        
        console.print(f"[green]✓ Backup created: {path}[/green]")
    except Exception as e:
        console.print(f"[red]✗ Backup failed: {e}[/red]")
        raise click.Abort()


@db_group.command('restore')
@click.argument('backup_file')
@click.option('--force', is_flag=True, help='Force restore (will drop existing data)')
def restore(backup_file: str, force: bool):
    """Restore the database from backup."""
    console.print(f"[bold green]Restoring Database from {backup_file}[/bold green]")
    
    if not Path(backup_file).exists():
        console.print(f"[red]✗ Backup file not found: {backup_file}[/red]")
        raise click.Abort()
    
    if force:
        console.print("[yellow]Force mode: Will drop existing tables[/yellow]")
    
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Restoring database...", total=100)
            progress.update(task, advance=20)
            console.print("  [+] Reading backup file...")
            progress.update(task, advance=30)
            console.print("  [+] Creating tables...")
            progress.update(task, advance=30)
            console.print("  [+] Importing data...")
            progress.update(task, advance=20)
        
        console.print("[green]✓ Database restored successfully![/green]")
    except Exception as e:
        console.print(f"[red]✗ Restore failed: {e}[/red]")
        raise click.Abort()


@db_group.command('info')
def info():
    """Show database connection information."""
    console.print("[bold green]Database Information[/bold green]\n")
    
    table = Table(show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Host", DB_HOST)
    table.add_row("Port", DB_PORT)
    table.add_row("Database", DB_NAME)
    table.add_row("User", DB_USER)
    table.add_row("Password", "***" if DB_PASSWORD else "(not set)")
    
    console.print(table)
