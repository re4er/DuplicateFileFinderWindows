r"""
================================================================================
  DUPLICATE FINDER
  Finds files with identical content inside or between folders on Windows
  and deletes the copies you choose
================================================================================

PURPOSE
  Hard disks filled over many years hold a lot of files two or more times:
  backups of backups, photo folders copied to several places, downloads saved
  twice. This program finds all files with identical content in one or more
  folders and all their subfolders, no matter how the files are named. It
  shows every copy with its full path and dates side by side and deletes the
  copies you mark, usually all but the oldest one.

MODES (main menu)
  1  Within folders    Every file that exists more than once anywhere in the
                       chosen folders. One or more folders.
  2  Between folders   Only files that exist in at least two of the chosen
                       folders. Two or more folders. If a folder holds several
                       copies of such a file, they are shown and handled like
                       all other copies. Files that are duplicated only inside
                       one folder are ignored.
  3  Selection window  Opens the selection window again for the last scan,
                       with all ticks made so far. Shown after a scan.
  The chosen folders must not lie inside each other.

WORKFLOW
  1  Console    choose the mode, the folders and the options
  2  Scan       the console shows the progress and then the largest groups
  3  Window     check the files with the preview, all copies except the
                oldest are ticked already, change the ticks where needed
  4  Console    check the deletion plan, choose the deletion method and
                confirm
  Afterwards the window can open again right away for the files that are
  left, or later with 3 in the main menu. The ticks are kept until the next
  scan, also after a simulation.
  Identical files are numbered and named by the start of their digest, for
  example "#12  3f8526d49df1e855", the same in the window, the console and
  the report.

HOW FILES ARE COMPARED
  Only the content counts. Names, extensions and dates do not matter.
    Step 1  Walk      all files are listed with their size
    Step 2  Check     files that share their size with another file are
                      checked for hard links and their dates are read
    Step 3  Start     the first 64 KB of these files are hashed
    Step 4  Content   files that still match are hashed completely
  Files with a unique size or a different start are sorted out early, without
  reading them completely, which saves most of the reading time. The hash
  function is SHA512, a cryptographic hash. Two different files with the same
  digest are practically impossible. Every digest is listed in the report and
  can be checked with PowerShell:
    Get-FileHash -Algorithm SHA512 "F:\Photos\image.jpg"
  Empty files are included, they are all identical to each other.
  Hard links are several paths of one and the same file on the disk. They are
  listed once only and reported, because deleting one of them frees no space.

SELECTION WINDOW (dark mode)
  Every set of identical files is one row with a preview image as the Windows
  Explorer shows it, its copies are listed below with folder letter, date,
  size and full path. The slider "Preview size" makes the preview images
  larger or smaller, the file type list shows only files of one type.
  * Ticked files are deleted. When the window opens for a new scan, every
    copy is ticked except the oldest one, also further copies in the same
    folder. So exactly one copy of every file stays unticked.
  * Age: for every file the older of its creation and modification date
    counts, the column "Date" shows it. Windows keeps the modification date
    when it copies a file, but sets the creation date to the time of copying,
    so the older of both dates usually belongs to the original.
  * Click a checkbox or press Space to switch the selected rows. The checkbox
    of a row with a digest ticks or unticks all its copies. Ticking every copy
    is possible, then no copy remains.
  * "Select all" ticks and "Unselect all" unticks every file shown, so with
    the file type filter for example all JPG files.
  * Folder priority: folders with drive letter, the top entry is kept first.
    A file belongs to the deepest listed folder containing it. Folders below
    the entry <all other locations> are deleted first, for example Downloads.
    "Apply folder priority" ticks all files shown anew: the copy in the
    folder with the best priority stays unticked, among equal priority the
    oldest copy, all other copies are ticked.
  * Preview: the right side shows the selected file. Videos and audio files
    can be played, PDF files up to 100 MB scrolled and text files read.
    Other files and larger PDF files show the preview image of Windows, for
    example Office documents. "Show in Explorer" opens the folder of the
    file, right click offers more.
  * "Continue with the ticked files" hands the ticks to the console, closing
    the window cancels. The ticks are kept when the window opens again.

OPTIONS ASKED FOR EVERY RUN
  * Operating system files: include or exclude. A system file is any file or
    folder with the Windows "System" attribute plus well known system items
    such as $RECYCLE.BIN, System Volume Information, pagefile.sys, desktop.ini
    or Thumbs.db. Excluded system folders are not entered at all.
  * Reports: save the list of all duplicates and a log of every deleted file
    as text files in the folder "reports" next to this script.
  * Deletion method: recycle bin (default), permanent, or a simulation that
    only shows what would be deleted. After a simulation the selection window
    can be opened again with the same scan result, without scanning again.
  * Empty folders after deleting: keep all folders, remove only the folders
    that became empty through the deletion, or remove all empty folders, also
    those that were empty before (default). Empty folders go the same way as
    the files: to the recycle bin, deleted permanently, or only shown in a
    simulation. A folder is moved to the recycle bin only if it is still
    empty right then, and empty folders on a drive without recycle bin are
    kept. The chosen folders themselves always stay. Folders holding skipped
    items, for example Thumbs.db or a link, are not empty, and excluded system
    folders are not entered.

STATUS OUTPUT
  * A live counter shows the current step and its progress.
  * Every minute a status line shows the elapsed time and the current folder
    or file.
  * At the end: groups and files found, the largest groups with full paths,
    deleted, skipped and failed files, removed folders and the duration.

SAFETY
  * Only the chosen folders and their subfolders are read. Links, junctions
    and other reparse points are never followed or deleted.
  * The recycle bin and System Volume Information currently used by Windows
    are never entered. Windows, Program Files and ProgramData with all their
    subfolders, your user profile itself and every folder containing one of
    them are refused. Folders inside the profile, for example Pictures, are
    allowed.
  * Right before a file is deleted, the program checks that it is unchanged
    since the scan (same file, size and modification time) and that a kept
    copy of it still exists unchanged. Otherwise the file is skipped. With the
    setting VERIFY_CONTENT_BEFORE_DELETION the content is also compared byte
    by byte with the kept copy.
  * Files of which every copy is ticked are listed and need an extra
    confirmation, otherwise all their copies are kept.
  * A real deletion only starts after the deletion plan was shown and
    confirmed by typing "yes" (recycle bin) or "delete" (permanent).
  * The recycle bin is only offered if every affected drive has one (internal
    and external hard disks, not USB sticks or network drives). If Windows
    cannot recycle a single file, for example because it is larger than the
    recycle bin, a Windows dialog asks before that file is deleted permanently.
    Paths longer than 259 characters and special names such as nul.txt or a
    name ending with a dot cannot be recycled at all. Such files are listed as
    failed and can be deleted with the permanent method.

REQUIREMENTS
  * Windows 10 or 11
  * Python 3.9 or newer
  * PySide6 6.5 or newer, installed with  python -m pip install PySide6
    The selection window is built on it, so the program does not start
    without it. If Python is installed for all users, install PySide6 from a
    console run as administrator, so all its parts end up in one place.
  * Everything else comes from the standard library
  * Administrator rights only for files your user account may not delete

USAGE
  python filemanagement_hashcomparison.py "F:\Photos" "G:\Backup\Photos"
  The folders can also be dragged onto the script file. Without folders the
  program asks for them. In the program the folders can be changed for each
  run by typing, pasting or dragging them into the console window.
  Questions show the possible answers in parentheses, for example (y/n), and
  the default in brackets, for example [n]. Enter takes the default.
  After a scan the console asks whether to open the selection window. Later
  it opens with 3 in the main menu. While the window is open the console
  waits, closing the window or "Continue with the ticked files" brings you
  back to the console.
  Ctrl+C stops a running scan or deletion safely and shows the results so far.
  During a question it returns to the main menu, in the main menu it ends the
  program and in the selection window it closes the window.
  Clicking into the console window pauses the program (QuickEdit mode of
  Windows), press Esc to let it continue.
  The hash function, intervals and other values can be adjusted in SETTINGS.
================================================================================
"""

# ==============================================================================
#   IMPORTS
# ==============================================================================

from __future__ import annotations

import argparse
import ctypes
import functools
import glob
import hashlib
import os
import re
import shutil
import signal
import stat
import string
import subprocess
import sys
import threading
import time
import traceback
import uuid
from ctypes import wintypes
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, Iterator, List, NamedTuple, Optional, Sequence, Set, Tuple

try:
    import shiboken6
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
    from PySide6.QtMultimediaWidgets import QVideoWidget
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtPdfWidgets import QPdfView
except ImportError as pyside_import_error:
    # The classes of the selection window are built on PySide6, so the program cannot start without it
    print(f"PySide6 is missing or incomplete: {pyside_import_error}")
    print("Install it with:  python -m pip install PySide6")
    try:
        input("Press Enter to close ...")
    except (EOFError, KeyboardInterrupt):
        pass
    sys.exit(1)


# ==============================================================================
#   SETTINGS
# ==============================================================================

HASH_ALGORITHM = "sha512"               # hashlib name, sha512 is fast on 64 bit and checkable with Get-FileHash
PARTIAL_HASH_BYTES = 64 * 1024          # start of a file that is hashed in step 3
HASH_CHUNK_BYTES = 1024 * 1024          # bytes read at once while hashing or comparing
VERIFY_CONTENT_BEFORE_DELETION = False  # also compare byte by byte with the kept copy, reads both files again
STATUS_INTERVAL_SECONDS = 60            # status line with the current folder or file
LIVE_COUNTER_INTERVAL_SECONDS = 0.5     # refresh rate of the live counter line
RECYCLE_BIN_BATCH_SIZE = 100            # files per recycle bin call, more is faster
CONSOLE_GROUP_LIMIT = 10                # largest groups listed in the console after the scan
CONSOLE_EXAMPLE_LIMIT = 15              # paths listed per problem type in the console
STORED_EXAMPLE_LIMIT = 100_000          # paths kept per problem type for reports
SHORT_DIGEST_LENGTH = 16                # characters of a digest shown in the console and the window
REPORT_FOLDER_NAME = "reports"          # created next to this script when saving reports
THUMBNAIL_DEFAULT_SIZE = 96             # edge length of the preview images in the list, the window has a slider
THUMBNAIL_THREAD_COUNT = 2              # preview images loaded at the same time, more only helps on SSDs
PREVIEW_IMAGE_MAX_PIXELS = 8000         # larger images are scaled down for the preview to save memory
PREVIEW_SHELL_IMAGE_SIZE = 1024         # size of the Windows preview image for documents and other types
PREVIEW_TEXT_BYTES = 64 * 1024          # start of a text file shown in the preview
PREVIEW_PDF_MAX_BYTES = 100 * 1024 * 1024  # PDF files are read into memory, larger ones show the Windows preview image
MEDIA_DEFAULT_VOLUME = 0.7              # volume of videos and audio files, from 0 to 1


# ==============================================================================
#   DEFINITIONS
# ==============================================================================

# ==== General =================================================================

PROGRAM_TITLE = "DUPLICATE FINDER"
PROGRAM_SUBTITLE = "Finds identical files inside or between folders and deletes the copies you choose"
LINE_WIDTH = 80
HASH_NAME = HASH_ALGORITHM.upper()      # SHA512 is also the name Get-FileHash uses
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
UNKNOWN_TIMESTAMP_TEXT = "unknown"
YES_ANSWERS = frozenset({"y", "yes", "j", "ja"})
NO_ANSWERS = frozenset({"n", "no", "nein"})

# ==== Operating system items ==================================================

# Folder names that always belong to Windows, compared in lower case
OPERATING_SYSTEM_FOLDER_NAMES = frozenset({
    "$recycle.bin",                     # recycle bin since Windows Vista
    "recycler",                         # recycle bin of Windows XP
    "recycled",                         # recycle bin of Windows 98 and old FAT drives
    "system volume information",        # restore points, search index, volume data
    "$windows.~bt",                     # Windows upgrade data
    "$windows.~ws",                     # Windows upgrade data
    "$winreagent",                      # Windows recovery agent data
    "$sysreset",                        # Windows reset data
    "config.msi",                       # Windows Installer rollback data
})

# File names that always belong to Windows, compared in lower case
OPERATING_SYSTEM_FILE_NAMES = frozenset({
    "pagefile.sys", "swapfile.sys", "hiberfil.sys",     # virtual memory and hibernation
    "desktop.ini", "thumbs.db", "ehthumbs.db",          # Explorer folder settings and thumbnails
    "ehthumbs_vista.db", "iconcache.db",                # Explorer caches
    "bootmgr", "bootnxt", "bootsect.bak",               # Windows boot manager
    "ntldr", "ntdetect.com", "boot.ini",                # Windows XP boot files
    "io.sys", "msdos.sys",                              # DOS and Windows 98 boot files
    "dumpstack.log", "dumpstack.log.tmp",               # crash dump logs
})

# Folders in the root of a drive that Windows is using right now.
# They are never entered, not even when system files are included.
ACTIVE_VOLUME_FOLDER_NAMES = ("$recycle.bin", "system volume information")

# ==== Paths and names =========================================================

EXTENDED_PATH_PREFIX = "\\\\?\\"            # lifts the 260 character limit of Windows paths
EXTENDED_UNC_PATH_PREFIX = "\\\\?\\UNC\\"   # the same for network paths
UNSAFE_NAME_CHARACTERS = frozenset('<>:"|?*')   # invalid in Windows names, * and ? are wildcards
RESERVED_DEVICE_NAMES = frozenset(
    ["CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"]
    + [f"COM{number}" for number in range(10)]
    + [f"LPT{number}" for number in range(10)]
)

# ==== Windows API =============================================================

FO_DELETE = 0x0003                      # SHFileOperationW: delete operation
FOF_SILENT = 0x0004                     # no progress dialog
FOF_NOCONFIRMATION = 0x0010             # no "are you sure" questions
FOF_ALLOWUNDO = 0x0040                  # use the recycle bin
FOF_NOERRORUI = 0x0400                  # no error dialogs
FOF_WANTNUKEWARNING = 0x4000            # ask before a file is deleted permanently instead of recycled
RECYCLE_BIN_FLAGS = (FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
                     | FOF_NOERRORUI | FOF_WANTNUKEWARNING)
SHELL_MAX_PATH_LENGTH = 259             # MAX_PATH without the terminating null character
VOLUME_PATH_BUFFER_LENGTH = 32768
DRIVE_FIXED = 3                         # GetDriveTypeW: internal or external hard disk
COINIT_APARTMENTTHREADED = 0x2          # CoInitializeEx: the COM mode the Windows shell expects
S_OK = 0
S_FALSE = 1                             # COM was initialized before, still needs CoUninitialize
SIIGBF_RESIZETOFIT = 0x0                # IShellItemImageFactory: preview image or icon fitted into the size
IMAGE_FACTORY_INTERFACE_ID = "bcc18b79-ba16-442f-80c4-8a59c30c463b"    # IShellItemImageFactory
COM_RELEASE_METHOD_INDEX = 2            # position of Release in the method table of every COM object
IMAGE_FACTORY_GET_IMAGE_METHOD_INDEX = 3
COM_RELEASE_PROTOTYPE = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)
IMAGE_FACTORY_GET_IMAGE_PROTOTYPE = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, wintypes.SIZE,
                                                       ctypes.c_int, ctypes.POINTER(wintypes.HBITMAP))
BI_RGB = 0                              # uncompressed bitmap
DIB_RGB_COLORS = 0
HWND_TOPMOST = -1                       # SetWindowPos: show a window above all others
HWND_NOTOPMOST = -2
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_SHOWWINDOW = 0x0040

DRIVE_TYPE_NAMES = {
    0: "unknown drive",
    1: "invalid drive",
    2: "removable drive",
    3: "hard disk",
    4: "network drive",
    5: "optical drive",
    6: "RAM disk",
}

# Return codes of SHFileOperationW
SHELL_ERROR_MESSAGES = {
    0x02: "file not found",
    0x05: "access denied",
    0x20: "file is used by another program",
    0x75: "cancelled in the Windows dialog",
    0x78: "access denied",
    0x79: "path too deep",
    0x7C: "invalid path",
    0x81: "file name too long",
    0x85: "file too large for the recycle bin",
    0x402: "unknown error of the Windows shell",
    0x4C7: "cancelled in the Windows dialog",
}
SHELL_CANCEL_CODES = frozenset({0x75, 0x4C7})

# ==== Selection window ========================================================

WINDOW_TITLE = "Duplicate Finder"
OTHER_LOCATIONS_ENTRY = "<all other locations>"     # placeholder in the priority list, < is invalid in paths
TREE_COLUMN_TITLES = ("File", "Folder", "Date", "Size", "Full path")
COLUMN_NAME, COLUMN_FOLDER, COLUMN_DATE, COLUMN_SIZE, COLUMN_PATH = range(5)
TREE_COLUMN_WIDTHS = {COLUMN_NAME: 320, COLUMN_FOLDER: 60, COLUMN_DATE: 150, COLUMN_SIZE: 90}
PATH_COLUMN_MINIMUM_WIDTH = 500
PATH_COLUMN_MAXIMUM_WIDTH = 4000
GROUP_DETAIL_ROLE = QtCore.Qt.ItemDataRole.UserRole + 1     # grey second line of a header row
GROUP_WARNING_ROLE = QtCore.Qt.ItemDataRole.UserRole + 2    # True if every copy is ticked
CHECK_STATE_FLAGS = {
    QtCore.Qt.CheckState.Unchecked: QtWidgets.QStyle.StateFlag.State_Off,
    QtCore.Qt.CheckState.PartiallyChecked: QtWidgets.QStyle.StateFlag.State_NoChange,
    QtCore.Qt.CheckState.Checked: QtWidgets.QStyle.StateFlag.State_On,
}
WINDOW_SCREEN_SHARE = 0.9               # part of the screen the window covers when it opens
SPLITTER_SIZES = [270, 1000, 480]       # priority, file list and preview, the file list gets extra space
THUMBNAIL_SOURCE_SIZE = 256             # size requested from Windows, the list scales it down
THUMBNAIL_MINIMUM_SIZE = 32
THUMBNAIL_MAXIMUM_SIZE = 256
THUMBNAIL_SIZE_STEP = 16
SINGLE_REFRESH_GROUP_LIMIT = 50         # changes of more rows redraw the whole list at once
INTERRUPT_CHECK_MILLISECONDS = 250      # lets Ctrl+C in the console reach the window
PREVIEW_DELAY_MILLISECONDS = 150        # the preview loads when the selection rests that long
THUMBNAIL_DELAY_MILLISECONDS = 80       # preview images load when scrolling rests that long
QT_LOGGING_RULES = "qt.multimedia.ffmpeg*=false"   # keeps messages of the video decoder out of the console
FFMPEG_UTILITY_LIBRARY_PATTERN = "avutil-*.dll"     # FFmpeg library that PySide6 brings along
AV_LOG_QUIET = -8                       # av_log_set_level: FFmpeg prints nothing

PRIORITY_HELP_TEXT = (
    "Folders with drive letter. A file belongs to the deepest listed folder containing it. "
    "Among equal priority the oldest file is kept."
)
LIST_HELP_TEXT = "Ticked files are deleted. Space switches the selected rows, right click shows more."
REOPEN_HINT = "Choose 3 in the main menu to open the selection window again, the ticks are kept."

# ==== Window theme ============================================================

# Spacing in pixels
WINDOW_MARGIN = 12
CARD_PADDING = 12
CARD_SPACING = 8
SPLITTER_HANDLE_WIDTH = 10
ROW_PADDING = 6                         # space above and below the content of a list row
HEADER_TEXT_INDENT = 6                  # gap between preview image and text in a header row
HEADER_LINE_GAP = 2                     # gap between the two lines of a header row

# Neutral dark greys, one blue accent, red for ticked files, amber for files without a kept copy
WINDOW_COLOR = "#1e1f22"                # background behind the panels
SURFACE_COLOR = "#2b2d30"               # panels
BASE_COLOR = "#1e1f22"                  # lists and input fields inside the panels
BORDER_COLOR = "#393b40"
BUTTON_COLOR = "#36383c"
BUTTON_HOVER_COLOR = "#424549"
BUTTON_BORDER_COLOR = "#4e5157"
TEXT_COLOR = "#dfe1e5"
SECONDARY_TEXT_COLOR = "#8c9096"
DISABLED_TEXT_COLOR = "#5f6268"
ACCENT_COLOR = "#3574f0"
ACCENT_HOVER_COLOR = "#4a84f5"
SELECTION_COLOR = "#2e436e"
GROUP_ROW_COLOR = "#26282c"
DELETE_ROW_COLOR = "#3a2427"            # ticked file
DELETE_TEXT_COLOR = "#f08b84"
WARNING_ROW_COLOR = "#3a3221"           # every copy is ticked
WARNING_TEXT_COLOR = "#e0b45a"
PREVIEW_BACKGROUND_COLOR = "#161719"
THUMBNAIL_PLACEHOLDER_COLOR = "#33363a"
SCROLLBAR_COLOR = "#4e5157"

