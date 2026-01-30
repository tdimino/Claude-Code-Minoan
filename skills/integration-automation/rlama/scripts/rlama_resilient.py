#!/usr/bin/env python3
"""
RLAMA Resilient Indexing Script - Processes files individually, skipping failures.

Unlike the standard RLAMA CLI which aborts on errors, this script continues
processing when individual files fail (e.g., due to embedding context overflow).

Usage:
    python3 rlama_resilient.py create my-rag ~/Documents
    python3 rlama_resilient.py create my-rag ~/Research --docs-only
    python3 rlama_resilient.py add my-rag ./more-docs
    python3 rlama_resilient.py add my-rag ~/Papers --docs-only --chunk-size 500
"""

import argparse
import subprocess
import sys
import os
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional

# Default model (qwen2.5:7b as of Jan 2026)
DEFAULT_MODEL = 'qwen2.5:7b'
LEGACY_MODEL = 'llama3.2'

# Supported file extensions by RLAMA
SUPPORTED_EXTENSIONS = {
    '.txt', '.md', '.markdown',
    '.pdf', '.docx', '.doc',
    '.py', '.js', '.ts', '.go', '.rs', '.java', '.rb', '.cpp', '.c', '.h',
    '.json', '.yaml', '.yml', '.csv',
    '.html', '.htm',
    '.org'
}

# Document-only extensions (for --docs-only)
DOC_EXTENSIONS = {'.pdf', '.md', '.txt', '.docx', '.doc', '.org'}

# Errors that indicate we should skip the file and continue
SKIP_ERRORS = [
    'input length exceeds the context length',
    'context length exceeded',
    'embedding generation failed',
    'failed to generate embedding',
]

# Errors that indicate we should abort entirely
FATAL_ERRORS = [
    'model not found',
    'rlama: command not found',
    'connection refused',
    'ollama not running',
]


def safe_relative_path(file_path: Path, base_folder: Path) -> str:
    """Get relative path safely, handling Python <3.9 and edge cases."""
    try:
        return str(file_path.relative_to(base_folder))
    except ValueError:
        return file_path.name


def is_skippable_error(stderr: str) -> bool:
    """Check if error is one we should skip and continue."""
    stderr_lower = stderr.lower()
    return any(err in stderr_lower for err in SKIP_ERRORS)


def is_fatal_error(stderr: str) -> bool:
    """Check if error is fatal and we should abort."""
    stderr_lower = stderr.lower()
    return any(err in stderr_lower for err in FATAL_ERRORS)


def get_supported_files(
    folder_path: Path,
    docs_only: bool = False,
    process_exts: Optional[List[str]] = None,
    exclude_exts: Optional[List[str]] = None,
    exclude_dirs: Optional[List[str]] = None,
) -> List[Path]:
    """Get list of supported files from folder."""

    # Determine which extensions to use
    if process_exts:
        allowed_exts = set(ext if ext.startswith('.') else f'.{ext}' for ext in process_exts)
    elif docs_only:
        allowed_exts = DOC_EXTENSIONS
    else:
        allowed_exts = SUPPORTED_EXTENSIONS

    # Extensions to exclude
    excluded_exts = set()
    if exclude_exts:
        excluded_exts = set(ext if ext.startswith('.') else f'.{ext}' for ext in exclude_exts)

    # Directories to exclude
    excluded_dirs = {'.git', '.osgrep', '.claude', 'node_modules', '__pycache__', 'venv', '.venv'}
    if exclude_dirs:
        excluded_dirs.update(exclude_dirs)

    files = []
    for root, dirs, filenames in os.walk(folder_path):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for filename in filenames:
            ext = Path(filename).suffix.lower()
            if ext in allowed_exts and ext not in excluded_exts:
                files.append(Path(root) / filename)

    return sorted(files)


