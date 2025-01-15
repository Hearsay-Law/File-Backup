# File Copier

A simple Python application that monitors a directory for new files and automatically copies them to a specified destination directory. Perfect for automating file transfers and backups.

## Features

- Real-time file monitoring
- Automatic file copying
- Colored console output for better visibility
- Error logging
- Easy directory switching via menu
- Configurable source and destination directories

## Requirements

- Python 3.6 or higher
- Required packages will be automatically installed on first run:
  - watchdog
  - colorama
  - keyboard

## Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/file-copier.git
   cd file-copier
   ```

2. Create your parameters file:

   - Copy `parameters.template.json` to `parameters.json`
   - Edit `parameters.json` with your desired source and destination directories:

   ```json
   {
     "base_source_dir": "C:\\Path\\To\\Your\\Source\\Directory",
     "destination_dir": "C:\\Path\\To\\Your\\Destination\\Directory"
   }
   ```

3. Run the application:
   ```bash
   python file_copier.py
   ```

## Usage

1. When the program starts, it will prompt you to enter a folder name in the format XX-XX (e.g., 01-04)
2. The program will then monitor the specified subfolder in your source directory
3. Any new or modified files will be automatically copied to the destination directory
4. Press ESC to open the menu where you can:
   - Change the source folder
   - Quit the program

## Log Files

The application creates a `file_copier.log` file in the same directory as the script, which contains detailed information about file operations and any errors that occur.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