# $NAME stands for the color constant of the same name
STYLE_SHEET_TEMPLATE = """
QWidget { color: $TEXT_COLOR; }
QMainWindow, QWidget#root { background: $WINDOW_COLOR; }
QFrame#card { background: $SURFACE_COLOR; border: 1px solid $BORDER_COLOR; border-radius: 8px; }
QLabel { background: transparent; border: none; }
QLabel#sectionTitle { color: $SECONDARY_TEXT_COLOR; font-weight: 600; letter-spacing: 1px; }
QLabel#secondary { color: $SECONDARY_TEXT_COLOR; }
QLabel#warning { color: $WARNING_TEXT_COLOR; font-weight: 600; }
QLabel#badge { background: $BUTTON_COLOR; border: 1px solid $BUTTON_BORDER_COLOR; border-radius: 4px;
               padding: 1px 7px; font-weight: 600; }
QPushButton { background: $BUTTON_COLOR; border: 1px solid $BUTTON_BORDER_COLOR; border-radius: 5px;
              padding: 5px 12px; }
QPushButton:hover { background: $BUTTON_HOVER_COLOR; }
QPushButton:pressed { background: $BORDER_COLOR; }
QPushButton:disabled { color: $DISABLED_TEXT_COLOR; border-color: $BORDER_COLOR; }
QPushButton#primary { background: $ACCENT_COLOR; border-color: $ACCENT_COLOR; color: #ffffff; font-weight: 600; }
QPushButton#primary:hover { background: $ACCENT_HOVER_COLOR; border-color: $ACCENT_HOVER_COLOR; }
QLineEdit, QComboBox { background: $BASE_COLOR; border: 1px solid $BUTTON_BORDER_COLOR; border-radius: 5px;
                       padding: 4px 8px; selection-background-color: $SELECTION_COLOR; }
QLineEdit:focus, QComboBox:focus, QComboBox:on { border-color: $ACCENT_COLOR; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView { background: $SURFACE_COLOR; border: 1px solid $BORDER_COLOR; outline: none;
                              selection-background-color: $SELECTION_COLOR; }
QListWidget { background: $BASE_COLOR; border: 1px solid $BORDER_COLOR; border-radius: 5px; padding: 3px;
              outline: none; }
QListWidget::item { padding: 5px 6px; border-radius: 4px; }
QListWidget::item:selected { background: $SELECTION_COLOR; color: $TEXT_COLOR; }
QTreeView { background: $BASE_COLOR; border: 1px solid $BORDER_COLOR; outline: none;
            selection-background-color: $SELECTION_COLOR; selection-color: $TEXT_COLOR; }
QHeaderView { background: $SURFACE_COLOR; border: none; }
QHeaderView::section { background: $SURFACE_COLOR; color: $SECONDARY_TEXT_COLOR; border: none;
                       border-bottom: 1px solid $BORDER_COLOR; padding: 5px 8px; font-weight: 600; }
QSplitter::handle { background: $WINDOW_COLOR; }
QSlider::groove:horizontal { height: 4px; background: $BORDER_COLOR; border-radius: 2px; }
QSlider::sub-page:horizontal { background: $ACCENT_COLOR; border-radius: 2px; }
QSlider::handle:horizontal { background: $TEXT_COLOR; width: 12px; height: 12px; margin: -4px 0;
                             border-radius: 6px; }
QScrollBar:vertical { background: transparent; width: 11px; margin: 0px; }
QScrollBar:horizontal { background: transparent; height: 11px; margin: 0px; }
QScrollBar::handle:vertical { background: $SCROLLBAR_COLOR; border-radius: 4px; min-height: 32px; margin: 2px; }
QScrollBar::handle:horizontal { background: $SCROLLBAR_COLOR; border-radius: 4px; min-width: 32px; margin: 2px; }
QScrollBar::handle:hover { background: $SECONDARY_TEXT_COLOR; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0px; height: 0px; }
QScrollBar::add-page, QScrollBar::sub-page { background: none; }
QToolButton { background: transparent; border: none; border-radius: 4px; padding: 4px; }
QToolButton:hover { background: $BUTTON_HOVER_COLOR; }
QPlainTextEdit { background: $PREVIEW_BACKGROUND_COLOR; border: none; border-radius: 6px; padding: 6px; }
QToolTip { background: $SURFACE_COLOR; color: $TEXT_COLOR; border: 1px solid $BORDER_COLOR; padding: 4px; }
QMenu { background: $SURFACE_COLOR; border: 1px solid $BORDER_COLOR; padding: 4px; }
QMenu::item { padding: 5px 18px; border-radius: 4px; }
QMenu::item:selected { background: $SELECTION_COLOR; }
QMenu::separator { height: 1px; background: $BORDER_COLOR; margin: 4px 6px; }
"""

# ==== Preview =================================================================

PDF_EXTENSIONS = frozenset({".pdf"})
VIDEO_EXTENSIONS = frozenset({
    ".mp4", ".m4v", ".mov", ".avi", ".mkv", ".wmv", ".mpg", ".mpeg", ".m2ts", ".mts", ".ts",
    ".webm", ".3gp", ".flv", ".ogv", ".vob",
})
AUDIO_EXTENSIONS = frozenset({
    ".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".oga", ".wma", ".opus", ".aif", ".aiff",
})
TEXT_EXTENSIONS = frozenset({
    ".txt", ".log", ".csv", ".tsv", ".md", ".json", ".xml", ".ini", ".cfg", ".conf", ".yaml", ".yml",
    ".py", ".ps1", ".bat", ".cmd", ".sql", ".html", ".htm", ".css", ".js", ".srt", ".nfo",
})

# ==== Choices =================================================================


class MainMenuChoice(Enum):
    """Entries of the main menu."""

    WITHIN_FOLDERS = "within folders"
    BETWEEN_FOLDERS = "between folders"
    SELECTION_WINDOW = "selection window"


class CompareMode(Enum):
    """How the folders are compared."""

    WITHIN_FOLDERS = "within the folders"
    BETWEEN_FOLDERS = "between the folders"


class DeletionMethod(Enum):
    """How marked files are removed."""

    RECYCLE_BIN = "move to the recycle bin"
    PERMANENT = "delete permanently"
    SIMULATION = "simulation, nothing is deleted"


class EmptyFolderPolicy(Enum):
    """What happens with empty folders after deleting."""

    KEEP = "keep all folders"
    REMOVE_EMPTIED = "remove folders that became empty through this deletion"
    REMOVE_ALL = "remove all empty folders, also those that were empty before"


class PreviewKind(Enum):
    """How the preview shows a file."""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "PDF document"
    TEXT = "text"
    OTHER = "other file type"


# ==============================================================================
#   CLASSES
# ==============================================================================

# ==== Data structures =========================================================


class FileRecord(NamedTuple):
    """A file found by the folder walk."""

    path: str               # extended length path, used for all file operations
    size_bytes: int


class FolderContent(NamedTuple):
    """Everything the folder walk found in one folder."""

    path: str                       # extended length path
    parent_path: Optional[str]      # None for a chosen folder itself
    files: List[FileRecord]         # files that may be processed
    entry_count: Optional[int]      # all entries including skipped ones, None if unreadable


class FoundFile(NamedTuple):
    """A file of the walk that shares its size with at least one other file."""

    walk_index: int         # position in the walk, reading in this order keeps disk seeks short
    path: str               # extended length path
    root_index: int         # position of its folder in the folder list
    size_bytes: int


@dataclass
class DuplicateFile:
    """A file with at least one identical copy, with everything needed to choose and delete."""

    walk_index: int
    path: str                       # extended length path, used for all file operations
    display_path: str               # path without prefix, for output
    comparison_path: str            # display path in lower case, for comparing paths
    root_index: int                 # position of its folder in the folder list
    size_bytes: int
    creation_time_ns: int
    modification_time_ns: int
    file_id: Tuple[int, int]        # volume serial number and file index, the index is 0 if unknown

    @property
    def oldest_time_ns(self) -> int:
        """The older of creation and modification date, which decides about the age."""
        return min(self.creation_time_ns, self.modification_time_ns)


@dataclass
class DuplicateGroup:
    """Files with identical content."""

    number: int                     # position in the list, largest reclaimable size first
    digest: str
    size_bytes: int                 # size of each single file
    files: List[DuplicateFile]

    @property
    def reclaimable_bytes(self) -> int:
        """Space that is freed when exactly one copy is kept."""
        return self.size_bytes * (len(self.files) - 1)

    @property
    def root_indexes(self) -> List[int]:
        return sorted({duplicate_file.root_index for duplicate_file in self.files})

    def folders_with_several_copies(self) -> List[Tuple[int, int]]:
        """(root index, number of copies) of every folder holding more than one copy."""
        copy_counts: Dict[int, int] = {}
        for duplicate_file in self.files:
            copy_counts[duplicate_file.root_index] = copy_counts.get(duplicate_file.root_index, 0) + 1
        return [(root_index, count) for root_index, count in sorted(copy_counts.items()) if count > 1]


@dataclass
class SizeStatistics:
    """Number of files and their total size."""

    file_count: int = 0
    total_bytes: int = 0

    def add(self, size_bytes: int) -> None:
        self.file_count += 1
        self.total_bytes += size_bytes


@dataclass
class PathCollection:
    """Counts paths of one kind and keeps the first ones as examples."""

    count: int = 0
    total_bytes: int = 0
    examples: List[Tuple[str, str]] = field(default_factory=list)

    def add(self, path: str, note: str = "", size_bytes: int = 0) -> None:
        self.count += 1
        self.total_bytes += size_bytes
        if len(self.examples) < STORED_EXAMPLE_LIMIT:
            self.examples.append((path, note))


@dataclass
class WalkStatistics:
    """Folders read by the walk and everything it skipped."""

    folders_read: int = 0
    skipped_system_files: PathCollection = field(default_factory=PathCollection)
    skipped_system_folders: PathCollection = field(default_factory=PathCollection)
    skipped_links: PathCollection = field(default_factory=PathCollection)
    unreadable_items: PathCollection = field(default_factory=PathCollection)


@dataclass
class ScanStatistics:
    """Numbers of the four steps and the files sorted out on the way."""

    files_found: int = 0
    bytes_found: int = 0
    same_size_files: int = 0        # candidates after step 1
    checked_files: int = 0          # candidates after step 2
    same_start_files: int = 0       # candidates after step 3
    hashed_bytes: int = 0           # bytes read in steps 3 and 4
    hard_links: PathCollection = field(default_factory=PathCollection)
    unreadable_files: PathCollection = field(default_factory=PathCollection)
    changed_files: PathCollection = field(default_factory=PathCollection)


@dataclass
class ScanResult:
    """Outcome of a scan."""

    mode: CompareMode
    root_folders: List[str]
    include_system_files: bool
    groups: List[DuplicateGroup]
    walk_statistics: WalkStatistics
    scan_statistics: ScanStatistics
    duration_seconds: float
    was_cancelled: bool

    @property
    def duplicate_file_count(self) -> int:
        return sum(len(group.files) for group in self.groups)

    @property
    def reclaimable_bytes(self) -> int:
        return sum(group.reclaimable_bytes for group in self.groups)

    @property
    def groups_with_internal_copies(self) -> int:
        return sum(1 for group in self.groups if group.folders_with_several_copies())


@dataclass
class SelectionState:
    """Choices made in the selection window, kept for its next opening."""

    marked_paths: Set[str] = field(default_factory=set)        # extended paths of files marked for deletion
    priority_entries: List[str] = field(default_factory=lambda: [OTHER_LOCATIONS_ENTRY])
    rules_applied: bool = False         # the first opening ticks all copies except the one to keep


@dataclass
class GroupDecision:
    """Files of one group that are deleted and kept."""

    group: DuplicateGroup
    files_to_delete: List[DuplicateFile]
    files_to_keep: List[DuplicateFile]


@dataclass
class DeletionPlan:
    """All decisions for one deletion run."""

    scan_result: ScanResult
    decisions: List[GroupDecision]
    method: DeletionMethod
    empty_folder_policy: EmptyFolderPolicy
    verify_content: bool

    @property
    def file_count(self) -> int:
        return sum(len(decision.files_to_delete) for decision in self.decisions)

    @property
    def total_bytes(self) -> int:
        return sum(len(decision.files_to_delete) * decision.group.size_bytes for decision in self.decisions)

    @property
    def groups_without_copy(self) -> int:
        return sum(1 for decision in self.decisions if not decision.files_to_keep)

    def statistics_per_folder(self) -> Dict[int, SizeStatistics]:
        statistics_by_root: Dict[int, SizeStatistics] = {}
        for decision in self.decisions:
            for duplicate_file in decision.files_to_delete:
                statistics_by_root.setdefault(duplicate_file.root_index, SizeStatistics()).add(
                    duplicate_file.size_bytes)
        return statistics_by_root


@dataclass
class DeletionResult:
    """Outcome of a deletion run."""

    plan: DeletionPlan
    deleted_paths: Set[str] = field(default_factory=set)      # extended paths, in a simulation the ones it would delete
    deleted_files: PathCollection = field(default_factory=PathCollection)
    skipped_files: PathCollection = field(default_factory=PathCollection)
    failed_files: PathCollection = field(default_factory=PathCollection)
    removed_folders: PathCollection = field(default_factory=PathCollection)
    failed_folders: PathCollection = field(default_factory=PathCollection)
    duration_seconds: float = 0.0
    was_cancelled: bool = False


@dataclass
class FolderState:
    """Bookkeeping of one folder for the removal of empty folders."""

    parent_path: Optional[str]          # None for a chosen folder, which is never removed
    entry_count: Optional[int]          # None if the folder could not be read
    volume: TargetVolume                # drive of its chosen folder, decides whether it can be recycled
    deleted_file_count: int = 0         # files deleted in it, or that a simulation would delete
    removed_subfolder_count: int = 0


# ==== Windows integration =====================================================


class ShellFileOperation(ctypes.Structure):
    """SHFILEOPSTRUCTW of the Windows shell API, byte packed on 32 bit Python."""

    _pack_ = 1 if ctypes.sizeof(ctypes.c_void_p) == 4 else 8
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("wFunc", wintypes.UINT),
        ("pFrom", wintypes.LPCWSTR),
        ("pTo", wintypes.LPCWSTR),
        ("fFlags", wintypes.WORD),
        ("fAnyOperationsAborted", wintypes.BOOL),
        ("hNameMappings", wintypes.LPVOID),
        ("lpszProgressTitle", wintypes.LPCWSTR),
    ]


class ComGuid(ctypes.Structure):
    """GUID of the Windows COM API, identifies an interface."""

    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


class WindowsBitmap(ctypes.Structure):
    """BITMAP of the Windows GDI API, describes the bitmap behind a handle."""

    _fields_ = [
        ("bmType", wintypes.LONG),
        ("bmWidth", wintypes.LONG),
        ("bmHeight", wintypes.LONG),
        ("bmWidthBytes", wintypes.LONG),
        ("bmPlanes", wintypes.WORD),
        ("bmBitsPixel", wintypes.WORD),
        ("bmBits", ctypes.c_void_p),
    ]


class BitmapInfoHeader(ctypes.Structure):
    """BITMAPINFOHEADER of the Windows GDI API, the pixel format GetDIBits delivers."""

    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class TargetVolume:
    """Drive that holds a folder and whether it has a recycle bin."""

    def __init__(self, folder: str) -> None:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        get_volume_path_name = kernel32.GetVolumePathNameW
        get_volume_path_name.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        get_volume_path_name.restype = wintypes.BOOL
        get_drive_type = kernel32.GetDriveTypeW
        get_drive_type.argtypes = [wintypes.LPCWSTR]
        get_drive_type.restype = wintypes.UINT

        volume_path_buffer = ctypes.create_unicode_buffer(VOLUME_PATH_BUFFER_LENGTH)
        if get_volume_path_name(folder, volume_path_buffer, VOLUME_PATH_BUFFER_LENGTH):
            self.root_path = volume_path_buffer.value
        else:
            self.root_path = os.path.splitdrive(folder)[0] + "\\"
        self.drive_type = int(get_drive_type(self.root_path))

    @property
    def supports_recycle_bin(self) -> bool:
        return self.drive_type == DRIVE_FIXED

    @property
    def description(self) -> str:
        return f"{self.root_path} ({DRIVE_TYPE_NAMES.get(self.drive_type, 'unknown drive')})"


class RecycleBin:
    """Moves files to the Windows recycle bin through the Windows shell."""

    def __init__(self) -> None:
        shell32 = ctypes.WinDLL("shell32")
        self._shell_file_operation = shell32.SHFileOperationW
        self._shell_file_operation.argtypes = [ctypes.POINTER(ShellFileOperation)]
        self._shell_file_operation.restype = ctypes.c_int

    def move_files(self, file_paths: List[str]) -> Dict[str, Optional[str]]:
        """Recycle files and return an error message per path, None means success."""
        outcomes: Dict[str, Optional[str]] = {}
        shell_paths: Dict[str, str] = {}
        for file_path in file_paths:
            display_path = to_display_path(file_path)
            if is_path_usable_by_shell(display_path):
                shell_paths[file_path] = display_path
            else:
                outcomes[file_path] = ("the recycle bin cannot handle this path (too long or special name), "
                                       "use permanent deletion")
        if shell_paths:
            outcomes.update(self._recycle_and_verify(shell_paths))
        return outcomes

    def _recycle_and_verify(self, shell_paths: Dict[str, str]) -> Dict[str, Optional[str]]:
        """Recycle a group of files and check which of them are really gone."""
        return_code, operations_aborted = self._run_shell_operation(list(shell_paths.values()))
        outcomes: Dict[str, Optional[str]] = {}
        remaining_paths: Dict[str, str] = {}
        for file_path, display_path in shell_paths.items():
            if os.path.lexists(file_path):
                remaining_paths[file_path] = display_path
            else:
                outcomes[file_path] = None
        if not remaining_paths:
            return outcomes

        was_cancelled = return_code in SHELL_CANCEL_CODES or (operations_aborted and return_code == 0)
        if len(shell_paths) == 1 or was_cancelled:
            error_message = describe_shell_result(return_code, was_cancelled)
            outcomes.update((file_path, error_message) for file_path in remaining_paths)
            return outcomes

        # The shell stops a group at the first problem, so the rest is retried one by one
        for file_path, display_path in remaining_paths.items():
            outcomes.update(self._recycle_and_verify({file_path: display_path}))
        return outcomes

    def _run_shell_operation(self, display_paths: List[str]) -> Tuple[int, bool]:
        """Call SHFileOperationW once for all paths and return its result."""
        # The shell expects all paths in one buffer, separated and ended by null characters
        path_list = "\0".join(display_paths) + "\0\0"
        path_buffer = ctypes.create_string_buffer(path_list.encode("utf-16-le", "surrogatepass"))
        operation = ShellFileOperation()
        operation.hwnd = None
        operation.wFunc = FO_DELETE
        operation.pFrom = wintypes.LPCWSTR(ctypes.addressof(path_buffer))
        operation.pTo = None
        operation.fFlags = RECYCLE_BIN_FLAGS
        return_code = self._shell_file_operation(ctypes.byref(operation))
        return return_code & 0xFFFFFFFF, bool(operation.fAnyOperationsAborted)


class InterruptGuard:
    """Turns Ctrl+C into a flag, so running work can stop at a safe point."""

    def __init__(self) -> None:
        self.was_requested = False
        self._previous_handler = None

    def __enter__(self) -> InterruptGuard:
        self.was_requested = False
        self._previous_handler = signal.signal(signal.SIGINT, self._request_stop)
        return self

    def __exit__(self, *exception_info) -> None:
        signal.signal(signal.SIGINT, self._previous_handler or signal.default_int_handler)

    def _request_stop(self, signal_number, stack_frame) -> None:
        if not self.was_requested:
            print("\n  Ctrl+C received, stopping at the next safe point ...", flush=True)
        self.was_requested = True


# ==== Folder walk =============================================================


class FolderWalker:
    """Walks through all subfolders of a folder without ever leaving it.

    Links, junctions and other reparse points are neither followed nor
    returned, so the walk cannot be redirected to a place outside the folder.
    """

    def __init__(self, root_folder: str, include_system_items: bool, volume_root: str,
                 statistics: WalkStatistics) -> None:
        self.root_folder = to_extended_path(root_folder)
        self.include_system_items = include_system_items
        self.statistics = statistics
        extended_volume_root = to_extended_path(volume_root)
        self._active_volume_folders = frozenset(
            os.path.normcase(os.path.join(extended_volume_root, folder_name))
            for folder_name in ACTIVE_VOLUME_FOLDER_NAMES
        )

    def iterate_folders(self) -> Iterator[FolderContent]:
        """Yield the content of every folder, the root folder first."""
        pending_folders: List[Tuple[str, Optional[str]]] = [(self.root_folder, None)]
        while pending_folders:
            folder_path, parent_path = pending_folders.pop()
            try:
                with os.scandir(folder_path) as folder_iterator:
                    entries = list(folder_iterator)
            except OSError as error:
                self.statistics.unreadable_items.add(to_display_path(folder_path), describe_os_error(error))
                yield FolderContent(folder_path, parent_path, [], None)
                continue

            self.statistics.folders_read += 1
            files: List[FileRecord] = []
            subfolders: List[str] = []
            for entry in entries:
                self._classify_entry(entry, files, subfolders)
            # Reversed, so the first subfolder is processed next
            pending_folders.extend((subfolder, folder_path) for subfolder in reversed(subfolders))
            yield FolderContent(folder_path, parent_path, files, len(entries))

    def _classify_entry(self, entry: os.DirEntry, files: List[FileRecord], subfolders: List[str]) -> None:
        """Add an entry to files or subfolders, or record why it is skipped."""
        try:
            # Without following links the data comes from the folder listing itself
            entry_stat = entry.stat(follow_symlinks=False)
        except OSError as error:
            self.statistics.unreadable_items.add(to_display_path(entry.path), describe_os_error(error))
            return
        attributes = entry_stat.st_file_attributes

        if attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            self.statistics.skipped_links.add(to_display_path(entry.path))
            return

        if attributes & stat.FILE_ATTRIBUTE_DIRECTORY:
            if os.path.normcase(entry.path) in self._active_volume_folders:
                self.statistics.skipped_system_folders.add(to_display_path(entry.path), "in use by Windows")
            elif not self.include_system_items and is_operating_system_item(entry.name, attributes,
                                                                            is_folder=True):
                self.statistics.skipped_system_folders.add(to_display_path(entry.path))
            else:
                subfolders.append(entry.path)
            return

        if not self.include_system_items and is_operating_system_item(entry.name, attributes, is_folder=False):
            self.statistics.skipped_system_files.add(to_display_path(entry.path), size_bytes=entry_stat.st_size)
            return
        files.append(FileRecord(entry.path, entry_stat.st_size))


# ==== Progress output =========================================================


class ProgressReporter:
    """Shows a live counter line and a status line with the current item every minute."""

    def __init__(self, activity: str, progress_text: Callable[[], str]) -> None:
        self.activity = activity
        self.current_item = ""
        self.current_item_label = "Current folder"
        self._progress_text = progress_text
        self._show_live_counter = sys.stdout.isatty()
        self._line_width = max(40, shutil.get_terminal_size().columns - 1)
        self._live_line_visible = False
        self._start_time = time.monotonic()
        self._next_status_time = self._start_time + STATUS_INTERVAL_SECONDS
        self._next_live_time = self._start_time

    def __enter__(self) -> ProgressReporter:
        self._start_time = time.monotonic()
        self._next_status_time = self._start_time + STATUS_INTERVAL_SECONDS
        self._next_live_time = self._start_time
        return self

    def __exit__(self, *exception_info) -> None:
        self.clear_live_line()

    def tick(self) -> None:
        """Called often by the running work, prints only when an interval is due."""
        now = time.monotonic()
        if now >= self._next_status_time:
            self._next_status_time = now + STATUS_INTERVAL_SECONDS
            self._print_status(now)
        if self._show_live_counter and now >= self._next_live_time:
            self._next_live_time = now + LIVE_COUNTER_INTERVAL_SECONDS
            self._draw_live_line(now)

    def clear_live_line(self) -> None:
        if self._live_line_visible:
            sys.stdout.write("\r" + " " * self._line_width + "\r")
            sys.stdout.flush()
            self._live_line_visible = False

    def _draw_live_line(self, now: float) -> None:
        elapsed = format_duration(now - self._start_time)
        live_text = f"  {self.activity} {elapsed} | {self._progress_text()}"
        sys.stdout.write("\r" + shorten_text(live_text, self._line_width).ljust(self._line_width))
        sys.stdout.flush()
        self._live_line_visible = True

    def _print_status(self, now: float) -> None:
        self.clear_live_line()
        elapsed = format_duration(now - self._start_time)
        print(f"[{clock_time()}] Still running for {elapsed} | {self.activity} | {self._progress_text()}")
        print(f"           {self.current_item_label}: {self.current_item}", flush=True)


# ==== Scan ====================================================================


