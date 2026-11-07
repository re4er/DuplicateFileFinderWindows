# DuplicateFileFinderWindows
Duplicate file finder for Windows. Compares file content with SHA-512, shows every copy with a preview in a dark PySide6 window and moves the copies you choose to the recycle bin or deletes them permanently. A simulation shows first what would happen.

<br>
The program is a single-file Python tool for Windows that finds files with
identical content inside one or more folders, or between them, no matter how the
files are named. It compares files in four steps: size, hard link check, SHA-512
of the first 64 KB and SHA-512 of the full content. Most files are sorted out
without being read completely.

A dark mode window lists every set of identical files with a preview of images,
videos, audio, PDF and text files. The oldest copy stays unticked, and a folder
priority list can decide which copy to keep. Before anything is deleted, the
program shows a deletion plan, asks for confirmation, checks that each file and
its kept copy are unchanged since the scan and compares them byte by byte. Files
and empty folders go to the recycle bin or are deleted permanently, or a
simulation only shows what would happen. Links and Windows folders are never
touched, and the program never deletes itself. Reports can be saved as text
files.

Requirements: Windows 10 or 11, Python 3.9 or newer, PySide6 6.5 or newer.