def run_rlama_command(args: List[str], timeout: int = 300) -> Tuple[str, str, int]:
    """Run an rlama command and return (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(
            ['rlama'] + args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return '', f'Command timed out after {timeout} seconds', 1
    except FileNotFoundError:
        return '', 'rlama command not found. Is RLAMA installed?', 1
    except (KeyboardInterrupt, SystemExit):
        raise  # Re-raise to allow proper termination
    except Exception as e:
        return '', f'Unexpected error: {str(e)}', 1


def create_initial_rag(
    rag_name: str,
    model: str,
    chunking: str,
    chunk_size: int,
    chunk_overlap: int,
) -> bool:
    """Create an initial RAG with a dummy file to establish the RAG structure."""

    # Create a temporary file with minimal content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('Initial RAG setup file. This can be removed.')
        temp_file = f.name

    try:
        cmd = [
            'rag', model, rag_name, temp_file,
            '--chunking', chunking,
            '--chunk-size', str(chunk_size),
            '--chunk-overlap', str(chunk_overlap),
        ]

        stdout, stderr, code = run_rlama_command(cmd, timeout=120)

        if code != 0:
            if is_fatal_error(stderr):
                print(f'Fatal error creating RAG: {stderr}', file=sys.stderr)
                return False
            print(f'Warning during RAG creation: {stderr}', file=sys.stderr)

        return True
    finally:
        # Clean up temp file (ignore errors if already deleted)
        try:
            os.unlink(temp_file)
        except OSError:
            pass


def add_single_file(rag_name: str, file_path: Path) -> Tuple[bool, str]:
    """Add a single file to the RAG. Returns (success, error_message)."""

    cmd = ['add-docs', rag_name, str(file_path)]
    stdout, stderr, code = run_rlama_command(cmd, timeout=120)

    if code == 0:
        return True, ''

    return False, stderr


def _process_files(rag_name: str, files: List[Path], base_folder: Path) -> Tuple[int, int, List[str], Optional[str]]:
    """
    Process files one by one, returning (added, skipped, skipped_files, fatal_error).

    If fatal_error is not None, processing was aborted due to a fatal error.
    """
    added = 0
    skipped = 0
    skipped_files = []

    for i, file_path in enumerate(files, 1):
        rel_path = safe_relative_path(file_path, base_folder)
        print(f'[{i}/{len(files)}] {rel_path}...', end=' ', flush=True)

        success, error = add_single_file(rag_name, file_path)

        if success:
            print('✓')
            added += 1
        else:
            if is_fatal_error(error):
                print(f'\nFatal error: {error}', file=sys.stderr)
                return added, skipped, skipped_files, error
            elif is_skippable_error(error):
                print('⚠ skipped (context overflow)')
                skipped += 1
                skipped_files.append(rel_path)
            else:
                # Show full error for debugging (don't truncate)
                print('⚠ skipped')
                print(f'    Error: {error}', file=sys.stderr)
                skipped += 1
                skipped_files.append(rel_path)

    return added, skipped, skipped_files, None


def _print_summary(added: int, skipped: int, skipped_files: List[str]) -> None:
    """Print processing summary."""
    print()
    print(f'Done! Added {added} files, skipped {skipped} files')

    if skipped_files:
        print(f'\nSkipped files:')
        for f in skipped_files:
            print(f'  - {f}')


def resilient_create(
    rag_name: str,
    folder_path: str,
    model: str = DEFAULT_MODEL,
    chunking: str = 'hybrid',
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    docs_only: bool = False,
    process_exts: Optional[List[str]] = None,
    exclude_exts: Optional[List[str]] = None,
    exclude_dirs: Optional[List[str]] = None,
) -> dict:
    """Create a RAG, processing files individually and skipping failures."""

    folder = Path(folder_path).expanduser().resolve()

    if not folder.exists():
        return {
            'success': False,
            'error': f'Folder not found: {folder}',
            'added': 0,
            'skipped': 0,
            'skipped_files': [],
        }

    # Get list of files to process
    files = get_supported_files(
        folder,
        docs_only=docs_only,
        process_exts=process_exts,
        exclude_exts=exclude_exts,
        exclude_dirs=exclude_dirs,
    )

    if not files:
        return {
            'success': False,
            'error': 'No supported files found in folder',
            'added': 0,
            'skipped': 0,
            'skipped_files': [],
        }

    print(f'Found {len(files)} files to index')
    print(f'Creating RAG "{rag_name}" with model {model}...')
    print()

    # Create initial RAG structure
    if not create_initial_rag(rag_name, model, chunking, chunk_size, chunk_overlap):
        return {
            'success': False,
            'error': 'Failed to create initial RAG structure',
            'added': 0,
            'skipped': 0,
            'skipped_files': [],
        }

    # Process files
    added, skipped, skipped_files, fatal_error = _process_files(rag_name, files, folder)

    if fatal_error:
        return {
            'success': False,
            'error': fatal_error,
            'added': added,
            'skipped': skipped,
            'skipped_files': skipped_files,
        }

    _print_summary(added, skipped, skipped_files)

    return {
        'success': True,
        'added': added,
        'skipped': skipped,
        'skipped_files': skipped_files,
    }


def resilient_add(
    rag_name: str,
    folder_path: str,
    docs_only: bool = False,
    process_exts: Optional[List[str]] = None,
    exclude_exts: Optional[List[str]] = None,
    exclude_dirs: Optional[List[str]] = None,
) -> dict:
    """Add files to an existing RAG, processing individually and skipping failures."""

    folder = Path(folder_path).expanduser().resolve()

    # Handle single file
    if folder.is_file():
        print(f'Adding single file: {folder.name}')
        success, error = add_single_file(rag_name, folder)

        if success:
            print('✓ Added successfully')
            return {'success': True, 'added': 1, 'skipped': 0, 'skipped_files': []}
        else:
            print(f'⚠ Failed: {error}')
            return {
                'success': False,
                'added': 0,
                'skipped': 1,
                'skipped_files': [str(folder.name)],
                'error': error,
            }

    if not folder.exists():
        return {
            'success': False,
            'error': f'Folder not found: {folder}',
            'added': 0,
            'skipped': 0,
            'skipped_files': [],
        }

    # Get list of files to process
    files = get_supported_files(
        folder,
        docs_only=docs_only,
        process_exts=process_exts,
        exclude_exts=exclude_exts,
        exclude_dirs=exclude_dirs,
    )

    if not files:
        return {
            'success': False,
            'error': 'No supported files found in folder',
            'added': 0,
            'skipped': 0,
            'skipped_files': [],
        }

    print(f'Found {len(files)} files to add to "{rag_name}"')
    print()

    # Process files
    added, skipped, skipped_files, fatal_error = _process_files(rag_name, files, folder)

    if fatal_error:
        return {
            'success': False,
            'error': fatal_error,
            'added': added,
            'skipped': skipped,
            'skipped_files': skipped_files,
        }

    _print_summary(added, skipped, skipped_files)

    return {
        'success': True,
        'added': added,
        'skipped': skipped,
        'skipped_files': skipped_files,
    }


def main():
    parser = argparse.ArgumentParser(
        description='Resilient RLAMA indexing - skips problem files instead of aborting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Commands:
  create   Create a new RAG, processing files individually
  add      Add documents to an existing RAG, skipping failures

Examples:
  %(prog)s create my-rag ~/Documents
  %(prog)s create my-rag ~/Research --docs-only
  %(prog)s create my-rag ~/Code --legacy --exclude-dirs node_modules dist
  %(prog)s add my-rag ./more-docs
  %(prog)s add my-rag ~/Papers --docs-only

Unlike standard rlama commands, this script:
- Processes files one at a time
- Skips files that fail (e.g., due to embedding context overflow)
- Reports a summary of what succeeded and what was skipped
'''
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new RAG (resilient mode)')
    create_parser.add_argument('rag_name', help='Name for the new RAG')
    create_parser.add_argument('folder_path', help='Path to folder with documents')
    create_parser.add_argument('--model', '-m', default=DEFAULT_MODEL,
        help=f'LLM model (default: {DEFAULT_MODEL})')
    create_parser.add_argument('--legacy', action='store_true',
        help=f'Use {LEGACY_MODEL} instead of {DEFAULT_MODEL}')
    create_parser.add_argument('--chunking', choices=['fixed', 'semantic', 'hybrid', 'hierarchical'],
        default='hybrid', help='Chunking strategy (default: hybrid)')
    create_parser.add_argument('--chunk-size', type=int, default=1000,
        help='Chunk size in characters (default: 1000)')
    create_parser.add_argument('--chunk-overlap', type=int, default=200,
        help='Chunk overlap in characters (default: 200)')
    create_parser.add_argument('--docs-only', action='store_true',
        help='Only index documents (PDF, MD, TXT, DOCX, DOC, ORG)')
    create_parser.add_argument('--process-exts', nargs='+',
        help='Only process these file extensions')
    create_parser.add_argument('--exclude-exts', nargs='+',
        help='Exclude these file extensions')
    create_parser.add_argument('--exclude-dirs', nargs='+',
        help='Exclude these directories')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add documents to a RAG (resilient mode)')
    add_parser.add_argument('rag_name', help='Name of the existing RAG')
    add_parser.add_argument('folder_path', help='Path to folder or file to add')
    add_parser.add_argument('--docs-only', action='store_true',
        help='Only index documents (PDF, MD, TXT, DOCX, DOC, ORG)')
    add_parser.add_argument('--process-exts', nargs='+',
        help='Only process these file extensions')
    add_parser.add_argument('--exclude-exts', nargs='+',
        help='Exclude these file extensions')
    add_parser.add_argument('--exclude-dirs', nargs='+',
        help='Exclude these directories')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'create':
        # Handle --legacy flag: only apply if model wasn't explicitly changed
        if args.legacy and args.model == DEFAULT_MODEL:
            model = LEGACY_MODEL
        else:
            model = args.model

        if args.docs_only:
            print(f'Using --docs-only mode: indexing PDF, MD, TXT, DOCX, DOC, ORG only')

        result = resilient_create(
            rag_name=args.rag_name,
            folder_path=args.folder_path,
            model=model,
            chunking=args.chunking,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            docs_only=args.docs_only,
            process_exts=args.process_exts,
            exclude_exts=args.exclude_exts,
            exclude_dirs=args.exclude_dirs,
        )

        sys.exit(0 if result['success'] else 1)

    elif args.command == 'add':
        if args.docs_only:
            print(f'Using --docs-only mode: indexing PDF, MD, TXT, DOCX, DOC, ORG only')

        result = resilient_add(
            rag_name=args.rag_name,
            folder_path=args.folder_path,
            docs_only=args.docs_only,
            process_exts=args.process_exts,
            exclude_exts=args.exclude_exts,
            exclude_dirs=args.exclude_dirs,
        )

        sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