class FileHasher:
    """Reads files in chunks and computes the digest of their content."""

    def __init__(self, interrupt_guard: InterruptGuard, on_bytes_read: Callable[[int], None]) -> None:
        self._interrupt_guard = interrupt_guard
        self._on_bytes_read = on_bytes_read
        self._buffer = memoryview(bytearray(HASH_CHUNK_BYTES))

    def hash_file(self, path: str, byte_limit: Optional[int]) -> Optional[Tuple[str, int]]:
        """Digest of the first byte_limit bytes, or of the whole file if byte_limit is None.

        Return (hex digest, bytes read) or None if Ctrl+C was pressed. Read errors raise OSError.
        """
        hash_object = hashlib.new(HASH_ALGORITHM)
        bytes_read = 0
        with open(path, "rb", buffering=0) as file:
            while byte_limit is None or bytes_read < byte_limit:
                if self._interrupt_guard.was_requested:
                    return None
                chunk_size = HASH_CHUNK_BYTES if byte_limit is None else min(HASH_CHUNK_BYTES,
                                                                             byte_limit - bytes_read)
                chunk_length = file.readinto(self._buffer[:chunk_size])
                if not chunk_length:
                    break
                hash_object.update(self._buffer[:chunk_length])
                bytes_read += chunk_length
                self._on_bytes_read(chunk_length)
        return hash_object.hexdigest(), bytes_read


class DuplicateScanner:
    """Finds groups of files with identical content in four steps.

    Step 1 groups all files by size, step 2 reads dates and file ids and drops
    hard links, step 3 hashes the start and step 4 the full content. After
    every step only files that can still have a copy are kept.
    """

    def __init__(self, mode: CompareMode, root_folders: List[str], include_system_files: bool) -> None:
        self.mode = mode
        self.root_folders = root_folders
        self.include_system_files = include_system_files
        self._walk_statistics = WalkStatistics()
        self._statistics = ScanStatistics()
        self._interrupt_guard = InterruptGuard()
        self._reporter = ProgressReporter("Step 1 of 4, walking", self._progress_text)
        self._hasher = FileHasher(self._interrupt_guard, self._count_hashed_bytes)
        self._step_number = 1
        self._files_done = 0            # files finished in the current step
        self._files_total = 0
        self._bytes_done = 0            # bytes hashed in the current step
        self._bytes_total = 0

    def run(self) -> ScanResult:
        """Run the four steps. A cancelled scan returns an empty, marked result."""
        start_time = time.monotonic()
        with self._interrupt_guard, self._reporter:
            groups = self._find_groups()
        return ScanResult(
            mode=self.mode,
            root_folders=self.root_folders,
            include_system_files=self.include_system_files,
            groups=groups or [],
            walk_statistics=self._walk_statistics,
            scan_statistics=self._statistics,
            duration_seconds=time.monotonic() - start_time,
            was_cancelled=groups is None,
        )

    def _find_groups(self) -> Optional[List[DuplicateGroup]]:
        """Run the four steps. None if Ctrl+C was pressed."""
        statistics = self._statistics
        size_groups = self._collect_size_groups()
        if size_groups is None:
            return None
        self._print_step(f"Step 1 of 4 finished: {format_count(statistics.files_found)} files "
                         f"({format_size(statistics.bytes_found)}), {format_count(statistics.same_size_files)} "
                         f"of them may have a copy because of their size")

        checked_groups = self._read_file_details(size_groups)
        if checked_groups is None:
            return None
        self._print_step(f"Step 2 of 4 finished: {format_quantity(statistics.checked_files, 'file')} remain, "
                         f"{format_quantity(statistics.hard_links.count, 'hard link')} listed once")

        start_groups = self._split_by_digest(checked_groups, PARTIAL_HASH_BYTES, 3,
                                             "Step 3 of 4, comparing the start")
        if start_groups is None:
            return None
        statistics.same_start_files = sum(len(files) for _, files in start_groups)
        self._print_step(f"Step 3 of 4 finished: {format_quantity(statistics.same_start_files, 'file')} "
                         f"with the same start remain")

        # Files up to PARTIAL_HASH_BYTES were read completely in step 3
        complete_groups = [(digest, files) for digest, files in start_groups
                           if files[0].size_bytes <= PARTIAL_HASH_BYTES]
        incomplete_groups = [files for _, files in start_groups if files[0].size_bytes > PARTIAL_HASH_BYTES]
        content_groups = self._split_by_digest(incomplete_groups, None, 4, "Step 4 of 4, comparing the content")
        if content_groups is None:
            return None
        groups = self._build_groups(complete_groups + content_groups)
        self._print_step(f"Step 4 of 4 finished: {format_count(sum(len(group.files) for group in groups))} "
                         f"identical files in {format_quantity(len(groups), 'group')}")
        return groups

    # ==== Step 1 ==============================================================

    def _collect_size_groups(self) -> Optional[List[List[FoundFile]]]:
        """Walk all folders and keep the files that share their size. None if cancelled."""
        files_by_size: Dict[int, List[FoundFile]] = {}
        walk_index = 0
        for root_index, root_folder in enumerate(self.root_folders):
            volume_root = TargetVolume(root_folder).root_path
            walker = FolderWalker(root_folder, self.include_system_files, volume_root, self._walk_statistics)
            for folder_content in walker.iterate_folders():
                if self._interrupt_guard.was_requested:
                    return None
                self._reporter.current_item = to_display_path(folder_content.path)
                for file_record in folder_content.files:
                    files_by_size.setdefault(file_record.size_bytes, []).append(
                        FoundFile(walk_index, file_record.path, root_index, file_record.size_bytes))
                    walk_index += 1
                    self._statistics.files_found += 1
                    self._statistics.bytes_found += file_record.size_bytes
                self._reporter.tick()
        size_groups = [files for files in files_by_size.values() if could_be_duplicates(files, self.mode)]
        self._statistics.same_size_files = sum(len(files) for files in size_groups)
        return size_groups

    # ==== Step 2 ==============================================================

    def _read_file_details(self, size_groups: List[List[FoundFile]]) -> Optional[List[List[DuplicateFile]]]:
        """Read dates and file ids of all candidates and drop hard links. None if cancelled."""
        files_to_check = sorted((found_file for files in size_groups for found_file in files),
                                key=lambda found_file: found_file.walk_index)
        self._start_step(2, "Step 2 of 4, checking", len(files_to_check), 0)
        first_path_by_file_id: Dict[Tuple[int, int], str] = {}
        checked_by_index: Dict[int, DuplicateFile] = {}
        for found_file in files_to_check:
            if self._interrupt_guard.was_requested:
                return None
            display_path = to_display_path(found_file.path)
            self._reporter.current_item = display_path
            duplicate_file = self._create_duplicate_file(found_file, display_path, first_path_by_file_id)
            if duplicate_file is not None:
                checked_by_index[found_file.walk_index] = duplicate_file
            self._files_done += 1
            self._reporter.tick()

        checked_groups: List[List[DuplicateFile]] = []
        for files in size_groups:
            checked_files = [checked_by_index[found_file.walk_index] for found_file in files
                             if found_file.walk_index in checked_by_index]
            if could_be_duplicates(checked_files, self.mode):
                checked_groups.append(checked_files)
        self._statistics.checked_files = sum(len(files) for files in checked_groups)
        return checked_groups

    def _create_duplicate_file(self, found_file: FoundFile, display_path: str,
                               first_path_by_file_id: Dict[Tuple[int, int], str]) -> Optional[DuplicateFile]:
        """Read dates and file id. None for unreadable or changed files and for further hard links."""
        try:
            file_stat = os.stat(found_file.path, follow_symlinks=False)
        except OSError as error:
            self._statistics.unreadable_files.add(display_path, describe_os_error(error), found_file.size_bytes)
            return None
        if file_stat.st_size != found_file.size_bytes:
            self._statistics.changed_files.add(display_path, "size changed during the scan", found_file.size_bytes)
            return None

        file_id = (file_stat.st_dev, file_stat.st_ino)
        # Some file systems report no file index, then hard links cannot be recognized
        if file_stat.st_ino:
            first_path = first_path_by_file_id.get(file_id)
            if first_path is not None:
                self._statistics.hard_links.add(display_path, f"same file as {first_path}", found_file.size_bytes)
                return None
            first_path_by_file_id[file_id] = display_path

        return DuplicateFile(
            walk_index=found_file.walk_index,
            path=found_file.path,
            display_path=display_path,
            comparison_path=os.path.normcase(display_path),
            root_index=found_file.root_index,
            size_bytes=found_file.size_bytes,
            creation_time_ns=get_creation_time_ns(file_stat),
            modification_time_ns=file_stat.st_mtime_ns,
            file_id=file_id,
        )

    # ==== Steps 3 and 4 =======================================================

    def _split_by_digest(self, groups: List[List[DuplicateFile]], byte_limit: Optional[int], step_number: int,
                         activity: str) -> Optional[List[Tuple[str, List[DuplicateFile]]]]:
        """Hash all files of the groups and split every group by digest. None if cancelled."""
        files_to_hash = sorted((duplicate_file for files in groups for duplicate_file in files),
                               key=lambda duplicate_file: duplicate_file.walk_index)
        total_bytes = sum(expected_read_bytes(duplicate_file, byte_limit) for duplicate_file in files_to_hash)
        self._start_step(step_number, activity, len(files_to_hash), total_bytes)
        digest_by_index: Dict[int, str] = {}
        for duplicate_file in files_to_hash:
            self._reporter.current_item = duplicate_file.display_path
            digest = self._hash_file(duplicate_file, byte_limit)
            if self._interrupt_guard.was_requested:
                return None
            if digest is not None:
                digest_by_index[duplicate_file.walk_index] = digest

        split_groups: List[Tuple[str, List[DuplicateFile]]] = []
        for files in groups:
            files_by_digest: Dict[str, List[DuplicateFile]] = {}
            for duplicate_file in files:
                digest = digest_by_index.get(duplicate_file.walk_index)
                if digest is not None:
                    files_by_digest.setdefault(digest, []).append(duplicate_file)
            split_groups.extend((digest, matching_files) for digest, matching_files in files_by_digest.items()
                                if could_be_duplicates(matching_files, self.mode))
        return split_groups

    def _hash_file(self, duplicate_file: DuplicateFile, byte_limit: Optional[int]) -> Optional[str]:
        """Digest of one file. None if it cannot be read, changed meanwhile or Ctrl+C was pressed."""
        expected_bytes = expected_read_bytes(duplicate_file, byte_limit)
        bytes_done_before = self._bytes_done
        digest: Optional[str] = None
        try:
            hash_outcome = self._hasher.hash_file(duplicate_file.path, byte_limit)
            if hash_outcome is not None:
                digest, bytes_read = hash_outcome
                if bytes_read != expected_bytes:
                    self._statistics.changed_files.add(duplicate_file.display_path, "size changed during the scan",
                                                       duplicate_file.size_bytes)
                    digest = None
        except OSError as error:
            self._statistics.unreadable_files.add(duplicate_file.display_path, describe_os_error(error),
                                                  duplicate_file.size_bytes)
        # The progress counts the expected bytes, so unreadable files do not distort it
        self._bytes_done = bytes_done_before + expected_bytes
        self._files_done += 1
        self._reporter.tick()
        return digest

    def _build_groups(self, digest_groups: List[Tuple[str, List[DuplicateFile]]]) -> List[DuplicateGroup]:
        """Number the groups, the largest reclaimable size first."""
        ordered_groups = sorted(digest_groups, key=lambda item: (
            -(item[1][0].size_bytes * (len(item[1]) - 1)), -item[1][0].size_bytes, item[0]))
        groups: List[DuplicateGroup] = []
        for number, (digest, files) in enumerate(ordered_groups, start=1):
            files.sort(key=lambda duplicate_file: (duplicate_file.root_index, duplicate_file.comparison_path))
            groups.append(DuplicateGroup(number, digest, files[0].size_bytes, files))
        return groups

    # ==== Helpers =============================================================

    def _start_step(self, step_number: int, activity: str, files_total: int, bytes_total: int) -> None:
        """Reset the progress counters for the next step."""
        self._step_number = step_number
        self._reporter.activity = activity
        self._reporter.current_item_label = "Current file"
        self._files_done = 0
        self._files_total = files_total
        self._bytes_done = 0
        self._bytes_total = bytes_total

    def _count_hashed_bytes(self, byte_count: int) -> None:
        self._bytes_done += byte_count
        self._statistics.hashed_bytes += byte_count
        self._reporter.tick()

    def _print_step(self, text: str) -> None:
        self._reporter.clear_live_line()
        print(f"[{clock_time()}] {text}", flush=True)

    def _progress_text(self) -> str:
        if self._step_number == 1:
            return (f"{format_count(self._statistics.files_found)} files | "
                    f"{format_count(self._walk_statistics.folders_read)} folders | "
                    f"{format_size(self._statistics.bytes_found)}")
        progress_text = f"{format_count(self._files_done)}/{format_count(self._files_total)} files"
        if self._bytes_total:
            percent = 100 * self._bytes_done / self._bytes_total
            progress_text += (f" | {format_size(self._bytes_done)} of {format_size(self._bytes_total)} "
                              f"({percent:.1f} %)")
        return progress_text


# ==== Rules ===================================================================


class KeepRules:
    """Decides by folder priority and age which single file of a group is kept."""

    def __init__(self, priority_entries: List[str]) -> None:
        self._other_locations_rank = priority_entries.index(OTHER_LOCATIONS_ENTRY)
        # (entry as typed, entry for comparing, rank), a lower rank is kept first
        self._entries: List[Tuple[str, str, int]] = [
            (entry, to_comparison_path(entry), rank)
            for rank, entry in enumerate(priority_entries) if entry != OTHER_LOCATIONS_ENTRY
        ]

    def rank_of(self, duplicate_file: DuplicateFile) -> int:
        """Rank of the deepest priority entry that contains the file."""
        best_rank = self._other_locations_rank
        best_length = -1
        for _, entry_path, rank in self._entries:
            if is_comparison_path_inside(duplicate_file.comparison_path, entry_path) and len(entry_path) > best_length:
                best_rank, best_length = rank, len(entry_path)
        return best_rank

    def age_key(self, duplicate_file: DuplicateFile) -> Tuple[int, int, int]:
        """Sort key of the age, the oldest file comes first.

        The older of creation and modification date counts, whichever it is.
        Copying keeps the modification date but renews the creation date, so the
        original usually has the oldest of both dates.
        """
        return (duplicate_file.oldest_time_ns, duplicate_file.creation_time_ns,
                duplicate_file.modification_time_ns)

    def best_file(self, group: DuplicateGroup) -> DuplicateFile:
        """Best priority, then oldest, then shortest path."""
        return min(group.files, key=lambda duplicate_file: (
            self.rank_of(duplicate_file), self.age_key(duplicate_file),
            len(duplicate_file.comparison_path), duplicate_file.comparison_path))

    def files_to_delete(self, group: DuplicateGroup) -> List[DuplicateFile]:
        """Every copy except the best one, also further copies in the folder of the best one."""
        best_file = self.best_file(group)
        return [duplicate_file for duplicate_file in group.files if duplicate_file is not best_file]

    def unused_entries(self, groups: List[DuplicateGroup]) -> List[str]:
        """Priority entries that contain none of the files, usually typing errors."""
        return [entry for entry, entry_path, _ in self._entries
                if not any(is_comparison_path_inside(duplicate_file.comparison_path, entry_path)
                           for group in groups for duplicate_file in group.files)]


# ==== Preview =================================================================


