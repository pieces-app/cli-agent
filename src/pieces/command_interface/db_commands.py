"""Export and import Pieces OS database (com.pieces.os)."""

import argparse
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from pieces.base_command import BaseCommand
from pieces.config.constants import get_pieces_os_data_dir
from pieces.help_structure import HelpBuilder
from pieces.settings import Settings
from pieces.urls import URLs


class ExportCommand(BaseCommand):
    """Export Pieces OS database to a zip archive."""

    def get_name(self) -> str:
        return "export"

    def get_help(self) -> str:
        return "Export Pieces OS database to a zip archive"

    def get_description(self) -> str:
        return (
            "Export the Pieces OS database (snippets, LTM context, embeddings) to a "
            "zip archive. Quit Pieces Desktop and PiecesOS before exporting for a "
            "consistent backup."
        )

    def get_examples(self):
        builder = HelpBuilder()
        builder.section(
            header="Export database:",
            command_template="pieces export [OPTIONS]",
        ).example(
            "pieces export",
            "Export to pieces-export-YYYYMMDD-HHMMSS.zip in current directory",
        ).example(
            "pieces export -o ~/backups/pieces.zip",
            "Export to a specific path",
        ).example(
            "pieces export --compress",
            "Compress archive (smaller file, slower)",
        ).example(
            "pieces export --full",
            "Export entire com.pieces.os (includes backups, staging)",
        )
        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_HELP_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "-o",
            "--output",
            dest="output",
            type=str,
            default=None,
            help="Output path for the zip archive (default: pieces-export-<timestamp>.zip in cwd)",
        )
        parser.add_argument(
            "--compress",
            dest="compress",
            action="store_true",
            help="Compress the archive (smaller file, slower). Default: no compression for speed.",
        )
        parser.add_argument(
            "--full",
            dest="full",
            action="store_true",
            help="Export entire com.pieces.os (includes backups, staging, old zips). Default: production DB only.",
        )

    def execute(self, **kwargs) -> int:
        output_path = kwargs.get("output")
        pieces_os_dir = get_pieces_os_data_dir()

        if Settings.pieces_client.is_pieces_running():
            Settings.logger.print(
                "[red]PiecesOS must be fully quit before export.[/red]"
            )
            Settings.logger.print(
                "[yellow]Quit Pieces Desktop and PiecesOS from the menu bar/system tray, then retry.[/yellow]"
            )
            return 1

        Settings.logger.print(
            "[yellow]⚠  This database contains all your snippets, code, and workflow data. "
            "Never share it with anyone.[/yellow]"
        )

        if not pieces_os_dir.exists():
            Settings.logger.print(
                f"[red]Pieces OS data directory not found: {pieces_os_dir}[/red]"
            )
            Settings.logger.print(
                "[yellow]Install PiecesOS first with `pieces install`.[/yellow]"
            )
            return 1

        production_dir = pieces_os_dir / "production"
        if not production_dir.exists():
            Settings.logger.print(
                f"[red]Production database not found: {production_dir}[/red]"
            )
            return 1

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_path = Path.cwd() / f"pieces-export-{timestamp}.zip"
        else:
            output_path = Path(output_path).expanduser().resolve()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        compress = kwargs.get("compress", False)
        full = kwargs.get("full", False)
        try:
            mode = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
            if compress:
                Settings.logger.print(
                    "[yellow]Compressing archive (slower, smaller output)[/yellow]"
                )
            if full:
                Settings.logger.print(
                    "[yellow]Full export: including backups, staging, and all data[/yellow]"
                )

            # Source: production folder only (default), or entire com.pieces.os (--full)
            source_dir = pieces_os_dir if full else production_dir
            prefix = "" if full else "production/"

            # Collect files with sizes (byte-based progress = accurate ETA)
            files_with_size = [
                (f, f.stat().st_size)
                for f in source_dir.rglob("*")
                if f.is_file()
            ]
            total_bytes = sum(s for _, s in files_with_size)

            def _fmt(b: int) -> str:
                return f"{b / (1024**3):.1f} GB" if b >= 1024**3 else f"{b / (1024**2):.0f} MB"

            progress = Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=40),
                TaskProgressColumn(),
                TextColumn("•"),
                TextColumn("[cyan]{task.fields[bytes_str]}"),
                TimeElapsedColumn(),
                TextColumn("•"),
                TimeRemainingColumn(),
                console=Settings.logger.console,
                transient=False,
            )

            with progress:
                task = progress.add_task(
                    "Exporting...",
                    total=total_bytes,
                    bytes_str=f"0 / {_fmt(total_bytes)}",
                )
                bytes_so_far = 0
                with zipfile.ZipFile(
                    output_path, "w", mode, allowZip64=True
                ) as zf:
                    for item, size in files_with_size:
                        arcname = prefix + str(item.relative_to(source_dir))
                        zf.write(item, arcname)
                        bytes_so_far += size
                        progress.update(
                            task,
                            advance=size,
                            bytes_str=f"{_fmt(bytes_so_far)} / {_fmt(total_bytes)}",
                        )

            size_mb = output_path.stat().st_size / (1024 * 1024)
            Settings.logger.print(
                f"[green]Export complete: {output_path} ({size_mb:.1f} MB)[/green]"
            )
            return 0
        except (zipfile.BadZipFile, OSError) as e:
            Settings.logger.print(f"[red]Export failed: {e}[/red]")
            return 1