class ShellThumbnailProvider:
    """Preview images exactly as the Windows Explorer shows them, for every file type Windows can preview.

    Works from any thread. Files without a preview image get the icon of their file type.
    """

    def __init__(self) -> None:
        # Own library objects, so the argument types set here do not affect other code
        shell32 = ctypes.WinDLL("shell32")
        ole32 = ctypes.WinDLL("ole32")
        gdi32 = ctypes.WinDLL("gdi32")
        user32 = ctypes.WinDLL("user32")
        self._create_item = shell32.SHCreateItemFromParsingName
        self._create_item.argtypes = [wintypes.LPCWSTR, ctypes.c_void_p, ctypes.POINTER(ComGuid),
                                      ctypes.POINTER(ctypes.c_void_p)]
        self._create_item.restype = ctypes.c_long
        self._initialize_com = ole32.CoInitializeEx
        self._initialize_com.argtypes = [ctypes.c_void_p, wintypes.DWORD]
        self._initialize_com.restype = ctypes.c_long
        self._uninitialize_com = ole32.CoUninitialize
        self._uninitialize_com.argtypes = []
        self._uninitialize_com.restype = None
        self._delete_object = gdi32.DeleteObject
        self._delete_object.argtypes = [wintypes.HGDIOBJ]
        self._delete_object.restype = wintypes.BOOL
        self._get_object = gdi32.GetObjectW
        self._get_object.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p]
        self._get_object.restype = ctypes.c_int
        self._get_dib_bits = gdi32.GetDIBits
        self._get_dib_bits.argtypes = [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT, ctypes.c_void_p,
                                       ctypes.POINTER(BitmapInfoHeader), wintypes.UINT]
        self._get_dib_bits.restype = ctypes.c_int
        self._get_device_context = user32.GetDC
        self._get_device_context.argtypes = [wintypes.HWND]
        self._get_device_context.restype = wintypes.HDC
        self._release_device_context = user32.ReleaseDC
        self._release_device_context.argtypes = [wintypes.HWND, wintypes.HDC]
        self._release_device_context.restype = ctypes.c_int
        self._image_factory_id = ComGuid.from_buffer_copy(uuid.UUID(IMAGE_FACTORY_INTERFACE_ID).bytes_le)

    def get_image(self, path: str, size: int) -> Optional[QtGui.QImage]:
        """Preview image or file type icon fitting into size x size pixels, None if Windows delivers nothing."""
        initialize_result = self._initialize_com(None, COINIT_APARTMENTTHREADED)
        try:
            factory = ctypes.c_void_p()
            result = self._create_item(path, None, ctypes.byref(self._image_factory_id), ctypes.byref(factory))
            if result != S_OK or not factory.value:
                return None
            # The first field of a COM object points to the table of its methods
            method_table = ctypes.cast(factory, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
            try:
                return self._render_image(factory, method_table, size)
            finally:
                COM_RELEASE_PROTOTYPE(method_table[COM_RELEASE_METHOD_INDEX])(factory)
        except OSError:
            return None
        finally:
            if initialize_result in (S_OK, S_FALSE):
                self._uninitialize_com()

    def _render_image(self, factory: ctypes.c_void_p, method_table, size: int) -> Optional[QtGui.QImage]:
        get_image = IMAGE_FACTORY_GET_IMAGE_PROTOTYPE(method_table[IMAGE_FACTORY_GET_IMAGE_METHOD_INDEX])
        bitmap_handle = wintypes.HBITMAP()
        result = get_image(factory, wintypes.SIZE(size, size), SIIGBF_RESIZETOFIT, ctypes.byref(bitmap_handle))
        if result != S_OK or not bitmap_handle.value:
            return None
        try:
            return self._bitmap_to_image(bitmap_handle)
        finally:
            self._delete_object(bitmap_handle)

    def _bitmap_to_image(self, bitmap_handle: wintypes.HBITMAP) -> Optional[QtGui.QImage]:
        """Copy the pixels of a Windows bitmap into a QImage."""
        bitmap = WindowsBitmap()
        if not self._get_object(bitmap_handle, ctypes.sizeof(bitmap), ctypes.byref(bitmap)):
            return None
        width, height = bitmap.bmWidth, abs(bitmap.bmHeight)
        if width <= 0 or height <= 0:
            return None
        header = BitmapInfoHeader()
        header.biSize = ctypes.sizeof(BitmapInfoHeader)
        header.biWidth = width
        header.biHeight = -height              # negative means the first line is the top line
        header.biPlanes = 1
        header.biBitCount = 32
        header.biCompression = BI_RGB
        pixel_buffer = ctypes.create_string_buffer(width * height * 4)
        device_context = self._get_device_context(None)
        try:
            copied_lines = self._get_dib_bits(device_context, bitmap_handle, 0, height, pixel_buffer,
                                              ctypes.byref(header), DIB_RGB_COLORS)
        finally:
            self._release_device_context(None, device_context)
        if copied_lines != height:
            return None
        pixel_data = pixel_buffer.raw
        # Photos come without alpha values, icons with them
        has_alpha = any(pixel_data[3::4])
        image_format = (QtGui.QImage.Format.Format_ARGB32_Premultiplied if has_alpha
                        else QtGui.QImage.Format.Format_RGB32)
        return QtGui.QImage(pixel_data, width, height, width * 4, image_format).copy()


class ThumbnailLoader(QtCore.QObject):
    """Loads the preview images of the list in background threads, the rows visible at the moment first."""

    thumbnail_ready = QtCore.Signal(int, object)        # group number, QImage or None

    def __init__(self, thumbnail_provider: ShellThumbnailProvider, parent: QtCore.QObject) -> None:
        super().__init__(parent)
        self._thumbnail_provider = thumbnail_provider
        self._thread_pool = QtCore.QThreadPool(self)
        self._thread_pool.setMaxThreadCount(THUMBNAIL_THREAD_COUNT)
        self._lock = threading.Lock()
        self._requested_numbers: Set[int] = set()       # waiting or running
        self._running_numbers: Set[int] = set()

    def request(self, paths_by_group_number: Dict[int, str]) -> None:
        """Load these preview images. Waiting requests for rows that are no longer visible are dropped."""
        self._thread_pool.clear()
        with self._lock:
            self._requested_numbers = set(self._running_numbers)
            new_requests = [(group_number, path) for group_number, path in paths_by_group_number.items()
                            if group_number not in self._requested_numbers]
            self._requested_numbers.update(group_number for group_number, _ in new_requests)
        for group_number, path in new_requests:
            self._thread_pool.start(functools.partial(self._load_thumbnail, group_number, path))

    def stop(self) -> None:
        self._thread_pool.clear()
        self._thread_pool.waitForDone()

    def _load_thumbnail(self, group_number: int, path: str) -> None:
        """Runs in a worker thread."""
        with self._lock:
            self._running_numbers.add(group_number)
        image = self._thumbnail_provider.get_image(path, THUMBNAIL_SOURCE_SIZE)
        with self._lock:
            self._running_numbers.discard(group_number)
            self._requested_numbers.discard(group_number)
        self.thumbnail_ready.emit(group_number, image)


class PreviewImageLoader(QtCore.QObject):
    """Loads the image of the preview in a background thread, so the list stays responsive."""

    image_ready = QtCore.Signal(int, object)            # request number, QImage or None

    def __init__(self, thumbnail_provider: ShellThumbnailProvider, parent: QtCore.QObject) -> None:
        super().__init__(parent)
        self._thumbnail_provider = thumbnail_provider
        self._thread_pool = QtCore.QThreadPool(self)
        self._thread_pool.setMaxThreadCount(1)

    def load(self, request_number: int, path: str, reads_image_file: bool) -> None:
        """Load the image file itself if reads_image_file, otherwise or if that fails the Windows preview image."""
        self._thread_pool.clear()
        self._thread_pool.start(functools.partial(self._load_image, request_number, path, reads_image_file))

    def stop(self) -> None:
        self._thread_pool.clear()
        self._thread_pool.waitForDone()

    def _load_image(self, request_number: int, path: str, reads_image_file: bool) -> None:
        """Runs in a worker thread."""
        image = read_image(path) if reads_image_file else None
        if image is None:
            image = self._thumbnail_provider.get_image(path, PREVIEW_SHELL_IMAGE_SIZE)
        self.image_ready.emit(request_number, image)


class ImageView(QtWidgets.QGraphicsView):
    """Shows an image fitted into the view. Small images are not enlarged."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self._scene = QtWidgets.QGraphicsScene(self)
        self._pixmap_item = self._scene.addPixmap(QtGui.QPixmap())
        self.setScene(self._scene)
        self.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QColor(PREVIEW_BACKGROUND_COLOR))
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

    def set_image(self, image: Optional[QtGui.QImage]) -> None:
        pixmap = QtGui.QPixmap.fromImage(image) if image is not None else QtGui.QPixmap()
        self._pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(QtCore.QRectF(pixmap.rect()))
        self._fit()

    def _fit(self) -> None:
        """Show the whole image, small images are not enlarged."""
        self.resetTransform()
        pixmap = self._pixmap_item.pixmap()
        if pixmap.isNull():
            return
        viewport_size = self.viewport().size()
        scale = min(viewport_size.width() / pixmap.width(), viewport_size.height() / pixmap.height(), 1.0)
        self.scale(scale, scale)
        self.centerOn(self._pixmap_item)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self._fit()


class MediaView(QtWidgets.QWidget):
    """Player for video and audio files. The Windows preview image is shown until playback starts."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self._is_video = False
        self._player = QMediaPlayer(self)
        # Only after the first player exists, because Qt sets the FFmpeg log level when it starts FFmpeg
        silence_video_decoder()
        self._audio_output = QAudioOutput(self)
        self._audio_output.setVolume(MEDIA_DEFAULT_VOLUME)
        self._player.setAudioOutput(self._audio_output)
        self._video_widget = QVideoWidget()
        self._player.setVideoOutput(self._video_widget)
        self._poster_view = ImageView()
        self._screen = QtWidgets.QStackedWidget()
        self._screen.addWidget(self._poster_view)
        self._screen.addWidget(self._video_widget)

        style = self.style()
        self._play_icon = style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay)
        self._pause_icon = style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause)
        self._play_button = QtWidgets.QToolButton()
        self._play_button.setIcon(self._play_icon)
        self._play_button.setToolTip("Play or pause")
        self._play_button.clicked.connect(self._toggle_playback)
        self._position_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self._position_slider.setRange(0, 0)
        self._position_slider.sliderMoved.connect(self._player.setPosition)
        self._time_label = QtWidgets.QLabel()
        self._mute_button = QtWidgets.QToolButton()
        self._mute_button.setCheckable(True)
        self._mute_button.setToolTip("Sound on or off")
        self._mute_button.toggled.connect(self._set_muted)
        self._set_muted(False)
        self._volume_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(round(MEDIA_DEFAULT_VOLUME * 100))
        self._volume_slider.setMaximumWidth(90)
        self._volume_slider.valueChanged.connect(lambda value: self._audio_output.setVolume(value / 100))
        self._message_label = QtWidgets.QLabel()
        self._message_label.setWordWrap(True)

        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.addWidget(self._play_button)
        controls_layout.addWidget(self._position_slider, 1)
        controls_layout.addWidget(self._time_label)
        controls_layout.addWidget(self._mute_button)
        controls_layout.addWidget(self._volume_slider)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._screen, 1)
        layout.addLayout(controls_layout)
        layout.addWidget(self._message_label)

        self._player.positionChanged.connect(self._show_position)
        self._player.durationChanged.connect(self._show_duration)
        self._player.playbackStateChanged.connect(self._show_playback_state)
        self._player.errorOccurred.connect(self._show_error)
        self._show_position(0)

    def set_source(self, path: str, is_video: bool) -> None:
        """Load a file without playing it."""
        self.stop()
        self._is_video = is_video
        self._poster_view.set_image(None)
        self._screen.setCurrentWidget(self._poster_view)
        self._player.setSource(QtCore.QUrl.fromLocalFile(path))

    def set_poster(self, image: Optional[QtGui.QImage]) -> None:
        self._poster_view.set_image(image)

    def stop(self) -> None:
        """Stop playing and release the file."""
        self._player.stop()
        self._player.setSource(QtCore.QUrl())
        self._message_label.clear()
        self._position_slider.setRange(0, 0)
        self._show_position(0)

    def _toggle_playback(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            return
        if self._is_video:
            self._screen.setCurrentWidget(self._video_widget)
        self._player.play()

    def _set_muted(self, is_muted: bool) -> None:
        self._audio_output.setMuted(is_muted)
        icon_type = (QtWidgets.QStyle.StandardPixmap.SP_MediaVolumeMuted if is_muted
                     else QtWidgets.QStyle.StandardPixmap.SP_MediaVolume)
        self._mute_button.setIcon(self.style().standardIcon(icon_type))

    def _show_position(self, position_milliseconds: int) -> None:
        if not self._position_slider.isSliderDown():
            self._position_slider.setValue(position_milliseconds)
        self._time_label.setText(f"{format_media_time(position_milliseconds)} / "
                                 f"{format_media_time(self._player.duration())}")

    def _show_duration(self, duration_milliseconds: int) -> None:
        self._position_slider.setRange(0, duration_milliseconds)
        self._show_position(self._player.position())

    def _show_playback_state(self, playback_state: QMediaPlayer.PlaybackState) -> None:
        is_playing = playback_state == QMediaPlayer.PlaybackState.PlayingState
        self._play_button.setIcon(self._pause_icon if is_playing else self._play_icon)

    def _show_error(self, error: QMediaPlayer.Error, error_text: str) -> None:
        if error != QMediaPlayer.Error.NoError:
            self._message_label.setText(f"This file cannot be played: {error_text}")
            self._screen.setCurrentWidget(self._poster_view)


class PreviewWidget(QtWidgets.QWidget):
    """Preview of one file.

    Images are shown fitted, videos and audio files can be played, PDF files
    up to PREVIEW_PDF_MAX_BYTES scrolled and the start of text files read.
    Everything else shows the preview image of Windows, which also covers
    Office documents and HEIC or RAW photos if Windows has the matching
    extension installed.
    """

    def __init__(self, thumbnail_provider: ShellThumbnailProvider, image_extensions: Set[str],
                 parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self._image_extensions = image_extensions
        self._current_file: Optional[DuplicateFile] = None
        self._request_number = 0                # results of older requests are ignored
        self._image_loader = PreviewImageLoader(thumbnail_provider, self)
        self._image_loader.image_ready.connect(self._show_loaded_image)

        self._name_label = QtWidgets.QLabel()
        name_font = self._name_label.font()
        name_font.setBold(True)
        self._name_label.setFont(name_font)
        self._name_label.setWordWrap(True)
        self._path_label = create_secondary_label("")
        self._path_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self._message_label = create_secondary_label("")
        self._message_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._image_view = ImageView()
        self._media_view = MediaView()
        self._pdf_document = QPdfDocument(self)
        self._pdf_buffer: Optional[QtCore.QBuffer] = None      # content of the shown PDF file
        self._pdf_view = QPdfView()
        self._pdf_view.setDocument(self._pdf_document)
        self._pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        self._pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        self._text_view = QtWidgets.QPlainTextEdit()
        self._text_view.setReadOnly(True)
        self._text_view.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont))
        self._pages = QtWidgets.QStackedWidget()
        for page in (self._message_label, self._image_view, self._media_view, self._pdf_view, self._text_view):
            self._pages.addWidget(page)

        self._explorer_button = create_button("Show in Explorer", self._show_in_explorer)
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self._explorer_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(CARD_SPACING)
        layout.addWidget(self._name_label)
        layout.addWidget(self._path_label)
        layout.addWidget(self._pages, 1)
        layout.addLayout(buttons_layout)
        self.show_file(None)

    def show_file(self, duplicate_file: Optional[DuplicateFile]) -> None:
        """Show a file, None shows a hint instead."""
        self.stop()
        self._current_file = duplicate_file
        self._explorer_button.setEnabled(duplicate_file is not None)
        if duplicate_file is None:
            self._name_label.clear()
            self._path_label.clear()
            self._show_message("Select a file in the list to see its preview.")
            return

        display_path = duplicate_file.display_path
        self._name_label.setText(to_window_text(os.path.basename(display_path)))
        self._path_label.setText(to_window_text(display_path))
        preview_kind = find_preview_kind(display_path, self._image_extensions)
        if not os.path.lexists(duplicate_file.path):
            self._show_message("The file no longer exists.")
        elif preview_kind is PreviewKind.PDF and self._show_pdf(duplicate_file.path):
            pass
        elif preview_kind in (PreviewKind.VIDEO, PreviewKind.AUDIO):
            self._media_view.set_source(display_path, is_video=preview_kind is PreviewKind.VIDEO)
            self._pages.setCurrentWidget(self._media_view)
            self._image_loader.load(self._request_number, display_path, reads_image_file=False)
        elif preview_kind is PreviewKind.TEXT:
            self._show_text(duplicate_file.path)
        else:
            self._show_message("Loading the preview ...")
            self._image_loader.load(self._request_number, display_path,
                                    reads_image_file=preview_kind is PreviewKind.IMAGE)

    def stop(self) -> None:
        """Stop playback and release open files."""
        self._request_number += 1
        self._media_view.stop()
        self._close_pdf()

    def shutdown(self) -> None:
        """Stop everything before the window closes."""
        self.stop()
        self._image_loader.stop()

    def _show_loaded_image(self, request_number: int, image: Optional[QtGui.QImage]) -> None:
        if request_number != self._request_number:
            return
        if self._pages.currentWidget() is self._media_view:
            self._media_view.set_poster(image)
            return
        if image is None:
            self._show_message("No preview available for this file type.")
            return
        self._image_view.set_image(image)
        self._pages.setCurrentWidget(self._image_view)

    def _show_pdf(self, path: str) -> bool:
        """Show a PDF file. False if it is too large or Qt cannot open it, then the Windows preview image is used.

        The file is read into memory, because a file opened by QPdfDocument itself stays
        open even after close() and could not be deleted afterwards.
        """
        try:
            with open(path, "rb") as pdf_file:
                # The size is checked first, so a large file is not read in vain
                if os.fstat(pdf_file.fileno()).st_size > PREVIEW_PDF_MAX_BYTES:
                    return False
                pdf_data = pdf_file.read()
        except OSError:
            return False
        self._pdf_buffer = QtCore.QBuffer()
        self._pdf_buffer.setData(pdf_data)
        self._pdf_buffer.open(QtCore.QIODevice.OpenModeFlag.ReadOnly)
        # A buffer is loaded at once, so the status is final here
        self._pdf_document.load(self._pdf_buffer)
        if self._pdf_document.status() != QPdfDocument.Status.Ready:
            self._close_pdf()
            return False
        self._pages.setCurrentWidget(self._pdf_view)
        return True

    def _close_pdf(self) -> None:
        self._pdf_document.close()
        # The document reads its pages from the buffer, so the buffer is released only after closing
        self._pdf_buffer = None

    def _show_text(self, path: str) -> None:
        try:
            with open(path, "rb") as text_file:
                data = text_file.read(PREVIEW_TEXT_BYTES + 1)
        except OSError as error:
            self._show_message(f"The file cannot be read: {describe_os_error(error)}")
            return
        text = decode_text(data[:PREVIEW_TEXT_BYTES])
        if len(data) > PREVIEW_TEXT_BYTES:
            text += f"\n\n[only the first {format_size(PREVIEW_TEXT_BYTES)} are shown]"
        self._text_view.setPlainText(text)
        self._pages.setCurrentWidget(self._text_view)

    def _show_message(self, text: str) -> None:
        self._message_label.setText(text)
        self._pages.setCurrentWidget(self._message_label)

    def _show_in_explorer(self) -> None:
        if self._current_file is not None:
            show_error_message(self, show_in_explorer(self._current_file.display_path))


# ==== Selection window ========================================================


class DuplicateTreeModel(QtCore.QAbstractItemModel):
    """Identical files under a header row with number and digest, read directly from the scan result.

    The internal id of an index is 0 for a header row. For a file row it is the
    row of its header row plus 1, which is enough to find the parent row.
    """

    marks_changed = QtCore.Signal()

    def __init__(self, scan_result: ScanResult, marked_paths: Set[str], thumbnail_provider: ShellThumbnailProvider,
                 parent: QtCore.QObject) -> None:
        super().__init__(parent)
        self.marked_paths = marked_paths        # extended paths of the files marked for deletion
        self._all_groups = scan_result.groups
        self._is_between_mode = scan_result.mode is CompareMode.BETWEEN_FOLDERS
        self._shown_groups: List[DuplicateGroup] = []
        self._row_by_group_number: Dict[int, int] = {}
        self._set_shown_groups(list(scan_result.groups))
        self._group_background = QtGui.QBrush(QtGui.QColor(GROUP_ROW_COLOR))
        self._warning_background = QtGui.QBrush(QtGui.QColor(WARNING_ROW_COLOR))
        self._delete_background = QtGui.QBrush(QtGui.QColor(DELETE_ROW_COLOR))
        self._delete_foreground = QtGui.QBrush(QtGui.QColor(DELETE_TEXT_COLOR))
        self._secondary_foreground = QtGui.QBrush(QtGui.QColor(SECONDARY_TEXT_COLOR))
        self._thumbnail_loader = ThumbnailLoader(thumbnail_provider, self)
        self._thumbnail_loader.thumbnail_ready.connect(self._store_thumbnail)
        self._thumbnail_images: Dict[int, Optional[QtGui.QImage]] = {}     # None if Windows had no image
        self._thumbnail_pixmaps: Dict[int, QtGui.QPixmap] = {}             # scaled to the current size
        self._thumbnail_size = THUMBNAIL_DEFAULT_SIZE
        self._device_pixel_ratio = 1.0
        self._placeholder_pixmap = self._create_placeholder_pixmap()
        self._line_height = QtGui.QFontMetrics(QtWidgets.QApplication.font()).height() + ROW_PADDING
        self._file_size_hint = QtCore.QSize(-1, self._line_height)
        self._group_size_hint = self._create_group_size_hint()

    # ==== Structure ===========================================================

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        # Checked here instead of hasIndex, which would ask rowCount and columnCount for every cell
        if not 0 <= column < len(TREE_COLUMN_TITLES):
            return QtCore.QModelIndex()
        if not parent.isValid():
            if 0 <= row < len(self._shown_groups):
                return self.createIndex(row, column, 0)
            return QtCore.QModelIndex()
        if (parent.internalId() == 0 and parent.column() == 0
                and 0 <= row < len(self._shown_groups[parent.row()].files)):
            return self.createIndex(row, column, parent.row() + 1)
        return QtCore.QModelIndex()

    def parent(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        if not index.isValid() or index.internalId() == 0:
            return QtCore.QModelIndex()
        return self.createIndex(index.internalId() - 1, 0, 0)

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        if not parent.isValid():
            return len(self._shown_groups)
        if parent.internalId() == 0 and parent.column() == 0:
            return len(self._shown_groups[parent.row()].files)
        return 0

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(TREE_COLUMN_TITLES)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation,
                   role: int = QtCore.Qt.ItemDataRole.DisplayRole):
        if orientation == QtCore.Qt.Orientation.Horizontal and role == QtCore.Qt.ItemDataRole.DisplayRole:
            return TREE_COLUMN_TITLES[section]
        return None

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags
        item_flags = QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable
        if index.column() == COLUMN_NAME:
            item_flags |= QtCore.Qt.ItemFlag.ItemIsUserCheckable
        return item_flags

    def group_at(self, index: QtCore.QModelIndex) -> DuplicateGroup:
        """Identical files of a header row or of a file row."""
        if index.internalId() == 0:
            return self._shown_groups[index.row()]
        return self._shown_groups[index.internalId() - 1]

    def file_at(self, index: QtCore.QModelIndex) -> Optional[DuplicateFile]:
        """File of a file row, None for a header row."""
        if index.internalId() == 0:
            return None
        return self._shown_groups[index.internalId() - 1].files[index.row()]

    @property
    def shown_groups(self) -> List[DuplicateGroup]:
        return self._shown_groups

    # ==== Content =============================================================

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        # The height of every row is asked for often, a ready answer keeps long lists fast
        if role == QtCore.Qt.ItemDataRole.SizeHintRole:
            return self._group_size_hint if index.internalId() == 0 else self._file_size_hint
        group = self.group_at(index)
        duplicate_file = self.file_at(index)
        if duplicate_file is None:
            return self._group_data(group, index.column(), role)
        return self._file_data(duplicate_file, index.column(), role)

    def setData(self, index: QtCore.QModelIndex, value, role: int = QtCore.Qt.ItemDataRole.EditRole) -> bool:
        """The checkbox of a file ticks it, the checkbox of a header row ticks all of its files."""
        if not index.isValid() or index.column() != COLUMN_NAME or role != QtCore.Qt.ItemDataRole.CheckStateRole:
            return False
        is_marked = QtCore.Qt.CheckState(value) == QtCore.Qt.CheckState.Checked
        group = self.group_at(index)
        duplicate_file = self.file_at(index)
        if duplicate_file is None:
            self.set_group_marks([(group, list(group.files) if is_marked else [])])
        else:
            self.set_file_marks([(group, duplicate_file)], is_marked)
        return True

    def _group_data(self, group: DuplicateGroup, column: int, role: int):
        """The header row spans all columns, so only the first column has content."""
        if column != COLUMN_NAME:
            return None
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return format_group_label(group)
        if role == GROUP_DETAIL_ROLE:
            return self._group_details(group)
        if role == GROUP_WARNING_ROLE:
            return self.marked_count(group) == len(group.files)
        if role == QtCore.Qt.ItemDataRole.CheckStateRole:
            marked_count = self.marked_count(group)
            if marked_count == 0:
                return QtCore.Qt.CheckState.Unchecked
            if marked_count == len(group.files):
                return QtCore.Qt.CheckState.Checked
            return QtCore.Qt.CheckState.PartiallyChecked
        if role == QtCore.Qt.ItemDataRole.DecorationRole:
            return self._thumbnail_pixmap(group)
        if role == QtCore.Qt.ItemDataRole.BackgroundRole:
            return self._warning_background if self.marked_count(group) == len(group.files) else self._group_background
        if role == QtCore.Qt.ItemDataRole.ToolTipRole:
            return f"{HASH_NAME} {group.digest}"
        return None

    def _file_data(self, duplicate_file: DuplicateFile, column: int, role: int):
        """Content of a file row, ticked files are red."""
        is_marked = duplicate_file.path in self.marked_paths
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if column == COLUMN_NAME:
                return to_window_text(os.path.basename(duplicate_file.display_path))
            if column == COLUMN_FOLDER:
                return folder_label(duplicate_file.root_index)
            if column == COLUMN_DATE:
                return format_timestamp(duplicate_file.oldest_time_ns)
            if column == COLUMN_SIZE:
                return format_size(duplicate_file.size_bytes)
            if column == COLUMN_PATH:
                return to_window_text(duplicate_file.display_path)
            return None
        if role == QtCore.Qt.ItemDataRole.TextAlignmentRole and column == COLUMN_SIZE:
            # Centered keeps a gap to the path, right aligned sizes would touch it
            return QtCore.Qt.AlignmentFlag.AlignCenter
        if role == QtCore.Qt.ItemDataRole.CheckStateRole and column == COLUMN_NAME:
            return QtCore.Qt.CheckState.Checked if is_marked else QtCore.Qt.CheckState.Unchecked
        if role == QtCore.Qt.ItemDataRole.ForegroundRole:
            if is_marked:
                return self._delete_foreground
            return None if column == COLUMN_NAME else self._secondary_foreground
        if role == QtCore.Qt.ItemDataRole.BackgroundRole and is_marked:
            return self._delete_background
        if role == QtCore.Qt.ItemDataRole.ToolTipRole:
            if column == COLUMN_DATE:
                return (f"created {format_timestamp(duplicate_file.creation_time_ns)}\n"
                        f"modified {format_timestamp(duplicate_file.modification_time_ns)}")
            return to_window_text(duplicate_file.display_path)
        return None

    def _group_details(self, group: DuplicateGroup) -> str:
        """Second line of a header row: copies, size and folders."""
        details = [f"{len(group.files)} identical files", f"{format_size(group.size_bytes)} each",
                   "folder " + ", ".join(folder_label(root_index) for root_index in group.root_indexes)]
        if self._is_between_mode:
            details += [f"{count} of them in folder {folder_label(root_index)}"
                        for root_index, count in group.folders_with_several_copies()]
        if self.marked_count(group) == len(group.files):
            details.append("no copy is kept")
        return "   \u00b7   ".join(details)

    # ==== Marks ===============================================================

    def marked_count(self, group: DuplicateGroup) -> int:
        return sum(1 for duplicate_file in group.files if duplicate_file.path in self.marked_paths)

    def set_file_marks(self, file_entries: List[Tuple[DuplicateGroup, DuplicateFile]], is_marked: bool) -> None:
        """Tick or untick single files."""
        groups_by_number: Dict[int, DuplicateGroup] = {}
        for group, duplicate_file in file_entries:
            groups_by_number[group.number] = group
            if is_marked:
                self.marked_paths.add(duplicate_file.path)
            else:
                self.marked_paths.discard(duplicate_file.path)
        self._refresh_groups(list(groups_by_number.values()))
        self.marks_changed.emit()

    def set_group_marks(self, group_marks: List[Tuple[DuplicateGroup, List[DuplicateFile]]]) -> None:
        """Replace the ticks of several header rows, each one with its list of files to delete."""
        for group, files_to_delete in group_marks:
            for duplicate_file in group.files:
                self.marked_paths.discard(duplicate_file.path)
            for duplicate_file in files_to_delete:
                self.marked_paths.add(duplicate_file.path)
        self._refresh_groups([group for group, _ in group_marks])
        self.marks_changed.emit()

    def marked_totals(self) -> Tuple[int, int, int]:
        """Ticked files, their bytes and the number of files of which no copy is kept."""
        file_count = total_bytes = no_copy_count = 0
        for group in self._all_groups:
            marked_count = self.marked_count(group)
            file_count += marked_count
            total_bytes += marked_count * group.size_bytes
            if marked_count == len(group.files):
                no_copy_count += 1
        return file_count, total_bytes, no_copy_count

    def _refresh_groups(self, groups: List[DuplicateGroup]) -> None:
        """Show changed ticks. Many rows at once are cheaper as one layout change."""
        if len(groups) > SINGLE_REFRESH_GROUP_LIMIT:
            self.layoutAboutToBeChanged.emit()
            self.layoutChanged.emit()
            return
        last_column = len(TREE_COLUMN_TITLES) - 1
        for group in groups:
            row = self._row_by_group_number.get(group.number)
            if row is None:
                continue
            group_index = self.index(row, 0)
            self.dataChanged.emit(group_index, self.index(row, last_column))
            if group.files:
                self.dataChanged.emit(self.index(0, 0, group_index),
                                      self.index(len(group.files) - 1, last_column, group_index))

    # ==== File type filter ====================================================

    def extension_counts(self) -> List[Tuple[str, int]]:
        """File types with the number of header rows that contain them, the most frequent first."""
        counts: Dict[str, int] = {}
        for group in self._all_groups:
            for extension in {get_file_extension(duplicate_file.display_path) for duplicate_file in group.files}:
                counts[extension] = counts.get(extension, 0) + 1
        return sorted(counts.items(), key=lambda item: (-item[1], item[0]))

    def set_extension_filter(self, extension: Optional[str]) -> None:
        """Show only identical files of this file type, None shows all."""
        self.beginResetModel()
        self._set_shown_groups([group for group in self._all_groups if extension is None
                                or any(get_file_extension(duplicate_file.display_path) == extension
                                       for duplicate_file in group.files)])
        self.endResetModel()

    def _set_shown_groups(self, groups: List[DuplicateGroup]) -> None:
        self._shown_groups = groups
        self._row_by_group_number = {group.number: row for row, group in enumerate(groups)}

    # ==== Preview images ======================================================

    def set_thumbnail_size(self, size: int, device_pixel_ratio: float) -> None:
        self._thumbnail_size = size
        self._device_pixel_ratio = device_pixel_ratio
        self._thumbnail_pixmaps.clear()
        self._placeholder_pixmap = self._create_placeholder_pixmap()
        self._group_size_hint = self._create_group_size_hint()
        if self._shown_groups:
            self.dataChanged.emit(self.index(0, COLUMN_NAME), self.index(len(self._shown_groups) - 1, COLUMN_NAME),
                                  [QtCore.Qt.ItemDataRole.DecorationRole, QtCore.Qt.ItemDataRole.SizeHintRole])

    def request_thumbnails(self, groups: List[DuplicateGroup]) -> None:
        """Load the preview images of these header rows if they are not loaded yet."""
        self._thumbnail_loader.request({group.number: group.files[0].display_path for group in groups
                                        if group.number not in self._thumbnail_images})

    def stop_thumbnails(self) -> None:
        self._thumbnail_loader.stop()

    def _thumbnail_pixmap(self, group: DuplicateGroup) -> QtGui.QPixmap:
        """Preview image in the current size, a placeholder until Windows delivers it."""
        pixmap = self._thumbnail_pixmaps.get(group.number)
        if pixmap is not None:
            return pixmap
        image = self._thumbnail_images.get(group.number)
        if image is None:
            return self._placeholder_pixmap
        pixmap = self._fit_into_square(QtGui.QPixmap.fromImage(image))
        self._thumbnail_pixmaps[group.number] = pixmap
        return pixmap

    def _store_thumbnail(self, group_number: int, image: Optional[QtGui.QImage]) -> None:
        self._thumbnail_images[group_number] = image
        self._thumbnail_pixmaps.pop(group_number, None)
        row = self._row_by_group_number.get(group_number)
        if row is not None:
            group_index = self.index(row, COLUMN_NAME)
            self.dataChanged.emit(group_index, group_index, [QtCore.Qt.ItemDataRole.DecorationRole])

    def _fit_into_square(self, pixmap: QtGui.QPixmap) -> QtGui.QPixmap:
        """Center the image on a square of the current size, so all header rows have the same height."""
        physical_size = round(self._thumbnail_size * self._device_pixel_ratio)
        canvas = QtGui.QPixmap(physical_size, physical_size)
        canvas.fill(QtCore.Qt.GlobalColor.transparent)
        scaled_pixmap = pixmap.scaled(physical_size, physical_size, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                      QtCore.Qt.TransformationMode.SmoothTransformation)
        painter = QtGui.QPainter(canvas)
        painter.drawPixmap((physical_size - scaled_pixmap.width()) // 2,
                           (physical_size - scaled_pixmap.height()) // 2, scaled_pixmap)
        painter.end()
        canvas.setDevicePixelRatio(self._device_pixel_ratio)
        return canvas

    def _create_group_size_hint(self) -> QtCore.QSize:
        """Height of a header row: two lines of text or the preview image. The width is left to the columns."""
        return QtCore.QSize(-1, max(2 * self._line_height, self._thumbnail_size + 2 * ROW_PADDING))

    def _create_placeholder_pixmap(self) -> QtGui.QPixmap:
        physical_size = round(self._thumbnail_size * self._device_pixel_ratio)
        placeholder = QtGui.QPixmap(physical_size, physical_size)
        placeholder.fill(QtGui.QColor(THUMBNAIL_PLACEHOLDER_COLOR))
        placeholder.setDevicePixelRatio(self._device_pixel_ratio)
        return placeholder


class HeaderRowDelegate(QtWidgets.QStyledItemDelegate):
    """Draws a header row: checkbox, preview image, number and digest in bold and a grey line of details.

    File rows are drawn as usual. The checkbox sits where Qt expects it, so clicks on it work as usual.
    """

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem,
              index: QtCore.QModelIndex) -> None:
        """Draw header rows, leave file rows to Qt."""
        if index.internalId() != 0 or index.column() != COLUMN_NAME:
            super().paint(painter, option, index)
            return
        item_option = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(item_option, index)
        widget = item_option.widget
        style = widget.style() if widget is not None else QtWidgets.QApplication.style()
        is_selected = bool(item_option.state & QtWidgets.QStyle.StateFlag.State_Selected)
        painter.save()
        painter.fillRect(item_option.rect, item_option.palette.highlight() if is_selected
                         else index.data(QtCore.Qt.ItemDataRole.BackgroundRole))
        painter.setPen(QtGui.QColor(BORDER_COLOR))
        painter.drawLine(item_option.rect.topLeft(), item_option.rect.topRight())

        check_option = QtWidgets.QStyleOptionViewItem(item_option)
        check_option.rect = style.subElementRect(QtWidgets.QStyle.SubElement.SE_ItemViewItemCheckIndicator,
                                                 item_option, widget)
        check_option.state = (item_option.state & ~QtWidgets.QStyle.StateFlag.State_HasFocus) | CHECK_STATE_FLAGS[
            QtCore.Qt.CheckState(item_option.checkState)]
        style.drawPrimitive(QtWidgets.QStyle.PrimitiveElement.PE_IndicatorItemViewItemCheck, check_option,
                            painter, widget)

        pixmap = index.data(QtCore.Qt.ItemDataRole.DecorationRole)
        if pixmap is not None:
            icon_rect = style.subElementRect(QtWidgets.QStyle.SubElement.SE_ItemViewItemDecoration,
                                             item_option, widget)
            painter.drawPixmap(icon_rect.topLeft(), pixmap)

        text_rect = style.subElementRect(QtWidgets.QStyle.SubElement.SE_ItemViewItemText, item_option, widget)
        text_rect.adjust(HEADER_TEXT_INDENT, 0, -HEADER_TEXT_INDENT, 0)
        title_font = QtGui.QFont(item_option.font)
        title_font.setBold(True)
        title_height = QtGui.QFontMetrics(title_font).height()
        detail_height = QtGui.QFontMetrics(item_option.font).height()
        top = text_rect.center().y() - (title_height + detail_height + HEADER_LINE_GAP) // 2
        painter.setFont(title_font)
        painter.setPen(item_option.palette.highlightedText().color() if is_selected else QtGui.QColor(TEXT_COLOR))
        painter.drawText(QtCore.QRect(text_rect.left(), top, text_rect.width(), title_height),
                         QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter, item_option.text)
        painter.setFont(item_option.font)
        painter.setPen(QtGui.QColor(WARNING_TEXT_COLOR if index.data(GROUP_WARNING_ROLE) else SECONDARY_TEXT_COLOR))
        painter.drawText(QtCore.QRect(text_rect.left(), top + title_height + HEADER_LINE_GAP, text_rect.width(),
                                      detail_height),
                         QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter,
                         index.data(GROUP_DETAIL_ROLE))
        painter.restore()


class DuplicateTreeView(QtWidgets.QTreeView):
    """List of the identical files. Space switches the selected rows between keep and delete.

    The last column always reaches the right edge, so header rows and the selection fill the whole width.
    """

    toggle_requested = QtCore.Signal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.minimum_last_column_width = 0      # wide enough for the longest path
        self.header().sectionResized.connect(self._on_section_resized)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_Space:
            self.toggle_requested.emit()
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self.fit_last_column()

    def fit_last_column(self) -> None:
        header = self.header()
        last_column = header.count() - 1
        if last_column < 0:
            return
        other_columns_width = sum(header.sectionSize(column) for column in range(last_column))
        header.resizeSection(last_column, max(self.minimum_last_column_width,
                                              self.viewport().width() - other_columns_width))

    def _on_section_resized(self, column: int, old_width: int, new_width: int) -> None:
        if column != self.header().count() - 1:
            self.fit_last_column()


class SelectionWindow(QtWidgets.QMainWindow):
    """Window to check the identical files with a preview and to tick the files to delete."""

    @classmethod
    def show_and_wait(cls, scan_result: ScanResult, state: SelectionState) -> bool:
        """Open the window and wait until it is closed. True if the ticked files should be deleted.

        The window is deleted afterwards. Lambdas in its signal connections refer to it, and as these
        connections live in Qt, Python would never notice that the window is unused and keep it with
        all its preview images until the program ends.
        """
        application = QtWidgets.QApplication.instance()
        if application is None:
            application = QtWidgets.QApplication([sys.argv[0]])
            # The video decoder would print technical details of every file into the console
            QtCore.QLoggingCategory.setFilterRules(QT_LOGGING_RULES)
            apply_dark_theme(application)
        window = cls(scan_result, state)
        try:
            return window._run(application)
        finally:
            # Safe here: background work only runs in the event loop, and closing the window stopped it
            shiboken6.delete(window)

    def __init__(self, scan_result: ScanResult, state: SelectionState) -> None:
        super().__init__()
        self._scan_result = scan_result
        self._groups = scan_result.groups
        self._state = state
        self._priority_entries: List[str] = list(state.priority_entries)
        self._was_confirmed = False
        self._thumbnail_provider = ShellThumbnailProvider()
        self._model = DuplicateTreeModel(scan_result, set(state.marked_paths), self._thumbnail_provider, self)
        self._model.marks_changed.connect(self._update_summary)
        self._preview_timer = self._create_single_shot_timer(PREVIEW_DELAY_MILLISECONDS, self._show_current_preview)
        self._thumbnail_timer = self._create_single_shot_timer(THUMBNAIL_DELAY_MILLISECONDS,
                                                               self._request_visible_thumbnails)

        self.setWindowTitle(f"{WINDOW_TITLE}: tick the files to delete")
        self._build_layout()
        self._fill_priority_list()
        # The first opening of a scan keeps the oldest copy, later openings show the ticks made so far
        if not state.rules_applied:
            self._apply_priority(self._groups)
            state.rules_applied = True
        self._update_summary()
        self._open_rows()
        resize_to_screen_share(self, WINDOW_SCREEN_SHARE)

    # ==== Window lifecycle ====================================================

    def _run(self, application: QtWidgets.QApplication) -> bool:
        """Show the window and wait until it closes. Ctrl+C in the console closes it as well."""
        previous_handler = signal.signal(signal.SIGINT, self._handle_interrupt)
        # Qt runs in C++, this timer lets Python notice Ctrl+C in the console
        interrupt_timer = QtCore.QTimer(self)
        interrupt_timer.timeout.connect(lambda: None)
        interrupt_timer.start(INTERRUPT_CHECK_MILLISECONDS)
        try:
            self.show()
            bring_window_to_front(self)
            self._apply_thumbnail_size(self._thumbnail_slider.value())
            self._select_first_file()
            application.exec()
        finally:
            interrupt_timer.stop()
            signal.signal(signal.SIGINT, previous_handler)
        return self._was_confirmed

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Store the ticks for the next opening and stop all background work."""
        self._state.marked_paths = set(self._model.marked_paths)
        self._state.priority_entries = list(self._priority_entries)
        self._preview_timer.stop()
        self._thumbnail_timer.stop()
        self._model.stop_thumbnails()
        self._preview.shutdown()
        super().closeEvent(event)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self._thumbnail_timer.start()

    def _cancel(self) -> None:
        self._was_confirmed = False
        self.close()

    def _continue(self) -> None:
        marked_file_count, _, no_copy_count = self._model.marked_totals()
        if not marked_file_count:
            QtWidgets.QMessageBox.information(self, WINDOW_TITLE, "No file is ticked for deletion.")
            return
        if no_copy_count and not self._ask_yes_no(
                f"Every copy is ticked for {format_quantity(no_copy_count, 'file')}, so no copy of "
                f"{'it' if no_copy_count == 1 else 'them'} will remain.\n\nContinue anyway?"):
            return
        self._was_confirmed = True
        self.close()

    def _handle_interrupt(self, signal_number: int, stack_frame) -> None:
        print("\n  Ctrl+C received, closing the selection window ...", flush=True)
        self._cancel()

    # ==== Layout ==============================================================

    def _build_layout(self) -> None:
        """Folder bar on top, then priority, list and preview side by side, the footer below."""
        root_widget = QtWidgets.QWidget()
        root_widget.setObjectName("root")
        layout = QtWidgets.QVBoxLayout(root_widget)
        layout.setContentsMargins(WINDOW_MARGIN, WINDOW_MARGIN, WINDOW_MARGIN, WINDOW_MARGIN)
        layout.setSpacing(WINDOW_MARGIN)
        layout.addLayout(self._build_folder_bar())

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.setHandleWidth(SPLITTER_HANDLE_WIDTH)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_priority_card())
        splitter.addWidget(self._build_list_card())
        splitter.addWidget(self._build_preview_card())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes(SPLITTER_SIZES)
        layout.addWidget(splitter, 1)
        layout.addWidget(self._build_footer())
        self.setCentralWidget(root_widget)

    def _build_folder_bar(self) -> QtWidgets.QHBoxLayout:
        """Folder letters with their paths in one line."""
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(CARD_SPACING)
        for root_index, folder in enumerate(self._scan_result.root_folders):
            badge = QtWidgets.QLabel(folder_label(root_index))
            badge.setObjectName("badge")
            layout.addWidget(badge)
            layout.addWidget(create_secondary_label(to_window_text(folder), word_wrap=False))
            layout.addSpacing(WINDOW_MARGIN)
        layout.addStretch(1)
        return layout

    def _build_priority_card(self) -> QtWidgets.QWidget:
        """Panel with the priority list and its buttons."""
        card, layout = create_card("Folder priority")
        layout.addWidget(create_secondary_label("The top folder is kept first. Folders below "
                                                "<all other locations> are deleted first."))
        self._priority_list = QtWidgets.QListWidget()
        self._priority_list.setToolTip(PRIORITY_HELP_TEXT)
        # Long paths are shortened in the middle, so drive and last folder stay visible
        self._priority_list.setTextElideMode(QtCore.Qt.TextElideMode.ElideMiddle)
        self._priority_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self._priority_list, 1)
        entry_layout = QtWidgets.QHBoxLayout()
        self._path_entry = QtWidgets.QLineEdit()
        self._path_entry.setPlaceholderText("F:\\Folder")
        self._path_entry.returnPressed.connect(self._add_typed_priority_entry)
        entry_layout.addWidget(self._path_entry, 1)
        entry_layout.addWidget(create_button("Browse", self._browse_priority_folder))
        layout.addLayout(entry_layout)
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(create_button("Add", self._add_typed_priority_entry,
                                               tooltip="Add the folder typed above to the list"))
        buttons_layout.addWidget(create_button("\u2191", lambda: self._move_priority_entry(-1), tooltip="Move up"))
        buttons_layout.addWidget(create_button("\u2193", lambda: self._move_priority_entry(1), tooltip="Move down"))
        buttons_layout.addWidget(create_button("Remove", self._remove_priority_entry))
        layout.addLayout(buttons_layout)
        layout.addWidget(create_button("Apply folder priority", lambda: self._apply_priority(
            self._model.shown_groups), is_primary=True,
            tooltip="Ticks all files shown anew: the copy in the folder with the best priority is kept, "
                    "among equal priority the oldest copy"))
        return card

    def _build_list_card(self) -> QtWidgets.QWidget:
        """Panel with file type filter, select buttons, preview size and the list."""
        card, layout = create_card("")
        toolbar_layout = QtWidgets.QHBoxLayout()
        toolbar_layout.setSpacing(CARD_SPACING)
        self._file_type_combobox = QtWidgets.QComboBox()
        self._file_type_combobox.addItem(f"All file types ({format_count(len(self._groups))})", None)
        for extension, count in self._model.extension_counts():
            self._file_type_combobox.addItem(f"{format_extension(extension)} ({format_count(count)})", extension)
        self._file_type_combobox.currentIndexChanged.connect(self._apply_file_type_filter)
        toolbar_layout.addWidget(self._file_type_combobox)
        toolbar_layout.addWidget(create_button("Select all", lambda: self._mark_shown_files(True),
                                               tooltip="Tick every file shown, they will be deleted"))
        toolbar_layout.addWidget(create_button("Unselect all", lambda: self._mark_shown_files(False),
                                               tooltip="Untick every file shown, they will be kept"))
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(create_secondary_label("Preview size", word_wrap=False))
        self._thumbnail_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self._thumbnail_slider.setRange(THUMBNAIL_MINIMUM_SIZE, THUMBNAIL_MAXIMUM_SIZE)
        self._thumbnail_slider.setSingleStep(THUMBNAIL_SIZE_STEP)
        self._thumbnail_slider.setPageStep(THUMBNAIL_SIZE_STEP * 2)
        self._thumbnail_slider.setValue(THUMBNAIL_DEFAULT_SIZE)
        self._thumbnail_slider.setFixedWidth(160)
        self._thumbnail_slider.valueChanged.connect(self._apply_thumbnail_size)
        toolbar_layout.addWidget(self._thumbnail_slider)
        layout.addLayout(toolbar_layout)

        self._tree = DuplicateTreeView()
        self._tree.setModel(self._model)
        self._tree.setItemDelegate(HeaderRowDelegate(self._tree))
        self._tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self._tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self._tree.setUniformRowHeights(False)          # header rows with a preview image are higher
        # Scrolling by pixel would make Qt measure every row of the list in advance, which takes
        # half a minute with tens of thousands of rows. Scrolling by row measures only the visible ones.
        self._tree.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerItem)
        self._tree.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self._tree.setRootIsDecorated(False)            # no arrows, the list is always fully open
        self._tree.setItemsExpandable(False)
        self._tree.setIconSize(QtCore.QSize(THUMBNAIL_DEFAULT_SIZE, THUMBNAIL_DEFAULT_SIZE))
        self._tree.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.setAllColumnsShowFocus(True)
        header = self._tree.header()
        header.setStretchLastSection(False)
        # The row size hints carry no width, so a double click on a column border would shrink the column
        header.sectionHandleDoubleClicked.disconnect()
        for column, width in TREE_COLUMN_WIDTHS.items():
            header.resizeSection(column, width)
        self._tree.minimum_last_column_width = self._path_column_width()
        self._tree.fit_last_column()
        self._tree.customContextMenuRequested.connect(self._show_context_menu)
        self._tree.toggle_requested.connect(self._toggle_selected_rows)
        self._tree.selectionModel().currentChanged.connect(lambda current, previous: self._preview_timer.start())
        self._tree.verticalScrollBar().valueChanged.connect(lambda value: self._thumbnail_timer.start())
        layout.addWidget(self._tree, 1)
        layout.addWidget(create_secondary_label(LIST_HELP_TEXT))
        return card

    def _build_preview_card(self) -> QtWidgets.QWidget:
        card, layout = create_card("Preview")
        self._preview = PreviewWidget(self._thumbnail_provider, supported_image_extensions())
        layout.addWidget(self._preview, 1)
        return card

    def _build_footer(self) -> QtWidgets.QWidget:
        """Number of ticked files on the left, Cancel and Continue on the right."""
        card = QtWidgets.QFrame()
        card.setObjectName("card")
        layout = QtWidgets.QHBoxLayout(card)
        layout.setContentsMargins(CARD_PADDING, CARD_SPACING, CARD_PADDING, CARD_SPACING)
        self._summary_label = QtWidgets.QLabel()
        summary_font = self._summary_label.font()
        summary_font.setBold(True)
        self._summary_label.setFont(summary_font)
        layout.addWidget(self._summary_label)
        self._warning_label = QtWidgets.QLabel()
        self._warning_label.setObjectName("warning")
        layout.addSpacing(WINDOW_MARGIN)
        layout.addWidget(self._warning_label)
        layout.addStretch(1)
        layout.addWidget(create_button("Cancel", self._cancel))
        continue_button = create_button("Continue with the ticked files", self._continue, is_primary=True)
        continue_button.setDefault(True)
        layout.addWidget(continue_button)
        return card

    def _path_column_width(self) -> int:
        """Wide enough for the longest path, so the horizontal scrollbar can reach its end."""
        longest_path = max((duplicate_file.display_path for group in self._groups for duplicate_file in group.files),
                           key=len, default="")
        measured_width = self._tree.fontMetrics().horizontalAdvance(to_window_text(longest_path)) + 40
        return max(PATH_COLUMN_MINIMUM_WIDTH, min(measured_width, PATH_COLUMN_MAXIMUM_WIDTH))

    def _create_single_shot_timer(self, interval_milliseconds: int, callback: Callable[[], None]) -> QtCore.QTimer:
        timer = QtCore.QTimer(self)
        timer.setSingleShot(True)
        timer.setInterval(interval_milliseconds)
        timer.timeout.connect(callback)
        return timer

    # ==== List and preview ====================================================

    def _open_rows(self) -> None:
        """Open all header rows and let them span all columns."""
        self._tree.expandAll()
        root_index = QtCore.QModelIndex()
        for row in range(self._model.rowCount()):
            self._tree.setFirstColumnSpanned(row, root_index, True)

    def _apply_file_type_filter(self) -> None:
        self._model.set_extension_filter(self._file_type_combobox.currentData())
        self._open_rows()
        self._select_first_file()
        self._thumbnail_timer.start()

    def _select_first_file(self) -> None:
        first_file_index = self._model.index(0, 0, self._model.index(0, 0))
        if first_file_index.isValid():
            self._tree.setCurrentIndex(first_file_index)
        self._preview_timer.start()

    def _apply_thumbnail_size(self, size: int) -> None:
        self._tree.setIconSize(QtCore.QSize(size, size))
        self._model.set_thumbnail_size(size, self._tree.devicePixelRatioF())
        self._thumbnail_timer.start()

    def _request_visible_thumbnails(self) -> None:
        """Load the preview images of the rows visible at the moment."""
        viewport_height = self._tree.viewport().height()
        groups_by_number: Dict[int, DuplicateGroup] = {}
        index = self._tree.indexAt(QtCore.QPoint(1, 1))
        while index.isValid() and self._tree.visualRect(index).top() < viewport_height:
            group = self._model.group_at(index)
            groups_by_number[group.number] = group
            index = self._tree.indexBelow(index)
        self._model.request_thumbnails(list(groups_by_number.values()))

    def _show_current_preview(self) -> None:
        """Preview of the selected file, for a header row of its first file. All copies are identical."""
        index = self._tree.currentIndex()
        if not index.isValid():
            self._preview.show_file(None)
            return
        self._preview.show_file(self._model.file_at(index) or self._model.group_at(index).files[0])

    def _show_context_menu(self, position: QtCore.QPoint) -> None:
        """Short menu for a file row."""
        index = self._tree.indexAt(position)
        duplicate_file = self._model.file_at(index) if index.isValid() else None
        if duplicate_file is None:
            return
        self._tree.setCurrentIndex(index)
        folder = os.path.dirname(duplicate_file.display_path)
        menu = QtWidgets.QMenu(self)
        menu.addAction("Show in Explorer",
                       lambda: show_error_message(self, show_in_explorer(duplicate_file.display_path)))
        menu.addAction("Copy full path",
                       lambda: QtWidgets.QApplication.clipboard().setText(duplicate_file.display_path))
        menu.addSeparator()
        menu.addAction("Add folder to the priority, keep first", lambda: self._add_priority_entry(folder, 0))
        menu.addAction("Add folder to the priority, delete first",
                       lambda: self._add_priority_entry(folder, len(self._priority_entries)))
        menu.exec(self._tree.viewport().mapToGlobal(position))

    def _toggle_selected_rows(self) -> None:
        """Tick all selected files, or untick them if all of them are ticked. A header row stands for its files."""
        file_entries: List[Tuple[DuplicateGroup, DuplicateFile]] = []
        for index in self._tree.selectionModel().selectedRows(COLUMN_NAME):
            group = self._model.group_at(index)
            duplicate_file = self._model.file_at(index)
            file_entries.extend((group, selected_file) for selected_file in
                                ([duplicate_file] if duplicate_file is not None else group.files))
        if file_entries:
            is_marked = any(duplicate_file.path not in self._model.marked_paths
                            for _, duplicate_file in file_entries)
            self._model.set_file_marks(file_entries, is_marked)

    def _mark_shown_files(self, is_marked: bool) -> None:
        """Tick or untick every file the file type filter shows."""
        shown_groups = self._model.shown_groups
        self._model.set_group_marks([(group, list(group.files) if is_marked else []) for group in shown_groups])

    def _update_summary(self) -> None:
        file_count, total_bytes, no_copy_count = self._model.marked_totals()
        self._summary_label.setText(f"{format_quantity(file_count, 'file')} ticked, {format_size(total_bytes)}")
        self._warning_label.setText(f"No copy is kept of {format_quantity(no_copy_count, 'file')}"
                                    if no_copy_count else "")

    # ==== Rules ===============================================================

    def _apply_priority(self, groups: List[DuplicateGroup]) -> None:
        """Tick every copy except the one to keep: best priority, then the oldest. Replaces the ticks."""
        rules = KeepRules(self._priority_entries)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            self._model.set_group_marks([(group, rules.files_to_delete(group)) for group in groups])
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    # ==== Priority list =======================================================

    def _fill_priority_list(self, selected_row: Optional[int] = None) -> None:
        self._priority_list.clear()
        for entry in self._priority_entries:
            item = QtWidgets.QListWidgetItem(to_window_text(entry))
            item.setToolTip(to_window_text(entry))
            if entry == OTHER_LOCATIONS_ENTRY:
                item.setForeground(QtGui.QBrush(QtGui.QColor(SECONDARY_TEXT_COLOR)))
            self._priority_list.addItem(item)
        if selected_row is not None:
            self._priority_list.setCurrentRow(selected_row)

    def _add_typed_priority_entry(self) -> None:
        if self._add_priority_entry(self._path_entry.text(), None):
            self._path_entry.clear()

    def _browse_priority_folder(self) -> None:
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose a folder for the priority",
                                                            self._scan_result.root_folders[0])
        if folder:
            self._add_priority_entry(folder, None)

    def _add_priority_entry(self, raw_path: str, position: Optional[int]) -> bool:
        """Insert a path at position, None means directly above <all other locations>."""
        path, error_message = normalize_priority_path(raw_path)
        if path is None:
            QtWidgets.QMessageBox.warning(self, WINDOW_TITLE, error_message)
            return False
        if any(os.path.normcase(entry) == os.path.normcase(path) for entry in self._priority_entries):
            QtWidgets.QMessageBox.information(self, WINDOW_TITLE, f"Already in the list:\n{path}")
            return False
        if KeepRules([path, OTHER_LOCATIONS_ENTRY]).unused_entries(self._groups):
            QtWidgets.QMessageBox.information(self, WINDOW_TITLE, f"None of the files lies in this folder, "
                                                                  f"please check it for typing errors:\n{path}")
        if position is None:
            position = self._priority_entries.index(OTHER_LOCATIONS_ENTRY)
        position = max(0, min(position, len(self._priority_entries)))
        self._priority_entries.insert(position, path)
        self._fill_priority_list(position)
        return True

    def _move_priority_entry(self, offset: int) -> None:
        row = self._priority_list.currentRow()
        new_row = row + offset
        if row < 0 or not 0 <= new_row < len(self._priority_entries):
            return
        entries = self._priority_entries
        entries[row], entries[new_row] = entries[new_row], entries[row]
        self._fill_priority_list(new_row)

    def _remove_priority_entry(self) -> None:
        row = self._priority_list.currentRow()
        if row < 0 or self._priority_entries[row] == OTHER_LOCATIONS_ENTRY:
            return
        del self._priority_entries[row]
        self._fill_priority_list(min(row, len(self._priority_entries) - 1))

    # ==== Messages ============================================================

    def _ask_yes_no(self, question: str) -> bool:
        answer = QtWidgets.QMessageBox.warning(
            self, WINDOW_TITLE, question,
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No)
        return answer == QtWidgets.QMessageBox.StandardButton.Yes


# ==== Deletion ================================================================


class DuplicateDeleter:
    """Deletes the marked files after checking them and optionally removes empty folders."""

    def __init__(self, plan: DeletionPlan, deletion_log: Optional[DeletionLog]) -> None:
        self.plan = plan
        self.result = DeletionResult(plan=plan)
        self._deletion_log = deletion_log
        self._is_simulation = plan.method is DeletionMethod.SIMULATION
        self._recycle_bin = RecycleBin() if plan.method is DeletionMethod.RECYCLE_BIN else None
        self._batch_size = RECYCLE_BIN_BATCH_SIZE if self._recycle_bin else 1
        self._pending_files: List[Tuple[DuplicateFile, Optional[DuplicateFile]]] = []
        self._files_processed = 0
        self._interrupt_guard = InterruptGuard()
        activity = "Simulating" if self._is_simulation else "Deleting"
        self._reporter = ProgressReporter(activity, self._progress_text)
        self._reporter.current_item_label = "Current file"

    def run(self) -> DeletionResult:
        """Delete the files of the plan, then remove empty folders if wanted."""
        start_time = time.monotonic()
        with self._interrupt_guard, self._reporter:
            completed = self._delete_marked_files()
            if completed and self.plan.empty_folder_policy is not EmptyFolderPolicy.KEEP:
                self._remove_empty_folders()
        self.result.duration_seconds = time.monotonic() - start_time
        return self.result

    # ==== Files ===============================================================

    def _delete_marked_files(self) -> bool:
        """Check and delete the files of every group. False if cancelled."""
        for decision in self.plan.decisions:
            if self._interrupt_guard.was_requested:
                self.result.was_cancelled = True
                return False
            self._process_decision(decision)
            self._reporter.tick()
        self._process_pending_files()
        return True

    def _process_decision(self, decision: GroupDecision) -> None:
        """Queue the files of one group that are still safe to delete."""
        kept_file: Optional[DuplicateFile] = None
        if decision.files_to_keep:
            kept_file = self._find_unchanged_file(decision.files_to_keep)
            if kept_file is None:
                for duplicate_file in decision.files_to_delete:
                    self._skip(duplicate_file, "no kept copy of this file is unchanged since the scan")
                return

        for duplicate_file in decision.files_to_delete:
            self._reporter.current_item = duplicate_file.display_path
            change = describe_file_change(duplicate_file)
            if change is not None:
                self._skip(duplicate_file, change)
                continue
            if self.plan.verify_content and kept_file is not None:
                try:
                    has_same_content = files_have_same_content(duplicate_file.path, kept_file.path)
                except OSError as error:
                    self._skip(duplicate_file, f"content check failed: {describe_os_error(error)}")
                    continue
                if not has_same_content:
                    self._skip(duplicate_file, f"content differs from the kept copy {kept_file.display_path}")
                    continue
            self._queue_file(duplicate_file, kept_file)

    def _find_unchanged_file(self, files: List[DuplicateFile]) -> Optional[DuplicateFile]:
        for duplicate_file in files:
            if describe_file_change(duplicate_file) is None:
                return duplicate_file
        return None

    def _skip(self, duplicate_file: DuplicateFile, reason: str) -> None:
        self.result.skipped_files.add(duplicate_file.display_path, reason, duplicate_file.size_bytes)
        self._files_processed += 1
        self._log("SKIPPED", duplicate_file.display_path, reason)

    def _queue_file(self, duplicate_file: DuplicateFile, kept_file: Optional[DuplicateFile]) -> None:
        self._pending_files.append((duplicate_file, kept_file))
        if len(self._pending_files) >= self._batch_size:
            self._process_pending_files()

    def _process_pending_files(self) -> None:
        """Delete all queued files and record the outcome of each one."""
        if not self._pending_files:
            return
        batch, self._pending_files = self._pending_files, []
        outcomes = self._delete_files([duplicate_file.path for duplicate_file, _ in batch])
        for duplicate_file, kept_file in batch:
            self._files_processed += 1
            error_message = outcomes.get(duplicate_file.path, "no result from the deletion")
            kept_note = f"kept: {kept_file.display_path}" if kept_file is not None else "no copy kept"
            if error_message is None:
                self.result.deleted_paths.add(duplicate_file.path)
                self.result.deleted_files.add(duplicate_file.display_path, kept_note, duplicate_file.size_bytes)
                self._log("WOULD DELETE" if self._is_simulation else "DELETED", duplicate_file.display_path,
                          kept_note)
            else:
                self.result.failed_files.add(duplicate_file.display_path, error_message, duplicate_file.size_bytes)
                self._log("FAILED", duplicate_file.display_path, error_message)
        self._reporter.tick()

    def _delete_files(self, file_paths: List[str]) -> Dict[str, Optional[str]]:
        """Delete files with the chosen method and return an error message per path."""
        outcomes: Dict[str, Optional[str]] = {}
        deletable_paths: List[str] = []
        for file_path in file_paths:
            if has_unsafe_characters(os.path.basename(file_path)):
                outcomes[file_path] = "file name contains characters Windows cannot handle"
            else:
                deletable_paths.append(file_path)

        if self.plan.method is DeletionMethod.SIMULATION:
            outcomes.update((file_path, None) for file_path in deletable_paths)
        elif self.plan.method is DeletionMethod.PERMANENT:
            outcomes.update((file_path, remove_path(file_path, os.remove)) for file_path in deletable_paths)
        elif deletable_paths and self._recycle_bin is not None:
            outcomes.update(self._recycle_bin.move_files(deletable_paths))
        return outcomes

    # ==== Empty folders =======================================================

    def _remove_empty_folders(self) -> None:
        """Remove empty folders bottom up, never a chosen folder itself.

        The chosen folders are walked again after deleting, with the same rules
        as the scan, so links and excluded system folders are never entered.
        Skipped items, for example Thumbs.db, still count as content. Folders
        are removed with the method of the files, recycled or permanently.
        """
        folder_states, visit_order = self._walk_folders_for_removal()
        if folder_states is None:
            return
        remove_all = self.plan.empty_folder_policy is EmptyFolderPolicy.REMOVE_ALL
        # The reversed visiting order handles every subfolder before its parent
        for folder_path in reversed(visit_order):
            if self._interrupt_guard.was_requested:
                self.result.was_cancelled = True
                return
            folder_state = folder_states[folder_path]
            if folder_state.parent_path is None or folder_state.entry_count is None:
                continue
            # A simulation still sees the files it would delete, so they are subtracted
            simulated_file_count = folder_state.deleted_file_count if self._is_simulation else 0
            if folder_state.entry_count - simulated_file_count - folder_state.removed_subfolder_count > 0:
                continue
            became_empty = folder_state.deleted_file_count + folder_state.removed_subfolder_count > 0
            if not became_empty and not remove_all:
                continue

            display_path = to_display_path(folder_path)
            self._reporter.current_item = display_path
            error_message = self._remove_folder(folder_path, folder_state.volume)
            if error_message is None:
                self.result.removed_folders.add(display_path)
                folder_states[folder_state.parent_path].removed_subfolder_count += 1
                self._log("WOULD REMOVE" if self._is_simulation else "REMOVED", display_path + "\\")
            else:
                self.result.failed_folders.add(display_path, error_message)
                self._log("FAILED", display_path + "\\", error_message)
            self._reporter.tick()

    def _remove_folder(self, folder_path: str, volume: TargetVolume) -> Optional[str]:
        """Remove an empty folder with the method chosen for the files. Return an error message, None on success."""
        if self._is_simulation:
            return None
        # Permanent deletion, the recycle bin object exists only for its own method
        if self._recycle_bin is None:
            return remove_path(folder_path, os.rmdir)
        # The recycle bin was checked for the drives of the deleted files, other chosen folders may lie elsewhere
        if not volume.supports_recycle_bin:
            return f"the recycle bin is not available on {volume.description}"
        # The shell would also recycle a folder with content, os.rmdir only removes empty folders
        folder_change = describe_folder_change(folder_path)
        if folder_change is not None:
            return folder_change
        return self._recycle_bin.move_files([folder_path]).get(folder_path, "no result from the recycle bin")

    def _walk_folders_for_removal(self) -> Tuple[Optional[Dict[str, FolderState]], List[str]]:
        """Entry counts of all folders and their visiting order. None if Ctrl+C was pressed."""
        deleted_file_counts: Dict[str, int] = {}
        for deleted_path in self.result.deleted_paths:
            folder_key = os.path.normcase(os.path.dirname(deleted_path))
            deleted_file_counts[folder_key] = deleted_file_counts.get(folder_key, 0) + 1
        scan_result = self.plan.scan_result
        folder_states: Dict[str, FolderState] = {}
        visit_order: List[str] = []
        self._reporter.current_item_label = "Current folder"
        for root_folder in scan_result.root_folders:
            volume = TargetVolume(root_folder)
            walker = FolderWalker(root_folder, scan_result.include_system_files, volume.root_path, WalkStatistics())
            for folder_content in walker.iterate_folders():
                if self._interrupt_guard.was_requested:
                    self.result.was_cancelled = True
                    return None, visit_order
                self._reporter.current_item = to_display_path(folder_content.path)
                folder_states[folder_content.path] = FolderState(
                    parent_path=folder_content.parent_path,
                    entry_count=folder_content.entry_count,
                    volume=volume,
                    deleted_file_count=deleted_file_counts.get(os.path.normcase(folder_content.path), 0),
                )
                visit_order.append(folder_content.path)
                self._reporter.tick()
        return folder_states, visit_order

    # ==== Output ==============================================================

    def _log(self, status: str, display_path: str, note: str = "") -> None:
        if self._deletion_log is not None:
            self._deletion_log.write_entry(status, display_path, note)

    def _progress_text(self) -> str:
        verb = "would delete" if self._is_simulation else "deleted"
        progress_text = (f"checked {format_count(self._files_processed)}/{format_count(self.plan.file_count)} | "
                         f"{verb} {format_count(self.result.deleted_files.count)} | "
                         f"skipped {format_count(self.result.skipped_files.count)} | "
                         f"failed {format_count(self.result.failed_files.count)}")
        if self.result.removed_folders.count:
            progress_text += f" | folders removed {format_count(self.result.removed_folders.count)}"
        return progress_text


# ==== Reports =================================================================


class ReportBuilder:
    """Builds the text lines shown in the console and written to report files."""

    @staticmethod
    def folder_lines(root_folders: List[str]) -> List[str]:
        return [f"  {'Folder ' + folder_label(root_index):<16}: {folder}"
                for root_index, folder in enumerate(root_folders)]

    @staticmethod
    def scan_lines(result: ScanResult, group_limit: Optional[int], example_limit: int,
                   digest_length: Optional[int]) -> List[str]:
        """Summary of a scan with the first group_limit groups, None lists all groups."""
        title = "SCAN RESULT" + ("   (cancelled, incomplete)" if result.was_cancelled else "")
        lines = section_lines(title)
        lines.append(f"  {'Mode':<16}: {result.mode.value}")
        lines += ReportBuilder.folder_lines(result.root_folders)
        lines.append(f"  {'System files':<16}: {'included' if result.include_system_files else 'excluded'}")
        lines.append(f"  {'Comparison':<16}: {HASH_NAME} of the first {format_size(PARTIAL_HASH_BYTES)}, "
                     f"then of the full content")
        lines.append(f"  {'Duration':<16}: {format_duration(result.duration_seconds)}")

        statistics = result.scan_statistics
        lines.append("")
        lines.append(f"  {'Files found':<29}: {format_count(statistics.files_found)} "
                     f"({format_size(statistics.bytes_found)})")
        lines.append(f"  {'Candidates with same size':<29}: {format_count(statistics.same_size_files)}")
        lines.append(f"  {'Candidates with same start':<29}: {format_count(statistics.same_start_files)}")
        lines.append(f"  {'Identical files':<29}: {format_count(result.duplicate_file_count)} in "
                     f"{format_quantity(len(result.groups), 'group')}")
        lines.append(f"  {'Reclaimable':<29}: up to {format_size(result.reclaimable_bytes)} "
                     f"if one copy of each group is kept")
        lines.append(f"  {'Bytes read for hashing':<29}: {format_size(statistics.hashed_bytes)}")
        if result.mode is CompareMode.BETWEEN_FOLDERS and result.groups_with_internal_copies:
            lines.append(f"  {'Several copies in one folder':<29}: in "
                         f"{format_quantity(result.groups_with_internal_copies, 'group')}")

        if not result.was_cancelled:
            lines += ReportBuilder._group_listing(result, group_limit, digest_length)
        lines += ReportBuilder.walk_lines(result.walk_statistics, example_limit)
        scan_sections = [
            ("Hard links, listed once", statistics.hard_links),
            ("Unreadable files", statistics.unreadable_files),
            ("Changed during the scan", statistics.changed_files),
        ]
        for title, collection in scan_sections:
            lines += ReportBuilder._collection_lines(title, collection, example_limit, show_size=True)
        return lines

    @staticmethod
    def group_lines(group: DuplicateGroup, digest_length: Optional[int], is_between_mode: bool) -> List[str]:
        digest = group.digest if digest_length is None else group.digest[:digest_length]
        lines = ["", f"  #{group.number}  {digest}   {len(group.files)} files of {format_size(group.size_bytes)}, "
                     f"{format_size(group.reclaimable_bytes)} reclaimable"]
        for duplicate_file in group.files:
            lines.append(f"      {folder_label(duplicate_file.root_index):<8}"
                         f"{format_timestamp(duplicate_file.creation_time_ns):<21}"
                         f"{format_timestamp(duplicate_file.modification_time_ns):<21}"
                         f"{duplicate_file.display_path}")
        if is_between_mode:
            for root_index, count in group.folders_with_several_copies():
                lines.append(f"      Note: folder {folder_label(root_index)} holds {count} copies of this file")
        return lines

    @staticmethod
    def no_copy_lines(decisions: List[GroupDecision], group_limit: int) -> List[str]:
        """Identical files of which every copy is marked for deletion."""
        file_count = len(decisions)
        lines = ["", f"WARNING: every copy of {format_quantity(file_count, 'file')} is marked, no copy of "
                     f"{'it' if file_count == 1 else 'them'} will remain:"]
        for decision in decisions[:group_limit]:
            group = decision.group
            lines.append(f"  {format_group_label(group)}   {len(group.files)} copies of "
                         f"{format_size(group.size_bytes)}")
            lines += [f"      {duplicate_file.display_path}" for duplicate_file in group.files]
        if file_count > group_limit:
            lines.append(f"  ... and {format_count(file_count - group_limit)} more")
        return lines

    @staticmethod
    def plan_lines(plan: DeletionPlan) -> List[str]:
        """Deletion plan shown before the confirmation and written into the log."""
        scan_result = plan.scan_result
        lines = section_lines("DELETION PLAN")
        lines.append(f"  {'Mode':<16}: {scan_result.mode.value}")
        lines += ReportBuilder.folder_lines(scan_result.root_folders)
        lines.append(f"  {'Files to delete':<16}: {format_quantity(plan.file_count, 'file')}, "
                     f"{format_size(plan.total_bytes)}")
        for root_index, statistics in sorted(plan.statistics_per_folder().items()):
            lines.append(f"  {'  in folder ' + folder_label(root_index):<16}: "
                         f"{format_quantity(statistics.file_count, 'file')}, {format_size(statistics.total_bytes)}")
        if plan.groups_without_copy:
            kept_text = f"NO copy remains of {format_quantity(plan.groups_without_copy, 'file')}"
        else:
            kept_text = "at least one copy of every file remains"
        lines.append(f"  {'Kept copies':<16}: {kept_text}")
        lines.append(f"  {'Method':<16}: {plan.method.value}")
        lines.append(f"  {'Empty folders':<16}: {plan.empty_folder_policy.value}")
        check_text = "unchanged since the scan (file, size, modification time)"
        if plan.verify_content:
            check_text += " and byte by byte equal to the kept copy"
        lines.append(f"  {'Checks':<16}: {check_text}")
        lines.append(f"  {'Created':<16}: {datetime.now():%Y-%m-%d %H:%M:%S}")
        return lines

    @staticmethod
    def deletion_lines(result: DeletionResult, example_limit: int) -> List[str]:
        """Outcome of a deletion or simulation."""
        plan = result.plan
        is_simulation = plan.method is DeletionMethod.SIMULATION
        title = "SIMULATION RESULT (nothing was deleted)" if is_simulation else "DELETION RESULT"
        if result.was_cancelled:
            title += "   (cancelled, incomplete)"
        lines = section_lines(title)
        lines.append(f"  {'Method':<29}: {plan.method.value}")
        lines.append(f"  {'Duration':<29}: {format_duration(result.duration_seconds)}")
        lines.append(f"  {'Marked files':<29}: {format_count(plan.file_count)} ({format_size(plan.total_bytes)})")
        deleted_title = "Files that would be deleted" if is_simulation else "Deleted files"
        lines.append(f"  {deleted_title:<29}: {format_count(result.deleted_files.count)} "
                     f"({format_size(result.deleted_files.total_bytes)})")
        lines += ReportBuilder._collection_lines("Skipped files", result.skipped_files, example_limit, True)
        lines += ReportBuilder._collection_lines("Failed files", result.failed_files, example_limit, True)
        if plan.empty_folder_policy is not EmptyFolderPolicy.KEEP:
            removed_title = "Folders that would be removed" if is_simulation else "Removed empty folders"
            lines.append(f"  {removed_title:<29}: {format_count(result.removed_folders.count)}")
            lines += ReportBuilder._collection_lines("Folders not removed", result.failed_folders, example_limit,
                                                     False)
        return lines

    @staticmethod
    def walk_lines(statistics: WalkStatistics, example_limit: int) -> List[str]:
        lines = ["", f"  {'Folders read':<29}: {format_count(statistics.folders_read)}"]
        sections = [
            ("Skipped system files", statistics.skipped_system_files, True),
            ("Skipped system folders", statistics.skipped_system_folders, False),
            ("Skipped links and junctions", statistics.skipped_links, False),
            ("Unreadable folders or files", statistics.unreadable_items, False),
        ]
        for title, collection, show_size in sections:
            lines += ReportBuilder._collection_lines(title, collection, example_limit, show_size)
        return lines

    @staticmethod
    def _group_listing(result: ScanResult, group_limit: Optional[int], digest_length: Optional[int]) -> List[str]:
        """The groups with all their files, limited to group_limit groups."""
        groups = result.groups
        if not groups:
            return ["", "  No duplicates found."]
        if group_limit is None or len(groups) <= group_limit:
            shown_groups = groups
            heading = f"ALL {format_count(len(groups))} GROUPS, largest reclaimable size first"
        else:
            shown_groups = groups[:group_limit]
            heading = (f"LARGEST {format_count(group_limit)} OF {format_count(len(groups))} GROUPS, "
                       f"the selection window shows all")
        lines = ["", f"  {heading}", "  " + "=" * (LINE_WIDTH - 2),
                 f"      {'Folder':<8}{'Created':<21}{'Modified':<21}Full path"]
        is_between_mode = result.mode is CompareMode.BETWEEN_FOLDERS
        for group in shown_groups:
            lines += ReportBuilder.group_lines(group, digest_length, is_between_mode)
        return lines

    @staticmethod
    def _collection_lines(title: str, collection: PathCollection, example_limit: int,
                          show_size: bool) -> List[str]:
        """Count of a path collection and its first examples, nothing if it is empty."""
        if collection.count == 0:
            return []
        amount_text = format_count(collection.count)
        if show_size:
            amount_text += f" ({format_size(collection.total_bytes)})"
        lines = [f"  {title:<29}: {amount_text}"]
        for path, note in collection.examples[:example_limit]:
            lines.append(f"      {path}" + (f"   [{note}]" if note else ""))
        not_listed_count = collection.count - min(example_limit, len(collection.examples))
        if not_listed_count > 0:
            lines.append(f"      ... and {format_count(not_listed_count)} more")
        return lines


class ReportWriter:
    """Creates report files in the reports folder next to this script."""

    def __init__(self) -> None:
        script_folder = os.path.dirname(os.path.abspath(__file__))
        self.folder = os.path.join(script_folder, REPORT_FOLDER_NAME)

    def new_report_path(self, report_name: str) -> str:
        """Create the reports folder if needed and return a new file path with timestamp."""
        os.makedirs(self.folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.folder, f"{report_name}_{timestamp}.txt")
        copy_number = 2
        while os.path.exists(report_path):
            report_path = os.path.join(self.folder, f"{report_name}_{timestamp}_{copy_number}.txt")
            copy_number += 1
        return report_path

    def save_lines(self, report_name: str, lines: List[str]) -> str:
        report_path = self.new_report_path(report_name)
        with open(report_path, "w", encoding="utf-8", errors="replace") as report_file:
            report_file.write("\n".join(lines) + "\n")
        return report_path


class DeletionLog:
    """Log file with one line for every deleted, skipped, failed or removed item."""

    def __init__(self, file_path: str, header_lines: List[str]) -> None:
        self.file_path = file_path
        self._log_file = open(file_path, "w", encoding="utf-8", errors="replace")
        self.write_lines(header_lines + [""])

    def __enter__(self) -> DeletionLog:
        return self

    def __exit__(self, *exception_info) -> None:
        self._log_file.close()

    def write_entry(self, status: str, path: str, note: str = "") -> None:
        line = f"{status:<14}{path}"
        if note:
            line += f"   [{note}]"
        self._log_file.write(line + "\n")

    def write_lines(self, lines: List[str]) -> None:
        self._log_file.write("\n".join(lines) + "\n")


# ==== Console dialog ==========================================================


class ConsoleDialog:
    """Asks the user all questions in the console. Every question repeats until the answer is valid."""

    def ask_main_menu(self, last_scan: Optional[ScanResult]) -> Optional[MainMenuChoice]:
        """Return the chosen entry or None to exit. Entry 3 is offered only while a scan result is kept."""
        print("\n".join(section_lines("MAIN MENU")))
        options = [
            ("1", "Within folders    files that exist more than once anywhere in the folders"),
            ("2", "Between folders   files that exist in at least two of the folders"),
        ]
        if last_scan is not None:
            options.append(("3", f"Selection window  open it again for the last scan, "
                                 f"{format_count(len(last_scan.groups))} with copies left"))
        options.append(("0", "Exit"))
        choice = self._choose(options, default_key=None,
                              footer="Ctrl+C cancels a running step and returns to this menu.")
        return {"1": MainMenuChoice.WITHIN_FOLDERS, "2": MainMenuChoice.BETWEEN_FOLDERS,
                "3": MainMenuChoice.SELECTION_WINDOW}.get(choice)

    def ask_folders(self, current_folders: List[str], minimum_count: int) -> List[str]:
        """Keep the current folders, add to them or enter new ones, at least minimum_count."""
        print()
        usable_folders = self._recheck_folders(current_folders)
        initial_folders: List[str] = []
        first_answer: Optional[str] = None
        if usable_folders:
            print("Folders:")
            print("\n".join(format_folder_list(usable_folders)))
            if len(usable_folders) >= minimum_count:
                print("Press Enter to keep them, or type, paste or drag the first new folder here.")
                prompt = "Folder A [keep]: "
            else:
                print(f"This mode needs at least {minimum_count} folders. Press Enter to keep these and add more,")
                print("or type, paste or drag the first new folder here.")
                prompt = "Folder A [keep and add]: "
            first_answer = input(prompt).strip() or None
            if first_answer is None:
                if len(usable_folders) >= minimum_count:
                    return usable_folders
                initial_folders = usable_folders
        else:
            needed_text = "one folder" if minimum_count == 1 else f"at least {minimum_count} folders"
            print(f"This mode needs {needed_text}. Type, paste or drag them here one by one.")
        folders = self._ask_new_folders(minimum_count, initial_folders, first_answer)
        print("Folders:")
        print("\n".join(format_folder_list(folders)))
        return folders

    def _recheck_folders(self, folders: List[str]) -> List[str]:
        """Folders that still exist and are allowed, a drive may have been removed meanwhile."""
        usable_folders: List[str] = []
        for folder in folders:
            resolved_folder, error_message = resolve_target_folder(folder)
            if resolved_folder is None:
                print(f"  {error_message}")
            else:
                usable_folders.append(resolved_folder)
        return usable_folders

    def _ask_new_folders(self, minimum_count: int, initial_folders: List[str],
                         first_answer: Optional[str]) -> List[str]:
        """Ask for folders one by one, Enter ends the input once enough folders are given."""
        folders = list(initial_folders)
        pending_answer = first_answer
        while True:
            if pending_answer is None:
                can_finish = len(folders) >= minimum_count
                finish_hint = " (Enter to finish)" if can_finish else ""
                answer = input(f"Folder {folder_label(len(folders))}{finish_hint}: ").strip()
                if not answer:
                    if can_finish:
                        return folders
                    print(f"  At least {minimum_count} folders are needed.")
                    continue
            else:
                answer, pending_answer = pending_answer, None
            # Several folders dragged at once arrive in one line
            for raw_folder in split_folder_input(answer):
                folder, error_message = resolve_target_folder(raw_folder)
                if folder is not None:
                    error_message = find_folder_overlap(folder, folders)
                if folder is None or error_message:
                    print(f"  {error_message}")
                    continue
                folders.append(folder)
                print(f"  Folder {folder_label(len(folders) - 1)}: {folder}")

    def ask_include_system_files(self) -> bool:
        print()
        print('Operating system files are files and folders with the Windows "System" attribute')
        print("and well known system items such as $RECYCLE.BIN, System Volume Information,")
        print("pagefile.sys, desktop.ini or Thumbs.db. Excluded system folders are not entered.")
        return self._ask_yes_no("Include operating system files?", default=False)

    def ask_save_reports(self, report_folder: str) -> bool:
        print()
        print(f"Reports are saved in {report_folder}")
        return self._ask_yes_no("Save the list of duplicates and the deletion log as text files?", default=False)

    def ask_open_selection(self) -> bool:
        print()
        print("The selection window shows all duplicates with a preview, all copies except the oldest are ticked.")
        return self._ask_yes_no("Open the selection window now?", default=True)

    def ask_reopen_selection(self) -> bool:
        print()
        return self._ask_yes_no("Open the selection window again?", default=True)

    def ask_delete_every_copy(self, file_count: int) -> bool:
        print()
        print("Answer n to keep every copy of them and delete the other marked files.")
        file_text = "this file" if file_count == 1 else f"these {format_count(file_count)} files"
        return self._ask_yes_no(f"Delete every copy of {file_text}?", default=False)

    def ask_deletion_method(self, volumes: List[TargetVolume]) -> DeletionMethod:
        """The recycle bin is offered only if every affected drive has one."""
        print()
        print("How should the files be deleted?")
        volumes_without_recycle_bin = [volume for volume in volumes if not volume.supports_recycle_bin]
        options = []
        if volumes_without_recycle_bin:
            for volume in volumes_without_recycle_bin:
                print(f"  The recycle bin is not available on {volume.description}.")
            default_key = "3"
        else:
            options.append(("1", "Move to the recycle bin"))
            default_key = "1"
        options.append(("2", "Delete permanently, cannot be undone"))
        options.append(("3", "Simulation only, shows what would be deleted"))
        choice = self._choose(options, default_key)
        return {"1": DeletionMethod.RECYCLE_BIN, "2": DeletionMethod.PERMANENT,
                "3": DeletionMethod.SIMULATION}[choice]

    def ask_empty_folder_policy(self) -> EmptyFolderPolicy:
        print()
        print("What should happen with empty folders after deleting?")
        choice = self._choose([
            ("1", "Keep all folders"),
            ("2", "Remove folders that became empty through this deletion"),
            ("3", "Remove all empty folders, also those that were empty before"),
        ], default_key="3")
        return {"1": EmptyFolderPolicy.KEEP, "2": EmptyFolderPolicy.REMOVE_EMPTIED,
                "3": EmptyFolderPolicy.REMOVE_ALL}[choice]

    def confirm_deletion(self, plan: DeletionPlan) -> bool:
        if plan.method is DeletionMethod.SIMULATION:
            print("\nSimulation: nothing will be deleted.")
            return True
        print()
        if plan.method is DeletionMethod.PERMANENT:
            print("WARNING: permanently deleted files cannot be restored.")
            keyword = "delete"
        else:
            keyword = "yes"
        answer = input(f'Type "{keyword}" to start, anything else cancels: ').strip().lower()
        return answer == keyword

    def _choose(self, options: List[Tuple[str, str]], default_key: Optional[str], footer: str = "") -> str:
        """Show numbered options and return the chosen key, Enter takes the default."""
        for key, label in options:
            default_marker = "   (default)" if key == default_key else ""
            print(f"  {key}  {label}{default_marker}")
        if footer:
            print(footer)
        valid_keys = [key for key, _ in options]
        prompt = f"Choice [{default_key}]: " if default_key else "Choice: "
        while True:
            answer = input(prompt).strip()
            if not answer and default_key:
                return default_key
            if answer in valid_keys:
                return answer
            print(f"  Please enter {', '.join(valid_keys[:-1])} or {valid_keys[-1]}.")

    def _ask_yes_no(self, question: str, default: bool) -> bool:
        """Ask a yes or no question. Enter takes the default, shown in brackets like in the other questions."""
        default_text = "y" if default else "n"
        while True:
            answer = input(f"{question} (y/n) [{default_text}]: ").strip().lower()
            if not answer:
                return default
            if answer in YES_ANSWERS:
                return True
            if answer in NO_ANSWERS:
                return False
            print("  Please answer y (yes) or n (no).")


# ==== Application =============================================================


class DuplicateFinderApp:
    """Main menu and the flow from the scan to the deletion."""

    def __init__(self, start_folders: List[str]) -> None:
        self._dialog = ConsoleDialog()
        self._report_writer = ReportWriter()
        self._last_folders = start_folders
        # The last scan stays available for entry 3 of the main menu until the next scan
        self._last_scan: Optional[ScanResult] = None
        self._last_selection = SelectionState()
        self._last_scan_saves_reports = False

    def run(self) -> int:
        """Main menu loop until the user exits."""
        print_banner()
        if self._last_folders:
            print("Folders:")
            print("\n".join(format_folder_list(self._last_folders)))

        while True:
            try:
                choice = self._dialog.ask_main_menu(self._last_scan)
            except (KeyboardInterrupt, EOFError):
                print()
                break
            if choice is None:
                break
            try:
                if choice is MainMenuChoice.SELECTION_WINDOW:
                    self._select_and_delete()
                elif choice is MainMenuChoice.BETWEEN_FOLDERS:
                    self._run_mode(CompareMode.BETWEEN_FOLDERS)
                else:
                    self._run_mode(CompareMode.WITHIN_FOLDERS)
            except KeyboardInterrupt:
                print("\n\nCancelled, back to the main menu.")
            except EOFError:
                print("\n\nNo more input, exiting.")
                break
            except OSError as error:
                # For example a disconnected drive or a full disk while writing a report
                print(f"\n\nError: {error}\nBack to the main menu.")
        print("Goodbye.")
        return 0

    def _run_mode(self, mode: CompareMode) -> None:
        """Ask for folders and options, scan and open the selection window."""
        minimum_count = 2 if mode is CompareMode.BETWEEN_FOLDERS else 1
        folders = self._dialog.ask_folders(self._last_folders, minimum_count)
        self._last_folders = folders
        include_system_files = self._dialog.ask_include_system_files()
        save_reports = self._dialog.ask_save_reports(self._report_writer.folder)

        scan_result = self._run_scan(mode, folders, include_system_files, save_reports)
        if scan_result.was_cancelled:
            print("\nThe scan was cancelled, its result is incomplete and cannot be used for deleting.")
            return
        if not scan_result.groups:
            print("\nNo duplicates found, nothing to delete.")
            self._last_scan = None
            return
        self._last_scan = scan_result
        self._last_selection = SelectionState()
        self._last_scan_saves_reports = save_reports
        if self._dialog.ask_open_selection():
            self._select_and_delete()
        else:
            print(REOPEN_HINT)

    def _run_scan(self, mode: CompareMode, folders: List[str], include_system_files: bool,
                  save_reports: bool) -> ScanResult:
        """Scan, show the result and save the report if wanted."""
        print()
        print(f"[{clock_time()}] Scan started, mode: {mode.value}")
        result = DuplicateScanner(mode, folders, include_system_files).run()
        state = "cancelled" if result.was_cancelled else "finished"
        print(f"[{clock_time()}] Scan {state} after {format_duration(result.duration_seconds)}")
        print("\n".join(ReportBuilder.scan_lines(result, CONSOLE_GROUP_LIMIT, CONSOLE_EXAMPLE_LIMIT,
                                                 SHORT_DIGEST_LENGTH)))
        if save_reports:
            self._save_report("duplicates_report", ReportBuilder.scan_lines(result, None, STORED_EXAMPLE_LIMIT, None))
        return result

    def _select_and_delete(self) -> None:
        """Selection window and deletion of the last scan, repeated while the user wants to go on."""
        scan_result, selection_state = self._last_scan, self._last_selection
        if scan_result is None:
            return
        while True:
            if not self._show_selection_window(scan_result, selection_state):
                print("The selection window was closed without continuing, nothing was deleted.")
                print(REOPEN_HINT)
                return
            deletion_result = self._plan_and_delete(scan_result, selection_state)
            if deletion_result is not None and deletion_result.plan.method is not DeletionMethod.SIMULATION:
                # Deleted files leave the groups, so the window can go on with what is left
                remove_deleted_files(scan_result, selection_state, deletion_result.deleted_paths)
                if not scan_result.groups:
                    print("\nNo duplicates of this scan are left.")
                    self._last_scan = None
                    return
                print(f"\nFiles with copies left of this scan: {format_count(len(scan_result.groups))}.")
            if not self._dialog.ask_reopen_selection():
                print(REOPEN_HINT)
                return

    def _show_selection_window(self, scan_result: ScanResult, selection_state: SelectionState) -> bool:
        print()
        print(f"[{clock_time()}] The selection window is open. If you do not see it, look in the taskbar.")
        print('           Close it or press "Continue with the ticked files" to come back here.')
        try:
            return SelectionWindow.show_and_wait(scan_result, selection_state)
        except Exception:
            # The scan result stays usable, so the window can be opened again from the main menu
            traceback.print_exc()
            print("The selection window failed, see above. Nothing was deleted.")
            return False

    def _plan_and_delete(self, scan_result: ScanResult, selection_state: SelectionState) -> Optional[DeletionResult]:
        """Build the plan from the marks and run it. None if nothing ran."""
        decisions = build_group_decisions(scan_result.groups, selection_state.marked_paths)
        decisions = self._confirm_groups_without_copy(decisions)
        if not decisions:
            print("\nNo files left to delete.")
            return None

        plan = DeletionPlan(
            scan_result=scan_result,
            decisions=decisions,
            method=self._dialog.ask_deletion_method(find_volumes(scan_result.root_folders, decisions)),
            empty_folder_policy=self._dialog.ask_empty_folder_policy(),
            verify_content=VERIFY_CONTENT_BEFORE_DELETION,
        )
        plan_lines = ReportBuilder.plan_lines(plan)
        print("\n".join(plan_lines))
        if not self._dialog.confirm_deletion(plan):
            print("Cancelled, nothing was deleted.")
            return None
        return self._run_deletion(plan, plan_lines)

    def _confirm_groups_without_copy(self, decisions: List[GroupDecision]) -> List[GroupDecision]:
        """Ask before deleting every copy of a group, otherwise leave such groups out."""
        decisions_without_copy = [decision for decision in decisions if not decision.files_to_keep]
        if not decisions_without_copy:
            return decisions
        print("\n".join(ReportBuilder.no_copy_lines(decisions_without_copy, CONSOLE_EXAMPLE_LIMIT)))
        if self._dialog.ask_delete_every_copy(len(decisions_without_copy)):
            return decisions
        print("  Every copy of these files is kept.")
        return [decision for decision in decisions if decision.files_to_keep]

    def _run_deletion(self, plan: DeletionPlan, plan_lines: List[str]) -> Optional[DeletionResult]:
        """Run the deletion, with a log if wanted. None if it could not start."""
        if not self._last_scan_saves_reports:
            return self._execute_deletion(plan, None)
        try:
            deletion_log = DeletionLog(self._report_writer.new_report_path("deletion_log"), plan_lines)
        except OSError as error:
            print(f"The deletion log could not be created ({describe_os_error(error)}), nothing was deleted.")
            return None
        with deletion_log:
            result = self._execute_deletion(plan, deletion_log)
        print(f"\nDeletion log saved: {deletion_log.file_path}")
        return result

    def _execute_deletion(self, plan: DeletionPlan, deletion_log: Optional[DeletionLog]) -> DeletionResult:
        """Delete the files of the plan and show the result."""
        print()
        if plan.method is DeletionMethod.RECYCLE_BIN:
            print("Note: if Windows cannot recycle a file, for example because it is larger than")
            print("the recycle bin, a Windows dialog asks before deleting it permanently.")
        activity = "Simulation" if plan.method is DeletionMethod.SIMULATION else "Deletion"
        print(f"[{clock_time()}] {activity} started")
        result = DuplicateDeleter(plan, deletion_log).run()
        state = "cancelled" if result.was_cancelled else "finished"
        print(f"[{clock_time()}] {activity} {state} after {format_duration(result.duration_seconds)}")
        print("\n".join(ReportBuilder.deletion_lines(result, CONSOLE_EXAMPLE_LIMIT)))
        if deletion_log is not None:
            deletion_log.write_lines([""] + ReportBuilder.deletion_lines(result, STORED_EXAMPLE_LIMIT))
        return result

    def _save_report(self, report_name: str, lines: List[str]) -> None:
        try:
            report_path = self._report_writer.save_lines(report_name, lines)
            print(f"\nReport saved: {report_path}")
        except OSError as error:
            print(f"\nThe report could not be saved: {describe_os_error(error)}")


# ==============================================================================
#   FUNCTIONS
# ==============================================================================

# ==== Paths ===================================================================


def to_extended_path(path: str) -> str:
    """Absolute path with the long path prefix, so deep paths and odd names work."""
    if path.startswith(EXTENDED_PATH_PREFIX):
        return path
    absolute_path = os.path.abspath(path)
    if absolute_path.startswith("\\\\"):
        return EXTENDED_UNC_PATH_PREFIX + absolute_path[2:]
    return EXTENDED_PATH_PREFIX + absolute_path


def to_display_path(path: str) -> str:
    """Path without the long path prefix, for output and for the Windows shell."""
    if path.startswith(EXTENDED_UNC_PATH_PREFIX):
        return "\\\\" + path[len(EXTENDED_UNC_PATH_PREFIX):]
    if path.startswith(EXTENDED_PATH_PREFIX) and path[5:6] == ":":
        return path[len(EXTENDED_PATH_PREFIX):]
    return path


def to_comparison_path(path: str) -> str:
    """Normalized lower case path for comparing paths."""
    return os.path.normcase(os.path.normpath(path))


def is_comparison_path_inside(path: str, folder: str) -> bool:
    """True if a comparison path equals folder or lies inside it. Partial names never match."""
    return path == folder or path.startswith(folder.rstrip("\\") + "\\")


def is_same_or_inside(path: str, base_path: str) -> bool:
    """True if path equals base_path or lies somewhere inside of it."""
    normalized_path = os.path.normcase(os.path.normpath(path))
    normalized_base_path = os.path.normcase(os.path.normpath(base_path))
    try:
        return os.path.commonpath([normalized_path, normalized_base_path]) == normalized_base_path
    except ValueError:
        return False


def find_protection_violation(folder: str) -> Optional[str]:
    """Return why a folder must not be used, or None if it is allowed."""
    windows_locations = [
        os.environ.get("SystemRoot"),
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
        os.environ.get("ProgramW6432"),
        os.environ.get("ProgramData"),
    ]
    for location in filter(None, windows_locations):
        if is_same_or_inside(folder, location):
            return f"it lies inside the Windows location {location}"
        if is_same_or_inside(location, folder):
            return f"it contains the Windows location {location}"
    user_profile = os.environ.get("USERPROFILE")
    if user_profile and is_same_or_inside(user_profile, folder):
        return f"it contains your user profile {user_profile}"
    volume_root = TargetVolume(folder).root_path
    for folder_name in ACTIVE_VOLUME_FOLDER_NAMES:
        active_folder = os.path.join(volume_root, folder_name)
        if is_same_or_inside(folder, active_folder):
            return f"Windows is using {active_folder} right now"
    return None


def resolve_target_folder(raw_input: str) -> Tuple[Optional[str], str]:
    """Turn user input into an existing, allowed folder. Return (folder, error message)."""
    cleaned_input = raw_input.strip().strip('"').strip("'").strip()
    if not cleaned_input:
        return None, "No folder entered."
    expanded_input = os.path.expandvars(os.path.expanduser(cleaned_input))
    if re.fullmatch(r"[A-Za-z]:", expanded_input):
        expanded_input += "\\"
    absolute_path = os.path.abspath(expanded_input)
    if os.path.isfile(absolute_path):
        return None, f"This is a file, not a folder: {absolute_path}"
    if not os.path.isdir(absolute_path):
        return None, f"Folder not found: {absolute_path}"
    # Links and substituted drives are resolved, so the checks see the real location
    resolved_path = to_display_path(os.path.realpath(absolute_path))
    violation = find_protection_violation(resolved_path)
    if violation:
        return None, f"This folder is not allowed because {violation}."
    return resolved_path, ""


def find_folder_overlap(folder: str, other_folders: List[str]) -> str:
    """Why folder cannot be used together with the other folders, empty if it can."""
    for other_folder in other_folders:
        is_inside_other = is_same_or_inside(folder, other_folder)
        contains_other = is_same_or_inside(other_folder, folder)
        if is_inside_other and contains_other:
            return f"This folder is already in the list: {other_folder}"
        if is_inside_other or contains_other:
            return f"Folders must not lie inside each other: {folder} and {other_folder}"
    return ""


def split_folder_input(text: str) -> List[str]:
    """Split typed input into folders. Several dragged folders arrive in one line, quoted if needed."""
    whole_input = text.strip().strip('"').strip()
    if os.path.isdir(whole_input):
        return [whole_input]
    tokens = [quoted or plain for quoted, plain in re.findall(r'"([^"]+)"|(\S+)', text)]
    if len(tokens) > 1 and all(re.match(r"[A-Za-z]:|\\\\", token) for token in tokens):
        return tokens
    return [text]


def normalize_priority_path(raw_path: str) -> Tuple[Optional[str], str]:
    """Turn a typed priority entry into a full path with drive letter. Return (path, error message)."""
    cleaned_path = raw_path.strip().strip('"').strip("'").strip()
    if not cleaned_path:
        return None, "No path entered."
    expanded_path = os.path.expandvars(cleaned_path)
    if re.fullmatch(r"[A-Za-z]:", expanded_path):
        expanded_path += "\\"
    if not os.path.splitdrive(expanded_path)[0] or not os.path.isabs(expanded_path):
        return None, f"Please enter the full path with drive letter, for example F:\\Downloads\n\n{cleaned_path}"
    normalized_path = os.path.normpath(expanded_path)
    if os.path.exists(normalized_path):
        # Links and substituted drives are resolved like the chosen folders
        normalized_path = to_display_path(os.path.realpath(normalized_path))
    return normalized_path, ""


def is_path_usable_by_shell(display_path: str) -> bool:
    """Check if the Windows shell addresses exactly this path and nothing else."""
    if display_path.startswith(EXTENDED_PATH_PREFIX) or len(display_path) > SHELL_MAX_PATH_LENGTH:
        return False
    for path_component in os.path.splitdrive(display_path)[1].split("\\"):
        if not path_component:
            continue
        # The shell would silently cut trailing dots and spaces or treat * and ? as wildcards
        if path_component[-1] in ". " or has_unsafe_characters(path_component):
            return False
        if path_component.split(".")[0].rstrip(" ").upper() in RESERVED_DEVICE_NAMES:
            return False
    return True


# ==== Files and folders =======================================================


def is_operating_system_item(name: str, attributes: int, is_folder: bool) -> bool:
    """True for items with the Windows system attribute or a well known system name."""
    if attributes & stat.FILE_ATTRIBUTE_SYSTEM:
        return True
    known_names = OPERATING_SYSTEM_FOLDER_NAMES if is_folder else OPERATING_SYSTEM_FILE_NAMES
    return name.lower() in known_names


def has_unsafe_characters(name: str) -> bool:
    """True if a name contains wildcards, control characters or characters invalid in Windows."""
    return any(character in UNSAFE_NAME_CHARACTERS or ord(character) < 32 for character in name)


def get_creation_time_ns(file_stat: os.stat_result) -> int:
    """Creation time. Python 3.12 added st_birthtime, before it st_ctime held it on Windows."""
    return getattr(file_stat, "st_birthtime_ns", file_stat.st_ctime_ns)


def expected_read_bytes(duplicate_file: DuplicateFile, byte_limit: Optional[int]) -> int:
    return duplicate_file.size_bytes if byte_limit is None else min(duplicate_file.size_bytes, byte_limit)


def describe_file_change(duplicate_file: DuplicateFile) -> Optional[str]:
    """Why a file is no longer the one the scan found, None if it is unchanged."""
    try:
        file_stat = os.stat(duplicate_file.path, follow_symlinks=False)
    except FileNotFoundError:
        return "no longer exists"
    except OSError as error:
        return describe_os_error(error)
    if file_stat.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        return "is a link now"
    if duplicate_file.file_id[1] and (file_stat.st_dev, file_stat.st_ino) != duplicate_file.file_id:
        return "replaced by another file since the scan"
    if file_stat.st_size != duplicate_file.size_bytes:
        return "size changed since the scan"
    if file_stat.st_mtime_ns != duplicate_file.modification_time_ns:
        return "modified since the scan"
    return None


def describe_folder_change(folder_path: str) -> Optional[str]:
    """Why a folder is no longer the empty folder the walk found, None if it is still empty."""
    try:
        if os.stat(folder_path, follow_symlinks=False).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            return "is a link now"
        with os.scandir(folder_path) as folder_iterator:
            if next(folder_iterator, None) is not None:
                return "no longer empty"
    except FileNotFoundError:
        return "no longer exists"
    except OSError as error:
        return describe_os_error(error)
    return None


def files_have_same_content(first_path: str, second_path: str) -> bool:
    """Compare two files byte by byte. Read errors raise OSError."""
    with open(first_path, "rb") as first_file, open(second_path, "rb") as second_file:
        while True:
            first_chunk = first_file.read(HASH_CHUNK_BYTES)
            second_chunk = second_file.read(HASH_CHUNK_BYTES)
            if first_chunk != second_chunk:
                return False
            if not first_chunk:
                return True


def remove_path(path: str, remove_function: Callable[[str], None]) -> Optional[str]:
    """Run os.remove or os.rmdir and return an error message or None on success.

    A read only attribute blocks deleting on Windows, so it is cleared once if needed.
    """
    try:
        remove_function(path)
        return None
    except FileNotFoundError:
        return "no longer exists"
    except PermissionError as error:
        if not clear_read_only_attribute(path):
            return describe_os_error(error)
        try:
            remove_function(path)
            return None
        except OSError as retry_error:
            return describe_os_error(retry_error)
    except OSError as error:
        return describe_os_error(error)


def clear_read_only_attribute(path: str) -> bool:
    """Clear the read only attribute. True if it was set and is cleared now."""
    try:
        attributes = os.stat(path, follow_symlinks=False).st_file_attributes
        if not attributes & stat.FILE_ATTRIBUTE_READONLY:
            return False
        os.chmod(path, stat.S_IWRITE)
        return True
    except OSError:
        return False


def describe_os_error(error: OSError) -> str:
    """Short readable reason of an operating system error."""
    return error.strerror or str(error)


def describe_shell_result(return_code: int, was_cancelled: bool) -> str:
    """Readable reason why the Windows shell did not recycle a file."""
    if was_cancelled:
        return "cancelled in the Windows dialog"
    if return_code == 0:
        return "could not be moved to the recycle bin"
    return SHELL_ERROR_MESSAGES.get(return_code, f"Windows shell error 0x{return_code:X}")


def get_file_extension(path: str) -> str:
    """Lower case extension including the dot, empty if the file has none."""
    extension = os.path.splitext(path)[1].lower()
    return "" if extension == "." else extension


def show_in_explorer(display_path: str) -> str:
    """Open the Explorer with the file selected. Return an error message, empty on success."""
    if not os.path.lexists(to_extended_path(display_path)):
        return f"The file no longer exists:\n{display_path}"
    try:
        # Explorer needs exactly this form, a list of arguments would be quoted differently
        subprocess.Popen(f'explorer /select,"{display_path}"')
    except OSError as error:
        return f"Explorer could not be started: {describe_os_error(error)}"
    return ""


# ==== Selection ===============================================================


def could_be_duplicates(files: Sequence, mode: CompareMode) -> bool:
    """True if the files can form a group: two or more, in mode 2 from two or more folders."""
    if len(files) < 2:
        return False
    if mode is CompareMode.WITHIN_FOLDERS:
        return True
    first_root_index = files[0].root_index
    return any(file_entry.root_index != first_root_index for file_entry in files)


def remove_deleted_files(scan_result: ScanResult, selection_state: SelectionState, deleted_paths: Set[str]) -> None:
    """Drop deleted files from the scan result and the groups that hold no duplicates any more."""
    remaining_groups: List[DuplicateGroup] = []
    for group in scan_result.groups:
        group.files = [duplicate_file for duplicate_file in group.files if duplicate_file.path not in deleted_paths]
        if could_be_duplicates(group.files, scan_result.mode):
            remaining_groups.append(group)
    scan_result.groups = remaining_groups
    remaining_paths = {duplicate_file.path for group in remaining_groups for duplicate_file in group.files}
    selection_state.marked_paths &= remaining_paths


def build_group_decisions(groups: List[DuplicateGroup], marked_paths: Set[str]) -> List[GroupDecision]:
    """Files to delete and to keep of every group with at least one marked file."""
    decisions: List[GroupDecision] = []
    for group in groups:
        files_to_delete = [duplicate_file for duplicate_file in group.files if duplicate_file.path in marked_paths]
        if files_to_delete:
            files_to_keep = [duplicate_file for duplicate_file in group.files
                             if duplicate_file.path not in marked_paths]
            decisions.append(GroupDecision(group, files_to_delete, files_to_keep))
    return decisions


def find_volumes(root_folders: List[str], decisions: List[GroupDecision]) -> List[TargetVolume]:
    """Drives that hold files to delete, each one once."""
    root_indexes = sorted({duplicate_file.root_index for decision in decisions
                           for duplicate_file in decision.files_to_delete})
    volumes_by_root_path: Dict[str, TargetVolume] = {}
    for root_index in root_indexes:
        volume = TargetVolume(root_folders[root_index])
        volumes_by_root_path.setdefault(os.path.normcase(volume.root_path), volume)
    return list(volumes_by_root_path.values())


# ==== Formatting ==============================================================


def format_count(number: int) -> str:
    return f"{number:,}"


def format_quantity(number: int, noun: str) -> str:
    """Number with a noun in singular or plural, for example 1 group or 2 groups."""
    return f"{number:,} {noun}" + ("" if number == 1 else "s")


def format_size(size_bytes: int) -> str:
    """Readable size with 1024 based units, as shown by Windows Explorer."""
    units = ("B", "KB", "MB", "GB", "TB", "PB")
    size = float(size_bytes)
    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{size_bytes:,} B"
    return f"{size:,.1f} {units[unit_index]}"


def format_duration(seconds: float) -> str:
    hours, remainder = divmod(int(seconds), 3600)
    minutes, remaining_seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"


def format_media_time(milliseconds: int) -> str:
    """Playing time as minutes:seconds, with hours in front if needed."""
    minutes, seconds = divmod(max(0, milliseconds) // 1000, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"


def format_timestamp(time_ns: int) -> str:
    """Local date and time, broken timestamps of damaged drives become "unknown"."""
    try:
        return datetime.fromtimestamp(time_ns / 1_000_000_000).strftime(TIMESTAMP_FORMAT)
    except (OSError, OverflowError, ValueError):
        return UNKNOWN_TIMESTAMP_TEXT


def folder_label(root_index: int) -> str:
    """Letter of a folder in the folder list: A to Z, then AA, AB and so on."""
    label = ""
    number = root_index + 1
    while number:
        number, remainder = divmod(number - 1, 26)
        label = chr(ord("A") + remainder) + label
    return label


def format_folder_list(folders: List[str]) -> List[str]:
    return [f"  {folder_label(root_index):<3}{folder}" for root_index, folder in enumerate(folders)]


def format_group_label(group: DuplicateGroup) -> str:
    """Number and start of the digest of identical files, the same in the window, the console and the report."""
    return f"#{group.number}  {group.digest[:SHORT_DIGEST_LENGTH]}"


def format_extension(extension: str) -> str:
    return extension if extension else "(no extension)"


def to_window_text(text: str) -> str:
    """Text the window can show, broken characters of damaged file names become question marks."""
    return text.encode("utf-8", "replace").decode("utf-8")


def shorten_text(text: str, maximum_length: int) -> str:
    if len(text) <= maximum_length:
        return text
    return text[:max(0, maximum_length - 3)] + "..."


def clock_time() -> str:
    return datetime.now().strftime("%H:%M:%S")


def section_lines(title: str) -> List[str]:
    return ["", "=" * LINE_WIDTH, f"  {title}", "=" * LINE_WIDTH]


# ==== Preview and window ======================================================


def supported_image_extensions() -> Set[str]:
    """Extensions of the image formats Qt can read. PDF files have a view of their own."""
    return {"." + bytes(image_format).decode("ascii", "replace").lower()
            for image_format in QtGui.QImageReader.supportedImageFormats()} - PDF_EXTENSIONS


def find_preview_kind(path: str, image_extensions: Set[str]) -> PreviewKind:
    """How the preview shows a file, decided by its extension."""
    extension = os.path.splitext(path)[1].lower()
    if extension in PDF_EXTENSIONS:
        return PreviewKind.PDF
    if extension in VIDEO_EXTENSIONS:
        return PreviewKind.VIDEO
    if extension in AUDIO_EXTENSIONS:
        return PreviewKind.AUDIO
    if extension in TEXT_EXTENSIONS:
        return PreviewKind.TEXT
    if extension in image_extensions:
        return PreviewKind.IMAGE
    return PreviewKind.OTHER


def read_image(path: str) -> Optional[QtGui.QImage]:
    """Image file turned upright as the camera noted it, very large images scaled down. None if unreadable."""
    image_reader = QtGui.QImageReader(path)
    image_reader.setAutoTransform(True)
    image_size = image_reader.size()
    if image_size.isValid() and max(image_size.width(), image_size.height()) > PREVIEW_IMAGE_MAX_PIXELS:
        image_reader.setScaledSize(image_size.scaled(PREVIEW_IMAGE_MAX_PIXELS, PREVIEW_IMAGE_MAX_PIXELS,
                                                     QtCore.Qt.AspectRatioMode.KeepAspectRatio))
    image = image_reader.read()
    return None if image.isNull() else image


def decode_text(data: bytes) -> str:
    """Text of the start of a file: UTF-16 if marked, else UTF-8, else the Windows code page 1252."""
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16", errors="replace")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        # A character cut off at the end of the shown part is no reason to give up on UTF-8
        if error.reason == "unexpected end of data":
            return data[:error.start].decode("utf-8-sig", errors="replace")
        return data.decode("cp1252", errors="replace")


def apply_dark_theme(application: QtWidgets.QApplication) -> None:
    """Dark colors and the style sheet for all windows of the program, also the title bar where Windows allows it."""
    application.setStyle("Fusion")
    try:
        application.styleHints().setColorScheme(QtCore.Qt.ColorScheme.Dark)
    except AttributeError:
        pass                    # older PySide6, the palette below still makes the window dark
    palette = QtGui.QPalette()
    color_roles = {
        QtGui.QPalette.ColorRole.Window: WINDOW_COLOR,
        QtGui.QPalette.ColorRole.WindowText: TEXT_COLOR,
        QtGui.QPalette.ColorRole.Base: BASE_COLOR,
        QtGui.QPalette.ColorRole.AlternateBase: SURFACE_COLOR,
        QtGui.QPalette.ColorRole.ToolTipBase: SURFACE_COLOR,
        QtGui.QPalette.ColorRole.ToolTipText: TEXT_COLOR,
        QtGui.QPalette.ColorRole.PlaceholderText: DISABLED_TEXT_COLOR,
        QtGui.QPalette.ColorRole.Text: TEXT_COLOR,
        QtGui.QPalette.ColorRole.Button: BUTTON_COLOR,
        QtGui.QPalette.ColorRole.ButtonText: TEXT_COLOR,
        QtGui.QPalette.ColorRole.BrightText: DELETE_TEXT_COLOR,
        QtGui.QPalette.ColorRole.Highlight: SELECTION_COLOR,
        QtGui.QPalette.ColorRole.HighlightedText: TEXT_COLOR,
        QtGui.QPalette.ColorRole.Link: ACCENT_COLOR,
    }
    for color_role, color in color_roles.items():
        palette.setColor(color_role, QtGui.QColor(color))
    for color_role in (QtGui.QPalette.ColorRole.Text, QtGui.QPalette.ColorRole.ButtonText,
                       QtGui.QPalette.ColorRole.WindowText):
        palette.setColor(QtGui.QPalette.ColorGroup.Disabled, color_role, QtGui.QColor(DISABLED_TEXT_COLOR))
    application.setPalette(palette)
    application.setStyleSheet(build_style_sheet())


def build_style_sheet() -> str:
    """Style sheet with the colors of the window theme filled in."""
    theme_colors = {
        "WINDOW_COLOR": WINDOW_COLOR, "SURFACE_COLOR": SURFACE_COLOR, "BASE_COLOR": BASE_COLOR,
        "BORDER_COLOR": BORDER_COLOR, "BUTTON_COLOR": BUTTON_COLOR, "BUTTON_HOVER_COLOR": BUTTON_HOVER_COLOR,
        "BUTTON_BORDER_COLOR": BUTTON_BORDER_COLOR, "TEXT_COLOR": TEXT_COLOR,
        "SECONDARY_TEXT_COLOR": SECONDARY_TEXT_COLOR, "DISABLED_TEXT_COLOR": DISABLED_TEXT_COLOR,
        "ACCENT_COLOR": ACCENT_COLOR, "ACCENT_HOVER_COLOR": ACCENT_HOVER_COLOR, "SELECTION_COLOR": SELECTION_COLOR,
        "WARNING_TEXT_COLOR": WARNING_TEXT_COLOR, "PREVIEW_BACKGROUND_COLOR": PREVIEW_BACKGROUND_COLOR,
        "SCROLLBAR_COLOR": SCROLLBAR_COLOR,
    }
    return string.Template(STYLE_SHEET_TEMPLATE).substitute(theme_colors)


def create_card(title: str) -> Tuple[QtWidgets.QFrame, QtWidgets.QVBoxLayout]:
    """Panel with a rounded border and an optional small title, the building block of the window."""
    card = QtWidgets.QFrame()
    card.setObjectName("card")
    layout = QtWidgets.QVBoxLayout(card)
    layout.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
    layout.setSpacing(CARD_SPACING)
    if title:
        title_label = QtWidgets.QLabel(title.upper())
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)
    return card, layout


def create_button(text: str, callback: Callable[[], None], is_primary: bool = False,
                  tooltip: str = "") -> QtWidgets.QPushButton:
    """Button in the style of the window, a primary button is blue and marks the main action."""
    button = QtWidgets.QPushButton(text)
    if is_primary:
        button.setObjectName("primary")
    if tooltip:
        button.setToolTip(tooltip)
    button.clicked.connect(callback)
    return button


def create_secondary_label(text: str, word_wrap: bool = True) -> QtWidgets.QLabel:
    """Grey label for hints and paths."""
    label = QtWidgets.QLabel(text)
    label.setObjectName("secondary")
    label.setWordWrap(word_wrap)
    return label


def show_error_message(parent: QtWidgets.QWidget, message: str) -> None:
    """Show a message box if there is an error message."""
    if message:
        QtWidgets.QMessageBox.warning(parent, WINDOW_TITLE, message)


def resize_to_screen_share(window: QtWidgets.QWidget, screen_share: float) -> None:
    """Size a window to a share of the screen and center it."""
    available_geometry = QtGui.QGuiApplication.primaryScreen().availableGeometry()
    window.resize(int(available_geometry.width() * screen_share), int(available_geometry.height() * screen_share))
    frame_geometry = window.frameGeometry()
    frame_geometry.moveCenter(available_geometry.center())
    window.move(frame_geometry.topLeft())


def silence_video_decoder() -> None:
    """Stop the FFmpeg libraries of Qt from printing warnings about media files into the console."""
    library_folder = os.path.dirname(QtCore.__file__)
    for library_path in glob.glob(os.path.join(library_folder, FFMPEG_UTILITY_LIBRARY_PATTERN)):
        try:
            # Windows hands out the library Qt has loaded already, so the setting reaches Qt
            ctypes.CDLL(library_path).av_log_set_level(AV_LOG_QUIET)
        except (OSError, AttributeError):
            pass


def bring_window_to_front(window: QtWidgets.QWidget) -> None:
    """Show a window above the console. Windows does not hand it the focus on its own."""
    user32 = ctypes.WinDLL("user32")
    set_window_position = user32.SetWindowPos
    set_window_position.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, wintypes.UINT]
    set_window_position.restype = wintypes.BOOL
    window_handle = wintypes.HWND(int(window.winId()))
    position_flags = SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
    # Topmost for a moment lifts the window above the console, then it behaves normally again
    set_window_position(window_handle, wintypes.HWND(HWND_TOPMOST), 0, 0, 0, 0, position_flags)
    set_window_position(window_handle, wintypes.HWND(HWND_NOTOPMOST), 0, 0, 0, 0, position_flags)
    window.raise_()
    window.activateWindow()


# ==== Program start ===========================================================


def print_banner() -> None:
    print("=" * LINE_WIDTH)
    print(f"  {PROGRAM_TITLE}")
    print(f"  {PROGRAM_SUBTITLE}")
    print("=" * LINE_WIDTH)


def configure_console_output() -> None:
    """Replace characters the console cannot show instead of crashing on odd file names."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def check_hash_algorithm() -> str:
    """Error message if the setting HASH_ALGORITHM cannot be used, empty if it works."""
    try:
        hashlib.new(HASH_ALGORITHM).hexdigest()
    except (ValueError, TypeError) as error:
        return f'The setting HASH_ALGORITHM = "{HASH_ALGORITHM}" cannot be used: {error}'
    return ""