class ImportCommand(BaseCommand):
    """Import/restore Pieces OS database from an exported zip or directory."""

    def get_name(self) -> str:
        return "import"

    def get_aliases(self):
        return ["restore"]

    def get_help(self) -> str:
        return "Import or restore database from export"

    def get_description(self) -> str:
        return (
            "Import a previously exported Pieces OS database. Quit Pieces Desktop "
            "and PiecesOS before importing. The import replaces your current database."
        )

    def get_examples(self):
        builder = HelpBuilder()
        builder.section(
            header="Import/restore database:",
            command_template="pieces import -d <path>",
        ).example(
            "pieces import -d ./pieces-export-20260306.zip",
            "Import from a zip archive",
        ).example(
            "pieces restore -d ./pieces-export-20260306.zip",
            "Restore from a zip archive (alias)",
        ).example(
            "pieces import -d /path/to/extracted/backup",
            "Import from an extracted directory",
        )
        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_HELP_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "-d",
            "--path",
            dest="path",
            type=str,
            required=True,
            help="Path to exported zip archive or directory containing the backup",
        )

    def execute(self, **kwargs) -> int:
        source = Path(kwargs["path"]).expanduser().resolve()
        pieces_os_dir = get_pieces_os_data_dir()

        if Settings.pieces_client.is_pieces_running():
            Settings.logger.print(
                "[red]PiecesOS must be fully quit before import/restore.[/red]"
            )
            Settings.logger.print(
                "[yellow]Quit Pieces Desktop and PiecesOS from the menu bar/system tray, then retry.[/yellow]"
            )
            return 1

        Settings.logger.print(
            "[yellow]⚠  This database contains all your snippets, code, and workflow data. "
            "Never share exported files with anyone.[/yellow]"
        )

        if not source.exists():
            Settings.logger.print(f"[red]Source not found: {source}[/red]")
            return 1

        if source.is_file():
            if source.suffix.lower() != ".zip":
                Settings.logger.print(
                    "[red]File must be a .zip archive. Use a directory path for "
                    "extracted backups.[/red]"
                )
                return 1
            return self._import_from_zip(source, pieces_os_dir)
        else:
            return self._import_from_dir(source, pieces_os_dir)

    def _import_from_zip(self, zip_path: Path, pieces_os_dir: Path) -> int:
        """Extract zip to temp dir, then copy to pieces_os_dir."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                with zipfile.ZipFile(zip_path, "r") as zf:
                    members = [m for m in zf.infolist() if not m.is_dir()]
                    total_bytes = sum(m.file_size for m in members)

                    def _fmt(b: int) -> str:
                        return (
                            f"{b / (1024**3):.1f} GB"
                            if b >= 1024**3
                            else f"{b / (1024**2):.0f} MB"
                        )

                    progress = Progress(
                        TextColumn("[bold blue]{task.description}"),
                        BarColumn(bar_width=40),
                        TaskProgressColumn(),
                        TextColumn("•"),
                        TextColumn("[cyan]{task.fields[bytes_str]}"),
                        TimeElapsedColumn(),
                        TextColumn("•"),
                        TimeRemainingColumn(),
                        console=Settings.logger.console,
                        transient=False,
                    )
                    with progress:
                        task = progress.add_task(
                            "Extracting...",
                            total=total_bytes,
                            bytes_str=f"0 / {_fmt(total_bytes)}",
                        )
                        bytes_so_far = 0
                        for m in members:
                            zf.extract(m, tmp_path)
                            bytes_so_far += m.file_size
                            progress.update(
                                task,
                                advance=m.file_size,
                                bytes_str=f"{_fmt(bytes_so_far)} / {_fmt(total_bytes)}",
                            )

                # Zip may have com.pieces.os/ at root or contents at root
                extract_root = tmp_path
                if (tmp_path / "production").exists():
                    pass  # contents at root
                elif (tmp_path / "com.pieces.os").exists():
                    extract_root = tmp_path / "com.pieces.os"
                else:
                    # Look for production in first-level dirs
                    subdirs = [d for d in tmp_path.iterdir() if d.is_dir()]
                    if len(subdirs) == 1 and (subdirs[0] / "production").exists():
                        extract_root = subdirs[0]
                    else:
                        Settings.logger.print(
                            "[red]Invalid export format: no production folder found.[/red]"
                        )
                        return 1

                return self._copy_to_pieces_os(extract_root, pieces_os_dir)
        except zipfile.BadZipFile as e:
            Settings.logger.print(f"[red]Invalid zip file: {e}[/red]")
            return 1

    def _import_from_dir(self, source_dir: Path, pieces_os_dir: Path) -> int:
        """Copy directory contents to pieces_os_dir."""
        # source_dir may be com.pieces.os or a dir containing production
        if (source_dir / "production").exists():
            extract_root = source_dir
        elif (source_dir / "com.pieces.os").exists():
            extract_root = source_dir / "com.pieces.os"
        else:
            Settings.logger.print(
                "[red]Directory must contain a production folder (valid export).[/red]"
            )
            return 1

        return self._copy_to_pieces_os(extract_root, pieces_os_dir)

    def _copy_to_pieces_os(self, source: Path, pieces_os_dir: Path) -> int:
        """Copy source contents into pieces_os_dir, backing up existing production."""
        try:
            pieces_os_dir.mkdir(parents=True, exist_ok=True)

            production_src = source / "production"
            production_dst = pieces_os_dir / "production"

            if not production_src.exists():
                Settings.logger.print(
                    "[red]Source has no production folder.[/red]"
                )
                return 1

            # Backup existing production if it exists
            if production_dst.exists():
                backup_name = f"production_backup_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                backup_path = pieces_os_dir / backup_name
                Settings.logger.print(
                    f"[yellow]Backing up existing database to {backup_name}...[/yellow]"
                )
                shutil.move(str(production_dst), str(backup_path))

            # Collect files for progress
            files_with_size = [
                (f, f.stat().st_size)
                for f in source.rglob("*")
                if f.is_file()
            ]
            total_bytes = sum(s for _, s in files_with_size)

            def _fmt(b: int) -> str:
                return (
                    f"{b / (1024**3):.1f} GB"
                    if b >= 1024**3
                    else f"{b / (1024**2):.0f} MB"
                )

            progress = Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=40),
                TaskProgressColumn(),
                TextColumn("•"),
                TextColumn("[cyan]{task.fields[bytes_str]}"),
                TimeElapsedColumn(),
                TextColumn("•"),
                TimeRemainingColumn(),
                console=Settings.logger.console,
                transient=False,
            )

            with progress:
                task = progress.add_task(
                    "Restoring...",
                    total=total_bytes,
                    bytes_str=f"0 / {_fmt(total_bytes)}",
                )
                bytes_so_far = 0
                for item, size in files_with_size:
                    rel = item.relative_to(source)
                    dst = pieces_os_dir / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dst)
                    bytes_so_far += size
                    progress.update(
                        task,
                        advance=size,
                        bytes_str=f"{_fmt(bytes_so_far)} / {_fmt(total_bytes)}",
                    )

            # Verify fidelity: production folder file count and byte count must match
            prod_dst = pieces_os_dir / "production"
            prod_src = source / "production"
            if prod_dst.exists() and prod_src.exists():
                dst_files = [p for p in prod_dst.rglob("*") if p.is_file()]
                src_files = [p for p in prod_src.rglob("*") if p.is_file()]
                dst_bytes = sum(p.stat().st_size for p in dst_files)
                src_bytes = sum(p.stat().st_size for p in src_files)
                files_match = len(src_files) == len(dst_files)
                # Allow tiny diff from filesystem block rounding (< 0.01%)
                bytes_match = (
                    src_bytes == dst_bytes
                    or abs(src_bytes - dst_bytes) / max(src_bytes, 1) < 0.0001
                )
                if files_match and bytes_match:
                    Settings.logger.print(
                        f"[green]Verified: {len(dst_files)} files, "
                        f"{_fmt(dst_bytes)} restored[/green]"
                    )
                else:
                    Settings.logger.print(
                        f"[yellow]Mismatch: source {len(src_files)} files "
                        f"({_fmt(src_bytes)}), dest {len(dst_files)} files "
                        f"({_fmt(dst_bytes)})[/yellow]"
                    )

            Settings.logger.print(
                "[green]Import complete. Restart PiecesOS to use the imported database.[/green]"
            )
            return 0
        except (OSError, shutil.Error) as e:
            Settings.logger.print(f"[red]Import failed: {e}[/red]")
            return 1