def wait_for_enter(prompt: str) -> None:
    """Keep a console window opened by double click open until the user has read the output."""
    try:
        input(prompt)
    except (EOFError, KeyboardInterrupt):
        pass


def parse_command_line_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Finds files with identical content inside or between folders and deletes the copies "
                    "you choose.")
    parser.add_argument("folders", nargs="*", metavar="folder", help="folders to search, optional")
    return parser.parse_args()


def find_start_folders(folder_arguments: List[str]) -> Tuple[Optional[List[str]], str]:
    """Check the folders given at start. Return (folders, error message)."""
    folders: List[str] = []
    for folder_argument in folder_arguments:
        folder, error_message = resolve_target_folder(folder_argument)
        if folder is None:
            return None, f"{error_message} Put paths with spaces in quotes."
        overlap_message = find_folder_overlap(folder, folders)
        if overlap_message:
            return None, overlap_message
        folders.append(folder)
    return folders, ""


def show_start_error(error_message: str) -> int:
    """Explain why the program cannot start and return the exit code."""
    print_banner()
    print()
    print("The program cannot start with these folders.")
    print(f"  {error_message}")
    print()
    print("Start it with one or more folders, for example:")
    print('  python filemanagement_hashcomparison.py "F:\\Photos" "G:\\Backup\\Photos"')
    print("or drag the folders onto the script file, or start it without folders.")
    wait_for_enter("\nPress Enter to close ...")
    return 2


# ==============================================================================
#   MAIN
# ==============================================================================


def main() -> int:
    """Check the environment and the start folders, then run the main menu."""
    if os.name != "nt":
        print("This program runs on Windows only.")
        return 1
    configure_console_output()
    arguments = parse_command_line_arguments()
    try:
        hash_error_message = check_hash_algorithm()
        if hash_error_message:
            print(hash_error_message)
            wait_for_enter("\nPress Enter to close ...")
            return 1
        start_folders, error_message = find_start_folders(arguments.folders)
        if start_folders is None:
            return show_start_error(error_message)
        return DuplicateFinderApp(start_folders).run()
    except Exception:
        # Last line of defence, keeps a console window opened by double click open to show the error
        traceback.print_exc()
        wait_for_enter("\nAn unexpected error occurred, see above. Press Enter to close ...")
        return 1


if __name__ == "__main__":
    sys.exit(main())
